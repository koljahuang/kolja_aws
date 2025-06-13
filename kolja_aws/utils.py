import configparser
import os
import re
import json
from datetime import datetime
from config import settings
from io import StringIO


aws_config = settings.AWS_CONFIG


def remove_block_from_config(file_path, section):

    config = configparser.ConfigParser()
    
    config.read(file_path)

    if config.has_section(section):
        config.remove_section(section)
        print(f"Removed section: {section}")
    else:
        print(f"Section not found: {section}, Inserting...")
    
    with open(file_path, 'w') as config_file:
        config.write(config_file)


def get_sso_sessions():
    with open(os.path.expanduser(aws_config), 'r') as f:
        text = f.read()
    matches = re.findall(r'\[sso-session (\S+)\]', text)
    if matches:
        sso_sessions = []
        for sso_session_value in matches:
            sso_sessions.append(sso_session_value)
            print(f"sso_session: {sso_session_value}")
    return sso_sessions


def get_latest_tokens_by_region(cache_dir="~/.aws/sso/cache"):
    cache_dir = os.path.expanduser(cache_dir) 
    region_tokens = {}

    for filename in os.listdir(cache_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(cache_dir, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)

                expires_at = data.get("expiresAt")
                access_token = data.get("accessToken")
                region = data.get("region")

                if expires_at and access_token and region:
                    expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))  # 转换时间格式

                    if region not in region_tokens or expires_at_dt > region_tokens[region]["expiresAt"]:
                        region_tokens[region] = {
                            "expiresAt": expires_at_dt,
                            "accessToken": access_token,
                        }
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return {region: info["accessToken"] for region, info in region_tokens.items()}



def get_section_metadata_from_template(config_file, section):
    """
    Args:
        config_file (str): configuration path。
        section (str): section name。
    
    Returns:
        tuple: (section content as string format, section content as dict)
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    if section not in config:
        raise ValueError(f"Section '{section}' not found in the configuration file.")
    
    section_dict = dict(config[section])

    section_string = StringIO()
    config.write(section_string)
    section_string.seek(0)
    
    section_lines = []
    in_target_section = False
    for line in section_string:
        line = line.strip()
        if line.startswith(f"[{section}]"):
            in_target_section = True
        elif line.startswith("[") and in_target_section:
            break
        if in_target_section:
            section_lines.append(line)
    
    return "\n".join(section_lines), section_dict


def construct_role_profile_section(file_path, section,
                                   sso_session, sso_account_id, 
                                   sso_role_name, region):
    remove_block_from_config(file_path, section)
    profile_section = f"""
[profile {sso_account_id}]
sso_session = {sso_session}
sso_account_id = {sso_account_id}
sso_role_name = {sso_role_name}
region = {region}
output = text
"""
    with open(file_path, 'a') as f:
        f.write(profile_section)
    
    print(f"Updated section: profile {sso_account_id}")



if __name__ == "__main__":
    print(get_latest_tokens_by_region())
    # print(get_section_metadata_from_template("/Users/huangchao/.aws/config", "sso-session adpn"))