"""
User experience enhancements

This module provides enhanced error handling, user feedback, and
performance optimizations for the shell profile switcher.
"""

import os
import sys
import time
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Confirm
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.shell_exceptions import (
    ShellIntegrationError,
    UnsupportedShellError,
    ConfigFileError,
    ProfileLoadError,
    BackupError
)


class UserExperienceManager:
    """用户体验管理器"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.error_suggestions = {
            'profile_not_found': [
                "Check if the profile name is spelled correctly",
                "Run 'kolja aws profiles' to generate profiles from your SSO sessions",
                "Verify your AWS configuration with 'aws configure list-profiles'",
                "Make sure you're logged in with 'kolja aws login'"
            ],
            'permission_denied': [
                "Check file permissions for your shell configuration file",
                "Try running the command with appropriate permissions",
                "Ensure the directory exists and is writable",
                "Contact your system administrator if needed"
            ],
            'shell_not_supported': [
                "Currently supported shells: bash, zsh, fish",
                "Consider switching to a supported shell",
                "Check if your shell is correctly detected",
                "File an issue if you need support for your shell"
            ],
            'aws_config_missing': [
                "Install AWS CLI: 'pip install awscli' or use your package manager",
                "Create AWS config directory: 'mkdir -p ~/.aws'",
                "Configure AWS: 'aws configure' or 'kolja aws set <session-name>'",
                "Check AWS documentation for setup instructions"
            ],
            'sso_not_configured': [
                "Set up SSO session: 'kolja aws set <session-name>'",
                "Login to SSO: 'kolja aws login'",
                "Generate profiles: 'kolja aws profiles'",
                "Check your SSO configuration and permissions"
            ]
        }
    
    def show_enhanced_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """显示增强的错误消息"""
        error_type = self._classify_error(error)
        suggestions = self._get_error_suggestions(error_type, context)
        
        # 创建错误面板
        error_text = Text()
        error_text.append("❌ Error: ", style="bold red")
        error_text.append(str(error), style="red")
        
        if suggestions:
            error_text.append("\n\n💡 Suggestions:\n", style="bold yellow")
            for i, suggestion in enumerate(suggestions, 1):
                error_text.append(f"{i}. {suggestion}\n", style="dim")
        
        # 添加故障排除链接
        error_text.append("\n🔗 Need more help? ", style="dim")
        error_text.append("Check the troubleshooting guide", style="dim cyan underline")
        
        self.console.print()
        self.console.print(Panel(
            error_text,
            title="Error Details",
            border_style="red",
            expand=False
        ))
        self.console.print()
    
    def show_loading_indicator(self, message: str, duration: Optional[float] = None) -> None:
        """显示加载指示器"""
        if duration:
            # 有确定时长的进度条
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(message, total=100)
                
                step = 100 / (duration * 10)  # 10 updates per second
                for i in range(int(duration * 10)):
                    time.sleep(0.1)
                    progress.update(task, advance=step)
        else:
            # 无限旋转的加载指示器
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                progress.add_task(message, total=None)
                time.sleep(1)  # 模拟加载时间
    
    def show_profile_table_enhanced(self, profiles: List[ProfileInfo], show_details: bool = True) -> None:
        """显示增强的 profile 表格"""
        if not profiles:
            self._show_no_profiles_help()
            return
        
        # 创建表格
        table = Table(
            title="🔄 AWS Profile Switcher",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        # 添加列
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Status", width=10, justify="center")
        table.add_column("Profile Name", style="cyan", min_width=20)
        
        if show_details:
            table.add_column("Account ID", style="green", width=12)
            table.add_column("Role", style="yellow", min_width=15)
            table.add_column("Region", style="blue", width=12)
            table.add_column("Type", width=6, justify="center")
        
        # 添加行
        for i, profile in enumerate(profiles, 1):
            # 状态指示器
            if profile.is_current:
                status = "[green]🟢 ACTIVE[/green]"
            elif profile.is_sso_profile():
                status = "[blue]🔐 SSO[/blue]"
            else:
                status = "[yellow]🔑 KEY[/yellow]"
            
            # 基本信息
            row = [str(i), status, profile.name]
            
            if show_details:
                # 详细信息
                account_id = profile.account_id or "[dim]-[/dim]"
                role_name = profile.role_name or "[dim]-[/dim]"
                region = profile.region or "[dim]-[/dim]"
                profile_type = "[blue]SSO[/blue]" if profile.is_sso_profile() else "[yellow]KEY[/yellow]"
                
                row.extend([account_id, role_name, region, profile_type])
            
            table.add_row(*row)
        
        # 显示表格
        self.console.print()
        self.console.print(table)
        self.console.print()
        
        # 显示使用提示
        self._show_usage_hints(len(profiles))
    
    def show_success_with_next_steps(self, message: str, next_steps: List[str]) -> None:
        """显示成功消息和后续步骤"""
        success_text = Text()
        success_text.append("✅ ", style="bold green")
        success_text.append(message, style="green")
        
        if next_steps:
            success_text.append("\n\n📋 Next steps:\n", style="bold")
            for i, step in enumerate(next_steps, 1):
                success_text.append(f"{i}. {step}\n", style="dim")
        
        self.console.print()
        self.console.print(Panel(
            success_text,
            title="Success",
            border_style="green",
            expand=False
        ))
        self.console.print()
    
    def show_warning_with_options(self, message: str, options: List[str]) -> Optional[str]:
        """显示警告消息和选项"""
        warning_text = Text()
        warning_text.append("⚠️  ", style="bold yellow")
        warning_text.append(message, style="yellow")
        
        if options:
            warning_text.append("\n\nAvailable options:\n", style="bold")
            for i, option in enumerate(options, 1):
                warning_text.append(f"{i}. {option}\n", style="dim")
        
        self.console.print()
        self.console.print(Panel(
            warning_text,
            title="Warning",
            border_style="yellow",
            expand=False
        ))
        
        # 让用户选择选项
        if options:
            from rich.prompt import Prompt
            choice = Prompt.ask(
                "Choose an option",
                choices=[str(i) for i in range(1, len(options) + 1)] + ['q'],
                default='q'
            )
            
            if choice != 'q':
                return options[int(choice) - 1]
        
        return None
    
    def confirm_action(self, message: str, default: bool = True) -> bool:
        """确认用户操作"""
        return Confirm.ask(f"🤔 {message}", default=default)
    
    def show_performance_tips(self) -> None:
        """显示性能优化提示"""
        tips = [
            "Use 'sp' command for quick profile switching",
            "Set KOLJA_LOG_LEVEL=ERROR to reduce output",
            "Keep your AWS profiles organized with descriptive names",
            "Regularly clean up unused profiles",
            "Use SSO for better security and performance"
        ]
        
        tips_text = Text()
        tips_text.append("💡 Performance Tips:\n\n", style="bold cyan")
        
        for tip in tips:
            tips_text.append(f"• {tip}\n", style="dim")
        
        self.console.print()
        self.console.print(Panel(
            tips_text,
            title="Tips & Tricks",
            border_style="cyan",
            expand=False
        ))
        self.console.print()
    
    def _classify_error(self, error: Exception) -> str:
        """分类错误类型"""
        error_str = str(error).lower()
        
        if isinstance(error, UnsupportedShellError):
            return 'shell_not_supported'
        elif isinstance(error, ProfileLoadError):
            if 'not found' in error_str:
                return 'aws_config_missing'
            else:
                return 'sso_not_configured'
        elif isinstance(error, ConfigFileError):
            if 'permission' in error_str:
                return 'permission_denied'
            else:
                return 'aws_config_missing'
        elif 'profile' in error_str and 'not found' in error_str:
            return 'profile_not_found'
        elif 'permission denied' in error_str:
            return 'permission_denied'
        else:
            return 'general'
    
    def _get_error_suggestions(self, error_type: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """获取错误建议"""
        suggestions = self.error_suggestions.get(error_type, [])
        
        # 根据上下文添加特定建议
        if context:
            if error_type == 'profile_not_found' and context.get('available_profiles'):
                available = context['available_profiles'][:3]  # 显示前3个
                suggestions.insert(0, f"Available profiles: {', '.join(available)}")
        
        return suggestions
    
    def _show_no_profiles_help(self) -> None:
        """显示没有 profiles 时的帮助信息"""
        help_text = Text()
        help_text.append("🔍 No AWS profiles found!\n\n", style="bold yellow")
        help_text.append("To get started:\n", style="bold")
        help_text.append("1. Configure SSO session: ", style="dim")
        help_text.append("kolja aws set <session-name>\n", style="cyan")
        help_text.append("2. Login to SSO: ", style="dim")
        help_text.append("kolja aws login\n", style="cyan")
        help_text.append("3. Generate profiles: ", style="dim")
        help_text.append("kolja aws profiles\n", style="cyan")
        help_text.append("4. Try the switcher again: ", style="dim")
        help_text.append("sp\n", style="cyan")
        
        self.console.print()
        self.console.print(Panel(
            help_text,
            title="Getting Started",
            border_style="yellow",
            expand=False
        ))
        self.console.print()
    
    def _show_usage_hints(self, profile_count: int) -> None:
        """显示使用提示"""
        hints = [
            f"💡 Enter a number (1-{profile_count}) to select a profile",
            "💡 Press 'q' to quit without changing profiles",
            "💡 Use Ctrl+C to cancel at any time"
        ]
        
        for hint in hints:
            self.console.print(f"[dim]{hint}[/dim]")
        
        self.console.print()
    
    def show_system_info(self) -> None:
        """显示系统信息（用于调试）"""
        info_table = Table(title="System Information", border_style="blue")
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="green")
        
        # 收集系统信息
        info_items = [
            ("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("Platform", sys.platform),
            ("Shell", os.environ.get('SHELL', 'Unknown')),
            ("AWS_PROFILE", os.environ.get('AWS_PROFILE', 'Not set')),
            ("Home Directory", os.path.expanduser('~')),
            ("Current Directory", os.getcwd())
        ]
        
        for prop, value in info_items:
            info_table.add_row(prop, value)
        
        self.console.print()
        self.console.print(info_table)
        self.console.print()


# 全局用户体验管理器实例
ux_manager = UserExperienceManager()


def show_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """显示增强的错误消息（便捷函数）"""
    ux_manager.show_enhanced_error(error, context)


def show_loading(message: str, duration: Optional[float] = None) -> None:
    """显示加载指示器（便捷函数）"""
    ux_manager.show_loading_indicator(message, duration)


def show_success(message: str, next_steps: Optional[List[str]] = None) -> None:
    """显示成功消息（便捷函数）"""
    ux_manager.show_success_with_next_steps(message, next_steps or [])


def show_warning(message: str, options: Optional[List[str]] = None) -> Optional[str]:
    """显示警告消息（便捷函数）"""
    return ux_manager.show_warning_with_options(message, options or [])


def confirm(message: str, default: bool = True) -> bool:
    """确认用户操作（便捷函数）"""
    return ux_manager.confirm_action(message, default)