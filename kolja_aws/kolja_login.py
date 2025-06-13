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
)


aws_config = settings.AWS_CONFIG
aws_region = settings.AWS_REGION


@click.group()
def cli():
    """Kolja CLI Tool for improve efficiency with aws."""


@click.group()
def aws():
    """Development commands."""


@click.command()
@click.argument('sso_sessions', nargs=-1)
def set(sso_sessions):
    # sso_sessions=list(sso_sessions)
    for sso_session in sso_sessions:
        if sso_session == "adpn-cn":
            remove_block_from_config(os.path.expanduser(aws_config), f'sso-session {sso_session}')
            section_content, _ = get_section_metadata_from_template("sso_session.template", f'sso-session {sso_session}')
            with open(os.path.expanduser(aws_config), 'a') as fw:
                fw.write(section_content)
        elif sso_session == "adpn":
            remove_block_from_config(os.path.expanduser(aws_config), f'sso-session {sso_session}')
            section_content, _ = get_section_metadata_from_template("sso_session.template", f'sso-session {sso_session}')
            with open(os.path.expanduser(aws_config), 'a') as fw:
                fw.write(section_content)
    

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


@click.command()
def profiles():
    latest_token = get_latest_tokens_by_region()
    try:
        sso_sessions = get_sso_sessions()
    except UnboundLocalError:
        print("pls set sso session first")
        return
    for sso_session in sso_sessions:
        # print(sso_session)
        _, section_dict = get_section_metadata_from_template("sso_session.template", f'sso-session {sso_session}')
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
        # TODO persist into aws.config
        accountList = eval(result.stdout)['accountList']
        accountIdList = map(lambda x: x['accountId'], accountList)
        for accountId in accountIdList:
            # print(accountId)
            # print(latest_token[section_dict["sso_region"]])
            # print(section_dict["sso_region"])
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
            roleList = eval(result.stdout)['roleList']
            roleNameList = map(lambda x: x['roleName'], roleList)
            for roleName in roleNameList:
                print(f"Dealing with accountId: {accountId}, Role: {roleName}")
                construct_role_profile_section(
                    os.path.expanduser(aws_config), f'profile {accountId}',
                    sso_session, accountId, roleName, section_dict["sso_region"]
                )
                
    


# register command
aws.add_command(login)
aws.add_command(get)
aws.add_command(set)
aws.add_command(profiles)
cli.add_command(aws)

# aws sso list-accounts --access-token  --region cn-north-1 --output json

if __name__ == "__main__":
    cli()
