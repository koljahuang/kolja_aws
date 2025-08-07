"""
Interactive configuration system for SSO parameters

This module provides the InteractiveConfig class that prompts users for
SSO configuration parameters, replacing static configuration files.
"""

import click
from typing import Dict, Any
from kolja_aws.session_config import SessionConfig
from kolja_aws.validators import URLValidator, RegionValidator


class InteractiveConfig:
    """
    Interactive configuration system for SSO parameters
    
    Provides methods to prompt users for SSO configuration parameters
    with validation and error handling.
    """
    
    def prompt_sso_config(self, session_name: str) -> SessionConfig:
        """
        Prompt user for SSO configuration parameters
        
        Args:
            session_name: Name of the SSO session being configured
            
        Returns:
            SessionConfig: Validated configuration object
            
        Raises:
            click.Abort: If user cancels the configuration process
        """
        click.echo(f"\nConfiguring SSO session: {session_name}")
        click.echo("Please provide the following SSO configuration parameters:")
        click.echo()
        
        # Prompt for SSO start URL
        sso_start_url = self._prompt_sso_url()
        
        # Prompt for SSO region
        sso_region = self._prompt_sso_region()
        
        # Use default registration scopes
        sso_registration_scopes = "sso:account:access"
        click.echo(f"Using default registration scopes: {sso_registration_scopes}")
        
        # Create and validate configuration
        config = SessionConfig(
            sso_start_url=sso_start_url,
            sso_region=sso_region,
            sso_registration_scopes=sso_registration_scopes
        )
        
        try:
            config.validate()
            click.echo()
            click.echo(click.style("✓ Configuration validated successfully!", fg='green'))
            return config
        except ValueError as e:
            click.echo()
            click.echo(click.style(f"✗ Configuration validation failed: {e}", fg='red'))
            raise click.Abort()
    
    def _prompt_sso_url(self) -> str:
        """
        Prompt user for SSO start URL
        
        Returns:
            str: SSO start URL
        """
        click.echo("SSO Start URL:")
        click.echo("  Example: https://your-company.awsapps.com/start")
        click.echo("  Example: https://your-org.awsapps.cn/start")
        
        url = click.prompt("Enter SSO start URL", type=str)
        
        if not url.strip():
            click.echo(click.style("✗ SSO start URL cannot be empty!", fg='red'))
            return self._prompt_sso_url()
        
        return url.strip()
    
    def _prompt_sso_region(self) -> str:
        """
        Prompt user for AWS region with validation
        
        Returns:
            str: Valid AWS region
        """
        while True:
            click.echo("AWS Region:")
            example_regions = RegionValidator.get_example_regions()
            click.echo(f"  Examples: {', '.join(example_regions[:4])}")
            click.echo(f"  More examples: {', '.join(example_regions[4:])}")
            
            region = click.prompt("Enter AWS region", type=str)
            
            if RegionValidator.is_valid_aws_region(region):
                return region.strip()
            else:
                click.echo()
                click.echo(click.style("✗ Invalid AWS region format!", fg='red'))
                click.echo("  • Region must be in lowercase")
                click.echo("  • Region format: <region>-<direction>-<number>")
                click.echo("  • Examples: us-east-1, ap-southeast-2, eu-west-1, cn-northwest-1")
                click.echo()
    
    def validate_sso_url(self, url: str) -> bool:
        """
        Validate SSO start URL format
        
        Args:
            url: The URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        return URLValidator.is_valid_sso_url(url)
    
    def validate_aws_region(self, region: str) -> bool:
        """
        Validate AWS region format
        
        Args:
            region: The region to validate
            
        Returns:
            bool: True if region is valid, False otherwise
        """
        return RegionValidator.is_valid_aws_region(region)
    
    def get_config_summary(self, config: SessionConfig, session_name: str) -> str:
        """
        Generate a summary of the configuration for user review
        
        Args:
            config: The SessionConfig object
            session_name: Name of the session
            
        Returns:
            str: Formatted configuration summary
        """
        return f"""
Configuration Summary for '{session_name}':
  SSO Start URL: {config.sso_start_url}
  SSO Region: {config.sso_region}
  Registration Scopes: {config.sso_registration_scopes}
"""