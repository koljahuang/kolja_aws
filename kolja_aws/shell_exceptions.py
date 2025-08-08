"""
Shell integration exceptions

This module defines the exception hierarchy for shell integration functionality.
"""


class ShellIntegrationError(Exception):
    """Shell 集成基础异常"""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}


class UnsupportedShellError(ShellIntegrationError):
    """不支持的 Shell 类型"""
    
    def __init__(self, shell_type: str, supported_shells: list = None):
        message = f"Unsupported shell type: {shell_type}"
        if supported_shells:
            message += f". Supported shells: {', '.join(supported_shells)}"
        
        context = {
            "shell_type": shell_type,
            "supported_shells": supported_shells or []
        }
        super().__init__(message, context)


class ConfigFileError(ShellIntegrationError):
    """配置文件操作错误"""
    
    def __init__(self, file_path: str, operation: str, details: str = None):
        message = f"Failed to {operation} config file: {file_path}"
        if details:
            message += f". {details}"
        
        context = {
            "file_path": file_path,
            "operation": operation,
            "details": details
        }
        super().__init__(message, context)


class ProfileLoadError(ShellIntegrationError):
    """Profile 加载错误"""
    
    def __init__(self, message: str, aws_config_path: str = None):
        super().__init__(message)
        self.context = {
            "aws_config_path": aws_config_path
        }


class BackupError(ShellIntegrationError):
    """备份操作错误"""
    
    def __init__(self, operation: str, file_path: str, details: str = None):
        message = f"Backup {operation} failed for {file_path}"
        if details:
            message += f": {details}"
        
        context = {
            "operation": operation,
            "file_path": file_path,
            "details": details
        }
        super().__init__(message, context)