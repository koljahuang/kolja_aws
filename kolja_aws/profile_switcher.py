"""
Interactive AWS Profile switcher

This module provides the interactive profile selection functionality
that will be called from shell scripts.
"""

import sys
import os
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
import click
from kolja_aws.profile_loader import ProfileLoader
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import ProfileLoadError
from kolja_aws.user_experience import UserExperienceManager


class ProfileSwitcher:
    """Profile 切换器（在 shell 脚本中调用）"""
    
    def __init__(self, profile_loader: Optional[ProfileLoader] = None):
        self.profile_loader = profile_loader or ProfileLoader()
        self.console = Console()
        self.ux_manager = UserExperienceManager(self.console)
    
    def show_interactive_menu(self) -> Optional[str]:
        """显示交互式选择菜单"""
        try:
            # Load available profiles
            profiles = self._load_profiles_with_fallback()
            
            if not profiles:
                self._show_no_profiles_message()
                return None
            
            # Show profiles in a nice table with enhanced UX
            self.ux_manager.show_profile_table_enhanced(profiles)
            
            # Get user selection
            try:
                while True:
                    choice = Prompt.ask(
                        "\n🔄 [bold cyan]Choose a profile[/bold cyan]",
                        choices=[str(i+1) for i in range(len(profiles))] + ['q'],
                        default='q'
                    )
                    
                    if choice.lower() == 'q':
                        self.console.print("👋 Profile switching cancelled")
                        return None
                    
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(profiles):
                            selected_profile = profiles[index]
                            return selected_profile.name
                        else:
                            self.console.print("[red]Invalid selection. Please try again.[/red]")
                    except ValueError:
                        self.console.print("[red]Invalid input. Please enter a number or 'q' to quit.[/red]")
                        
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                self.console.print("\n👋 Profile switching cancelled")
                return None
                
        except Exception as e:
            self._show_error(f"Unexpected error: {e}")
            return None
    
    def switch_profile(self, profile_name: str) -> bool:
        """切换到指定 profile"""
        try:
            # Validate that the profile exists
            if not self.profile_loader.validate_profile(profile_name):
                self._show_error(f"Profile '{profile_name}' not found")
                return False
            
            # The actual environment variable setting is handled by the shell script
            # This method is mainly for validation and future extensions
            return True
            
        except Exception as e:
            self._show_error(f"Failed to switch profile: {e}")
            return False
    
    def set_environment_variable(self, profile_name: str) -> bool:
        """设置 AWS_PROFILE 环境变量（仅用于验证和日志记录）
        
        注意：实际的环境变量设置由 shell 脚本处理，因为 Python 进程
        无法修改父 shell 的环境变量。这个方法主要用于验证和提供
        用户反馈。
        
        Args:
            profile_name: 要设置的 profile 名称
            
        Returns:
            bool: 如果 profile 有效且可以设置则返回 True
        """
        try:
            # 验证 profile 是否存在
            if not self.profile_loader.validate_profile(profile_name):
                self._show_error(f"Cannot set AWS_PROFILE: profile '{profile_name}' not found")
                return False
            
            # 获取 profile 详细信息用于确认消息
            profile_info = self.profile_loader.get_profile_by_name(profile_name)
            
            if profile_info:
                # 显示详细的切换确认信息
                self._show_profile_switch_confirmation(profile_info)
            else:
                # 基本确认消息
                self._show_success(f"AWS_PROFILE set to: {profile_name}")
            
            return True
            
        except Exception as e:
            self._show_error(f"Failed to set AWS_PROFILE: {e}")
            return False
    
    def get_environment_variable_status(self) -> dict:
        """获取当前环境变量状态信息
        
        Returns:
            dict: 包含环境变量状态的字典
        """
        try:
            current_profile = self.get_current_profile()
            
            status = {
                "aws_profile_set": current_profile is not None,
                "current_profile": current_profile,
                "profile_exists": False,
                "profile_valid": False
            }
            
            if current_profile:
                # 检查当前 profile 是否存在且有效
                status["profile_exists"] = self.profile_loader.validate_profile(current_profile)
                status["profile_valid"] = status["profile_exists"]
                
                # 获取 profile 详细信息
                if status["profile_exists"]:
                    profile_info = self.profile_loader.get_profile_by_name(current_profile)
                    if profile_info:
                        status["profile_info"] = {
                            "name": profile_info.name,
                            "is_sso": profile_info.is_sso_profile(),
                            "account_id": profile_info.account_id,
                            "role_name": profile_info.role_name,
                            "region": profile_info.region
                        }
            
            return status
            
        except Exception as e:
            return {
                "error": str(e),
                "aws_profile_set": False,
                "current_profile": None,
                "profile_exists": False,
                "profile_valid": False
            }
    
    def validate_environment_setup(self) -> bool:
        """验证环境设置是否正确
        
        Returns:
            bool: 如果环境设置正确则返回 True
        """
        try:
            status = self.get_environment_variable_status()
            
            if status.get("error"):
                self._show_error(f"Environment validation failed: {status['error']}")
                return False
            
            if not status.get("aws_profile_set"):
                self.console.print("[yellow]ℹ️  No AWS_PROFILE environment variable set[/yellow]")
                return True  # This is not necessarily an error
            
            if not status.get("profile_valid"):
                current = status.get("current_profile", "unknown")
                self._show_error(f"Current AWS_PROFILE '{current}' is not valid")
                return False
            
            # Environment is valid
            current = status.get("current_profile")
            self.console.print(f"[green]✅ AWS_PROFILE is set to valid profile: {current}[/green]")
            return True
            
        except Exception as e:
            self._show_error(f"Environment validation error: {e}")
            return False
    
    def list_profiles(self) -> List[ProfileInfo]:
        """列出所有可用的 profiles"""
        try:
            return self.profile_loader.load_profiles()
        except ProfileLoadError as e:
            self._show_error(f"Failed to load profiles: {e}")
            return []
    
    def get_current_profile(self) -> Optional[str]:
        """获取当前活动的 profile"""
        return self.profile_loader.get_current_profile()
    
    def _load_profiles_with_fallback(self) -> List[ProfileInfo]:
        """加载 profiles，包含错误处理和回退机制"""
        try:
            profiles = self.profile_loader.load_profiles()
            return profiles
        except ProfileLoadError as e:
            # Show a more user-friendly error message
            self._show_profile_load_error(e)
            return []
    
    def _display_profiles_table(self, profiles: List[ProfileInfo]) -> None:
        """显示 profiles 表格"""
        table = Table(title="🔄 AWS Profile Switcher", show_header=True, header_style="bold magenta")
        
        table.add_column("#", style="dim", width=3)
        table.add_column("Status", width=8)
        table.add_column("Profile Name", style="cyan")
        table.add_column("Account ID", style="green")
        table.add_column("Role", style="yellow")
        table.add_column("Region", style="blue")
        table.add_column("Type", width=6)
        
        for i, profile in enumerate(profiles, 1):
            # Status indicator
            if profile.is_current:
                status = "🟢 ACTIVE"
            elif profile.is_sso_profile():
                status = "🔐 SSO"
            else:
                status = "🔑 KEY"
            
            # Profile details
            account_id = profile.account_id or "-"
            role_name = profile.role_name or "-"
            region = profile.region or "-"
            profile_type = "SSO" if profile.is_sso_profile() else "KEY"
            
            table.add_row(
                str(i),
                status,
                profile.name,
                account_id,
                role_name,
                region,
                profile_type
            )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
        self.console.print("💡 [dim]Enter the number of your choice, or 'q' to quit[/dim]")
    
    def _validate_selected_profile(self, selected_display: str, profiles: List[ProfileInfo]) -> bool:
        """验证选中的 profile 是否有效"""
        # Extract the actual profile name from the display text
        # The display format is: "🟢 [ACTIVE] profile-name (...)"
        for profile in profiles:
            if profile.get_display_for_inquirer() == selected_display:
                return True
        return False
    
    def _extract_profile_name_from_display(self, display_text: str) -> Optional[str]:
        """从显示文本中提取实际的 profile 名称"""
        # Parse the display format to extract the profile name
        # Format: "🟢 [ACTIVE] profile-name (Account: 123 | Region: us-east-1)"
        try:
            # Remove status indicators and extract name
            parts = display_text.split('] ', 1)
            if len(parts) == 2:
                name_part = parts[1]
                # Remove additional info in parentheses
                if '(' in name_part:
                    name_part = name_part.split('(')[0].strip()
                return name_part
            return None
        except Exception:
            return None
    
    def _show_no_profiles_message(self) -> None:
        """显示没有找到 profiles 的消息"""
        # 使用增强的用户体验管理器
        self.ux_manager._show_no_profiles_help()
    
    def _show_profile_load_error(self, error: ProfileLoadError) -> None:
        """显示 profile 加载错误的详细信息"""
        # 使用增强的错误处理
        context = {"error_type": "profile_load"}
        self.ux_manager.show_enhanced_error(error, context)
    
    def _show_error(self, message: str) -> None:
        """显示错误消息"""
        self.console.print(f"[bold red]❌ Error:[/bold red] {message}")
    
    def _show_success(self, message: str) -> None:
        """显示成功消息"""
        self.console.print(f"[bold green]✅[/bold green] {message}")
    
    def _show_profile_switch_confirmation(self, profile_info: ProfileInfo) -> None:
        """显示 profile 切换确认信息"""
        self.console.print()
        
        # 创建确认消息
        confirmation_text = f"[bold green]✅ Switched to profile:[/bold green] [cyan]{profile_info.name}[/cyan]"
        
        # 添加详细信息
        details = []
        if profile_info.account_id:
            details.append(f"Account: [yellow]{profile_info.account_id}[/yellow]")
        if profile_info.role_name:
            details.append(f"Role: [yellow]{profile_info.role_name}[/yellow]")
        if profile_info.region:
            details.append(f"Region: [yellow]{profile_info.region}[/yellow]")
        
        profile_type = "SSO" if profile_info.is_sso_profile() else "Access Key"
        details.append(f"Type: [yellow]{profile_type}[/yellow]")
        
        if details:
            detail_text = " | ".join(details)
            confirmation_text += f"\n[dim]{detail_text}[/dim]"
        
        self.console.print(confirmation_text)
        self.console.print()
    
    def _show_environment_status(self) -> None:
        """显示当前环境变量状态"""
        status = self.get_environment_variable_status()
        
        if status.get("error"):
            self._show_error(f"Cannot get environment status: {status['error']}")
            return
        
        self.console.print("\n[bold]Current Environment Status:[/bold]")
        
        if status.get("aws_profile_set"):
            current = status.get("current_profile")
            if status.get("profile_valid"):
                self.console.print(f"AWS_PROFILE: [green]{current}[/green] ✅")
                
                # 显示 profile 详细信息
                profile_info = status.get("profile_info", {})
                if profile_info:
                    if profile_info.get("account_id"):
                        self.console.print(f"Account ID: [yellow]{profile_info['account_id']}[/yellow]")
                    if profile_info.get("role_name"):
                        self.console.print(f"Role: [yellow]{profile_info['role_name']}[/yellow]")
                    if profile_info.get("region"):
                        self.console.print(f"Region: [yellow]{profile_info['region']}[/yellow]")
                    
                    profile_type = "SSO" if profile_info.get("is_sso") else "Access Key"
                    self.console.print(f"Type: [yellow]{profile_type}[/yellow]")
            else:
                self.console.print(f"AWS_PROFILE: [red]{current}[/red] ❌ (invalid)")
        else:
            self.console.print("AWS_PROFILE: [dim]not set[/dim]")
        
        self.console.print()


# Standalone function for shell script integration
def main():
    """主入口点，供 shell 脚本调用"""
    try:
        switcher = ProfileSwitcher()
        selected_profile = switcher.show_interactive_menu()
        
        if selected_profile:
            # selected_profile is now the actual profile name
            print(selected_profile)  # Output for shell script to capture
            sys.exit(0)
        else:
            # No profile selected or user cancelled
            sys.exit(1)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nProfile switching cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()