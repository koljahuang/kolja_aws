#!/usr/bin/env python3
"""
Test script for arrow key navigation

This script demonstrates the new arrow key navigation functionality.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from kolja_aws.shell_integration import show_interactive_menu


def main():
    """Test the arrow key navigation"""
    print("🧪 Testing Arrow Key Navigation")
    print("This will show the interactive profile selector with arrow key support.")
    print("Use ↑↓ to navigate, Enter to select, Ctrl+C to cancel.\n")
    
    try:
        result = show_interactive_menu()
        if result:
            print(f"\n✅ You selected: {result}")
        else:
            print("\n👋 Selection cancelled")
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()