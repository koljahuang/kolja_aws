"""
Tests for shell integration module
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.shell_integration import (
    get_profile_switcher,
    show_interactive_menu,
    list_profiles,
    get_current_profile,
    validate_profile,
    switch_profile,
    health_check,
    main,
    ShellIntegrationError
)
from kolja_aws.shell_models import ProfileInfo


class TestShellIntegration:
    """Test shell integration module functions"""
    
    def test_get_profile_switcher_success(self):
        """Test successful ProfileSwitcher creation"""
        with patch('kolja_aws.shell_integration.ProfileSwitcher') as mock_switcher_class:
            mock_switcher = Mock()
            mock_switcher_class.return_value = mock_switcher
            
            result = get_profile_switcher()
            
            assert result == mock_switcher
            mock_switcher_class.assert_called_once()
    
    def test_get_profile_switcher_error(self):
        """Test ProfileSwitcher creation with error"""
        with patch('kolja_aws.shell_integration.ProfileSwitcher') as mock_switcher_class:
            mock_switcher_class.side_effect = Exception("Test error")
            
            with pytest.raises(ShellIntegrationError) as exc_info:
                get_profile_switcher()
            
            assert "Failed to initialize profile switcher" in str(exc_info.value)
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_show_interactive_menu_success(self, mock_get_switcher):
        """Test successful interactive menu"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = "test-profile"
        
        result = show_interactive_menu()
        
        assert result == "test-profile"
        mock_switcher.show_interactive_menu.assert_called_once()
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_show_interactive_menu_cancelled(self, mock_get_switcher):
        """Test interactive menu when user cancels"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = None
        
        result = show_interactive_menu()
        
        assert result is None
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_show_interactive_menu_keyboard_interrupt(self, mock_get_switcher):
        """Test interactive menu with keyboard interrupt"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.show_interactive_menu.side_effect = KeyboardInterrupt()
        
        result = show_interactive_menu()
        
        assert result is None
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_show_interactive_menu_error(self, mock_get_switcher):
        """Test interactive menu with error"""
        mock_get_switcher.side_effect = Exception("Test error")
        
        with patch('builtins.print') as mock_print:
            result = show_interactive_menu()
            
            assert result is None
            mock_print.assert_called_with("Error: Test error", file=sys.stderr)
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_list_profiles_success(self, mock_get_switcher):
        """Test successful profile listing"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        
        sample_profiles = [
            ProfileInfo(name="profile1"),
            ProfileInfo(name="profile2"),
            ProfileInfo(name="profile3")
        ]
        mock_switcher.list_profiles.return_value = sample_profiles
        
        result = list_profiles()
        
        assert result == ["profile1", "profile2", "profile3"]
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_list_profiles_error(self, mock_get_switcher):
        """Test profile listing with error"""
        mock_get_switcher.side_effect = Exception("Test error")
        
        result = list_profiles()
        
        assert result == []
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_get_current_profile_success(self, mock_get_switcher):
        """Test successful current profile retrieval"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.get_current_profile.return_value = "current-profile"
        
        result = get_current_profile()
        
        assert result == "current-profile"
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_get_current_profile_none(self, mock_get_switcher):
        """Test current profile retrieval when none is set"""
        mock_switcher = Mock()
        mock_get_switcher.return_value = mock_switcher
        mock_switcher.get_current_profile.return_value = None
        
        result = get_current_profile()
        
        assert result is None
    
    @patch('kolja_aws.shell_integration.get_profile_switcher')
    def test_get_current_profile_error(self, mock_get_switcher):
        """Test current profile retrieval with error"""
        mock_get_switcher.side_effect = Exception("Test error")
        
        result = get_current_profile()
        
        assert result is None
    
    @patch('kolja_aws.shell_integration.ProfileLoader')
    def test_validate_profile_valid(self, mock_loader_class):
        """Test profile validation - valid profile"""
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.validate_profile.return_value = True
        
        result = validate_profile("test-profile")
        
        assert result is True
        mock_loader.validate_profile.assert_called_once_with("test-profile")
    
    @patch('kolja_aws.shell_integration.ProfileLoader')
    def test_validate_profile_invalid(self, mock_loader_class):
        """Test profile validation - invalid profile"""
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.validate_profile.return_value = False
        
        result = validate_profile("nonexistent-profile")
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.ProfileLoader')
    def test_validate_profile_error(self, mock_loader_class):
        """Test profile validation with error"""
        mock_loader_class.side_effect = Exception("Test error")
        
        result = validate_profile("test-profile")
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.validate_profile')
    def test_switch_profile_valid(self, mock_validate):
        """Test profile switching - valid profile"""
        mock_validate.return_value = True
        
        result = switch_profile("test-profile")
        
        assert result is True
        mock_validate.assert_called_once_with("test-profile")
    
    @patch('kolja_aws.shell_integration.validate_profile')
    def test_switch_profile_invalid(self, mock_validate):
        """Test profile switching - invalid profile"""
        mock_validate.return_value = False
        
        result = switch_profile("nonexistent-profile")
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.validate_profile')
    def test_switch_profile_error(self, mock_validate):
        """Test profile switching with error"""
        mock_validate.side_effect = Exception("Test error")
        
        result = switch_profile("test-profile")
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.ProfileLoader')
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    def test_health_check_success(self, mock_switcher_class, mock_loader_class):
        """Test successful health check"""
        mock_loader = Mock()
        mock_loader_class.return_value = mock_loader
        mock_loader.load_profiles.return_value = [ProfileInfo(name="test")]
        
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        
        result = health_check()
        
        assert result is True
    
    @patch('kolja_aws.shell_integration.ProfileLoader')
    def test_health_check_failure(self, mock_loader_class):
        """Test health check failure"""
        mock_loader_class.side_effect = Exception("Test error")
        
        result = health_check()
        
        assert result is False
    
    @patch('kolja_aws.shell_integration.show_interactive_menu')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_show_menu):
        """Test successful main function execution"""
        mock_show_menu.return_value = "selected-profile"
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once_with("selected-profile")
            mock_exit.assert_called_once_with(0)
    
    @patch('kolja_aws.shell_integration.show_interactive_menu')
    @patch('sys.exit')
    def test_main_no_selection(self, mock_exit, mock_show_menu):
        """Test main function when no profile is selected"""
        mock_show_menu.return_value = None
        
        main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('kolja_aws.shell_integration.show_interactive_menu')
    @patch('sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_show_menu):
        """Test main function with keyboard interrupt"""
        mock_show_menu.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once_with("Profile switching cancelled", file=sys.stderr)
            mock_exit.assert_called_once_with(1)
    
    @patch('kolja_aws.shell_integration.show_interactive_menu')
    @patch('sys.exit')
    def test_main_unexpected_error(self, mock_exit, mock_show_menu):
        """Test main function with unexpected error"""
        mock_show_menu.side_effect = Exception("Unexpected error")
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once_with("Error: Unexpected error", file=sys.stderr)
            mock_exit.assert_called_once_with(1)


class TestLogging:
    """Test logging functionality"""
    
    def test_setup_logging_default(self):
        """Test logging setup with default level"""
        with patch.dict('os.environ', {}, clear=True):
            from kolja_aws.shell_integration import _setup_logging
            
            logger = _setup_logging()
            
            assert logger.level == 40  # ERROR level
            assert len(logger.handlers) >= 1
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level"""
        with patch.dict('os.environ', {'KOLJA_LOG_LEVEL': 'DEBUG'}):
            from kolja_aws.shell_integration import _setup_logging
            
            logger = _setup_logging()
            
            assert logger.level == 10  # DEBUG level
    
    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level"""
        with patch.dict('os.environ', {'KOLJA_LOG_LEVEL': 'INVALID'}):
            from kolja_aws.shell_integration import _setup_logging
            
            logger = _setup_logging()
            
            assert logger.level == 40  # Falls back to ERROR level


class TestModuleExports:
    """Test module exports"""
    
    def test_all_exports(self):
        """Test that all expected functions are exported"""
        from kolja_aws import shell_integration
        
        expected_exports = [
            'ProfileSwitcher',
            'show_interactive_menu',
            'list_profiles',
            'get_current_profile',
            'validate_profile',
            'switch_profile',
            'set_environment_variable',
            'get_environment_status',
            'validate_environment',
            'health_check',
            'main'
        ]
        
        for export in expected_exports:
            assert hasattr(shell_integration, export)
            assert export in shell_integration.__all__