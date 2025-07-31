#!/usr/bin/env python3
"""
Demo script showing the new profile generation functionality
with AccountID-RoleName format
"""

import os
import sys
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kolja_aws.utils import construct_role_profile_section


def demo_profile_generation():
    """Demonstrate the new profile generation functionality"""
    print("🚀 Kolja AWS Profile Generation Demo")
    print("=" * 50)
    
    # Create a temporary config file for demonstration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.config', delete=False) as temp_file:
        # Initial config content
        initial_content = """# AWS Config File
[sso-session kolja-cn]
sso_start_url = https://xxx.awsapps.cn/start#replace-with-your-sso-url
sso_region = cn-northwest-1
sso_registration_scopes = sso:account:access

[sso-session kolja]
sso_start_url = https://xxx.awsapps.com/start#replace-with-your-sso-url
sso_region = ap-southeast-2
sso_registration_scopes = sso:account:access
"""
        temp_file.write(initial_content)
        temp_file_path = temp_file.name
    
    print(f"📁 Created temporary config file: {temp_file_path}")
    print("\n📋 Initial config content:")
    with open(temp_file_path, 'r') as f:
        print(f.read())
    
    # Demo data: simulate multiple accounts and roles
    demo_data = [
        {
            "sso_session": "kolja-cn",
            "account_id": "555286235540",
            "role_name": "AdminRole",
            "region": "cn-northwest-1"
        },
        {
            "sso_session": "kolja-cn", 
            "account_id": "555286235540",
            "role_name": "ReadOnlyRole",
            "region": "cn-northwest-1"
        },
        {
            "sso_session": "kolja",
            "account_id": "987654321098",
            "role_name": "DeveloperRole", 
            "region": "ap-southeast-2"
        },
        {
            "sso_session": "kolja",
            "account_id": "123456789012",
            "role_name": "PowerUserRole",
            "region": "ap-southeast-2"
        }
    ]
    
    print("\n🔧 Generating profiles with new AccountID-RoleName format...")
    print("-" * 60)
    
    # Generate profiles for each account-role combination
    for data in demo_data:
        account_id = data["account_id"]
        role_name = data["role_name"]
        profile_name = f"{account_id}-{role_name}"
        section_name = f"profile {profile_name}"
        
        print(f"Creating profile: {profile_name}")
        
        construct_role_profile_section(
            temp_file_path,
            section_name,
            data["sso_session"],
            account_id,
            role_name,
            data["region"]
        )
    
    print("\n✅ Profile generation completed!")
    print("\n📋 Final config content:")
    print("=" * 50)
    
    with open(temp_file_path, 'r') as f:
        final_content = f.read()
        print(final_content)
    
    print("\n🎯 Profile Summary:")
    print("-" * 30)
    
    # Extract and display generated profiles
    import re
    profile_matches = re.findall(r'\[profile ([^\]]+)\]', final_content)
    for i, profile in enumerate(profile_matches, 1):
        if '-' in profile:  # Only show our new format profiles
            account_id, role_name = profile.split('-', 1)
            print(f"{i}. Profile: {profile}")
            print(f"   Account: {account_id}")
            print(f"   Role: {role_name}")
            print()
    
    print("🔗 Usage with AWS Profile Switchers:")
    print("   aws --profile 555286235540-AdminRole s3 ls")
    print("   assume 555286235540-ReadOnlyRole")
    print("   granted assume 987654321098-DeveloperRole")
    
    # Clean up
    try:
        os.unlink(temp_file_path)
        print(f"\n🧹 Cleaned up temporary file: {temp_file_path}")
    except:
        pass


if __name__ == "__main__":
    demo_profile_generation()