"""
Tests for interactive AWS profile switcher
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.profile_switcher import ProfileSwitcher, main
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import ProfileLoadError


class TestProfileSwitcher:
    """Test ProfileSwitcher class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create mock profile loader
        self.mock_loader = Mock()
        self.switcher = ProfileSwitcher(profile_loader=self.mock_loader)
        
        # Sample profiles for testing
        self.sample_profiles = [
            ProfileInfo(
                name="555286235540-AdministratorAccess",
                is_current=True,
                sso_session="my-sso",
                account_id="555286235540",
                role_name="AdministratorAccess",
                region="us-east-1"
            ),
            ProfileInfo(
                name="612674025488-AdministratorAccess",
                is_current=False,
                sso_session="my-sso",
                account_id="612674025488",
                role_name="AdministratorAccess",
                region="us-west-2"
            ),
            ProfileInfo(
                name="default",
                is_current=False,
                region="us-east-1"
            )
        ]
    
    def test_init_default_loader(self):
        """Test ProfileSwitcher initialization with default loader"""
        switcher = ProfileSwitcher()
        assert switcher.profile_loader is not None
        assert switcher.console is not None
    
    def test_init_custom_loader(self):
        """Test ProfileSwitcher initialization with custom loader"""
        custom_loader = Mock()
        switcher = ProfileSwitcher(profile_loader=custom_loader)
        assert switcher.profile_loader is custom_loader
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_interactive_menu_success(self, mock_prompt):
        """Test successful interactive menu selection"""
        # Setup mock responses
        self.mock_loader.load_profiles.return_value = self.sample_profiles
        mock_prompt.return_value = '1'  # Select first profile
        
        with patch.object(self.switcher, '_display_profiles_table'):
            result = self.switcher.show_interactive_menu()
            
            # Should return the actual profile name
            assert result == '555286235540-AdministratorAccess'
            mock_prompt.assert_called_once()
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_interactive_menu_no_profiles(self, mock_prompt):
        """Test interactive menu with no profiles available"""
        self.mock_loader.load_profiles.return_value = []
        
        with patch.object(self.switcher, '_show_no_profiles_message') as mock_show_message:
            result = self.switcher.show_interactive_menu()
            
            assert result is None
            mock_show_message.assert_called_once()
            mock_prompt.assert_not_called()
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_interactive_menu_user_cancelled(self, mock_prompt):
        """Test interactive menu when user cancels"""
        self.mock_loader.load_profiles.return_value = self.sample_profiles
        mock_prompt.return_value = 'q'  # User cancelled
        
        with patch.object(self.switcher, '_display_profiles_table'):
            result = self.switcher.show_interactive_menu()
            assert result is None
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_interactive_menu_keyboard_interrupt(self, mock_prompt):
        """Test interactive menu with keyboard interrupt"""
        self.mock_loader.load_profiles.return_value = self.sample_profiles
        mock_prompt.side_effect = KeyboardInterrupt()
        
        with patch.object(self.switcher.console, 'print') as mock_print:
            with patch.object(self.switcher, '_display_profiles_table'):
                result = self.switcher.show_interactive_menu()
                
                assert result is None
                mock_print.assert_called_with("\n👋 Profile switching cancelled")
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_interactive_menu_load_error(self, mock_prompt):
        """Test interactive menu with profile loading error"""
        self.mock_loader.load_profiles.side_effect = ProfileLoadError("Config not found")
        
        with patch.object(self.switcher, '_show_profile_load_error') as mock_show_error:
            result = self.switcher.show_interactive_menu()
            
            assert result is None
            mock_show_error.assert_called_once()
            mock_prompt.assert_not_called()
    
    def test_switch_profile_success(self):
        """Test successful profile switching"""
        self.mock_loader.validate_profile.return_value = True
        
        result = self.switcher.switch_profile("test-profile")
        assert result is True
        self.mock_loader.validate_profile.assert_called_once_with("test-profile")
    
    def test_switch_profile_not_found(self):
        """Test profile switching with non-existent profile"""
        self.mock_loader.validate_profile.return_value = False
        
        with patch.object(self.switcher, '_show_error') as mock_show_error:
            result = self.switcher.switch_profile("nonexistent-profile")
            
            assert result is False
            mock_show_error.assert_called_with("Profile 'nonexistent-profile' not found")
    
    def test_switch_profile_exception(self):
        """Test profile switching with exception"""
        self.mock_loader.validate_profile.side_effect = Exception("Test error")
        
        with patch.object(self.switcher, '_show_error') as mock_show_error:
            result = self.switcher.switch_profile("test-profile")
            
            assert result is False
            mock_show_error.assert_called_with("Failed to switch profile: Test error")
    
    def test_list_profiles_success(self):
        """Test successful profile listing"""
        self.mock_loader.load_profiles.return_value = self.sample_profiles
        
        result = self.switcher.list_profiles()
        assert result == self.sample_profiles
    
    def test_list_profiles_error(self):
        """Test profile listing with error"""
        self.mock_loader.load_profiles.side_effect = ProfileLoadError("Load error")
        
        with patch.object(self.switcher, '_show_error') as mock_show_error:
            result = self.switcher.list_profiles()
            
            assert result == []
            mock_show_error.assert_called_with("Failed to load profiles: Load error")
    
    def test_get_current_profile(self):
        """Test getting current profile"""
        self.mock_loader.get_current_profile.return_value = "current-profile"
        
        result = self.switcher.get_current_profile()
        assert result == "current-profile"
    
    def test_display_profiles_table(self):
        """Test displaying profiles table"""
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._display_profiles_table(self.sample_profiles)
            
            # Should print table and instructions
            assert mock_print.call_count >= 3  # Empty lines + table + instructions
            
            # Verify that print was called with a Table object
            table_call = None
            for call in mock_print.call_args_list:
                if call[0] and hasattr(call[0][0], 'title'):
                    table_call = call[0][0]
                    break
            
            assert table_call is not None
            assert "AWS Profile Switcher" in str(table_call.title)
    
    def test_show_no_profiles_message(self):
        """Test showing no profiles message"""
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_no_profiles_message()
            
            # Should print panel with helpful message
            assert mock_print.call_count >= 2  # Empty lines + panel
            
            # Verify that print was called with a Panel object
            panel_call = None
            for call in mock_print.call_args_list:
                if call[0] and hasattr(call[0][0], 'renderable'):
                    panel_call = call[0][0]
                    break
            
            assert panel_call is not None
    
    def test_show_profile_load_error_not_found(self):
        """Test showing profile load error for file not found"""
        error = ProfileLoadError("Config file not found", "~/.aws/config")
        
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_profile_load_error(error)
            
            # Should print panel with error message
            assert mock_print.call_count >= 2  # Empty lines + panel
            
            # Verify that print was called with a Panel object
            panel_call = None
            for call in mock_print.call_args_list:
                if call[0] and hasattr(call[0][0], 'renderable'):
                    panel_call = call[0][0]
                    break
            
            assert panel_call is not None
    
    def test_show_profile_load_error_parse(self):
        """Test showing profile load error for parse error"""
        error = ProfileLoadError("Failed to parse config file")
        
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_profile_load_error(error)
            
            # Should print panel with error message
            assert mock_print.call_count >= 2  # Empty lines + panel
            
            # Verify that print was called with a Panel object
            panel_call = None
            for call in mock_print.call_args_list:
                if call[0] and hasattr(call[0][0], 'renderable'):
                    panel_call = call[0][0]
                    break
            
            assert panel_call is not None
    
    def test_show_error(self):
        """Test showing error message"""
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_error("Test error message")
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "❌ Error:" in call_args
            assert "Test error message" in call_args
    
    def test_show_success(self):
        """Test showing success message"""
        with patch.object(self.switcher.console, 'print') as mock_print:
            self.switcher._show_success("Test success message")
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "✅" in call_args
            assert "Test success message" in call_args


class TestMainFunction:
    """Test the main function for shell script integration"""
    
    @patch('kolja_aws.profile_switcher.ProfileSwitcher')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_switcher_class):
        """Test successful main function execution"""
        # Setup mocks
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = "test-profile"
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once_with("test-profile")
            mock_exit.assert_called_once_with(0)
    
    @patch('kolja_aws.profile_switcher.ProfileSwitcher')
    @patch('sys.exit')
    def test_main_no_selection(self, mock_exit, mock_switcher_class):
        """Test main function when no profile is selected"""
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = None
        
        main()
        mock_exit.assert_called_once_with(1)
    
    @patch('kolja_aws.profile_switcher.ProfileSwitcher')
    @patch('sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_switcher_class):
        """Test main function with keyboard interrupt"""
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        mock_switcher.show_interactive_menu.side_effect = KeyboardInterrupt()
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "cancelled" in call_args.lower()
            mock_exit.assert_called_once_with(1)
    
    @patch('kolja_aws.profile_switcher.ProfileSwitcher')
    @patch('sys.exit')
    def test_main_exception(self, mock_exit, mock_switcher_class):
        """Test main function with unexpected exception"""
        mock_switcher_class.side_effect = Exception("Test error")
        
        with patch('builtins.print') as mock_print:
            main()
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "Error: Test error" in call_args
            mock_exit.assert_called_once_with(1)