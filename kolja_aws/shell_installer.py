"""
Shell integration installer

This module provides the main installer class that coordinates all components
to install, uninstall, and manage shell integration for the profile switcher.
"""

import os
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from kolja_aws.shell_detector import ShellDetector
from kolja_aws.script_generator import ScriptGenerator
from kolja_aws.backup_manager import BackupManager
from kolja_aws.shell_models import ShellConfig
from kolja_aws.shell_exceptions import (
    ShellIntegrationError,
    UnsupportedShellError,
    ConfigFileError,
    BackupError
)
from kolja_aws.user_experience import UserExperienceManager


class ShellInstaller:
    """Shell 集成安装器"""
    
    def __init__(self):
        self.shell_detector = ShellDetector()
        self.script_generator = ScriptGenerator()
        self.backup_manager = BackupManager()
        self.console = Console()
        self.ux_manager = UserExperienceManager(self.console)
    
    def install(self) -> bool:
        """安装 shell 集成"""
        try:
            self.console.print("\n🚀 [bold cyan]Installing Shell Integration[/bold cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                
                # Step 1: Detect shell environment
                task1 = progress.add_task("Detecting shell environment...", total=None)
                shell_config = self._detect_and_validate_shell()
                progress.update(task1, description="✅ Shell environment detected")
                
                # Step 2: Generate script
                task2 = progress.add_task("Generating shell script...", total=None)
                script = self.script_generator.get_script_for_shell(shell_config.shell_type)
                progress.update(task2, description="✅ Shell script generated")
                
                # Step 3: Create backup
                task3 = progress.add_task("Creating backup...", total=None)
                backup_path = self._create_backup_safely(shell_config)
                shell_config.backup_file = backup_path
                progress.update(task3, description="✅ Backup created")
                
                # Step 4: Install script
                task4 = progress.add_task("Installing script...", total=None)
                self._install_script_safely(shell_config, script)
                progress.update(task4, description="✅ Script installed")
            
            # Show success message
            self._show_installation_success(shell_config)
            return True
            
        except ShellIntegrationError as e:
            self._handle_installation_error(e)
            return False
        except Exception as e:
            self._handle_unexpected_error(e)
            return False
    
    def uninstall(self) -> bool:
        """卸载 shell 集成"""
        try:
            self.console.print("\n🗑️  [bold yellow]Uninstalling Shell Integration[/bold yellow]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                
                # Step 1: Detect shell environment
                task1 = progress.add_task("Detecting shell environment...", total=None)
                shell_config = self._detect_and_validate_shell()
                progress.update(task1, description="✅ Shell environment detected")
                
                # Step 2: Check if installed
                task2 = progress.add_task("Checking installation status...", total=None)
                if not self.is_installed():
                    progress.update(task2, description="ℹ️  Not installed")
                    self.console.print("\n[yellow]Shell integration is not currently installed.[/yellow]")
                    return True
                progress.update(task2, description="✅ Installation found")
                
                # Step 3: Create backup before uninstall
                task3 = progress.add_task("Creating backup...", total=None)
                backup_path = self._create_backup_safely(shell_config)
                progress.update(task3, description="✅ Backup created")
                
                # Step 4: Remove script
                task4 = progress.add_task("Removing script...", total=None)
                self._uninstall_script_safely(shell_config)
                progress.update(task4, description="✅ Script removed")
            
            # Show success message
            self._show_uninstallation_success(shell_config)
            return True
            
        except ShellIntegrationError as e:
            self._handle_installation_error(e)
            return False
        except Exception as e:
            self._handle_unexpected_error(e)
            return False
    
    def is_installed(self) -> bool:
        """检查是否已安装"""
        try:
            shell_config = self._detect_and_validate_shell()
            
            # Read config file
            config_content = self._read_config_file(shell_config.config_file)
            
            # Check if script is installed
            return self.script_generator.is_script_installed(config_content)
            
        except ShellIntegrationError:
            return False
        except Exception:
            return False
    
    def get_installation_status(self) -> dict:
        """获取安装状态信息"""
        try:
            shell_config = self._detect_and_validate_shell()
            is_installed = self.is_installed()
            
            status = {
                "installed": is_installed,
                "shell_type": shell_config.shell_type,
                "config_file": shell_config.config_file,
                "config_file_exists": os.path.exists(shell_config.get_expanded_config_path())
            }
            
            if is_installed:
                # Get backup information
                backups = self.backup_manager.list_backups(shell_config.config_file)
                status["backup_count"] = len(backups)
                status["latest_backup"] = backups[0] if backups else None
            
            return status
            
        except Exception as e:
            return {
                "installed": False,
                "error": str(e)
            }
    
    def _detect_and_validate_shell(self) -> ShellConfig:
        """检测并验证 shell 环境"""
        try:
            # Detect shell type
            shell_type = self.shell_detector.detect_shell()
            
            # Get config file path
            config_file = self.shell_detector.get_config_file(shell_type)
            
            # Create shell config
            shell_config = ShellConfig(
                shell_type=shell_type,
                config_file=config_file
            )
            
            # Validate file access
            self.shell_detector.validate_config_file_access(config_file)
            
            return shell_config
            
        except UnsupportedShellError as e:
            raise ShellIntegrationError(
                f"Unsupported shell: {e.context['shell_type']}. "
                f"Supported shells: {', '.join(e.context['supported_shells'])}"
            )
        except ConfigFileError as e:
            raise ShellIntegrationError(f"Config file error: {e}")
    
    def _create_backup_safely(self, shell_config: ShellConfig) -> str:
        """安全地创建备份"""
        try:
            expanded_path = shell_config.get_expanded_config_path()
            
            if os.path.exists(expanded_path):
                backup_path = self.backup_manager.create_backup(shell_config.config_file)
                
                # Cleanup old backups
                self.backup_manager.cleanup_old_backups(shell_config.config_file)
                
                return backup_path
            else:
                # Config file doesn't exist, no backup needed
                return ""
                
        except BackupError as e:
            raise ShellIntegrationError(f"Backup failed: {e}")
    
    def _install_script_safely(self, shell_config: ShellConfig, script: str) -> None:
        """安全地安装脚本"""
        try:
            # Read current config content
            config_content = self._read_config_file(shell_config.config_file)
            
            # Insert script into config
            updated_content = self.script_generator.insert_script_into_config(
                config_content, script, shell_config.shell_type
            )
            
            # Write updated config
            self._write_config_file(shell_config.config_file, updated_content)
            
            # Validate script syntax
            if not self.script_generator.validate_script_syntax(script, shell_config.shell_type):
                raise ShellIntegrationError("Generated script has invalid syntax")
                
        except Exception as e:
            # Restore backup if something went wrong
            if shell_config.backup_file and os.path.exists(shell_config.backup_file):
                try:
                    self.backup_manager.restore_backup(shell_config.backup_file)
                except BackupError:
                    pass  # Don't mask the original error
            
            raise ShellIntegrationError(f"Script installation failed: {e}")
    
    def _uninstall_script_safely(self, shell_config: ShellConfig) -> None:
        """安全地卸载脚本"""
        try:
            # Read current config content
            config_content = self._read_config_file(shell_config.config_file)
            
            # Remove script from config
            updated_content = self.script_generator.remove_existing_script(config_content)
            
            # Write updated config
            self._write_config_file(shell_config.config_file, updated_content)
            
        except Exception as e:
            raise ShellIntegrationError(f"Script uninstallation failed: {e}")
    
    def _read_config_file(self, config_file: str) -> str:
        """读取配置文件内容"""
        expanded_path = os.path.expanduser(config_file)
        
        try:
            if os.path.exists(expanded_path):
                with open(expanded_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""  # File doesn't exist, return empty content
        except (OSError, IOError) as e:
            raise ConfigFileError(config_file, "read", str(e))
    
    def _write_config_file(self, config_file: str, content: str) -> None:
        """写入配置文件内容"""
        expanded_path = os.path.expanduser(config_file)
        
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(expanded_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except (OSError, IOError) as e:
            raise ConfigFileError(config_file, "write", str(e))
    
    def _show_installation_success(self, shell_config: ShellConfig) -> None:
        """显示安装成功消息"""
        instructions = self.script_generator.get_installation_instructions(
            shell_config.shell_type, shell_config.config_file
        )
        
        self.console.print()
        self.console.print(Panel(
            instructions,
            title="✅ Installation Complete",
            border_style="green"
        ))
        self.console.print()
    
    def _show_uninstallation_success(self, shell_config: ShellConfig) -> None:
        """显示卸载成功消息"""
        message = f"""[bold green]Shell integration removed successfully![/bold green]

Configuration updated: {shell_config.config_file}

The 'sp' command has been removed from your shell.
You can reinstall it anytime by running:
  [cyan]kolja aws sp[/cyan]

To activate the changes, run:
  [cyan]source {shell_config.config_file}[/cyan]

Or restart your terminal."""
        
        self.console.print()
        self.console.print(Panel(
            message,
            title="✅ Uninstallation Complete",
            border_style="green"
        ))
        self.console.print()
    
    def _handle_installation_error(self, error: ShellIntegrationError) -> None:
        """处理安装错误"""
        # 使用增强的错误处理
        context = {"operation": "installation"}
        self.ux_manager.show_enhanced_error(error, context)
    
    def _handle_unexpected_error(self, error: Exception) -> None:
        """处理意外错误"""
        # 使用增强的错误处理
        context = {"operation": "installation", "unexpected": True}
        self.ux_manager.show_enhanced_error(error, context)