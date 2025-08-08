#!/usr/bin/env python3
"""
Shell Integration Demo

This script demonstrates the shell integration functionality
without requiring actual shell installation.
"""

import sys
import os

# Add the parent directory to the path so we can import kolja_aws
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kolja_aws.shell_integration import (
    show_interactive_menu,
    list_profiles,
    get_current_profile,
    validate_profile,
    health_check
)
from kolja_aws.shell_detector import ShellDetector
from kolja_aws.script_generator import ScriptGenerator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


def main():
    """Run the shell integration demo"""
    console = Console()
    
    # Welcome message
    welcome_text = Text()
    welcome_text.append("🚀 Shell Integration Demo\n", style="bold blue")
    welcome_text.append("This demo shows the shell integration functionality", style="dim")
    
    console.print(Panel(welcome_text, title="kolja-aws Demo", border_style="blue"))
    
    try:
        # Demo 1: Health Check
        console.print("\n1️⃣ [bold]Health Check[/bold]")
        if health_check():
            console.print("✅ Shell integration system is working", style="green")
        else:
            console.print("❌ Shell integration system has issues", style="red")
            return
        
        # Demo 2: Shell Detection
        console.print("\n2️⃣ [bold]Shell Detection[/bold]")
        detector = ShellDetector()
        try:
            shell_type = detector.detect_shell()
            config_file = detector.get_config_file(shell_type)
            console.print(f"Detected shell: {shell_type}", style="green")
            console.print(f"Config file: {config_file}", style="cyan")
        except Exception as e:
            console.print(f"Shell detection failed: {e}", style="yellow")
        
        # Demo 3: Script Generation
        console.print("\n3️⃣ [bold]Script Generation[/bold]")
        generator = ScriptGenerator()
        try:
            bash_script = generator.generate_bash_script()
            console.print("Generated Bash script (first 200 chars):", style="green")
            console.print(bash_script[:200] + "...", style="dim cyan")
        except Exception as e:
            console.print(f"Script generation failed: {e}", style="yellow")
        
        # Demo 4: Profile Listing
        console.print("\n4️⃣ [bold]Profile Listing[/bold]")
        try:
            profiles = list_profiles()
            if profiles:
                console.print(f"Found {len(profiles)} profiles:", style="green")
                for profile in profiles[:5]:  # Show first 5
                    console.print(f"  • {profile}", style="cyan")
                if len(profiles) > 5:
                    console.print(f"  ... and {len(profiles) - 5} more", style="dim")
            else:
                console.print("No profiles found. Run 'kolja aws profiles' first.", style="yellow")
        except Exception as e:
            console.print(f"Profile listing failed: {e}", style="red")
        
        # Demo 5: Current Profile
        console.print("\n5️⃣ [bold]Current Profile[/bold]")
        try:
            current = get_current_profile()
            if current:
                console.print(f"Current profile: {current}", style="green")
            else:
                console.print("No current profile set", style="yellow")
        except Exception as e:
            console.print(f"Current profile check failed: {e}", style="red")
        
        # Demo 6: Profile Validation
        console.print("\n6️⃣ [bold]Profile Validation[/bold]")
        test_profiles = ["123456789012-AdminRole", "nonexistent-profile"]
        for profile in test_profiles:
            try:
                is_valid = validate_profile(profile)
                status = "✅ Valid" if is_valid else "❌ Invalid"
                console.print(f"{profile}: {status}", style="green" if is_valid else "red")
            except Exception as e:
                console.print(f"{profile}: Error - {e}", style="red")
        
        # Demo 7: Interactive Menu (optional)
        console.print("\n7️⃣ [bold]Interactive Menu Demo[/bold]")
        console.print("Would you like to try the interactive profile selector?", style="yellow")
        console.print("(This will show the actual profile selection menu)", style="dim")
        
        try:
            response = input("Try interactive menu? (y/N): ").lower().strip()
            if response in ['y', 'yes']:
                console.print("Starting interactive menu...", style="cyan")
                selected = show_interactive_menu()
                if selected:
                    console.print(f"You selected: {selected}", style="green")
                else:
                    console.print("No profile selected", style="yellow")
            else:
                console.print("Skipping interactive menu demo", style="dim")
        except KeyboardInterrupt:
            console.print("\nDemo interrupted by user", style="yellow")
        except Exception as e:
            console.print(f"Interactive menu demo failed: {e}", style="red")
        
        # Summary
        console.print("\n🎉 [bold green]Demo Complete![/bold green]")
        console.print("To use shell integration in your terminal:", style="dim")
        console.print("1. Install: pip install kolja-aws", style="dim")
        console.print("2. Setup: kolja-install-shell (if not automatic)", style="dim")
        console.print("3. Use: sp (in your terminal)", style="dim")
        
    except KeyboardInterrupt:
        console.print("\n\nDemo interrupted by user", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Demo failed with error: {e}", style="red")
        import traceback
        console.print(traceback.format_exc(), style="dim red")


if __name__ == "__main__":
    main()