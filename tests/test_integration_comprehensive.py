"""
Comprehensive integration test suite for shell profile switcher

This module provides comprehensive end-to-end testing covering:
- Installation across different shell environments
- Interactive functionality automation
- Backup and restore mechanisms
- Uninstallation verification
- Error scenario handling

Requirements coverage: All requirements (1.1-5.5) integration verification
"""

import os
import tempfile
import pytest
import time
from unittest.mock import Mock, patch
from kolja_aws.shell_installer import ShellInstaller
from kolja_aws.profile_switcher import ProfileSwitcher
from kolja_aws.shell_integration import main as shell_integration_main
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import UnsupportedShellError, ProfileLoadError, BackupError
from kolja_aws.backup_manager import BackupManager
from kolja_aws.profile_loader import ProfileLoader


class TestComprehensiveInstallation:
    """Test comprehensive installation scenarios across different shells"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.shell_configs = {
            'bash': os.path.join(self.temp_dir, '.bashrc'),
            'zsh': os.path.join(self.temp_dir, '.zshrc'),
            'fish': os.path.join(self.temp_dir, 'config.fish')
        }
        
        # Create shell config files
        shell_contents = {
            'bash': '# Bash configuration\nexport PATH=/usr/local/bin:$PATH\n',
            'zsh': '# Zsh configuration\nexport PATH=/usr/local/bin:$PATH\n',
            'fish': '# Fish configuration\nset -gx PATH /usr/local/bin $PATH\n'
        }
        
        for shell, config_file in self.shell_configs.items():
            with open(config_file, 'w') as f:
                f.write(shell_contents[shell])
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.parametrize("shell_type", ["bash", "zsh", "fish"])
    def test_installation_across_shells(self, shell_type):
        """Test installation across different shell types"""
        config_file = self.shell_configs[shell_type]
        
        with patch('kolja_aws.shell_detector.ShellDetector.detect_shell') as mock_detect, \
             patch('kolja_aws.shell_detector.ShellDetector.get_config_file') as mock_get_config, \
             patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = shell_type
            mock_get_config.return_value = config_file
            mock_validate.return_value = None
            
            installer = ShellInstaller()
            
            with patch.object(installer.console, 'print'):
                result = installer.install()
            
            assert result is True
            
            # Verify script was added
            with open(config_file, 'r') as f:
                content = f.read()
            
            assert '# kolja-aws profile switcher - START' in content
            assert '# kolja-aws profile switcher - END' in content
            
            # Check shell-specific syntax
            if shell_type in ['bash', 'zsh']:
                assert 'sp()' in content
            elif shell_type == 'fish':
                assert 'function sp' in content
            
            assert installer.is_installed() is True
    
    def test_installation_failure_scenarios(self):
        """Test installation failure scenarios"""
        # Test unsupported shell
        with patch('kolja_aws.shell_detector.ShellDetector.detect_shell') as mock_detect:
            mock_detect.side_effect = UnsupportedShellError('tcsh', ['bash', 'zsh', 'fish'])
            
            installer = ShellInstaller()
            with patch.object(installer.console, 'print'):
                result = installer.install()
            
            assert result is False


class TestInteractiveFunctionality:
    """Test interactive functionality automation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_profiles = [
            ProfileInfo(name="default", is_current=False, region="us-east-1"),
            ProfileInfo(
                name="test-profile-1",
                is_current=True,
                sso_session="my-sso",
                account_id="123456789",
                role_name="AdminRole",
                region="us-east-1"
            )
        ]
    
    @patch('kolja_aws.profile_switcher.ProfileLoader')
    @patch('rich.prompt.Prompt.ask')
    def test_profile_selection_automation(self, mock_prompt, mock_loader_class):
        """Test automated profile selection scenarios"""
        mock_loader = Mock()
        mock_loader.load_profiles.return_value = self.sample_profiles
        mock_loader_class.return_value = mock_loader
        
        switcher = ProfileSwitcher()
        
        # Test selecting first profile
        mock_prompt.return_value = '1'
        with patch.object(switcher, '_display_profiles_table'):
            result = switcher.show_interactive_menu()
        assert result == "default"
        
        # Test user cancellation
        mock_prompt.return_value = 'q'
        with patch.object(switcher, '_display_profiles_table'):
            result = switcher.show_interactive_menu()
        assert result is None


class TestBackupAndRestore:
    """Test backup and restore mechanisms"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, '.bashrc')
        self.original_content = '# Original configuration\nexport PATH=/usr/bin\n'
        
        with open(self.config_file, 'w') as f:
            f.write(self.original_content)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_backup_creation_and_restoration(self):
        """Test backup creation and restoration process"""
        backup_manager = BackupManager()
        
        # Create backup
        backup_path = backup_manager.create_backup(self.config_file)
        
        assert os.path.exists(backup_path)
        assert '.kolja-backup_' in backup_path
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        assert backup_content == self.original_content
        
        # Modify original file
        modified_content = '# Modified configuration\n'
        with open(self.config_file, 'w') as f:
            f.write(modified_content)
        
        # Restore backup
        result = backup_manager.restore_backup(backup_path)
        assert result is True
        
        # Verify restoration
        with open(self.config_file, 'r') as f:
            restored_content = f.read()
        assert restored_content == self.original_content


class TestUninstallationVerification:
    """Test uninstallation functionality verification"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, '.bashrc')
        self.original_content = '# Original configuration\nexport PATH=/usr/bin\n'
        
        with open(self.config_file, 'w') as f:
            f.write(self.original_content)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_uninstallation_flow(self):
        """Test complete uninstallation flow"""
        with patch('kolja_aws.shell_detector.ShellDetector.detect_shell') as mock_detect, \
             patch('kolja_aws.shell_detector.ShellDetector.get_config_file') as mock_get_config, \
             patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = 'bash'
            mock_get_config.return_value = self.config_file
            mock_validate.return_value = None
            
            installer = ShellInstaller()
            
            # First install
            with patch.object(installer.console, 'print'):
                install_result = installer.install()
            
            assert install_result is True
            assert installer.is_installed() is True
            
            # Now uninstall
            with patch.object(installer.console, 'print'):
                uninstall_result = installer.uninstall()
            
            assert uninstall_result is True
            assert installer.is_installed() is False
            
            # Verify uninstallation
            with open(self.config_file, 'r') as f:
                uninstalled_content = f.read()
            
            # Script should be removed
            assert '# kolja-aws profile switcher - START' not in uninstalled_content
            
            # Original content should be preserved
            assert '# Original configuration' in uninstalled_content


class TestErrorScenarios:
    """Test comprehensive error scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, '.bashrc')
        
        with open(self.config_file, 'w') as f:
            f.write('# Test configuration\n')
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_profile_loading_errors(self):
        """Test profile loading error scenarios"""
        # Test missing AWS config file
        non_existent_config = os.path.join(self.temp_dir, 'non_existent_config')
        loader = ProfileLoader(non_existent_config)
        
        with pytest.raises(ProfileLoadError):
            loader.load_profiles()
        
        # Test empty AWS config file
        empty_config = os.path.join(self.temp_dir, 'empty_config')
        with open(empty_config, 'w') as f:
            f.write('')
        
        loader = ProfileLoader(empty_config)
        profiles = loader.load_profiles()
        assert len(profiles) == 0


@pytest.mark.integration
class TestFullSystemIntegration:
    """Test full system integration scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, '.bashrc')
        self.aws_config_file = os.path.join(self.temp_dir, 'aws_config')
        
        # Create shell config
        with open(self.config_file, 'w') as f:
            f.write('# Test shell configuration\nexport PATH=/usr/bin\n')
        
        # Create AWS config
        aws_config_content = """[default]
region = us-east-1
output = json

[profile test-profile-1]
sso_session = test-sso
sso_account_id = 123456789
sso_role_name = AdminRole
region = us-east-1
"""
        
        with open(self.aws_config_file, 'w') as f:
            f.write(aws_config_content)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Step 1: Install shell integration
        with patch('kolja_aws.shell_detector.ShellDetector.detect_shell') as mock_detect, \
             patch('kolja_aws.shell_detector.ShellDetector.get_config_file') as mock_get_config, \
             patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = 'bash'
            mock_get_config.return_value = self.config_file
            mock_validate.return_value = None
            
            installer = ShellInstaller()
            
            with patch.object(installer.console, 'print'):
                install_result = installer.install()
            
            assert install_result is True
            assert installer.is_installed() is True
        
        # Step 2: Test profile switching
        with patch('kolja_aws.profile_switcher.ProfileLoader') as mock_loader_class, \
             patch('rich.prompt.Prompt.ask') as mock_prompt:
            
            # Setup profile loader
            loader = ProfileLoader(self.aws_config_file)
            profiles = loader.load_profiles()
            
            mock_loader = Mock()
            mock_loader.load_profiles.return_value = profiles
            mock_loader_class.return_value = mock_loader
            
            # Test profile selection
            mock_prompt.return_value = '2'  # Select second profile
            
            switcher = ProfileSwitcher()
            
            with patch.object(switcher, '_display_profiles_table'):
                selected_profile = switcher.show_interactive_menu()
            
            assert selected_profile == 'test-profile-1'
        
        # Step 3: Test shell integration main
        with patch('kolja_aws.shell_integration.ProfileSwitcher') as mock_switcher_class, \
             patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            mock_switcher = Mock()
            mock_switcher.show_interactive_menu.return_value = 'test-profile-1'
            mock_switcher_class.return_value = mock_switcher
            
            shell_integration_main()
            
            mock_print.assert_called_once_with('test-profile-1')
            mock_exit.assert_called_once_with(0)
        
        # Step 4: Verify complete cleanup after uninstallation
        with patch('kolja_aws.shell_detector.ShellDetector.detect_shell') as mock_detect, \
             patch('kolja_aws.shell_detector.ShellDetector.get_config_file') as mock_get_config, \
             patch('kolja_aws.shell_detector.ShellDetector.validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = 'bash'
            mock_get_config.return_value = self.config_file
            mock_validate.return_value = None
            
            with patch.object(installer.console, 'print'):
                uninstall_result = installer.uninstall()
            
            assert uninstall_result is True
            assert installer.is_installed() is False
        
        # Step 5: Verify complete cleanup
        with open(self.config_file, 'r') as f:
            final_content = f.read()
        
        assert '# kolja-aws profile switcher - START' not in final_content
        assert '# Test shell configuration' in final_content
        assert 'export PATH=/usr/bin' in final_content