"""
Post-installation script for shell integration

This script runs after package installation to automatically set up
shell integration for the AWS profile switcher.
"""

import sys
import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from kolja_aws.shell_detector import ShellDetector
from kolja_aws.shell_installer import ShellInstaller
from kolja_aws.shell_exceptions import ShellIntegrationError


def main():
    """Main post-install function"""
    console = Console()
    
    # Show welcome message
    welcome_text = Text()
    welcome_text.append("🚀 Setting up kolja-aws shell integration...\n", style="bold blue")
    welcome_text.append("This will add the 'sp' command to your shell for quick AWS profile switching.", style="dim")
    
    console.print(Panel(welcome_text, title="kolja-aws Setup", border_style="blue"))
    
    try:
        # Attempt automatic installation
        installer = ShellInstaller()
        
        console.print("🔍 Detecting shell environment...", style="yellow")
        
        if installer.install():
            # Installation successful
            success_text = Text()
            success_text.append("✅ Shell integration installed successfully!\n\n", style="bold green")
            success_text.append("To start using the profile switcher:\n", style="bold")
            success_text.append("1. Reload your shell: ", style="dim")
            
            # 动态显示正确的配置文件
            try:
                detector = ShellDetector()
                shell_type = detector.detect_shell()
                config_file = detector.get_config_file(shell_type)
                success_text.append(f"source {config_file}", style="bold cyan")
            except:
                success_text.append("source your shell config file", style="bold cyan")
                success_text.append(" (e.g., ~/.bashrc, ~/.zshrc)", style="dim")
            
            success_text.append(" (or restart your terminal)\n", style="dim")
            success_text.append("2. Use the command: ", style="dim")
            success_text.append("sp", style="bold cyan")
            success_text.append(" to switch AWS profiles\n", style="dim")
            
            console.print(Panel(success_text, title="Installation Complete", border_style="green"))
            
        else:
            # Installation failed but didn't raise exception
            _show_manual_installation_guide(console)
            
    except ShellIntegrationError as e:
        # Handle known shell integration errors
        console.print(f"⚠️  Automatic installation failed: {e}", style="yellow")
        _show_manual_installation_guide(console)
        
    except Exception as e:
        # Handle unexpected errors
        console.print(f"❌ Unexpected error during installation: {e}", style="red")
        _show_manual_installation_guide(console)
        
        # Don't fail the entire pip install process
        console.print("📦 Package installation completed successfully despite shell integration issues.", style="dim")


def _show_manual_installation_guide(console: Console):
    """Show manual installation instructions"""
    manual_text = Text()
    manual_text.append("🔧 Manual Installation Available\n\n", style="bold yellow")
    manual_text.append("You can set up shell integration manually later:\n", style="dim")
    manual_text.append("Run: ", style="dim")
    manual_text.append("kolja-install-shell", style="bold cyan")
    manual_text.append(" after installation completes\n\n", style="dim")
    manual_text.append("Or add this function to your shell config manually:\n", style="dim")
    
    # Show a basic shell function example
    shell_function = '''sp() {
    python -c "
from kolja_aws.shell_integration import ProfileSwitcher
switcher = ProfileSwitcher()
profile = switcher.show_interactive_menu()
if profile: print(profile)
" | read selected_profile
    
    if [ -n "$selected_profile" ]; then
        export AWS_PROFILE="$selected_profile"
        echo "✅ Switched to profile: $selected_profile"
    fi
}'''
    
    manual_text.append(shell_function, style="dim cyan")
    
    console.print(Panel(manual_text, title="Manual Setup", border_style="yellow"))


def install_shell_integration_interactive():
    """Interactive shell integration installer (for manual use)"""
    console = Console()
    
    console.print("🔧 Manual Shell Integration Setup", style="bold blue")
    console.print("This will install the 'sp' command for AWS profile switching.\n")
    
    try:
        detector = ShellDetector()
        shell_type = detector.detect_shell()
        config_file = detector.get_config_file(shell_type)
        
        console.print(f"Detected shell: {shell_type}", style="green")
        console.print(f"Config file: {config_file}", style="green")
        
        # Ask for user confirmation
        from rich.prompt import Confirm
        if Confirm.ask("Proceed with installation?"):
            installer = ShellInstaller()
            if installer.install():
                console.print("✅ Installation completed successfully!", style="bold green")
                console.print(f"Please run: source {config_file}", style="cyan")
            else:
                console.print("❌ Installation failed", style="red")
                return False
        else:
            console.print("Installation cancelled by user.", style="yellow")
            return False
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        return False
    
    return True


if __name__ == "__main__":
    # If called directly, run interactive installation
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        install_shell_integration_interactive()
    else:
        main()