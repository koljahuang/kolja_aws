"""
Shell integration module

This module provides the main entry point for shell scripts to interact
with the AWS profile switcher functionality. It's designed to be called
directly from shell functions without depending on the CLI framework.
"""

import sys
import os
import logging
from typing import Optional
from kolja_aws.profile_switcher import ProfileSwitcher
from kolja_aws.profile_loader import ProfileLoader
from kolja_aws.shell_exceptions import ProfileLoadError, ShellIntegrationError


# Configure logging for shell integration
def _setup_logging():
    """Set up logging for shell integration"""
    log_level = os.environ.get('KOLJA_LOG_LEVEL', 'ERROR').upper()
    
    # Create logger
    logger = logging.getLogger('kolja_aws.shell_integration')
    logger.setLevel(getattr(logging, log_level, logging.ERROR))
    
    # Only add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Module-level logger
logger = _setup_logging()


class ShellIntegrationError(Exception):
    """Shell integration specific error"""
    pass


def get_profile_switcher() -> ProfileSwitcher:
    """Get a configured ProfileSwitcher instance"""
    try:
        return ProfileSwitcher()
    except Exception as e:
        logger.error(f"Failed to create ProfileSwitcher: {e}")
        raise ShellIntegrationError(f"Failed to initialize profile switcher: {e}")


def show_interactive_menu() -> Optional[str]:
    """Show interactive profile selection menu with arrow key navigation
    
    Returns:
        str: Selected profile name, or None if cancelled/error
    """
    try:
        logger.debug("Starting interactive profile selection")
        
        # Import here to avoid circular imports
        from kolja_aws.profile_loader import ProfileLoader
        import questionary
        
        profile_loader = ProfileLoader()
        
        # Load profiles
        profiles = profile_loader.load_profiles()
        if not profiles:
            print("❌ No AWS profiles found. Please run 'kolja aws profiles' first.", file=sys.stderr)
            return None
        
        # Create choices for questionary
        choices = []
        current_profile = os.environ.get('AWS_PROFILE')
        default_index = 0
        
        for i, profile in enumerate(profiles):
            # Mark current profile and set as default
            if profile.name == current_profile:
                display_name = f"🟢 {profile.name} (current)"
                default_index = i
            else:
                display_name = f"   {profile.name}"
            choices.append(questionary.Choice(display_name, value=profile.name))
        
        # Show header to stderr
        print("\n🔄 AWS Profile Switcher", file=sys.stderr)
        print("Use ↑↓ arrow keys to navigate, Enter to select, Ctrl+C to cancel\n", file=sys.stderr)
        
        try:
            # Create and show the interactive menu
            selected_profile = questionary.select(
                "Select AWS Profile:",
                choices=choices,
                use_shortcuts=True,
                use_arrow_keys=True,
                use_emacs_keys=True,
                style=questionary.Style([
                    ('question', 'bold cyan'),
                    ('answer', 'bold green'),
                    ('pointer', 'bold cyan'),
                    ('highlighted', 'bold cyan'),
                    ('selected', 'bold green'),
                ])
            ).ask()
            
            if selected_profile:
                logger.info(f"Profile selected: {selected_profile}")
                return selected_profile
            else:
                print("👋 Profile switching cancelled", file=sys.stderr)
                return None
                
        except KeyboardInterrupt:
            print("\n👋 Profile switching cancelled", file=sys.stderr)
            return None
        
    except KeyboardInterrupt:
        logger.info("Profile selection interrupted by user")
        return None
    except Exception as e:
        logger.error(f"Error in interactive menu: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return None


def list_profiles() -> list:
    """List all available AWS profiles
    
    Returns:
        list: List of profile names
    """
    try:
        logger.debug("Listing available profiles")
        switcher = get_profile_switcher()
        profiles = switcher.list_profiles()
        
        profile_names = [profile.name for profile in profiles]
        logger.debug(f"Found {len(profile_names)} profiles")
        
        return profile_names
        
    except Exception as e:
        logger.error(f"Error listing profiles: {e}")
        return []


def get_current_profile() -> Optional[str]:
    """Get the currently active AWS profile
    
    Returns:
        str: Current profile name, or None if not set
    """
    try:
        logger.debug("Getting current profile")
        switcher = get_profile_switcher()
        current = switcher.get_current_profile()
        
        if current:
            logger.debug(f"Current profile: {current}")
        else:
            logger.debug("No current profile set")
            
        return current
        
    except Exception as e:
        logger.error(f"Error getting current profile: {e}")
        return None


def validate_profile(profile_name: str) -> bool:
    """Validate that a profile exists
    
    Args:
        profile_name: Name of the profile to validate
        
    Returns:
        bool: True if profile exists, False otherwise
    """
    try:
        logger.debug(f"Validating profile: {profile_name}")
        loader = ProfileLoader()
        is_valid = loader.validate_profile(profile_name)
        
        logger.debug(f"Profile {profile_name} is {'valid' if is_valid else 'invalid'}")
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating profile {profile_name}: {e}")
        return False


def switch_profile(profile_name: str) -> bool:
    """Switch to a specific profile (validation only)
    
    Note: The actual environment variable setting is handled by the shell script.
    This function only validates that the profile exists.
    
    Args:
        profile_name: Name of the profile to switch to
        
    Returns:
        bool: True if profile is valid and switch can proceed
    """
    try:
        logger.debug(f"Switching to profile: {profile_name}")
        
        if not validate_profile(profile_name):
            logger.warning(f"Profile {profile_name} does not exist")
            return False
        
        logger.info(f"Profile switch validated: {profile_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error switching to profile {profile_name}: {e}")
        return False


def set_environment_variable(profile_name: str) -> bool:
    """Set AWS_PROFILE environment variable (validation and confirmation)
    
    Note: The actual environment variable setting is handled by the shell script.
    This function validates the profile and provides user feedback.
    
    Args:
        profile_name: Name of the profile to set
        
    Returns:
        bool: True if profile is valid and can be set
    """
    try:
        logger.debug(f"Setting AWS_PROFILE to: {profile_name}")
        switcher = get_profile_switcher()
        
        result = switcher.set_environment_variable(profile_name)
        
        if result:
            logger.info(f"AWS_PROFILE set to: {profile_name}")
        else:
            logger.warning(f"Failed to set AWS_PROFILE to: {profile_name}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error setting AWS_PROFILE to {profile_name}: {e}")
        return False


def get_environment_status() -> dict:
    """Get current environment variable status
    
    Returns:
        dict: Environment status information
    """
    try:
        logger.debug("Getting environment status")
        switcher = get_profile_switcher()
        
        status = switcher.get_environment_variable_status()
        logger.debug(f"Environment status: {status}")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting environment status: {e}")
        return {"error": str(e)}


def validate_environment() -> bool:
    """Validate current environment setup
    
    Returns:
        bool: True if environment is properly configured
    """
    try:
        logger.debug("Validating environment setup")
        switcher = get_profile_switcher()
        
        is_valid = switcher.validate_environment_setup()
        
        if is_valid:
            logger.info("Environment validation passed")
        else:
            logger.warning("Environment validation failed")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating environment: {e}")
        return False


def main():
    """Main entry point for shell script integration
    
    This function is called directly by shell scripts and handles
    the interactive profile selection process.
    """
    try:
        # Show interactive menu and get selected profile
        selected_profile = show_interactive_menu()
        
        if selected_profile:
            # Output the selected profile name for shell script to capture
            print(selected_profile)
            sys.exit(0)
        else:
            # No profile selected or user cancelled
            sys.exit(1)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Profile switching cancelled", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in main: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# Convenience functions for shell scripts
def quick_switch():
    """Quick profile switch without menu (for advanced users)
    
    This function can be extended to support quick switching
    based on environment variables or command line arguments.
    """
    # For now, just call the main interactive menu
    return main()


def health_check() -> bool:
    """Perform a health check of the shell integration
    
    Returns:
        bool: True if everything is working correctly
    """
    try:
        logger.debug("Performing health check")
        
        # Test profile loading
        loader = ProfileLoader()
        profiles = loader.load_profiles()
        
        # Test profile switcher creation
        switcher = ProfileSwitcher()
        
        logger.info("Health check passed")
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False


# Export main classes and functions for external use
__all__ = [
    'ProfileSwitcher',
    'show_interactive_menu',
    'list_profiles',
    'get_current_profile',
    'validate_profile',
    'switch_profile',
    'set_environment_variable',
    'get_environment_status',
    'validate_environment',
    'health_check',
    'main'
]


if __name__ == "__main__":
    # If called directly, run the main interactive function
    main()