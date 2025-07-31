#!/usr/bin/env python3
"""
Script to sanitize configuration files before committing to Git
"""

import os
import re
import shutil
from pathlib import Path


def sanitize_settings_toml(input_file, output_file):
    """Sanitize settings.toml file by replacing sensitive information"""
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found")
        return False
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Replace sensitive URLs
    content = re.sub(
        r'sso_start_url = "https://[^"]*"',
        'sso_start_url = "https://xxx.awsapps.com/start#replace-with-your-sso-url"',
        content
    )
    
    # Replace specific regions with generic ones
    content = re.sub(
        r'sso_region = "[^"]*"',
        'sso_region = "your-aws-region"',
        content
    )
    
    # Replace session names with generic ones
    content = re.sub(
        r'\[sso_sessions\.([^\]]+)\]',
        lambda m: f'[sso_sessions.your-session-name-{hash(m.group(1)) % 10}]',
        content
    )
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Sanitized {input_file} -> {output_file}")
    return True


def sanitize_sso_template(input_file, output_file):
    """Sanitize sso_session.template file by replacing sensitive information"""
    
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found")
        return False
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Replace sensitive URLs
    content = re.sub(
        r'sso_start_url = https://[^\s]*',
        'sso_start_url = https://xxx.awsapps.com/start#replace-with-your-sso-url',
        content
    )
    
    # Replace specific regions
    content = re.sub(
        r'sso_region = [^\s]*',
        'sso_region = your-aws-region',
        content
    )
    
    # Replace session names
    content = re.sub(
        r'\[sso-session ([^\]]+)\]',
        lambda m: f'[sso-session your-session-name-{hash(m.group(1)) % 10}]',
        content
    )
    
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Sanitized {input_file} -> {output_file}")
    return True


def main():
    """Main function to sanitize configuration files"""
    
    print("🔒 Sanitizing configuration files...")
    print()
    
    # Sanitize settings.toml
    if sanitize_settings_toml('settings.toml', 'settings.toml.example'):
        print("   Created sanitized settings.toml.example")
    
    # Sanitize sso_session.template
    if sanitize_sso_template('kolja_aws/sso_session.template', 'kolja_aws/sso_session.template.example'):
        print("   Created sanitized sso_session.template.example")
    
    print()
    print("🎯 Next steps:")
    print("   1. Review the .example files")
    print("   2. Add sensitive files to .gitignore")
    print("   3. Commit only the .example files")
    print("   4. Git hooks should already be set up from installation")


if __name__ == "__main__":
    main()