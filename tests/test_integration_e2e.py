"""
End-to-end integration tests for shell profile switcher

These tests verify the complete functionality of the shell profile switcher
system, including installation, profile switching, and uninstallation.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.shell_installer import ShellInstaller
from kolja_aws.profile_switcher import ProfileSwitcher
from kolja_aws.shell_integration import main as shell_integration_main
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.profile_loader import ProfileLoader


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, '.bashrc')
        self.aws_config_file = os.path.join(self.temp_dir, 'aws_config')
        
        # Create sample AWS config content
        self.aws_config_content = """[default]
region = us-east-1
output = json

[profile test-profile-1]
sso_session = test-sso
sso_account_id = 123456789
sso_role_name = AdminRole
region = us-east-1

[profile test-profile-2]
sso_session = test-sso
sso_account_id = 987654321
sso_role_name = ReadOnlyRole
region = us-west-2

[sso-session test-sso]
sso_start_url = https://test.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
"""
        
        # Write AWS config file
        with open(self.aws_config_file, 'w') as f:
            f.write(self.aws_config_content)
        
        # Create empty shell config file
        with open(self.config_file, 'w') as f:
            f.write('# Test shell configuration\nexport PATH=/usr/bin\n')
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('kolja_aws.shell_detector.ShellDetector.detect_shell')
    @patch('kolja_aws.shell_detector.ShellDetector.get_config_file')
    @patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access')
    def test_complete_installation_flow(self, mock_validate, mock_get_config, mock_detect):
        """Test complete installation flow"""
        # Setup mocks
        mock_detect.return_value = 'bash'
        mock_get_config.return_value = self.config_file
        mock_validate.return_value = None
        
        # Create installer
        installer = ShellInstaller()
        
        # Test installation
        with patch.object(installer.console, 'print'):
            result = installer.install()
        
        assert result is True
        
        # Verify script was added to config file
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        assert '# kolja-aws profile switcher - START' in content
        assert 'sp()' in content
        assert '# kolja-aws profile switcher - END' in content
        
        # Test that installation is detected
        assert installer.is_installed() is True
        
        # Test installation status
        status = installer.get_installation_status()
        assert status['installed'] is True
        assert status['shell_type'] == 'bash'
        assert status['config_file'] == self.config_file
    
    @patch('kolja_aws.shell_detector.ShellDetector.detect_shell')
    @patch('kolja_aws.shell_detector.ShellDetector.get_config_file')
    @patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access')
    def test_complete_uninstallation_flow(self, mock_validate, mock_get_config, mock_detect):
        """Test complete uninstallation flow"""
        # Setup mocks
        mock_detect.return_value = 'bash'
        mock_get_config.return_value = self.config_file
        mock_validate.return_value = None
        
        # Create installer and install first
        installer = ShellInstaller()
        
        with patch.object(installer.console, 'print'):
            installer.install()
        
        # Verify installation
        assert installer.is_installed() is True
        
        # Test uninstallation
        with patch.object(installer.console, 'print'):
            result = installer.uninstall()
        
        assert result is True
        
        # Verify script was removed from config file
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        assert '# kolja-aws profile switcher - START' not in content
        assert 'sp()' not in content
        assert '# kolja-aws profile switcher - END' not in content
        
        # Original content should still be there
        assert '# Test shell configuration' in content
        assert 'export PATH=/usr/bin' in content
        
        # Test that installation is no longer detected
        assert installer.is_installed() is False
    
    def test_profile_loading_and_switching(self):
        """Test profile loading and switching functionality"""
        # Create profile loader with test AWS config
        loader = ProfileLoader(self.aws_config_file)
        
        # Test profile loading
        profiles = loader.load_profiles()
        
        assert len(profiles) == 3  # default + 2 test profiles
        profile_names = [p.name for p in profiles]
        assert 'default' in profile_names
        assert 'test-profile-1' in profile_names
        assert 'test-profile-2' in profile_names
        
        # Test profile validation
        assert loader.validate_profile('test-profile-1') is True
        assert loader.validate_profile('nonexistent-profile') is False
        
        # Test profile details
        profile1 = loader.get_profile_by_name('test-profile-1')
        assert profile1 is not None
        assert profile1.account_id == '123456789'
        assert profile1.role_name == 'AdminRole'
        assert profile1.region == 'us-east-1'
        assert profile1.is_sso_profile() is True
        
        # Create profile switcher
        switcher = ProfileSwitcher(profile_loader=loader)
        
        # Test profile switching validation
        assert switcher.switch_profile('test-profile-1') is True
        assert switcher.switch_profile('nonexistent-profile') is False
    
    @patch.dict('os.environ', {'AWS_PROFILE': 'test-profile-1'})
    def test_current_profile_detection(self):
        """Test current profile detection"""
        loader = ProfileLoader(self.aws_config_file)
        
        # Test current profile detection
        current = loader.get_current_profile()
        assert current == 'test-profile-1'
        
        # Load profiles and check current status
        profiles = loader.load_profiles()
        current_profiles = [p for p in profiles if p.is_current]
        
        assert len(current_profiles) == 1
        assert current_profiles[0].name == 'test-profile-1'
    
    @patch('rich.prompt.Prompt.ask')
    def test_interactive_profile_selection(self, mock_prompt):
        """Test interactive profile selection"""
        # Create profile loader with test AWS config
        loader = ProfileLoader(self.aws_config_file)
        
        # Mock user selection (select second profile - index 1)
        mock_prompt.return_value = '2'  # Select second profile
        
        # Create switcher with real loader
        switcher = ProfileSwitcher(profile_loader=loader)
        
        with patch.object(switcher.ux_manager, 'show_profile_table_enhanced'):
            result = switcher.show_interactive_menu()
        
        # Should return the second profile name (test-profile-1)
        assert result == 'test-profile-1'
        mock_prompt.assert_called_once()
    
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    @patch('sys.exit')
    def test_shell_integration_main_success(self, mock_exit, mock_switcher_class):
        """Test shell integration main function"""
        # Setup mock switcher
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = 'selected-profile'
        
        # Test main function
        with patch('builtins.print') as mock_print:
            shell_integration_main()
        
        # Should print selected profile and exit with 0
        mock_print.assert_called_once_with('selected-profile')
        mock_exit.assert_called_once_with(0)
    
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    @patch('sys.exit')
    def test_shell_integration_main_cancelled(self, mock_exit, mock_switcher_class):
        """Test shell integration main function when cancelled"""
        # Setup mock switcher
        mock_switcher = Mock()
        mock_switcher_class.return_value = mock_switcher
        mock_switcher.show_interactive_menu.return_value = None
        
        # Test main function
        shell_integration_main()
        
        # Should exit with 1
        mock_exit.assert_called_once_with(1)
    
    def test_backup_and_restore_functionality(self):
        """Test backup and restore functionality"""
        from kolja_aws.backup_manager import BackupManager
        
        # Create backup manager
        backup_manager = BackupManager()
        
        # Create backup
        backup_path = backup_manager.create_backup(self.config_file)
        
        assert os.path.exists(backup_path)
        assert backup_path != self.config_file
        assert '.kolja-backup_' in backup_path
        
        # Modify original file
        with open(self.config_file, 'w') as f:
            f.write('# Modified content\n')
        
        # Restore backup
        result = backup_manager.restore_backup(backup_path)
        assert result is True
        
        # Verify restoration
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        assert '# Test shell configuration' in content
        assert 'export PATH=/usr/bin' in content
        
        # Clean up backup
        backup_manager.delete_backup(backup_path)
        assert not os.path.exists(backup_path)
    
    def test_error_handling_integration(self):
        """Test error handling across components"""
        from kolja_aws.shell_exceptions import ProfileLoadError, UnsupportedShellError
        from kolja_aws.user_experience import UserExperienceManager
        
        ux_manager = UserExperienceManager()
        
        # Test profile load error handling
        profile_error = ProfileLoadError('Config file not found', '~/.aws/config')
        
        with patch.object(ux_manager.console, 'print'):
            ux_manager.show_enhanced_error(profile_error)
        
        # Test unsupported shell error handling
        shell_error = UnsupportedShellError('tcsh', ['bash', 'zsh', 'fish'])
        
        with patch.object(ux_manager.console, 'print'):
            ux_manager.show_enhanced_error(shell_error)
        
        # Should not raise exceptions
        assert True
    
    @patch('kolja_aws.shell_detector.ShellDetector.detect_shell')
    @patch('kolja_aws.shell_detector.ShellDetector.get_config_file')
    def test_installation_with_existing_script(self, mock_get_config, mock_detect):
        """Test installation when script already exists"""
        # Setup mocks
        mock_detect.return_value = 'bash'
        mock_get_config.return_value = self.config_file
        
        # Add existing script to config file
        existing_script = '''
# kolja-aws profile switcher - START
sp() {
    echo "old script"
}
# kolja-aws profile switcher - END
'''
        
        with open(self.config_file, 'a') as f:
            f.write(existing_script)
        
        # Create installer
        installer = ShellInstaller()
        
        # Test installation (should replace existing script)
        with patch.object(installer.console, 'print'):
            result = installer.install()
        
        assert result is True
        
        # Verify new script replaced old one
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        assert 'old script' not in content
        assert 'from kolja_aws.shell_integration import main' in content
        
        # Should only have one set of markers
        assert content.count('# kolja-aws profile switcher - START') == 1
        assert content.count('# kolja-aws profile switcher - END') == 1