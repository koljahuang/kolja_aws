"""
Shell integration data models

This module defines the data models used for shell integration functionality.
"""

import os
from dataclasses import dataclass
from typing import Optional
from kolja_aws.shell_exceptions import ShellIntegrationError


@dataclass
class ShellConfig:
    """Shell 配置信息"""
    shell_type: str
    config_file: str
    backup_file: Optional[str] = None
    install_marker: str = "# kolja-aws profile switcher"
    
    def validate(self) -> None:
        """验证配置有效性"""
        # Import here to avoid circular imports
        from kolja_aws.shell_detector import ShellDetector
        
        if self.shell_type not in ShellDetector.SUPPORTED_SHELLS:
            raise ValueError(f"Unsupported shell: {self.shell_type}")
        
        expanded_path = os.path.expanduser(self.config_file)
        if not os.path.exists(expanded_path):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
    
    def get_expanded_config_path(self) -> str:
        """获取展开的配置文件路径"""
        return os.path.expanduser(self.config_file)
    
    def get_expanded_backup_path(self) -> Optional[str]:
        """获取展开的备份文件路径"""
        if self.backup_file:
            return os.path.expanduser(self.backup_file)
        return None


@dataclass
class ProfileInfo:
    """AWS Profile 信息"""
    name: str
    is_current: bool = False
    sso_session: Optional[str] = None
    account_id: Optional[str] = None
    role_name: Optional[str] = None
    region: Optional[str] = None
    last_used: Optional[str] = None
    
    def __str__(self) -> str:
        marker = " ❯" if self.is_current else "  "
        return f"{marker} {self.name}"
    
    def get_display_name(self) -> str:
        """获取用于显示的名称"""
        if self.account_id and self.role_name:
            return f"{self.name} ({self.account_id}-{self.role_name})"
        return self.name
    
    def get_display_for_inquirer(self) -> str:
        """获取用于 inquirer 显示的格式"""
        # 状态指示器
        if self.is_current:
            status = "🟢 [ACTIVE]"
        elif self.is_sso_profile():
            status = "🔐 [SSO]"
        else:
            status = "🔑 [KEY]"
        
        # 主要信息
        main_info = f"{status} {self.name}"
        
        # 附加信息
        details = []
        if self.account_id:
            details.append(f"Account: {self.account_id}")
        if self.region:
            details.append(f"Region: {self.region}")
        
        if details:
            detail_str = " | ".join(details)
            return f"{main_info} ({detail_str})"
        
        return main_info
    
    def get_search_text(self) -> str:
        """获取用于搜索的文本"""
        search_parts = [self.name]
        if self.account_id:
            search_parts.append(self.account_id)
        if self.role_name:
            search_parts.append(self.role_name)
        if self.region:
            search_parts.append(self.region)
        return " ".join(search_parts).lower()
    
    def is_sso_profile(self) -> bool:
        """检查是否为 SSO profile"""
        return self.sso_session is not None