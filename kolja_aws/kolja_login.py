import click
import subprocess
import os
from config import settings
from kolja_aws.utils import (
    remove_block_from_config, 
    get_latest_tokens_by_region,
    get_sso_sessions,
    get_section_metadata_from_template,
    construct_role_profile_section,
    get_available_sso_sessions,
    get_sso_session_config,
)


aws_config = settings.AWS_CONFIG


@click.group()
def cli():
    """Kolja CLI Tool for improve efficiency with aws."""


@click.group()
def aws():
    """Development commands."""


@click.command()
@click.argument('sso_sessions', nargs=-1)
def set(sso_sessions):
    """Set SSO session configuration with dynamic configuration support"""
    available_sessions = get_available_sso_sessions()
    
    # If no parameters provided, show available sessions
    if not sso_sessions:
        print("Available SSO sessions:")
        for session in available_sessions:
            print(f"  - {session}")
        print("\nUsage: kolja aws set <session_name> [<session_name2> ...]")
        return
    
    for sso_session in sso_sessions:
        if sso_session not in available_sessions:
            print(f"Warning: SSO session '{sso_session}' not found in configuration")
            print(f"Available sessions: {', '.join(available_sessions)}")
            continue
            
        try:
            # Remove existing configuration
            remove_block_from_config(os.path.expanduser(aws_config), f'sso-session {sso_session}')
            
            # Use updated utility function to get configuration content (supports dynamic configuration)
            section_content, _ = get_section_metadata_from_template(
                os.path.expanduser(aws_config), f'sso-session {sso_session}'
            )
            
            # Write configuration
            with open(os.path.expanduser(aws_config), 'a') as fw:
                fw.write('\n')  # Ensure line separator
                fw.write(section_content)
                fw.write('\n')  # Ensure ending line break
            
            print(f"✅ SSO session '{sso_session}' configuration updated")
            
        except Exception as e:
            print(f"❌ Failed to set SSO session '{sso_session}': {e}")
    

@click.command()
def get():
    try:
        res = get_sso_sessions()
    except UnboundLocalError:
        print("pls set sso session first")
        return
    return res


@click.command()
def login():
    # aws sso login --sso-session xxx
    sso_sessions = get_sso_sessions()
    for i in sso_sessions:

        result = subprocess.run(
            ['aws', 'sso', 'login', '--sso-session', i], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print(f"Login successful for session: {i}")
        else:
            print(f"Login failed for session: {i}")
            print(f"Error: {result.stderr}")
            print(f"👀It is recommended to remove the local AWS_PROFILE environment variable and retry")


@click.command()
def profiles():
    """Generate AWS profile sections in configuration file with dynamic configuration support"""
    latest_token = get_latest_tokens_by_region()
    
    try:
        sso_sessions = get_sso_sessions()
    except UnboundLocalError:
        print("Please set SSO session first")
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
                
                # TODO: Persist account information into aws.config
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
                
    


# register command
aws.add_command(login)
aws.add_command(get)
aws.add_command(set)
aws.add_command(profiles)
cli.add_command(aws)

# aws sso list-accounts --access-token  --region cn-north-1 --output json

if __name__ == "__main__":
    cli()
