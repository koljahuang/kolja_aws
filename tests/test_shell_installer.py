"""
Tests for shell integration installer
"""

import os
import tempfile
import pytest
from unittest.mock import Mock, patch, MagicMock
from kolja_aws.shell_installer import ShellInstaller
from kolja_aws.shell_models import ShellConfig
from kolja_aws.shell_exceptions import (
    ShellIntegrationError,
    UnsupportedShellError,
    ConfigFileError,
    BackupError
)


class TestShellInstaller:
    """Test ShellInstaller class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.installer = ShellInstaller()
        
        # Create sample shell config
        self.sample_config = ShellConfig(
            shell_type="bash",
            config_file="~/.bashrc"
        )
    
    def test_init(self):
        """Test ShellInstaller initialization"""
        assert self.installer.shell_detector is not None
        assert self.installer.script_generator is not None
        assert self.installer.backup_manager is not None
        assert self.installer.console is not None
    
    @patch('kolja_aws.shell_installer.Progress')
    def test_install_success(self, mock_progress):
        """Test successful installation"""
        # Setup mocks
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer.script_generator, 'get_script_for_shell') as mock_get_script, \
             patch.object(self.installer, '_create_backup_safely') as mock_backup, \
             patch.object(self.installer, '_install_script_safely') as mock_install, \
             patch.object(self.installer, '_show_installation_success') as mock_show_success:
            
            mock_detect.return_value = self.sample_config
            mock_get_script.return_value = "sp() { echo 'test'; }"
            mock_backup.return_value = "/backup/path"
            
            result = self.installer.install()
            
            assert result is True
            mock_detect.assert_called_once()
            mock_get_script.assert_called_once_with("bash")
            mock_backup.assert_called_once()
            mock_install.assert_called_once()
            mock_show_success.assert_called_once()
    
    @patch('kolja_aws.shell_installer.Progress')
    def test_install_shell_integration_error(self, mock_progress):
        """Test installation with shell integration error"""
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, '_handle_installation_error') as mock_handle_error:
            
            mock_detect.side_effect = ShellIntegrationError("Test error")
            
            result = self.installer.install()
            
            assert result is False
            mock_handle_error.assert_called_once()
    
    @patch('kolja_aws.shell_installer.Progress')
    def test_install_unexpected_error(self, mock_progress):
        """Test installation with unexpected error"""
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, '_handle_unexpected_error') as mock_handle_error:
            
            mock_detect.side_effect = Exception("Unexpected error")
            
            result = self.installer.install()
            
            assert result is False
            mock_handle_error.assert_called_once()
    
    @patch('kolja_aws.shell_installer.Progress')
    def test_uninstall_success(self, mock_progress):
        """Test successful uninstallation"""
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, 'is_installed') as mock_is_installed, \
             patch.object(self.installer, '_create_backup_safely') as mock_backup, \
             patch.object(self.installer, '_uninstall_script_safely') as mock_uninstall, \
             patch.object(self.installer, '_show_uninstallation_success') as mock_show_success:
            
            mock_detect.return_value = self.sample_config
            mock_is_installed.return_value = True
            mock_backup.return_value = "/backup/path"
            
            result = self.installer.uninstall()
            
            assert result is True
            mock_detect.assert_called_once()
            mock_is_installed.assert_called_once()
            mock_backup.assert_called_once()
            mock_uninstall.assert_called_once()
            mock_show_success.assert_called_once()
    
    @patch('kolja_aws.shell_installer.Progress')
    def test_uninstall_not_installed(self, mock_progress):
        """Test uninstallation when not installed"""
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, 'is_installed') as mock_is_installed, \
             patch.object(self.installer.console, 'print') as mock_print:
            
            mock_detect.return_value = self.sample_config
            mock_is_installed.return_value = False
            
            result = self.installer.uninstall()
            
            assert result is True
            mock_print.assert_called()
    
    def test_is_installed_true(self):
        """Test is_installed when script is installed"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, '_read_config_file') as mock_read, \
             patch.object(self.installer.script_generator, 'is_script_installed') as mock_is_installed:
            
            mock_detect.return_value = self.sample_config
            mock_read.return_value = "# config content with script"
            mock_is_installed.return_value = True
            
            result = self.installer.is_installed()
            assert result is True
    
    def test_is_installed_false(self):
        """Test is_installed when script is not installed"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, '_read_config_file') as mock_read, \
             patch.object(self.installer.script_generator, 'is_script_installed') as mock_is_installed:
            
            mock_detect.return_value = self.sample_config
            mock_read.return_value = "# config content without script"
            mock_is_installed.return_value = False
            
            result = self.installer.is_installed()
            assert result is False
    
    def test_is_installed_error(self):
        """Test is_installed with error"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect:
            mock_detect.side_effect = ShellIntegrationError("Test error")
            
            result = self.installer.is_installed()
            assert result is False
    
    def test_get_installation_status_installed(self):
        """Test getting installation status when installed"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, 'is_installed') as mock_is_installed, \
             patch.object(self.installer.backup_manager, 'list_backups') as mock_list_backups, \
             patch('os.path.exists') as mock_exists:
            
            mock_detect.return_value = self.sample_config
            mock_is_installed.return_value = True
            mock_list_backups.return_value = ["/backup1", "/backup2"]
            mock_exists.return_value = True
            
            status = self.installer.get_installation_status()
            
            assert status['installed'] is True
            assert status['shell_type'] == "bash"
            assert status['config_file'] == "~/.bashrc"
            assert status['config_file_exists'] is True
            assert status['backup_count'] == 2
            assert status['latest_backup'] == "/backup1"
    
    def test_get_installation_status_not_installed(self):
        """Test getting installation status when not installed"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect, \
             patch.object(self.installer, 'is_installed') as mock_is_installed, \
             patch('os.path.exists') as mock_exists:
            
            mock_detect.return_value = self.sample_config
            mock_is_installed.return_value = False
            mock_exists.return_value = True
            
            status = self.installer.get_installation_status()
            
            assert status['installed'] is False
            assert status['shell_type'] == "bash"
            assert 'backup_count' not in status
    
    def test_get_installation_status_error(self):
        """Test getting installation status with error"""
        with patch.object(self.installer, '_detect_and_validate_shell') as mock_detect:
            mock_detect.side_effect = Exception("Test error")
            
            status = self.installer.get_installation_status()
            
            assert status['installed'] is False
            assert 'error' in status
    
    def test_detect_and_validate_shell_success(self):
        """Test successful shell detection and validation"""
        with patch.object(self.installer.shell_detector, 'detect_shell') as mock_detect, \
             patch.object(self.installer.shell_detector, 'get_config_file') as mock_get_config, \
             patch.object(self.installer.shell_detector, 'validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = "bash"
            mock_get_config.return_value = "~/.bashrc"
            
            result = self.installer._detect_and_validate_shell()
            
            assert isinstance(result, ShellConfig)
            assert result.shell_type == "bash"
            assert result.config_file == "~/.bashrc"
    
    def test_detect_and_validate_shell_unsupported(self):
        """Test shell detection with unsupported shell"""
        with patch.object(self.installer.shell_detector, 'detect_shell') as mock_detect:
            mock_detect.side_effect = UnsupportedShellError("tcsh", ["bash", "zsh"])
            
            with pytest.raises(ShellIntegrationError) as exc_info:
                self.installer._detect_and_validate_shell()
            
            assert "Unsupported shell: tcsh" in str(exc_info.value)
    
    def test_detect_and_validate_shell_config_error(self):
        """Test shell detection with config file error"""
        with patch.object(self.installer.shell_detector, 'detect_shell') as mock_detect, \
             patch.object(self.installer.shell_detector, 'get_config_file') as mock_get_config, \
             patch.object(self.installer.shell_detector, 'validate_config_file_access') as mock_validate:
            
            mock_detect.return_value = "bash"
            mock_get_config.return_value = "~/.bashrc"
            mock_validate.side_effect = ConfigFileError("~/.bashrc", "read", "Permission denied")
            
            with pytest.raises(ShellIntegrationError) as exc_info:
                self.installer._detect_and_validate_shell()
            
            assert "Config file error" in str(exc_info.value)
    
    def test_create_backup_safely_success(self):
        """Test successful backup creation"""
        with patch('os.path.exists') as mock_exists, \
             patch.object(self.installer.backup_manager, 'create_backup') as mock_create, \
             patch.object(self.installer.backup_manager, 'cleanup_old_backups') as mock_cleanup:
            
            mock_exists.return_value = True
            mock_create.return_value = "/backup/path"
            
            result = self.installer._create_backup_safely(self.sample_config)
            
            assert result == "/backup/path"
            mock_create.assert_called_once_with("~/.bashrc")
            mock_cleanup.assert_called_once_with("~/.bashrc")
    
    def test_create_backup_safely_no_file(self):
        """Test backup creation when config file doesn't exist"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            result = self.installer._create_backup_safely(self.sample_config)
            
            assert result == ""
    
    def test_create_backup_safely_error(self):
        """Test backup creation with error"""
        with patch('os.path.exists') as mock_exists, \
             patch.object(self.installer.backup_manager, 'create_backup') as mock_create:
            
            mock_exists.return_value = True
            mock_create.side_effect = BackupError("create", "~/.bashrc", "Permission denied")
            
            with pytest.raises(ShellIntegrationError) as exc_info:
                self.installer._create_backup_safely(self.sample_config)
            
            assert "Backup failed" in str(exc_info.value)
    
    def test_install_script_safely_success(self):
        """Test successful script installation"""
        script = "sp() { echo 'test'; }"
        
        with patch.object(self.installer, '_read_config_file') as mock_read, \
             patch.object(self.installer.script_generator, 'insert_script_into_config') as mock_insert, \
             patch.object(self.installer, '_write_config_file') as mock_write, \
             patch.object(self.installer.script_generator, 'validate_script_syntax') as mock_validate:
            
            mock_read.return_value = "# existing config"
            mock_insert.return_value = "# existing config\nsp() { echo 'test'; }"
            mock_validate.return_value = True
            
            self.installer._install_script_safely(self.sample_config, script)
            
            mock_read.assert_called_once_with("~/.bashrc")
            mock_insert.assert_called_once()
            mock_write.assert_called_once()
            mock_validate.assert_called_once()
    
    def test_install_script_safely_invalid_syntax(self):
        """Test script installation with invalid syntax"""
        script = "invalid script"
        
        with patch.object(self.installer, '_read_config_file') as mock_read, \
             patch.object(self.installer.script_generator, 'insert_script_into_config') as mock_insert, \
             patch.object(self.installer, '_write_config_file') as mock_write, \
             patch.object(self.installer.script_generator, 'validate_script_syntax') as mock_validate:
            
            mock_read.return_value = "# existing config"
            mock_insert.return_value = "# existing config\ninvalid script"
            mock_validate.return_value = False
            
            with pytest.raises(ShellIntegrationError) as exc_info:
                self.installer._install_script_safely(self.sample_config, script)
            
            assert "invalid syntax" in str(exc_info.value)
    
    def test_install_script_safely_with_backup_restore(self):
        """Test script installation with backup restore on error"""
        script = "sp() { echo 'test'; }"
        self.sample_config.backup_file = "/backup/path"
        
        with patch.object(self.installer, '_read_config_file') as mock_read, \
             patch.object(self.installer, '_write_config_file') as mock_write, \
             patch.object(self.installer.backup_manager, 'restore_backup') as mock_restore, \
             patch('os.path.exists') as mock_exists:
            
            mock_read.return_value = "# existing config"
            mock_write.side_effect = Exception("Write failed")
            mock_exists.return_value = True
            
            with pytest.raises(ShellIntegrationError):
                self.installer._install_script_safely(self.sample_config, script)
            
            mock_restore.assert_called_once_with("/backup/path")
    
    def test_read_config_file_exists(self):
        """Test reading existing config file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("# test config\nexport PATH=/usr/bin")
            temp_path = temp_file.name
        
        try:
            content = self.installer._read_config_file(temp_path)
            assert "# test config" in content
            assert "export PATH=/usr/bin" in content
        finally:
            os.unlink(temp_path)
    
    def test_read_config_file_not_exists(self):
        """Test reading non-existent config file"""
        content = self.installer._read_config_file("/nonexistent/file")
        assert content == ""
    
    def test_read_config_file_permission_error(self):
        """Test reading config file with permission error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigFileError) as exc_info:
                self.installer._read_config_file("~/.bashrc")
            
            assert exc_info.value.context['operation'] == 'read'
    
    def test_write_config_file_success(self):
        """Test successful config file writing"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            content = "# new config\nexport TEST=value"
            self.installer._write_config_file(temp_path, content)
            
            with open(temp_path, 'r') as f:
                written_content = f.read()
            
            assert written_content == content
        finally:
            os.unlink(temp_path)
    
    def test_write_config_file_create_directory(self):
        """Test config file writing with directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "subdir", "config")
            content = "# test config"
            
            self.installer._write_config_file(config_path, content)
            
            assert os.path.exists(config_path)
            with open(config_path, 'r') as f:
                assert f.read() == content
    
    def test_write_config_file_permission_error(self):
        """Test config file writing with permission error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigFileError) as exc_info:
                self.installer._write_config_file("~/.bashrc", "content")
            
            assert exc_info.value.context['operation'] == 'write'
    
    def test_show_installation_success(self):
        """Test showing installation success message"""
        with patch.object(self.installer.script_generator, 'get_installation_instructions') as mock_get_instructions, \
             patch.object(self.installer.console, 'print') as mock_print:
            
            mock_get_instructions.return_value = "Installation instructions"
            
            self.installer._show_installation_success(self.sample_config)
            
            mock_get_instructions.assert_called_once_with("bash", "~/.bashrc")
            assert mock_print.call_count >= 2  # Empty lines + panel
    
    def test_show_uninstallation_success(self):
        """Test showing uninstallation success message"""
        with patch.object(self.installer.console, 'print') as mock_print:
            self.installer._show_uninstallation_success(self.sample_config)
            
            assert mock_print.call_count >= 2  # Empty lines + panel
    
    def test_handle_installation_error(self):
        """Test handling installation error"""
        error = ShellIntegrationError("Test error")
        
        with patch.object(self.installer.console, 'print') as mock_print:
            self.installer._handle_installation_error(error)
            
            assert mock_print.call_count >= 2  # Empty lines + panel
    
    def test_handle_unexpected_error(self):
        """Test handling unexpected error"""
        error = Exception("Unexpected error")
        
        with patch.object(self.installer.console, 'print') as mock_print:
            self.installer._handle_unexpected_error(error)
            
            assert mock_print.call_count >= 2  # Empty lines + panel