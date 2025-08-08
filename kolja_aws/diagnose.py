#!/usr/bin/env python3
"""
Diagnostic script for kolja-aws shell integration

This script helps diagnose common issues with the shell integration.
"""

import os
import sys
import subprocess
from typing import List, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from kolja_aws.shell_detector import ShellDetector
from kolja_aws.shell_integration import health_check, list_profiles
from kolja_aws.script_generator import ScriptGenerator


def main():
    """Run diagnostic checks"""
    console = Console()
    
    # Header
    header_text = Text()
    header_text.append("🔍 kolja-aws Shell Integration Diagnostics\n", style="bold blue")
    header_text.append("This tool will help diagnose common shell integration issues", style="dim")
    
    console.print(Panel(header_text, title="Diagnostics", border_style="blue"))
    
    # Run all diagnostic checks
    checks = [
        ("Python Environment", check_python_environment),
        ("Shell Detection", check_shell_detection),
        ("AWS Configuration", check_aws_configuration),
        ("Shell Integration", check_shell_integration),
        ("Profile Loading", check_profile_loading),
        ("Function Installation", check_function_installation),
    ]
    
    results = []
    for check_name, check_func in checks:
        console.print(f"\n🔍 Running {check_name} check...", style="yellow")
        try:
            status, message = check_func()
            results.append((check_name, status, message))
            
            if status == "✅":
                console.print(f"✅ {check_name}: {message}", style="green")
            elif status == "⚠️":
                console.print(f"⚠️ {check_name}: {message}", style="yellow")
            else:
                console.print(f"❌ {check_name}: {message}", style="red")
                
        except Exception as e:
            results.append((check_name, "❌", f"Error: {e}"))
            console.print(f"❌ {check_name}: Error: {e}", style="red")
    
    # Summary table
    console.print("\n📊 Diagnostic Summary", style="bold blue")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    for check_name, status, message in results:
        table.add_row(check_name, status, message)
    
    console.print(table)
    
    # Recommendations
    failed_checks = [r for r in results if r[1] == "❌"]
    warning_checks = [r for r in results if r[1] == "⚠️"]
    
    if failed_checks or warning_checks:
        console.print("\n💡 Recommendations", style="bold yellow")
        
        if failed_checks:
            console.print("Critical issues found:", style="red")
            for check_name, _, message in failed_checks:
                console.print(f"  • {check_name}: {message}", style="red")
        
        if warning_checks:
            console.print("Warnings:", style="yellow")
            for check_name, _, message in warning_checks:
                console.print(f"  • {check_name}: {message}", style="yellow")
        
        console.print("\nSuggested actions:", style="bold")
        console.print("1. Run: kolja-install-shell", style="cyan")
        console.print("2. Reload shell: source ~/.zshrc (or appropriate config file)", style="cyan")
        console.print("3. Check AWS profiles: kolja aws profiles", style="cyan")
        
    else:
        console.print("\n🎉 All checks passed! Shell integration should be working.", style="bold green")


def check_python_environment() -> Tuple[str, str]:
    """Check Python environment"""
    try:
        python_version = sys.version.split()[0]
        if sys.version_info >= (3, 8):
            return "✅", f"Python {python_version} (compatible)"
        else:
            return "❌", f"Python {python_version} (requires 3.8+)"
    except Exception as e:
        return "❌", f"Cannot determine Python version: {e}"


def check_shell_detection() -> Tuple[str, str]:
    """Check shell detection"""
    try:
        detector = ShellDetector()
        shell_type = detector.detect_shell()
        config_file = detector.get_config_file(shell_type)
        
        if os.path.exists(os.path.expanduser(config_file)):
            return "✅", f"Detected {shell_type}, config: {config_file}"
        else:
            return "⚠️", f"Detected {shell_type}, but {config_file} doesn't exist"
            
    except Exception as e:
        return "❌", f"Shell detection failed: {e}"


def check_aws_configuration() -> Tuple[str, str]:
    """Check AWS configuration"""
    aws_config_path = os.path.expanduser("~/.aws/config")
    
    if not os.path.exists(aws_config_path):
        return "❌", "No ~/.aws/config file found"
    
    try:
        with open(aws_config_path, 'r') as f:
            content = f.read()
        
        # Count profiles
        profile_count = content.count('[profile ')
        
        if profile_count == 0:
            return "⚠️", "No AWS profiles found in config"
        else:
            return "✅", f"Found {profile_count} AWS profiles"
            
    except Exception as e:
        return "❌", f"Cannot read AWS config: {e}"


def check_shell_integration() -> Tuple[str, str]:
    """Check shell integration health"""
    try:
        if health_check():
            return "✅", "Shell integration system is healthy"
        else:
            return "❌", "Shell integration system has issues"
    except Exception as e:
        return "❌", f"Health check failed: {e}"


def check_profile_loading() -> Tuple[str, str]:
    """Check profile loading"""
    try:
        profiles = list_profiles()
        if profiles:
            return "✅", f"Successfully loaded {len(profiles)} profiles"
        else:
            return "⚠️", "No profiles loaded (run 'kolja aws profiles' first)"
    except Exception as e:
        return "❌", f"Profile loading failed: {e}"


def check_function_installation() -> Tuple[str, str]:
    """Check if sp function is installed in shell"""
    try:
        detector = ShellDetector()
        shell_type = detector.detect_shell()
        config_file = detector.get_config_file(shell_type)
        config_path = os.path.expanduser(config_file)
        
        if not os.path.exists(config_path):
            return "❌", f"Shell config file {config_file} not found"
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        generator = ScriptGenerator()
        if generator.is_script_installed(content):
            return "✅", f"sp function installed in {config_file}"
        else:
            return "❌", f"sp function not found in {config_file}"
            
    except Exception as e:
        return "❌", f"Cannot check function installation: {e}"


if __name__ == "__main__":
    main()