"""
Tests for AWS profile loader
"""

import os
import tempfile
import pytest
from unittest.mock import patch
from kolja_aws.profile_loader import ProfileLoader
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import ProfileLoadError


class TestProfileLoader:
    """Test ProfileLoader class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a temporary AWS config file for testing
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.config')
        self.temp_config_path = self.temp_config.name
        
        # Write sample AWS config
        sample_config = """[default]
region = us-east-1
output = json

[profile 555286235540-AdministratorAccess]
sso_session = my-sso
sso_account_id = 555286235540
sso_role_name = AdministratorAccess
region = us-east-1

[profile 612674025488-AdministratorAccess]
sso_session = my-sso
sso_account_id = 612674025488
sso_role_name = AdministratorAccess
region = us-west-2

[profile regular-profile]
aws_access_key_id = AKIA...
aws_secret_access_key = secret...
region = eu-west-1

[sso-session my-sso]
sso_start_url = https://example.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
"""
        self.temp_config.write(sample_config)
        self.temp_config.close()
        
        self.loader = ProfileLoader(self.temp_config_path)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config_path):
            os.unlink(self.temp_config_path)
    
    def test_init_default_path(self):
        """Test ProfileLoader initialization with default path"""
        loader = ProfileLoader()
        expected_path = os.path.expanduser("~/.aws/config")
        assert loader.aws_config_path == expected_path
    
    def test_init_custom_path(self):
        """Test ProfileLoader initialization with custom path"""
        custom_path = "/custom/path/config"
        loader = ProfileLoader(custom_path)
        assert loader.aws_config_path == custom_path
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_current_profile_none(self):
        """Test getting current profile when AWS_PROFILE is not set"""
        current = self.loader.get_current_profile()
        assert current is None
    
    @patch.dict(os.environ, {'AWS_PROFILE': 'test-profile'})
    def test_get_current_profile_set(self):
        """Test getting current profile when AWS_PROFILE is set"""
        current = self.loader.get_current_profile()
        assert current == 'test-profile'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_load_profiles_success(self):
        """Test successful profile loading"""
        profiles = self.loader.load_profiles()
        
        # Should have 4 profiles: default, 2 SSO profiles, 1 regular profile
        assert len(profiles) == 4
        
        # Check profile names
        profile_names = [p.name for p in profiles]
        expected_names = ['default', '555286235540-AdministratorAccess', 
                         '612674025488-AdministratorAccess', 'regular-profile']
        assert set(profile_names) == set(expected_names)
        
        # Check SSO profile details
        sso_profile = next(p for p in profiles if p.name == '555286235540-AdministratorAccess')
        assert sso_profile.sso_session == 'my-sso'
        assert sso_profile.account_id == '555286235540'
        assert sso_profile.role_name == 'AdministratorAccess'
        assert sso_profile.region == 'us-east-1'
        assert sso_profile.is_sso_profile() is True
        
        # Check regular profile
        regular_profile = next(p for p in profiles if p.name == 'regular-profile')
        assert regular_profile.sso_session is None
        assert regular_profile.region == 'eu-west-1'
        assert regular_profile.is_sso_profile() is False
    
    @patch.dict(os.environ, {'AWS_PROFILE': '555286235540-AdministratorAccess'})
    def test_load_profiles_with_current(self):
        """Test profile loading with current profile set"""
        profiles = self.loader.load_profiles()
        
        # Find the current profile
        current_profile = next(p for p in profiles if p.is_current)
        assert current_profile.name == '555286235540-AdministratorAccess'
        
        # Current profile should be first in the list
        assert profiles[0].is_current is True
    
    def test_load_profiles_nonexistent_file(self):
        """Test profile loading with non-existent config file"""
        loader = ProfileLoader('/nonexistent/config')
        
        with pytest.raises(ProfileLoadError) as exc_info:
            loader.load_profiles()
        
        assert "AWS config file not found" in str(exc_info.value)
        assert exc_info.value.context['aws_config_path'] == '/nonexistent/config'
    
    def test_load_profiles_invalid_config(self):
        """Test profile loading with invalid config file"""
        # Create invalid config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as invalid_config:
            invalid_config.write("invalid config content [[[")
            invalid_config_path = invalid_config.name
        
        try:
            loader = ProfileLoader(invalid_config_path)
            
            with pytest.raises(ProfileLoadError) as exc_info:
                loader.load_profiles()
            
            assert "Failed to parse AWS config file" in str(exc_info.value)
        finally:
            os.unlink(invalid_config_path)
    
    def test_validate_profile_exists(self):
        """Test profile validation - existing profile"""
        assert self.loader.validate_profile('default') is True
        assert self.loader.validate_profile('555286235540-AdministratorAccess') is True
    
    def test_validate_profile_not_exists(self):
        """Test profile validation - non-existing profile"""
        assert self.loader.validate_profile('nonexistent-profile') is False
    
    def test_validate_profile_load_error(self):
        """Test profile validation when loading fails"""
        loader = ProfileLoader('/nonexistent/config')
        assert loader.validate_profile('any-profile') is False
    
    def test_get_profile_by_name_exists(self):
        """Test getting profile by name - existing profile"""
        profile = self.loader.get_profile_by_name('555286235540-AdministratorAccess')
        
        assert profile is not None
        assert profile.name == '555286235540-AdministratorAccess'
        assert profile.account_id == '555286235540'
        assert profile.role_name == 'AdministratorAccess'
    
    def test_get_profile_by_name_not_exists(self):
        """Test getting profile by name - non-existing profile"""
        profile = self.loader.get_profile_by_name('nonexistent-profile')
        assert profile is None
    
    def test_get_profile_by_name_load_error(self):
        """Test getting profile by name when loading fails"""
        loader = ProfileLoader('/nonexistent/config')
        profile = loader.get_profile_by_name('any-profile')
        assert profile is None
    
    def test_get_profile_count(self):
        """Test getting profile count"""
        count = self.loader.get_profile_count()
        assert count == 4
    
    def test_get_profile_count_load_error(self):
        """Test getting profile count when loading fails"""
        loader = ProfileLoader('/nonexistent/config')
        count = loader.get_profile_count()
        assert count == 0
    
    def test_get_sso_profiles(self):
        """Test getting SSO profiles only"""
        sso_profiles = self.loader.get_sso_profiles()
        
        # Should have 2 SSO profiles
        assert len(sso_profiles) == 2
        
        sso_names = [p.name for p in sso_profiles]
        expected_sso = ['555286235540-AdministratorAccess', '612674025488-AdministratorAccess']
        assert set(sso_names) == set(expected_sso)
        
        # All should be SSO profiles
        assert all(p.is_sso_profile() for p in sso_profiles)
    
    def test_get_regular_profiles(self):
        """Test getting regular (non-SSO) profiles only"""
        regular_profiles = self.loader.get_regular_profiles()
        
        # Should have 2 regular profiles (default and regular-profile)
        assert len(regular_profiles) == 2
        
        regular_names = [p.name for p in regular_profiles]
        expected_regular = ['default', 'regular-profile']
        assert set(regular_names) == set(expected_regular)
        
        # None should be SSO profiles
        assert all(not p.is_sso_profile() for p in regular_profiles)
    
    def test_refresh_profiles(self):
        """Test refreshing profiles"""
        profiles1 = self.loader.load_profiles()
        profiles2 = self.loader.refresh_profiles()
        
        # Should return the same profiles
        assert len(profiles1) == len(profiles2)
        
        names1 = [p.name for p in profiles1]
        names2 = [p.name for p in profiles2]
        assert set(names1) == set(names2)
    
    def test_parse_profile_section_with_account_role_in_name(self):
        """Test parsing profile section with account/role in name"""
        # Create a profile with account/role info only in the name
        section_data = {'region': 'us-east-1'}
        
        profile = self.loader._parse_profile_section(
            '123456789-TestRole', 
            section_data, 
            None
        )
        
        assert profile.name == '123456789-TestRole'
        assert profile.account_id == '123456789'
        assert profile.role_name == 'TestRole'
        assert profile.region == 'us-east-1'
        assert profile.is_current is False
    
    def test_parse_profile_section_current_profile(self):
        """Test parsing profile section for current profile"""
        section_data = {'region': 'us-east-1'}
        
        profile = self.loader._parse_profile_section(
            'test-profile', 
            section_data, 
            'test-profile'  # This is the current profile
        )
        
        assert profile.name == 'test-profile'
        assert profile.is_current is True