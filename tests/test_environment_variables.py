"""
Tests for environment variable setting functionality
"""

import pytest
from unittest.mock import Mock, patch
from kolja_aws.profile_switcher import ProfileSwitcher
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_integration import (
    set_environment_variable,
    get_environment_status,
    validate_environment
)


class TestProfileSwitcherEnvironment:
    """Test ProfileSwitcher environment variable functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_loader = Mock()
        self.switcher = ProfileSwitcher(profile_loader=self.mock_loader)
        
        # Sample profile for testing
        self.sample_profile = ProfileInfo(
            name="test-profile",
            account_id="123456789",
            role_name="TestRole",
            region="us-east-1",
            sso_session="test-sso"
        )
    
    def test_set_environment_variable_success(self):
        """Test successful environment variable setting"""
        self.mock_loader.validate_profile.return_value = True
        self.mock_loader.get_profile_by_name.return_value = self.sample_profile
        
        with patch.object(self.switcher, '_show_profile_switch_confirmation') as mock_show:
            result = self.switcher.set_environment_variable("test-profile")
            
            assert result is True
            mock_show.assert_called_once_with(self.sample_profile)
    
    def test_set_environment_variable_profile_not_found(self):
        """Test environment variable setting with non-existent profile"""
        self.mock_loader.validate_profile.return_value = False
        
        with patch.object(self.switcher, '_show_error') as mock_show_error:
            result = self.switcher.set_environment_variable("nonexistent-profile")
            
            assert result is False
            mock_show_error.assert_called_with("Cannot set AWS_PROFILE: profile 'nonexistent-profile' not found")
    
    def test_set_environment_variable_no_profile_info(self):
        """Test environment variable setting when profile info is not available"""
        self.mock_loader.validate_profile.return_value = True
        self.mock_loader.get_profile_by_name.return_value = None
        
        with patch.object(self.switcher, '_show_success') as mock_show_success:
            result = self.switcher.set_environment_variable("test-profile")
            
            assert result is True
            mock_show_success.assert_called_with("AWS_PROFILE set to: test-profile")
    
    def test_set_environment_variable_exception(self):
        """Test environment variable setting with exception"""
        self.mock_loader.validate_profile.side_effect = Exception("Test error")
        
        with patch.object(self.switcher, '_show_error') as mock_show_error:
            result = self.switcher.set_environment_variable("test-profile")
            
            assert result is False
            mock_show_error.assert_called_with("Failed to set AWS_PROFILE: Test error")
    
    @patch.dict('os.environ', {'AWS_PROFILE': 'current-profile'})
    def test_get_environment_variable_status_with_valid_profile(self):
        """Test getting environment status with valid current profile"""
        self.mock_loader.get_current_profile.return_value = "current-profile"
        self.mock_loader.validate_profile.return_value = True
        self.mock_loader.get_profile_by_name.return_value = self.sample_profile
        
        status = self.switcher.get_environment_variable_status()
        
        assert status["aws_profile_set"] is True
        assert status["current_profile"] == "current-profile"
        assert status["profile_exists"] is True
        assert status["profile_valid"] is True
        assert "profile_info" in status
        assert status["profile_info"]["name"] == "test-profile"
    
    def test_get_environment_variable_status_no_profile_set(self):
        """Test getting environment status when no profile is set"""
        self.mock_loader.get_current_profile.return_value = None
        
        status = self.switcher.get_environment_variable_status()
        
        assert status["aws_profile_set"] is False
        assert status["current_profile"] is None
        assert status["profile_exists"] is False
        assert status["profile_valid"] is False
    
    @patch.dict('os.environ', {'AWS_PROFILE': 'invalid-profile'})
    def test_get_environment_variable_status_invalid_profile(self):
        """Test getting environment status with invalid current profile"""
        self.mock_loader.get_current_profile.return_value = "invalid-profile"
        self.mock_loader.validate_profile.return_value = False
        
        status = self.switcher.get_environment_variable_status()
        
        assert status["aws_profile_set"] is True
        assert status["current_profile"] == "invalid-profile"
        assert status["profile_exists"] is False
        assert status["profile_valid"] is False
    
    def test_get_environment_variable_status_exception(self):
        """Test getting environment status with exception"""
        self.mock_loader.get_current_profile.side_effect = Exception("Test error")
        
        status = self.switcher.get_environment_variable_status()
        
        assert "error" in status
        assert status["aws_profile_set"] is False
    
    def test_validate_environment_setup_no_profile(self):
        """Test environment validation when no profile is set"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.return_value = {
                "aws_profile_set": False,
                "current_profile": None,
                "profile_exists": False,
                "profile_valid": False
            }
            
            with patch.object(self.switcher.console, 'print') as mock_print:
                result = self.switcher.validate_environment_setup()
                
                assert result is True  # No profile set is not an error
                mock_print.assert_called_with("[yellow]ℹ️  No AWS_PROFILE environment variable set[/yellow]")
    
    def test_validate_environment_setup_valid_profile(self):
        """Test environment validation with valid profile"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.return_value = {
                "aws_profile_set": True,
                "current_profile": "valid-profile",
                "profile_exists": True,
                "profile_valid": True
            }
            
            with patch.object(self.switcher.console, 'print') as mock_print:
                result = self.switcher.validate_environment_setup()
                
                assert result is True
                mock_print.assert_called_with("[green]✅ AWS_PROFILE is set to valid profile: valid-profile[/green]")
    
    def test_validate_environment_setup_invalid_profile(self):
        """Test environment validation with invalid profile"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.return_value = {
                "aws_profile_set": True,
                "current_profile": "invalid-profile",
                "profile_exists": False,
                "profile_valid": False
            }
            
            with patch.object(self.switcher, '_show_error') as mock_show_error:
                result = self.switcher.validate_environment_setup()
                
                assert result is False
                mock_show_error.assert_called_with("Current AWS_PROFILE 'invalid-profile' is not valid")
    
    def test_validate_environment_setup_error(self):
        """Test environment validation with error"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.return_value = {"error": "Test error"}
            
            with patch.object(self.switcher, '_show_error') as mock_show_error:
                result = self.switcher.validate_environment_setup()
                
                assert result is False
                mock_show_error.assert_called_with("Environment validation failed: Test error")
    
    def test_validate_environment_setup_exception(self):
        """Test environment validation with exception"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.side_effect = Exception("Test error")
            
            with patch.object(self.switcher, '_show_error') as mock_show_error:
                result = self.switcher.validate_environment_setup()
                
                assert result is False
                mock_show_error.assert_called_with("Environment validation error: Test error")
    
    def test_show_profile_switch_confirmation(self):
        """Test showing profile switch confirmation"""
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_profile_switch_confirmation(self.sample_profile)
            
            # Should print confirmation message with profile details
            assert mock_print.call_count >= 2  # Empty lines + confirmation
    
    def test_show_environment_status_valid_profile(self):
        """Test showing environment status with valid profile"""
        with patch.object(self.switcher, 'get_environment_variable_status') as mock_get_status:
            mock_get_status.return_value = {
                "aws_profile_set": True,
                "current_profile": "test-profile",
                "profile_valid": True,
                "profile_info": {
                    "account_id": "123456789",
                    "role_name": "TestRole",
                    "region": "us-east-1",
                    "is_sso": True
                }
            }
            
            with patch.object(self.switcher.console, 'print') as mock_print:
                self.switcher._show_environment_status()
                
                # Should print status information
                assert mock_print.call_count >= 5  # Header + profile info + details


class TestShellIntegrationEnvironment:
    """Test shell integration environment variable functions"""
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_set_environment_variable_success(self, mock_get_switcher):
        """Test successful environment variable setting via shell integration"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.set_environment_variable.return_value = True
        
        result = set_environment_variable("test-profile")
        
        assert result is True
        mock_switcher.set_environment_variable.assert_called_once_with("test-profile")
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_set_environment_variable_failure(self, mock_get_switcher):
        """Test failed environment variable setting via shell integration"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.set_environment_variable.return_value = False
        
        result = set_environment_variable("invalid-profile")
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_get_environment_status_success(self, mock_get_switcher):
        """Test getting environment status via shell integration"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        expected_status = {"aws_profile_set": True, "current_profile": "test-profile"}
        mock_switcher.get_environment_variable_status.return_value = expected_status
        
        result = get_environment_status()
        
        assert result == expected_status
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_validate_environment_success(self, mock_get_switcher):
        """Test environment validation via shell integration"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.validate_environment_setup.return_value = True
        
        result = validate_environment()
        
        assert result is True
        mock_switcher.validate_environment_setup.assert_called_once()
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_validate_environment_failure(self, mock_get_switcher):
        """Test environment validation failure via shell integration"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.validate_environment_setup.return_value = False
        
        result = validate_environment()
        
        assert result is False