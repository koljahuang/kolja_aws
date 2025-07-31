#!/usr/bin/env python3
"""
Test profile generation functionality with account-role naming format
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kolja_aws.utils import construct_role_profile_section


class TestProfileGeneration(unittest.TestCase):
    """Test profile generation with account-role naming format"""
    
    def setUp(self):
        """Setup before tests"""
        self.test_config_content = """
[sso-session test-session]
sso_start_url = https://xxx.awsapps.com/start#replace-with-your-sso-url
sso_region = us-east-1
sso_registration_scopes = sso:account:access

[profile existing-profile]
sso_session = test-session
sso_account_id = 123456789012
sso_role_name = ExistingRole
region = us-east-1
output = text
"""
    
    def test_construct_role_profile_section_with_account_role_format(self):
        """Test profile section generation with account-role naming format"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.config', delete=False) as temp_file:
            temp_file.write(self.test_config_content)
            temp_file_path = temp_file.name
        
        try:
            # Test data
            sso_session = "test-session"
            account_id = "555286235540"
            role_name = "AdminRole"
            region = "us-east-1"
            expected_profile_name = f"{account_id}-{role_name}"
            section_name = f"profile {expected_profile_name}"
            
            # Call the function
            construct_role_profile_section(
                temp_file_path, section_name,
                sso_session, account_id, role_name, region
            )
            
            # Read the updated file
            with open(temp_file_path, 'r') as f:
                updated_content = f.read()
            
            # Verify the profile was created with correct format
            self.assertIn(f"[profile {expected_profile_name}]", updated_content)
            self.assertIn(f"sso_session = {sso_session}", updated_content)
            self.assertIn(f"sso_account_id = {account_id}", updated_content)
            self.assertIn(f"sso_role_name = {role_name}", updated_content)
            self.assertIn(f"region = {region}", updated_content)
            self.assertIn("output = text", updated_content)
            
            # Verify the expected profile name format
            self.assertEqual(expected_profile_name, "555286235540-AdminRole")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def test_multiple_roles_same_account(self):
        """Test generating profiles for multiple roles in the same account"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.config', delete=False) as temp_file:
            temp_file.write(self.test_config_content)
            temp_file_path = temp_file.name
        
        try:
            account_id = "555286235540"
            roles = ["AdminRole", "ReadOnlyRole", "DeveloperRole"]
            sso_session = "test-session"
            region = "us-east-1"
            
            # Generate profiles for all roles
            for role_name in roles:
                profile_name = f"{account_id}-{role_name}"
                section_name = f"profile {profile_name}"
                construct_role_profile_section(
                    temp_file_path, section_name,
                    sso_session, account_id, role_name, region
                )
            
            # Read the updated file
            with open(temp_file_path, 'r') as f:
                updated_content = f.read()
            
            # Verify all profiles were created
            for role_name in roles:
                expected_profile_name = f"{account_id}-{role_name}"
                self.assertIn(f"[profile {expected_profile_name}]", updated_content)
                self.assertIn(f"sso_role_name = {role_name}", updated_content)
            
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def test_profile_name_format_consistency(self):
        """Test that profile names follow consistent format"""
        test_cases = [
            ("123456789012", "AdminRole", "123456789012-AdminRole"),
            ("987654321098", "ReadOnlyRole", "987654321098-ReadOnlyRole"),
            ("555286235540", "DeveloperRole", "555286235540-DeveloperRole"),
            ("111222333444", "PowerUserRole", "111222333444-PowerUserRole"),
        ]
        
        for account_id, role_name, expected_profile_name in test_cases:
            with self.subTest(account_id=account_id, role_name=role_name):
                actual_profile_name = f"{account_id}-{role_name}"
                self.assertEqual(actual_profile_name, expected_profile_name)
    
    def test_profile_replacement(self):
        """Test that existing profiles are replaced correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.config', delete=False) as temp_file:
            # Create initial content with an existing profile
            initial_content = """
[profile 555286235540-AdminRole]
sso_session = old-session
sso_account_id = 555286235540
sso_role_name = AdminRole
region = us-west-2
output = json
"""
            temp_file.write(initial_content)
            temp_file_path = temp_file.name
        
        try:
            # Update the profile with new values
            account_id = "555286235540"
            role_name = "AdminRole"
            profile_name = f"{account_id}-{role_name}"
            section_name = f"profile {profile_name}"
            
            construct_role_profile_section(
                temp_file_path, section_name,
                "new-session", account_id, role_name, "us-east-1"
            )
            
            # Read the updated file
            with open(temp_file_path, 'r') as f:
                updated_content = f.read()
            
            # Verify the profile was updated
            self.assertIn(f"[profile {profile_name}]", updated_content)
            self.assertIn("sso_session = new-session", updated_content)
            self.assertIn("region = us-east-1", updated_content)
            self.assertIn("output = text", updated_content)
            
            # Verify old values are not present
            self.assertNotIn("sso_session = old-session", updated_content)
            self.assertNotIn("region = us-west-2", updated_content)
            self.assertNotIn("output = json", updated_content)
            
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass


if __name__ == '__main__':
    unittest.main()