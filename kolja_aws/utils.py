import configparser
import os
import re
import json
from datetime import datetime
from config import settings
from io import StringIO
import tempfile


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
                    expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))  # Convert time format

                    if region not in region_tokens or expires_at_dt > region_tokens[region]["expiresAt"]:
                        region_tokens[region] = {
                            "expiresAt": expires_at_dt,
                            "accessToken": access_token,
                        }
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return {region: info["accessToken"] for region, info in region_tokens.items()}



def _generate_dynamic_sso_template():
    """
    Dynamically generate SSO session template content from settings.toml
    
    Returns:
        str: Generated SSO session template content
    """
    try:
        # Check if settings has sso_sessions configuration
        if hasattr(settings, 'sso_sessions') and settings.sso_sessions:
            template_content = ""
            
            for session_name, session_config in settings.sso_sessions.items():
                # Validate required configuration fields
                if not all(key in session_config for key in ['sso_start_url', 'sso_region']):
                    continue
                
                # Set default registration_scopes
                registration_scopes = session_config.get('sso_registration_scopes', 'sso:account:access')
                
                # Generate configuration block
                template_content += f"[sso-session {session_name}]\n"
                template_content += f"sso_start_url = {session_config['sso_start_url']}\n"
                template_content += f"sso_region = {session_config['sso_region']}\n"
                template_content += f"sso_registration_scopes = {registration_scopes}\n\n"
            
            return template_content.strip()
    except Exception as e:
        print(f"Warning: Failed to generate dynamic SSO template: {e}")
    
    # If dynamic generation fails, fallback to reading template file
    template_file = os.path.join(os.path.dirname(__file__), 'sso_session.template')
    try:
        with open(template_file, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Failed to read template file: {e}")
        return ""


def get_section_metadata_from_template(config_file, section):
    """
    Get section metadata from configuration file or dynamically generated template
    
    Args:
        config_file (str): configuration path
        section (str): section name
    
    Returns:
        tuple: (section content as string format, section content as dict)
    """
    config = configparser.ConfigParser()
    
    # First try to read from actual configuration file
    if os.path.exists(config_file):
        config.read(config_file)
        
        if section in config:
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
    
    # If section not found in configuration file, try to get from dynamically generated template
    dynamic_template = _generate_dynamic_sso_template()
    if dynamic_template:
        # Create temporary file to parse dynamically generated template
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as temp_file:
            temp_file.write(dynamic_template)
            temp_file_path = temp_file.name
        
        try:
            temp_config = configparser.ConfigParser()
            temp_config.read(temp_file_path)
            
            if section in temp_config:
                section_dict = dict(temp_config[section])
                
                section_string = StringIO()
                temp_config.write(section_string)
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
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    raise ValueError(f"Section '{section}' not found in the configuration file or dynamic template.")


def get_available_sso_sessions():
    """
    Get all available SSO session names with dynamic configuration support
    
    Returns:
        list: SSO session name list
    """
    sessions = []
    
    # First try to get from dynamic configuration
    try:
        if hasattr(settings, 'sso_sessions') and settings.sso_sessions:
            sessions.extend(settings.sso_sessions.keys())
            return sessions
    except Exception as e:
        print(f"Warning: Failed to get sessions from dynamic config: {e}")
    
    # Fallback to getting from template file
    template_file = os.path.join(os.path.dirname(__file__), 'sso_session.template')
    try:
        with open(template_file, 'r') as f:
            content = f.read()
        matches = re.findall(r'\[sso-session (\S+)\]', content)
        sessions.extend(matches)
    except Exception as e:
        print(f"Warning: Failed to read template file: {e}")
    
    return sessions


def get_sso_session_config(session_name):
    """
    Get specified SSO session configuration information with dynamic configuration support
    
    Args:
        session_name (str): SSO session name
        
    Returns:
        dict: SSO session configuration information
    """
    # First try to get from dynamic configuration
    try:
        if hasattr(settings, 'sso_sessions') and settings.sso_sessions:
            if session_name in settings.sso_sessions:
                config = dict(settings.sso_sessions[session_name])
                # Ensure default registration_scopes
                if 'sso_registration_scopes' not in config:
                    config['sso_registration_scopes'] = 'sso:account:access'
                return config
    except Exception as e:
        print(f"Warning: Failed to get session config from dynamic config: {e}")
    
    # Fallback to getting from template file
    template_file = os.path.join(os.path.dirname(__file__), 'sso_session.template')
    try:
        config = configparser.ConfigParser()
        config.read(template_file)
        section_name = f"sso-session {session_name}"
        if section_name in config:
            return dict(config[section_name])
    except Exception as e:
        print(f"Warning: Failed to read session config from template: {e}")
    
    raise ValueError(f"SSO session '{session_name}' not found in configuration")


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


def write_dynamic_sso_template_to_file(output_path=None):
    """
    Write dynamically generated SSO template to file
    
    Args:
        output_path (str, optional): Output file path, defaults to sso_session.template
        
    Returns:
        str: Written file path
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), 'sso_session.template')
    
    template_content = _generate_dynamic_sso_template()
    
    if template_content:
        with open(output_path, 'w') as f:
            f.write(template_content)
        print(f"Dynamic SSO template written to: {output_path}")
        return output_path
    else:
        raise ValueError("Failed to generate dynamic SSO template content")



if __name__ == "__main__":
    print(get_latest_tokens_by_region())
    # print(get_section_metadata_from_template("/Users/huangchao/.aws/config", "sso-session kolja"))