"""
Tests for shell integration data models
"""

import os
import tempfile
import pytest
from kolja_aws.shell_models import ShellConfig, ProfileInfo


class TestShellConfig:
    """Test ShellConfig data model"""
    
    def test_shell_config_creation(self):
        """Test basic ShellConfig creation"""
        config = ShellConfig(
            shell_type="bash",
            config_file="~/.bashrc"
        )
        
        assert config.shell_type == "bash"
        assert config.config_file == "~/.bashrc"
        assert config.backup_file is None
        assert config.install_marker == "# kolja-aws profile switcher"
    
    def test_shell_config_with_backup(self):
        """Test ShellConfig with backup file"""
        config = ShellConfig(
            shell_type="zsh",
            config_file="~/.zshrc",
            backup_file="~/.zshrc.backup"
        )
        
        assert config.backup_file == "~/.zshrc.backup"
    
    def test_get_expanded_config_path(self):
        """Test config path expansion"""
        config = ShellConfig(
            shell_type="bash",
            config_file="~/.bashrc"
        )
        
        expanded = config.get_expanded_config_path()
        assert expanded == os.path.expanduser("~/.bashrc")
    
    def test_get_expanded_backup_path(self):
        """Test backup path expansion"""
        config = ShellConfig(
            shell_type="bash",
            config_file="~/.bashrc",
            backup_file="~/.bashrc.backup"
        )
        
        expanded = config.get_expanded_backup_path()
        assert expanded == os.path.expanduser("~/.bashrc.backup")
    
    def test_get_expanded_backup_path_none(self):
        """Test backup path expansion when backup_file is None"""
        config = ShellConfig(
            shell_type="bash",
            config_file="~/.bashrc"
        )
        
        expanded = config.get_expanded_backup_path()
        assert expanded is None
    
    def test_validate_unsupported_shell(self):
        """Test validation with unsupported shell"""
        config = ShellConfig(
            shell_type="tcsh",
            config_file="~/.tcshrc"
        )
        
        with pytest.raises(ValueError, match="Unsupported shell: tcsh"):
            config.validate()
    
    def test_validate_missing_config_file(self):
        """Test validation with missing config file"""
        config = ShellConfig(
            shell_type="bash",
            config_file="/nonexistent/config"
        )
        
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            config.validate()
    
    def test_validate_success(self):
        """Test successful validation"""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            config = ShellConfig(
                shell_type="bash",
                config_file=temp_path
            )
            
            # Should not raise any exception
            config.validate()
        finally:
            os.unlink(temp_path)


class TestProfileInfo:
    """Test ProfileInfo data model"""
    
    def test_profile_info_creation(self):
        """Test basic ProfileInfo creation"""
        profile = ProfileInfo(name="default")
        
        assert profile.name == "default"
        assert profile.is_current is False
        assert profile.sso_session is None
        assert profile.account_id is None
        assert profile.role_name is None
        assert profile.region is None
        assert profile.last_used is None
    
    def test_profile_info_with_sso_details(self):
        """Test ProfileInfo with SSO details"""
        profile = ProfileInfo(
            name="555286235540-AdministratorAccess",
            is_current=True,
            sso_session="my-sso",
            account_id="555286235540",
            role_name="AdministratorAccess",
            region="us-east-1",
            last_used="2024-01-15"
        )
        
        assert profile.name == "555286235540-AdministratorAccess"
        assert profile.is_current is True
        assert profile.sso_session == "my-sso"
        assert profile.account_id == "555286235540"
        assert profile.role_name == "AdministratorAccess"
        assert profile.region == "us-east-1"
        assert profile.last_used == "2024-01-15"
    
    def test_str_representation_current(self):
        """Test string representation for current profile"""
        profile = ProfileInfo(name="default", is_current=True)
        assert str(profile) == " ❯ default"
    
    def test_str_representation_not_current(self):
        """Test string representation for non-current profile"""
        profile = ProfileInfo(name="default", is_current=False)
        assert str(profile) == "   default"
    
    def test_get_display_name_basic(self):
        """Test display name for basic profile"""
        profile = ProfileInfo(name="default")
        assert profile.get_display_name() == "default"
    
    def test_get_display_name_with_account_role(self):
        """Test display name with account ID and role"""
        profile = ProfileInfo(
            name="555286235540-AdministratorAccess",
            account_id="555286235540",
            role_name="AdministratorAccess"
        )
        
        expected = "555286235540-AdministratorAccess (555286235540-AdministratorAccess)"
        assert profile.get_display_name() == expected
    
    def test_get_display_for_inquirer_current_profile(self):
        """Test inquirer display for current profile"""
        profile = ProfileInfo(
            name="my-profile",
            is_current=True,
            account_id="123456789",
            region="us-east-1"
        )
        
        display = profile.get_display_for_inquirer()
        assert "🟢 [ACTIVE] my-profile" in display
        assert "Account: 123456789" in display
        assert "Region: us-east-1" in display
    
    def test_get_display_for_inquirer_sso_profile(self):
        """Test inquirer display for SSO profile"""
        profile = ProfileInfo(
            name="sso-profile",
            sso_session="my-sso",
            account_id="987654321"
        )
        
        display = profile.get_display_for_inquirer()
        assert "🔐 [SSO] sso-profile" in display
        assert "Account: 987654321" in display
    
    def test_get_display_for_inquirer_regular_profile(self):
        """Test inquirer display for regular profile"""
        profile = ProfileInfo(name="regular-profile")
        
        display = profile.get_display_for_inquirer()
        assert "🔑 [KEY] regular-profile" in display
    
    def test_get_search_text(self):
        """Test search text generation"""
        profile = ProfileInfo(
            name="MyProfile",
            account_id="123456789",
            role_name="AdminRole",
            region="us-east-1"
        )
        
        search_text = profile.get_search_text()
        expected = "myprofile 123456789 adminrole us-east-1"
        assert search_text == expected
    
    def test_get_search_text_minimal(self):
        """Test search text with minimal info"""
        profile = ProfileInfo(name="SimpleProfile")
        
        search_text = profile.get_search_text()
        assert search_text == "simpleprofile"
    
    def test_is_sso_profile_true(self):
        """Test SSO profile detection - positive case"""
        profile = ProfileInfo(
            name="sso-profile",
            sso_session="my-sso"
        )
        
        assert profile.is_sso_profile() is True
    
    def test_is_sso_profile_false(self):
        """Test SSO profile detection - negative case"""
        profile = ProfileInfo(name="regular-profile")
        assert profile.is_sso_profile() is False