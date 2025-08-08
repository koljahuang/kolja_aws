"""
Tests for shell integration exceptions
"""

import pytest
from kolja_aws.shell_exceptions import (
    ShellIntegrationError,
    UnsupportedShellError,
    ConfigFileError,
    ProfileLoadError,
    BackupError
)


class TestShellIntegrationError:
    """Test base ShellIntegrationError class"""
    
    def test_basic_exception(self):
        """Test basic exception creation"""
        error = ShellIntegrationError("Test error")
        assert str(error) == "Test error"
        assert error.context == {}
    
    def test_exception_with_context(self):
        """Test exception with context"""
        context = {"key": "value"}
        error = ShellIntegrationError("Test error", context)
        assert str(error) == "Test error"
        assert error.context == context


class TestUnsupportedShellError:
    """Test UnsupportedShellError class"""
    
    def test_unsupported_shell_basic(self):
        """Test basic unsupported shell error"""
        error = UnsupportedShellError("tcsh")
        assert "Unsupported shell type: tcsh" in str(error)
        assert error.context["shell_type"] == "tcsh"
        assert error.context["supported_shells"] == []
    
    def test_unsupported_shell_with_supported_list(self):
        """Test unsupported shell error with supported shells list"""
        supported = ["bash", "zsh", "fish"]
        error = UnsupportedShellError("tcsh", supported)
        
        error_msg = str(error)
        assert "Unsupported shell type: tcsh" in error_msg
        assert "bash, zsh, fish" in error_msg
        assert error.context["shell_type"] == "tcsh"
        assert error.context["supported_shells"] == supported


class TestConfigFileError:
    """Test ConfigFileError class"""
    
    def test_config_file_error_basic(self):
        """Test basic config file error"""
        error = ConfigFileError("/path/to/config", "read")
        assert "Failed to read config file: /path/to/config" in str(error)
        assert error.context["file_path"] == "/path/to/config"
        assert error.context["operation"] == "read"
        assert error.context["details"] is None
    
    def test_config_file_error_with_details(self):
        """Test config file error with details"""
        error = ConfigFileError("/path/to/config", "write", "Permission denied")
        
        error_msg = str(error)
        assert "Failed to write config file: /path/to/config" in error_msg
        assert "Permission denied" in error_msg
        assert error.context["details"] == "Permission denied"


class TestProfileLoadError:
    """Test ProfileLoadError class"""
    
    def test_profile_load_error_basic(self):
        """Test basic profile load error"""
        error = ProfileLoadError("Failed to load profiles")
        assert str(error) == "Failed to load profiles"
        assert error.context["aws_config_path"] is None
    
    def test_profile_load_error_with_path(self):
        """Test profile load error with AWS config path"""
        error = ProfileLoadError("Failed to load profiles", "~/.aws/config")
        assert str(error) == "Failed to load profiles"
        assert error.context["aws_config_path"] == "~/.aws/config"


class TestBackupError:
    """Test BackupError class"""
    
    def test_backup_error_basic(self):
        """Test basic backup error"""
        error = BackupError("create", "/path/to/file")
        assert "Backup create failed for /path/to/file" in str(error)
        assert error.context["operation"] == "create"
        assert error.context["file_path"] == "/path/to/file"
        assert error.context["details"] is None
    
    def test_backup_error_with_details(self):
        """Test backup error with details"""
        error = BackupError("restore", "/path/to/file", "File not found")
        
        error_msg = str(error)
        assert "Backup restore failed for /path/to/file" in error_msg
        assert "File not found" in error_msg
        assert error.context["details"] == "File not found"