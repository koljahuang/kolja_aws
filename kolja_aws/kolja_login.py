import click
import subprocess
import os
from kolja_aws.utils import (
    remove_block_from_config, 
    get_latest_tokens_by_region,
    get_sso_sessions,
    construct_role_profile_section,
    get_sso_session_config,
)
from kolja_aws.interactive_config import InteractiveConfig
from kolja_aws.session_config import SessionConfig
from kolja_aws.shell_installer import ShellInstaller


def get_version():
    """Get the current version of kolja-aws"""
    try:
        # Try importlib.metadata first (Python 3.8+)
        from importlib.metadata import version
        return version("kolja-aws")
    except Exception:
        try:
            # Fallback to pkg_resources
            import pkg_resources
            return pkg_resources.get_distribution("kolja-aws").version
        except Exception:
            pass
    
    # Final fallback: read from version file
    try:
        from kolja_aws.__version__ import __version__
        return f"{__version__}"
    except Exception:
        return "unknown"


aws_config = "~/.aws/config"


@click.group()
@click.version_option(version=get_version(), prog_name="kolja")
def cli():
    """Kolja CLI Tool for AWS SSO management with interactive configuration.
    
    This tool helps you manage AWS SSO sessions and profiles through
    interactive prompts, eliminating the need for configuration files.
    """


@click.group()
def aws():
    """AWS SSO session and profile management commands.
    
    Use these commands to interactively configure SSO sessions,
    login to AWS, and generate profiles for your accounts.
    """


@click.command()
@click.argument('session_name')
def set(session_name):
    """Configure an SSO session through interactive prompts.
    
    This command will guide you through entering:
    - SSO start URL (e.g., https://xxx.awsapps.com/start)
    - SSO region (e.g., ap-southeast-2, cn-northwest-1)
    
    The system automatically sets registration scopes to 'sso:account:access'.
    
    Example:
        kolja aws set my-company
    """
    try:
        # Initialize interactive configuration system
        interactive_config = InteractiveConfig()
        
        # Prompt user for SSO configuration parameters
        session_config = interactive_config.prompt_sso_config(session_name)
        
        # Display configuration summary for user review
        summary = interactive_config.get_config_summary(session_config, session_name)
        click.echo(summary)
        
        # Confirm with user before applying configuration
        if click.confirm("Apply this configuration?", default=True):
            # Remove existing configuration if it exists
            remove_block_from_config(os.path.expanduser(aws_config), f'sso-session {session_name}')
            
            # Generate AWS config section content
            section_content = session_config.to_aws_config_section(session_name)
            
            # Write configuration to AWS config file
            with open(os.path.expanduser(aws_config), 'a') as fw:
                fw.write('\n')  # Ensure line separator
                fw.write(section_content)
                fw.write('\n')  # Ensure ending line break
            
            click.echo(click.style(f"✅ SSO session '{session_name}' configuration applied successfully!", fg='green'))
        else:
            click.echo("Configuration cancelled.")
            
    except click.Abort:
        click.echo("\nConfiguration cancelled by user.")
    except Exception as e:
        click.echo(click.style(f"❌ Failed to set SSO session '{session_name}': {e}", fg='red'))
    

@click.command()
def get():
    """List all configured SSO sessions.
    
    Shows all SSO sessions that have been configured through
    the interactive 'kolja aws set' command.
    
    Example:
        kolja aws get
    """
    try:
        res = get_sso_sessions()
        if not res:
            click.echo("No SSO sessions found. Use 'kolja aws set <session_name>' to configure a session interactively.")
        return res
    except Exception as e:
        click.echo(f"Error retrieving SSO sessions: {e}")
        return


@click.command()
def login():
    """Login to all configured SSO sessions.
    
    Attempts to authenticate with all SSO sessions that have been
    configured through the interactive setup process.
    
    Example:
        kolja aws login
    """
    try:
        sso_sessions = get_sso_sessions()
        if not sso_sessions:
            click.echo("No SSO sessions found. Use 'kolja aws set <session_name>' to configure a session interactively first.")
            return
            
        for session in sso_sessions:
            click.echo(f"Logging into session: {session}")
            result = subprocess.run(
                ['aws', 'sso', 'login', '--sso-session', session], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                click.echo(click.style(f"✅ Login successful for session: {session}", fg='green'))
            else:
                click.echo(click.style(f"❌ Login failed for session: {session}", fg='red'))
                click.echo(f"Error: {result.stderr}")
                click.echo("💡 Tip: Remove the AWS_PROFILE environment variable and retry if needed")
                
    except Exception as e:
        click.echo(click.style(f"❌ Error during login process: {e}", fg='red'))


@click.command()
def profiles():
    """Generate AWS profile sections for all available accounts and roles.
    
    Automatically discovers all accounts and roles accessible through
    your configured SSO sessions and creates AWS profiles for them.
    
    Example:
        kolja aws profiles
    """
    try:
        latest_token = get_latest_tokens_by_region()
        sso_sessions = get_sso_sessions()
        
        if not sso_sessions:
            click.echo("No SSO sessions found. Use 'kolja aws set <session_name>' to configure a session interactively first.")
            return
    except Exception as e:
        click.echo(click.style(f"❌ Error initializing profiles command: {e}", fg='red'))
        return
    
    for sso_session in sso_sessions:
        try:
            # Use new utility function to get session configuration (supports dynamic configuration)
            section_dict = get_sso_session_config(sso_session)
            
            if section_dict:
                result = subprocess.run([
                                'aws', 'sso', 'list-accounts',
                                "--access-token", latest_token[section_dict["sso_region"]],
                                "--region", section_dict["sso_region"],
                                "--output", "json",
                            ], 
                            stdout=subprocess.PIPE,     
                            stderr=subprocess.PIPE,    
                            text=True                  
                        )
                
                if result.returncode != 0:
                    print(f"❌ Failed to get account list (session: {sso_session}): {result.stderr}")
                    continue
                
                accountList = eval(result.stdout)['accountList']
                accountIdList = map(lambda x: x['accountId'], accountList)
                
                for accountId in accountIdList:
                    result = subprocess.run([
                                    'aws', 'sso', 'list-account-roles', '--account-id', accountId,
                                    "--access-token", latest_token[section_dict["sso_region"]],
                                    "--region", section_dict["sso_region"],
                                    "--output", "json",
                                ], 
                                stdout=subprocess.PIPE,     
                                stderr=subprocess.PIPE,    
                                text=True                  
                            )
                    
                    if result.returncode != 0:
                        print(f"❌ Failed to get role list (account: {accountId}): {result.stderr}")
                        continue
                    
                    roleList = eval(result.stdout)['roleList']
                    roleNameList = map(lambda x: x['roleName'], roleList)
                    
                    for roleName in roleNameList:
                        print(f"Processing account ID: {accountId}, role: {roleName}")
                        # Use accountId-roleName format for profile section name
                        profile_name = f"{accountId}-{roleName}"
                        construct_role_profile_section(
                            os.path.expanduser(aws_config), f'profile {profile_name}',
                            sso_session, accountId, roleName, section_dict["sso_region"]
                        )
        
        except Exception as e:
            print(f"❌ Failed to process SSO session '{sso_session}': {e}")


@click.command()
@click.option('--uninstall', is_flag=True, help='Uninstall shell integration')
@click.option('--status', is_flag=True, help='Check installation status')
def sp(uninstall, status):
    """Install shell integration for quick AWS profile switching.
    
    This command installs a shell function 'sp' that provides an interactive
    AWS profile switcher. After installation, you can use 'sp' in your terminal
    to quickly switch between AWS profiles.
    
    Examples:
        kolja aws sp              # Install shell integration
        kolja aws sp --status     # Check installation status
        kolja aws sp --uninstall  # Remove shell integration
    """
    try:
        installer = ShellInstaller()
        
        if status:
            # Show installation status
            status_info = installer.get_installation_status()
            
            if status_info.get('installed', False):
                click.echo(click.style("✅ Shell integration is installed", fg='green'))
                click.echo(f"Shell type: {status_info.get('shell_type', 'unknown')}")
                click.echo(f"Config file: {status_info.get('config_file', 'unknown')}")
                
                backup_count = status_info.get('backup_count', 0)
                if backup_count > 0:
                    click.echo(f"Backups available: {backup_count}")
            else:
                click.echo(click.style("❌ Shell integration is not installed", fg='red'))
                if 'error' in status_info:
                    click.echo(f"Error: {status_info['error']}")
                    
        elif uninstall:
            # Uninstall shell integration
            # Note: installer.uninstall() will show its own progress messages
            if installer.uninstall():
                # Success message is already shown by installer.uninstall()
                pass
            else:
                click.echo(click.style("❌ Failed to uninstall shell integration", fg='red'))
                
        else:
            # Install shell integration
            # Note: installer.install() will show its own progress messages
            if installer.install():
                # Success message is already shown by installer.install()
                pass
            else:
                click.echo(click.style("❌ Failed to install shell integration", fg='red'))
                click.echo("\n💡 You can try the manual installation script:")
                click.echo("kolja-install-shell --interactive")
                
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg='red'))


# register command
aws.add_command(login)
aws.add_command(get)
aws.add_command(set)
aws.add_command(profiles)
aws.add_command(sp)
cli.add_command(aws)

# aws sso list-accounts --access-token  --region cn-north-1 --output json

if __name__ == "__main__":
    cli()
