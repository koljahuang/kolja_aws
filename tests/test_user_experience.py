"""
Tests for user experience enhancements
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.user_experience import UserExperienceManager, show_error, show_success
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import (
    UnsupportedShellError,
    ProfileLoadError,
    ConfigFileError
)


class TestUserExperienceManager:
    """Test UserExperienceManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_console = Mock()
        self.ux_manager = UserExperienceManager(console=self.mock_console)
        
        # Sample profiles for testing
        self.sample_profiles = [
            ProfileInfo(
                name="current-profile",
                is_current=True,
                account_id="123456789",
                role_name="AdminRole",
                region="us-east-1",
                sso_session="test-sso"
            ),
            ProfileInfo(
                name="sso-profile",
                account_id="987654321",
                role_name="ReadOnlyRole",
                region="us-west-2",
                sso_session="test-sso"
            ),
            ProfileInfo(
                name="regular-profile",
                region="eu-west-1"
            )
        ]
    
    def test_init_default_console(self):
        """Test UserExperienceManager initialization with default console"""
        manager = UserExperienceManager()
        assert manager.console is not None
        assert manager.error_suggestions is not None
    
    def test_init_custom_console(self):
        """Test UserExperienceManager initialization with custom console"""
        custom_console = Mock()
        manager = UserExperienceManager(console=custom_console)
        assert manager.console is custom_console
    
    def test_classify_error_unsupported_shell(self):
        """Test error classification for unsupported shell"""
        error = UnsupportedShellError("tcsh", ["bash", "zsh"])
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'shell_not_supported'
    
    def test_classify_error_profile_load_not_found(self):
        """Test error classification for profile load error - not found"""
        error = ProfileLoadError("Config file not found")
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'aws_config_missing'
    
    def test_classify_error_profile_load_sso(self):
        """Test error classification for profile load error - SSO"""
        error = ProfileLoadError("SSO session not configured")
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'sso_not_configured'
    
    def test_classify_error_config_file_permission(self):
        """Test error classification for config file permission error"""
        error = ConfigFileError("~/.bashrc", "write", "Permission denied")
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'permission_denied'
    
    def test_classify_error_profile_not_found(self):
        """Test error classification for profile not found"""
        error = Exception("Profile 'test-profile' not found")
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'profile_not_found'
    
    def test_classify_error_general(self):
        """Test error classification for general error"""
        error = Exception("Some unexpected error")
        error_type = self.ux_manager._classify_error(error)
        assert error_type == 'general'
    
    def test_get_error_suggestions_profile_not_found(self):
        """Test getting error suggestions for profile not found"""
        suggestions = self.ux_manager._get_error_suggestions('profile_not_found')
        assert len(suggestions) > 0
        assert any('kolja aws profiles' in s for s in suggestions)
    
    def test_get_error_suggestions_with_context(self):
        """Test getting error suggestions with context"""
        context = {"available_profiles": ["profile1", "profile2", "profile3"]}
        suggestions = self.ux_manager._get_error_suggestions('profile_not_found', context)
        
        # Should include available profiles in suggestions
        assert any('Available profiles:' in s for s in suggestions)
        assert any('profile1' in s for s in suggestions)
    
    def test_show_enhanced_error(self):
        """Test showing enhanced error message"""
        error = UnsupportedShellError("tcsh", ["bash", "zsh"])
        
        self.ux_manager.show_enhanced_error(error)
        
        # Should print error panel
        assert self.mock_console.print.call_count >= 2  # Empty lines + panel
    
    @patch('kolja_aws.user_experience.Progress')
    def test_show_loading_indicator_with_duration(self, mock_progress_class):
        """Test showing loading indicator with duration"""
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            self.ux_manager.show_loading_indicator("Loading...", duration=0.1)
        
        # Should have created Progress instance
        mock_progress_class.assert_called_once()
        mock_progress.add_task.assert_called_once_with("Loading...", total=100)
    
    @patch('kolja_aws.user_experience.Progress')
    def test_show_loading_indicator_without_duration(self, mock_progress_class):
        """Test showing loading indicator without duration"""
        mock_progress = MagicMock()
        mock_progress_class.return_value.__enter__.return_value = mock_progress
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            self.ux_manager.show_loading_indicator("Loading...")
        
        # Should have created Progress instance
        mock_progress_class.assert_called_once()
        mock_progress.add_task.assert_called_once_with("Loading...", total=None)
    
    def test_show_profile_table_enhanced_with_profiles(self):
        """Test showing enhanced profile table with profiles"""
        self.ux_manager.show_profile_table_enhanced(self.sample_profiles)
        
        # Should print table and usage hints
        assert self.mock_console.print.call_count >= 5  # Empty lines + table + hints
    
    def test_show_profile_table_enhanced_no_profiles(self):
        """Test showing enhanced profile table with no profiles"""
        with patch.object(self.ux_manager, '_show_no_profiles_help') as mock_help:
            self.ux_manager.show_profile_table_enhanced([])
            mock_help.assert_called_once()
    
    def test_show_profile_table_enhanced_no_details(self):
        """Test showing enhanced profile table without details"""
        self.ux_manager.show_profile_table_enhanced(self.sample_profiles, show_details=False)
        
        # Should still print table but with fewer columns
        assert self.mock_console.print.call_count >= 5
    
    def test_show_success_with_next_steps(self):
        """Test showing success message with next steps"""
        next_steps = ["Step 1", "Step 2", "Step 3"]
        
        self.ux_manager.show_success_with_next_steps("Operation completed", next_steps)
        
        # Should print success panel
        assert self.mock_console.print.call_count >= 2  # Empty lines + panel
    
    def test_show_success_without_next_steps(self):
        """Test showing success message without next steps"""
        self.ux_manager.show_success_with_next_steps("Operation completed", [])
        
        # Should print success panel
        assert self.mock_console.print.call_count >= 2
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_warning_with_options(self, mock_prompt):
        """Test showing warning message with options"""
        options = ["Option 1", "Option 2", "Option 3"]
        mock_prompt.return_value = "1"
        
        result = self.ux_manager.show_warning_with_options("Warning message", options)
        
        assert result == "Option 1"
        assert self.mock_console.print.call_count >= 2  # Empty lines + panel
        mock_prompt.assert_called_once()
    
    @patch('rich.prompt.Prompt.ask')
    def test_show_warning_with_options_quit(self, mock_prompt):
        """Test showing warning message with options - user quits"""
        options = ["Option 1", "Option 2"]
        mock_prompt.return_value = "q"
        
        result = self.ux_manager.show_warning_with_options("Warning message", options)
        
        assert result is None
    
    @patch('rich.prompt.Confirm.ask')
    def test_confirm_action_yes(self, mock_confirm):
        """Test confirming action - yes"""
        mock_confirm.return_value = True
        
        result = self.ux_manager.confirm_action("Continue?")
        
        assert result is True
        mock_confirm.assert_called_once_with("🤔 Continue?", default=True)
    
    @patch('rich.prompt.Confirm.ask')
    def test_confirm_action_no(self, mock_confirm):
        """Test confirming action - no"""
        mock_confirm.return_value = False
        
        result = self.ux_manager.confirm_action("Continue?", default=False)
        
        assert result is False
        mock_confirm.assert_called_once_with("🤔 Continue?", default=False)
    
    def test_show_performance_tips(self):
        """Test showing performance tips"""
        self.ux_manager.show_performance_tips()
        
        # Should print tips panel
        assert self.mock_console.print.call_count >= 2  # Empty lines + panel
    
    def test_show_no_profiles_help(self):
        """Test showing no profiles help"""
        self.ux_manager._show_no_profiles_help()
        
        # Should print help panel
        assert self.mock_console.print.call_count >= 2  # Empty lines + panel
    
    def test_show_usage_hints(self):
        """Test showing usage hints"""
        self.ux_manager._show_usage_hints(5)
        
        # Should print hints
        assert self.mock_console.print.call_count >= 3  # Multiple hints + empty line
    
    def test_show_system_info(self):
        """Test showing system information"""
        self.ux_manager.show_system_info()
        
        # Should print system info table
        assert self.mock_console.print.call_count >= 2  # Empty lines + table


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @patch('kolja_aws.user_experience.ux_manager')
    def test_show_error_convenience(self, mock_ux_manager):
        """Test show_error convenience function"""
        error = Exception("Test error")
        context = {"test": "context"}
        
        show_error(error, context)
        
        mock_ux_manager.show_enhanced_error.assert_called_once_with(error, context)
    
    @patch('kolja_aws.user_experience.ux_manager')
    def test_show_success_convenience(self, mock_ux_manager):
        """Test show_success convenience function"""
        message = "Success message"
        next_steps = ["Step 1", "Step 2"]
        
        show_success(message, next_steps)
        
        mock_ux_manager.show_success_with_next_steps.assert_called_once_with(message, next_steps)
    
    @patch('kolja_aws.user_experience.ux_manager')
    def test_show_success_convenience_no_steps(self, mock_ux_manager):
        """Test show_success convenience function without steps"""
        message = "Success message"
        
        show_success(message)
        
        mock_ux_manager.show_success_with_next_steps.assert_called_once_with(message, [])