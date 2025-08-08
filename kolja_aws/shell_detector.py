"""
Shell environment detection

This module provides functionality to detect the current shell environment
and determine appropriate configuration file paths.
"""

import os
import subprocess
from typing import Dict, List, Optional
from kolja_aws.shell_exceptions import UnsupportedShellError, ConfigFileError


class ShellDetector:
    """Shell 环境检测器"""
    
    SUPPORTED_SHELLS: Dict[str, List[str]] = {
        'bash': ['~/.bashrc', '~/.bash_profile'],
        'zsh': ['~/.zshrc'],
        'fish': ['~/.config/fish/config.fish']
    }
    
    def detect_shell(self) -> str:
        """检测当前 shell 类型"""
        # 方法1: 检查 SHELL 环境变量
        shell_env = os.environ.get('SHELL', '')
        if shell_env:
            shell_name = os.path.basename(shell_env)
            if self.is_shell_supported(shell_name):
                return shell_name
        
        # 方法2: 检查父进程
        try:
            # 使用 ps 命令获取父进程信息
            result = subprocess.run(
                ['ps', '-p', str(os.getppid()), '-o', 'comm='],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                parent_process = result.stdout.strip()
                shell_name = os.path.basename(parent_process)
                if self.is_shell_supported(shell_name):
                    return shell_name
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # ps 命令可能不可用或超时，继续其他方法
            pass
        
        # 方法3: 检查常见的 shell 可执行文件
        common_shells = ['zsh', 'bash', 'fish']
        for shell in common_shells:
            if self._is_shell_executable_available(shell) and self.is_shell_supported(shell):
                return shell
        
        # 如果都检测不到，抛出异常
        supported_list = list(self.SUPPORTED_SHELLS.keys())
        raise UnsupportedShellError("unknown", supported_list)
    
    def get_config_file(self, shell_type: str) -> str:
        """获取 shell 配置文件路径"""
        if not self.is_shell_supported(shell_type):
            supported_list = list(self.SUPPORTED_SHELLS.keys())
            raise UnsupportedShellError(shell_type, supported_list)
        
        config_files = self.SUPPORTED_SHELLS[shell_type]
        
        # 查找第一个存在的配置文件
        for config_file in config_files:
            expanded_path = os.path.expanduser(config_file)
            if os.path.exists(expanded_path):
                return config_file
        
        # 如果没有找到现有文件，返回第一个作为默认创建目标
        # 但首先确保目录存在
        default_config = config_files[0]
        expanded_default = os.path.expanduser(default_config)
        config_dir = os.path.dirname(expanded_default)
        
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
            except OSError as e:
                raise ConfigFileError(
                    default_config, 
                    "create directory", 
                    f"Failed to create directory {config_dir}: {e}"
                )
        
        return default_config
    
    def is_shell_supported(self, shell_type: str) -> bool:
        """检查 shell 是否支持"""
        return shell_type in self.SUPPORTED_SHELLS
    
    def get_all_supported_shells(self) -> List[str]:
        """获取所有支持的 shell 类型"""
        return list(self.SUPPORTED_SHELLS.keys())
    
    def get_config_files_for_shell(self, shell_type: str) -> List[str]:
        """获取指定 shell 的所有可能配置文件路径"""
        if not self.is_shell_supported(shell_type):
            return []
        return self.SUPPORTED_SHELLS[shell_type].copy()
    
    def _is_shell_executable_available(self, shell_name: str) -> bool:
        """检查 shell 可执行文件是否可用"""
        try:
            result = subprocess.run(
                ['which', shell_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def validate_config_file_access(self, config_file: str) -> None:
        """验证配置文件的访问权限"""
        expanded_path = os.path.expanduser(config_file)
        
        if os.path.exists(expanded_path):
            # 检查读写权限
            if not os.access(expanded_path, os.R_OK):
                raise ConfigFileError(config_file, "read", "No read permission")
            if not os.access(expanded_path, os.W_OK):
                raise ConfigFileError(config_file, "write", "No write permission")
        else:
            # 检查目录的写权限
            config_dir = os.path.dirname(expanded_path)
            if config_dir and not os.access(config_dir, os.W_OK):
                raise ConfigFileError(
                    config_file, 
                    "create", 
                    f"No write permission in directory {config_dir}"
                )