"""
Tests for CLI integration of shell profile switcher
"""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from kolja_aws.kolja_login import cli


class TestCLIIntegration:
    """Test CLI integration for shell profile switcher"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_install_success(self, mock_installer_class):
        """Test successful shell integration installation"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.install.return_value = True
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp'])
        
        # Verify
        assert result.exit_code == 0
        # Note: The actual installation messages come from ShellInstaller, not CLI
        mock_installer.install.assert_called_once()
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_install_failure(self, mock_installer_class):
        """Test failed shell integration installation"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.install.return_value = False
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp'])
        
        # Verify
        assert result.exit_code == 0
        assert "❌ Failed to install shell integration" in result.output
        assert "kolja-install-shell --interactive" in result.output
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_uninstall_success(self, mock_installer_class):
        """Test successful shell integration uninstallation"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.uninstall.return_value = True
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp', '--uninstall'])
        
        # Verify
        assert result.exit_code == 0
        # Note: The actual uninstallation messages come from ShellInstaller, not CLI
        mock_installer.uninstall.assert_called_once()
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_uninstall_failure(self, mock_installer_class):
        """Test failed shell integration uninstallation"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.uninstall.return_value = False
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp', '--uninstall'])
        
        # Verify
        assert result.exit_code == 0
        assert "❌ Failed to uninstall shell integration" in result.output
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_status_installed(self, mock_installer_class):
        """Test status check when shell integration is installed"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.get_installation_status.return_value = {
            'installed': True,
            'shell_type': 'bash',
            'config_file': '~/.bashrc',
            'backup_count': 2
        }
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp', '--status'])
        
        # Verify
        assert result.exit_code == 0
        assert "✅ Shell integration is installed" in result.output
        assert "Shell type: bash" in result.output
        assert "Config file: ~/.bashrc" in result.output
        assert "Backups available: 2" in result.output
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_status_not_installed(self, mock_installer_class):
        """Test status check when shell integration is not installed"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.get_installation_status.return_value = {
            'installed': False
        }
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp', '--status'])
        
        # Verify
        assert result.exit_code == 0
        assert "❌ Shell integration is not installed" in result.output
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_status_with_error(self, mock_installer_class):
        """Test status check with error"""
        # Setup mock
        mock_installer = Mock()
        mock_installer_class.return_value = mock_installer
        mock_installer.get_installation_status.return_value = {
            'installed': False,
            'error': 'Shell detection failed'
        }
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp', '--status'])
        
        # Verify
        assert result.exit_code == 0
        assert "❌ Shell integration is not installed" in result.output
        assert "Error: Shell detection failed" in result.output
    
    @patch('kolja_aws.kolja_login.ShellInstaller')
    def test_sp_exception_handling(self, mock_installer_class):
        """Test exception handling in sp command"""
        # Setup mock to raise exception
        mock_installer_class.side_effect = Exception("Test error")
        
        # Run command
        result = self.runner.invoke(cli, ['aws', 'sp'])
        
        # Verify
        assert result.exit_code == 0
        assert "❌ Error: Test error" in result.output
    
    def test_sp_help(self):
        """Test sp command help"""
        result = self.runner.invoke(cli, ['aws', 'sp', '--help'])
        
        assert result.exit_code == 0
        assert "Install shell integration for quick AWS profile switching" in result.output
        assert "--uninstall" in result.output
        assert "--status" in result.output
    
    def test_aws_group_includes_sp(self):
        """Test that sp command is included in aws group"""
        result = self.runner.invoke(cli, ['aws', '--help'])
        
        assert result.exit_code == 0
        assert "sp" in result.output