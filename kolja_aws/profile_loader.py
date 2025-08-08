"""
AWS Profile loader

This module provides functionality to load and manage AWS profiles,
reusing existing kolja-aws logic for profile discovery.
"""

import os
import configparser
import re
from typing import List, Optional, Dict, Any
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import ProfileLoadError


class ProfileLoader:
    """AWS Profile 加载器"""
    
    def __init__(self, aws_config_path: str = "~/.aws/config"):
        self.aws_config_path = os.path.expanduser(aws_config_path)
    
    def load_profiles(self) -> List[ProfileInfo]:
        """加载所有可用的 AWS profiles"""
        try:
            if not os.path.exists(self.aws_config_path):
                raise ProfileLoadError(
                    f"AWS config file not found: {self.aws_config_path}",
                    self.aws_config_path
                )
            
            profiles = []
            current_profile = self.get_current_profile()
            
            # Parse AWS config file
            config = configparser.ConfigParser()
            config.read(self.aws_config_path)
            
            # Extract profiles from config sections
            for section_name in config.sections():
                if section_name.startswith('profile '):
                    # Extract profile name (remove 'profile ' prefix)
                    profile_name = section_name[8:]  # len('profile ') = 8
                    profile_info = self._parse_profile_section(
                        profile_name, 
                        dict(config[section_name]),
                        current_profile
                    )
                    profiles.append(profile_info)
                elif section_name == 'default':
                    # Handle default profile (no 'profile ' prefix)
                    profile_info = self._parse_profile_section(
                        'default',
                        dict(config[section_name]),
                        current_profile
                    )
                    profiles.append(profile_info)
            
            # Sort profiles: current first, then alphabetically
            profiles.sort(key=lambda p: (not p.is_current, p.name.lower()))
            
            return profiles
            
        except configparser.Error as e:
            raise ProfileLoadError(
                f"Failed to parse AWS config file: {e}",
                self.aws_config_path
            )
        except Exception as e:
            raise ProfileLoadError(
                f"Unexpected error loading profiles: {e}",
                self.aws_config_path
            )
    
    def get_current_profile(self) -> Optional[str]:
        """获取当前活动的 profile"""
        # Check AWS_PROFILE environment variable
        return os.environ.get('AWS_PROFILE')
    
    def validate_profile(self, profile_name: str) -> bool:
        """验证 profile 是否存在"""
        try:
            profiles = self.load_profiles()
            return any(profile.name == profile_name for profile in profiles)
        except ProfileLoadError:
            return False
    
    def get_profile_by_name(self, profile_name: str) -> Optional[ProfileInfo]:
        """根据名称获取 profile 信息"""
        try:
            profiles = self.load_profiles()
            for profile in profiles:
                if profile.name == profile_name:
                    return profile
            return None
        except ProfileLoadError:
            return None
    
    def _parse_profile_section(self, profile_name: str, section_data: Dict[str, str], current_profile: Optional[str]) -> ProfileInfo:
        """解析 profile 配置段"""
        is_current = profile_name == current_profile
        
        # Extract SSO information
        sso_session = section_data.get('sso_session')
        account_id = section_data.get('sso_account_id')
        role_name = section_data.get('sso_role_name')
        region = section_data.get('region')
        
        # Try to extract account ID and role from profile name if not in config
        # Format: accountId-roleName (e.g., "555286235540-AdministratorAccess")
        if not account_id or not role_name:
            match = re.match(r'^(\d+)-(.+)$', profile_name)
            if match:
                account_id = account_id or match.group(1)
                role_name = role_name or match.group(2)
        
        return ProfileInfo(
            name=profile_name,
            is_current=is_current,
            sso_session=sso_session,
            account_id=account_id,
            role_name=role_name,
            region=region
        )
    
    def get_profile_count(self) -> int:
        """获取 profile 总数"""
        try:
            profiles = self.load_profiles()
            return len(profiles)
        except ProfileLoadError:
            return 0
    
    def get_sso_profiles(self) -> List[ProfileInfo]:
        """获取所有 SSO profiles"""
        try:
            profiles = self.load_profiles()
            return [profile for profile in profiles if profile.is_sso_profile()]
        except ProfileLoadError:
            return []
    
    def get_regular_profiles(self) -> List[ProfileInfo]:
        """获取所有非 SSO profiles"""
        try:
            profiles = self.load_profiles()
            return [profile for profile in profiles if not profile.is_sso_profile()]
        except ProfileLoadError:
            return []
    
    def refresh_profiles(self) -> List[ProfileInfo]:
        """刷新并重新加载 profiles"""
        # This method can be extended to implement caching if needed
        return self.load_profiles()