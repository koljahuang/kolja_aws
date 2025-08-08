"""
Tests for shell environment detection
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from kolja_aws.shell_detector import ShellDetector
from kolja_aws.shell_exceptions import UnsupportedShellError, ConfigFileError


class TestShellDetector:
    """Test ShellDetector class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = ShellDetector()
    
    def test_is_shell_supported_true(self):
        """Test shell support check - positive cases"""
        assert self.detector.is_shell_supported('bash') is True
        assert self.detector.is_shell_supported('zsh') is True
        assert self.detector.is_shell_supported('fish') is True
    
    def test_is_shell_supported_false(self):
        """Test shell support check - negative cases"""
        assert self.detector.is_shell_supported('tcsh') is False
        assert self.detector.is_shell_supported('csh') is False
        assert self.detector.is_shell_supported('unknown') is False
    
    def test_get_all_supported_shells(self):
        """Test getting all supported shells"""
        supported = self.detector.get_all_supported_shells()
        expected = ['bash', 'zsh', 'fish']
        assert set(supported) == set(expected)
    
    def test_get_config_files_for_shell_bash(self):
        """Test getting config files for bash"""
        config_files = self.detector.get_config_files_for_shell('bash')
        expected = ['~/.bashrc', '~/.bash_profile']
        assert config_files == expected
    
    def test_get_config_files_for_shell_zsh(self):
        """Test getting config files for zsh"""
        config_files = self.detector.get_config_files_for_shell('zsh')
        expected = ['~/.zshrc']
        assert config_files == expected
    
    def test_get_config_files_for_shell_fish(self):
        """Test getting config files for fish"""
        config_files = self.detector.get_config_files_for_shell('fish')
        expected = ['~/.config/fish/config.fish']
        assert config_files == expected
    
    def test_get_config_files_for_unsupported_shell(self):
        """Test getting config files for unsupported shell"""
        config_files = self.detector.get_config_files_for_shell('tcsh')
        assert config_files == []
    
    @patch.dict(os.environ, {'SHELL': '/bin/bash'})
    def test_detect_shell_from_env_bash(self):
        """Test shell detection from SHELL environment variable - bash"""
        shell = self.detector.detect_shell()
        assert shell == 'bash'
    
    @patch.dict(os.environ, {'SHELL': '/usr/local/bin/zsh'})
    def test_detect_shell_from_env_zsh(self):
        """Test shell detection from SHELL environment variable - zsh"""
        shell = self.detector.detect_shell()
        assert shell == 'zsh'
    
    @patch.dict(os.environ, {'SHELL': '/usr/bin/fish'})
    def test_detect_shell_from_env_fish(self):
        """Test shell detection from SHELL environment variable - fish"""
        shell = self.detector.detect_shell()
        assert shell == 'fish'
    
    @patch.dict(os.environ, {'SHELL': '/bin/tcsh'})
    @patch('subprocess.run')
    def test_detect_shell_unsupported_env_fallback_to_ps(self, mock_run):
        """Test fallback to ps when SHELL env has unsupported shell"""
        # Mock ps command to return zsh
        mock_run.return_value = MagicMock(returncode=0, stdout='zsh\n')
        
        shell = self.detector.detect_shell()
        assert shell == 'zsh'
        
        # Verify ps was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert 'ps' in args
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('subprocess.run')
    def test_detect_shell_from_ps_command(self, mock_run):
        """Test shell detection from ps command when SHELL env is not set"""
        # Mock ps command to return bash
        mock_run.return_value = MagicMock(returncode=0, stdout='bash\n')
        
        shell = self.detector.detect_shell()
        assert shell == 'bash'
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('subprocess.run')
    def test_detect_shell_ps_fails_fallback_to_which(self, mock_run):
        """Test fallback to which command when ps fails"""
        # First call (ps) fails, second call (which zsh) succeeds
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=''),  # ps fails
            MagicMock(returncode=0, stdout='/usr/bin/zsh\n'),  # which zsh succeeds
            MagicMock(returncode=1, stdout=''),  # which bash fails
            MagicMock(returncode=1, stdout=''),  # which fish fails
        ]
        
        shell = self.detector.detect_shell()
        assert shell == 'zsh'
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('subprocess.run')
    def test_detect_shell_all_methods_fail(self, mock_run):
        """Test exception when all detection methods fail"""
        # All subprocess calls fail
        mock_run.return_value = MagicMock(returncode=1, stdout='')
        
        with pytest.raises(UnsupportedShellError) as exc_info:
            self.detector.detect_shell()
        
        assert exc_info.value.context['shell_type'] == 'unknown'
        assert 'bash' in exc_info.value.context['supported_shells']
    
    def test_get_config_file_unsupported_shell(self):
        """Test getting config file for unsupported shell"""
        with pytest.raises(UnsupportedShellError) as exc_info:
            self.detector.get_config_file('tcsh')
        
        assert exc_info.value.context['shell_type'] == 'tcsh'
    
    def test_get_config_file_existing_file(self):
        """Test getting config file when file exists"""
        # Create a temporary file to simulate existing config
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bashrc') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Mock the SUPPORTED_SHELLS to use our temp file
            original_shells = self.detector.SUPPORTED_SHELLS.copy()
            self.detector.SUPPORTED_SHELLS['bash'] = [temp_path]
            
            config_file = self.detector.get_config_file('bash')
            assert config_file == temp_path
        finally:
            # Restore original and cleanup
            self.detector.SUPPORTED_SHELLS = original_shells
            os.unlink(temp_path)
    
    def test_get_config_file_no_existing_file(self):
        """Test getting config file when no file exists"""
        # Use a non-existent path
        non_existent = '/tmp/test_nonexistent_config'
        
        # Mock the SUPPORTED_SHELLS
        original_shells = self.detector.SUPPORTED_SHELLS.copy()
        self.detector.SUPPORTED_SHELLS['bash'] = [non_existent]
        
        try:
            config_file = self.detector.get_config_file('bash')
            assert config_file == non_existent
        finally:
            # Restore original
            self.detector.SUPPORTED_SHELLS = original_shells
    
    def test_get_config_file_create_directory(self):
        """Test creating directory when it doesn't exist"""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'subdir', 'config')
            
            # Mock the SUPPORTED_SHELLS
            original_shells = self.detector.SUPPORTED_SHELLS.copy()
            self.detector.SUPPORTED_SHELLS['test'] = [config_path]
            
            try:
                config_file = self.detector.get_config_file('test')
                assert config_file == config_path
                # Directory should be created
                assert os.path.exists(os.path.dirname(config_path))
            finally:
                # Restore original
                self.detector.SUPPORTED_SHELLS = original_shells
    
    def test_validate_config_file_access_existing_readable_writable(self):
        """Test config file validation - existing file with proper permissions"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Should not raise any exception
            self.detector.validate_config_file_access(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_config_file_access_nonexistent_writable_dir(self):
        """Test config file validation - non-existent file in writable directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'nonexistent_config')
            
            # Should not raise any exception
            self.detector.validate_config_file_access(config_path)
    
    @patch('os.access')
    def test_validate_config_file_access_no_read_permission(self, mock_access):
        """Test config file validation - no read permission"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Mock os.access to return False for read permission
            def access_side_effect(path, mode):
                if mode == os.R_OK:
                    return False
                return True
            
            mock_access.side_effect = access_side_effect
            
            with pytest.raises(ConfigFileError) as exc_info:
                self.detector.validate_config_file_access(temp_path)
            
            assert "read" in exc_info.value.context['operation']
        finally:
            os.unlink(temp_path)
    
    @patch('os.access')
    def test_validate_config_file_access_no_write_permission(self, mock_access):
        """Test config file validation - no write permission"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Mock os.access to return False for write permission
            def access_side_effect(path, mode):
                if mode == os.W_OK:
                    return False
                return True
            
            mock_access.side_effect = access_side_effect
            
            with pytest.raises(ConfigFileError) as exc_info:
                self.detector.validate_config_file_access(temp_path)
            
            assert "write" in exc_info.value.context['operation']
        finally:
            os.unlink(temp_path)