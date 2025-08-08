"""
Integration tests for shell profile switcher

These tests verify the end-to-end functionality of the shell integration system,
including installation, profile switching, and error handling scenarios.
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.shell_installer import ShellInstaller
from kolja_aws.profile_switcher import ProfileSwitcher
from kolja_aws.shell_integration import main as shell_integration_main
from kolja_aws.shell_models import ProfileInfo, ShellConfig
from kolja_aws.shell_exceptions import ShellIntegrationError


class TestEndToEndInstallation:
    """Test end-to-end installation scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = os.path.join(self.temp_dir, ".bashrc")
        
        # Create a temporary config file
        with open(self.temp_config, 'w') as f:
            f.write("# Test bashrc\nexport PATH=/usr/bin\n")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    @patch('kolja_aws.shell_installer.ScriptGenerator')
    @patch('kolja_aws.shell_installer.BackupManager')
    def test_complete_installation_flow(self, mock_backup_manager_class, 
                                       mock_script_generator_class, 
                                       mock_shell_detector_class):
        """Test complete installation flow from detection to script installation"""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = self.temp_config
        mock_detector.validate_config_file_access.return_value = None
        mock_shell_detector_class.return_value = mock_detector
        
        mock_generator = Mock()
        mock_generator.get_script_for_shell.return_value = "sp() { echo 'test'; }"
        mock_generator.validate_script_syntax.return_value = True
        mock_generator.insert_script_into_config.return_value = "# Test bashrc\nexport PATH=/usr/bin\nsp() { echo 'test'; }"
        mock_script_generator_class.return_value = mock_generator
        
        mock_backup_mgr = Mock()
        mock_backup_mgr.create_backup.return_value = f"{self.temp_config}.backup"
        mock_backup_mgr.cleanup_old_backups.return_value = None
        mock_backup_manager_class.return_value = mock_backup_mgr
        
        # Test installation
        installer = ShellInstaller()
        result = installer.install()
        
        # Verify installation succeeded
        assert result is True
        
        # Verify all components were called
        mock_detector.detect_shell.assert_called_once()
        mock_detector.get_config_file.assert_called_once_with("bash")
        mock_generator.get_script_for_shell.assert_called_once_with("bash")
        mock_backup_mgr.create_backup.assert_called_once()
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    def test_installation_with_unsupported_shell(self, mock_shell_detector_class):
        """Test installation failure with unsupported shell"""
        mock_detector = Mock()
        mock_detector.detect_shell.side_effect = ShellIntegrationError("Unsupported shell: tcsh")
        mock_shell_detector_class.return_value = mock_detector
        
        installer = ShellInstaller()
        result = installer.install()
        
        assert result is False
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    @patch('kolja_aws.shell_installer.ScriptGenerator')
    @patch('kolja_aws.shell_installer.BackupManager')
    def test_installation_with_backup_failure(self, mock_backup_manager_class,
                                             mock_script_generator_class,
                                             mock_shell_detector_class):
        """Test installation handling when backup fails"""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = self.temp_config
        mock_detector.validate_config_file_access.return_value = None
        mock_shell_detector_class.return_value = mock_detector
        
        mock_generator = Mock()
        mock_script_generator_class.return_value = mock_generator
        
        mock_backup_mgr = Mock()
        mock_backup_mgr.create_backup.side_effect = Exception("Backup failed")
        mock_backup_manager_class.return_value = mock_backup_mgr
        
        installer = ShellInstaller()
        result = installer.install()
        
        assert result is False
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    @patch('kolja_aws.shell_installer.ScriptGenerator')
    @patch('kolja_aws.shell_installer.BackupManager')
    def test_uninstallation_flow(self, mock_backup_manager_class,
                                mock_script_generator_class,
                                mock_shell_detector_class):
        """Test complete uninstallation flow"""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = self.temp_config
        mock_detector.validate_config_file_access.return_value = None
        mock_shell_detector_class.return_value = mock_detector
        
        mock_generator = Mock()
        mock_generator.is_script_installed.return_value = True
        mock_generator.remove_existing_script.return_value = "# Test bashrc\nexport PATH=/usr/bin"
        mock_script_generator_class.return_value = mock_generator
        
        mock_backup_mgr = Mock()
        mock_backup_mgr.create_backup.return_value = f"{self.temp_config}.backup"
        mock_backup_manager_class.return_value = mock_backup_mgr
        
        installer = ShellInstaller()
        result = installer.uninstall()
        
        assert result is True
        mock_generator.remove_existing_script.assert_called_once()


class TestEndToEndProfileSwitching:
    """Test end-to-end profile switching scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
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
                name="612674025488-ReadOnlyAccess",
                is_current=False,
                sso_session="my-sso",
                account_id="612674025488",
                role_name="ReadOnlyAccess",
                region="us-west-2"
            ),
            ProfileInfo(
                name="default",
                is_current=False,
                region="us-east-1"
            )
        ]
    
    @patch('kolja_aws.profile_switcher.ProfileLoader')
    @patch('rich.prompt.Prompt.ask')
    def test_complete_profile_switching_flow(self, mock_prompt, mock_loader_class):
        """Test complete profile switching flow"""
        # Setup mocks
        mock_loader = Mock()
        mock_loader.load_profiles.return_value = self.sample_profiles
        mock_loader_class.return_value = mock_loader
        
        mock_prompt.return_value = '2'  # Select second profile
        
        switcher = ProfileSwitcher()
        
        with patch.object(switcher, '_display_profiles_table'):
            result = switcher.show_interactive_menu()
        
        assert result == "612674025488-ReadOnlyAccess"
        mock_loader.load_profiles.assert_called_once()
    
    @patch('kolja_aws.profile_switcher.ProfileLoader')
    @patch('rich.prompt.Prompt.ask')
    def test_profile_switching_with_no_profiles(self, mock_prompt, mock_loader_class):
        """Test profile switching when no profiles are available"""
        mock_loader = Mock()
        mock_loader.load_profiles.return_value = []
        mock_loader_class.return_value = mock_loader
        
        switcher = ProfileSwitcher()
        
        with patch.object(switcher, '_show_no_profiles_message') as mock_show_message:
            result = switcher.show_interactive_menu()
        
        assert result is None
        mock_show_message.assert_called_once()
    
    @patch('kolja_aws.profile_switcher.ProfileLoader')
    @patch('rich.prompt.Prompt.ask')
    def test_profile_switching_user_cancellation(self, mock_prompt, mock_loader_class):
        """Test profile switching when user cancels"""
        mock_loader = Mock()
        mock_loader.load_profiles.return_value = self.sample_profiles
        mock_loader_class.return_value = mock_loader
        
        mock_prompt.return_value = 'q'  # User quits
        
        switcher = ProfileSwitcher()
        
        with patch.object(switcher, '_display_profiles_table'):
            result = switcher.show_interactive_menu()
        
        assert result is None


class TestShellIntegrationMain:
    """Test shell integration main function"""
    
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    @patch('sys.exit')
    def test_shell_integration_main_success(self, mock_exit, mock_switcher_class):
        """Test shell integration main function success"""
        mock_switcher = Mock()
        mock_switcher.show_interactive_menu.return_value = "test-profile"
        mock_switcher_class.return_value = mock_switcher
        
        with patch('builtins.print') as mock_print:
            shell_integration_main()
        
        mock_print.assert_called_once_with("test-profile")
        mock_exit.assert_called_once_with(0)
    
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    @patch('sys.exit')
    def test_shell_integration_main_no_selection(self, mock_exit, mock_switcher_class):
        """Test shell integration main function with no selection"""
        mock_switcher = Mock()
        mock_switcher.show_interactive_menu.return_value = None
        mock_switcher_class.return_value = mock_switcher
        
        shell_integration_main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('kolja_aws.shell_integration.ProfileSwitcher')
    @patch('sys.exit')
    def test_shell_integration_main_keyboard_interrupt(self, mock_exit, mock_switcher_class):
        """Test shell integration main function with keyboard interrupt"""
        mock_switcher = Mock()
        mock_switcher.show_interactive_menu.side_effect = KeyboardInterrupt()
        mock_switcher_class.return_value = mock_switcher
        
        with patch('builtins.print') as mock_print:
            shell_integration_main()
        
        mock_print.assert_called_once_with("Profile switching cancelled", file=pytest.importorskip('sys').stderr)
        mock_exit.assert_called_once_with(1)


class TestErrorScenarios:
    """Test various error scenarios and recovery"""
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    def test_permission_denied_error_handling(self, mock_shell_detector_class):
        """Test handling of permission denied errors"""
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = "~/.bashrc"
        mock_detector.validate_config_file_access.side_effect = PermissionError("Permission denied")
        mock_shell_detector_class.return_value = mock_detector
        
        installer = ShellInstaller()
        result = installer.install()
        
        assert result is False
    
    @patch('kolja_aws.profile_switcher.ProfileLoader')
    def test_aws_config_missing_error_handling(self, mock_loader_class):
        """Test handling of missing AWS config"""
        mock_loader = Mock()
        mock_loader.load_profiles.side_effect = FileNotFoundError("AWS config not found")
        mock_loader_class.return_value = mock_loader
        
        switcher = ProfileSwitcher()
        
        with patch.object(switcher, '_show_profile_load_error') as mock_show_error:
            result = switcher.show_interactive_menu()
        
        assert result is None
        mock_show_error.assert_called_once()
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    @patch('kolja_aws.shell_installer.ScriptGenerator')
    @patch('kolja_aws.shell_installer.BackupManager')
    def test_script_validation_failure(self, mock_backup_manager_class,
                                     mock_script_generator_class,
                                     mock_shell_detector_class):
        """Test handling of script validation failure"""
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = "/tmp/test_config"
        mock_detector.validate_config_file_access.return_value = None
        mock_shell_detector_class.return_value = mock_detector
        
        mock_generator = Mock()
        mock_generator.get_script_for_shell.return_value = "invalid script"
        mock_generator.validate_script_syntax.return_value = False  # Validation fails
        mock_script_generator_class.return_value = mock_generator
        
        mock_backup_mgr = Mock()
        mock_backup_mgr.create_backup.return_value = "/tmp/test_config.backup"
        mock_backup_manager_class.return_value = mock_backup_mgr
        
        installer = ShellInstaller()
        result = installer.install()
        
        assert result is False


class TestBackupAndRecovery:
    """Test backup and recovery mechanisms"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config = os.path.join(self.temp_dir, ".bashrc")
        
        # Create a temporary config file
        with open(self.temp_config, 'w') as f:
            f.write("# Original config\nexport PATH=/usr/bin\n")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('kolja_aws.shell_installer.ShellDetector')
    @patch('kolja_aws.shell_installer.ScriptGenerator')
    def test_backup_creation_and_restoration(self, mock_script_generator_class, 
                                            mock_shell_detector_class):
        """Test backup creation and restoration on failure"""
        from kolja_aws.backup_manager import BackupManager
        
        # Setup mocks
        mock_detector = Mock()
        mock_detector.detect_shell.return_value = "bash"
        mock_detector.get_config_file.return_value = self.temp_config
        mock_detector.validate_config_file_access.return_value = None
        mock_shell_detector_class.return_value = mock_detector
        
        mock_generator = Mock()
        mock_generator.get_script_for_shell.return_value = "sp() { echo 'test'; }"
        mock_generator.insert_script_into_config.side_effect = Exception("Write failed")
        mock_script_generator_class.return_value = mock_generator
        
        # Test that backup is created and restored on failure
        installer = ShellInstaller()
        result = installer.install()
        
        assert result is False
        
        # Verify original content is preserved
        with open(self.temp_config, 'r') as f:
            content = f.read()
        
        assert "# Original config" in content
        assert "export PATH=/usr/bin" in content
    
    def test_backup_manager_integration(self):
        """Test backup manager integration"""
        from kolja_aws.backup_manager import BackupManager
        
        backup_mgr = BackupManager()
        
        # Create backup
        backup_path = backup_mgr.create_backup(self.temp_config)
        assert os.path.exists(backup_path)
        
        # Modify original file
        with open(self.temp_config, 'w') as f:
            f.write("# Modified config\n")
        
        # Restore backup
        result = backup_mgr.restore_backup(backup_path)
        assert result is True
        
        # Verify restoration
        with open(self.temp_config, 'r') as f:
            content = f.read()
        
        assert "# Original config" in content
        assert "export PATH=/usr/bin" in content


class TestCrossShellCompatibility:
    """Test compatibility across different shells"""
    
    @pytest.mark.parametrize("shell_type,expected_script_elements", [
        ("bash", ["sp()", "export AWS_PROFILE", "if ["]),
        ("zsh", ["sp()", "export AWS_PROFILE", "if ["]),
        ("fish", ["function sp", "set -gx AWS_PROFILE", "if test"])
    ])
    def test_script_generation_for_different_shells(self, shell_type, expected_script_elements):
        """Test script generation for different shell types"""
        from kolja_aws.script_generator import ScriptGenerator
        
        generator = ScriptGenerator()
        script = generator.get_script_for_shell(shell_type)
        
        for element in expected_script_elements:
            assert element in script
        
        # Verify script syntax validation
        is_valid = generator.validate_script_syntax(script, shell_type)
        assert is_valid is True
    
    def test_shell_detection_fallback(self):
        """Test shell detection with various environment configurations"""
        from kolja_aws.shell_detector import ShellDetector
        
        detector = ShellDetector()
        
        # Test with different SHELL environment variables
        test_shells = [
            ("/bin/bash", "bash"),
            ("/usr/local/bin/zsh", "zsh"),
            ("/usr/bin/fish", "fish")
        ]
        
        for shell_path, expected_shell in test_shells:
            with patch.dict('os.environ', {'SHELL': shell_path}):
                detected = detector.detect_shell()
                assert detected == expected_shell


class TestPerformanceAndScalability:
    """Test performance with large numbers of profiles"""
    
    def test_large_profile_list_handling(self):
        """Test handling of large numbers of profiles"""
        # Create a large number of profiles
        large_profile_list = []
        for i in range(100):
            profile = ProfileInfo(
                name=f"profile-{i:03d}",
                account_id=f"{123456789 + i}",
                role_name=f"Role{i}",
                region="us-east-1" if i % 2 == 0 else "us-west-2"
            )
            large_profile_list.append(profile)
        
        with patch('kolja_aws.profile_switcher.ProfileLoader') as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load_profiles.return_value = large_profile_list
            mock_loader_class.return_value = mock_loader
            
            switcher = ProfileSwitcher()
            
            # Test that large profile lists are handled efficiently
            with patch.object(switcher, '_display_profiles_table') as mock_display:
                with patch('rich.prompt.Prompt.ask', return_value='q'):
                    result = switcher.show_interactive_menu()
            
            assert result is None
            mock_display.assert_called_once_with(large_profile_list)
    
    def test_profile_loading_performance(self):
        """Test profile loading performance"""
        import time
        
        with patch('kolja_aws.profile_loader.ProfileLoader') as mock_loader_class:
            mock_loader = Mock()
            
            # Simulate slow profile loading
            def slow_load():
                time.sleep(0.1)  # Simulate some delay
                return [ProfileInfo(name="test-profile")]
            
            mock_loader.load_profiles.side_effect = slow_load
            mock_loader_class.return_value = mock_loader
            
            switcher = ProfileSwitcher()
            
            start_time = time.time()
            profiles = switcher.list_profiles()
            end_time = time.time()
            
            # Verify profiles are loaded
            assert len(profiles) == 1
            assert profiles[0].name == "test-profile"
            
            # Verify reasonable performance (should complete quickly)
            assert end_time - start_time < 1.0  # Should complete within 1 second