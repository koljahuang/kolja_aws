"""
SessionConfig data model for SSO configuration

This module provides the SessionConfig dataclass for managing SSO session
configuration data in memory, replacing configuration file dependencies.
"""

from dataclasses import dataclass
from typing import Dict, Any
from kolja_aws.validators import URLValidator, RegionValidator


@dataclass
class SessionConfig:
    """
    Data model for SSO session configuration
    
    Attributes:
        sso_start_url: The SSO start URL (e.g., https://your-company.awsapps.com/start)
        sso_region: The AWS region for SSO (e.g., us-east-1)
        sso_registration_scopes: The registration scopes (default: "sso:account:access")
    """
    sso_start_url: str
    sso_region: str
    sso_registration_scopes: str = "sso:account:access"
    
    def validate(self) -> bool:
        """
        Validate all configuration parameters
        
        Returns:
            bool: True if all parameters are valid, False otherwise
            
        Raises:
            ValueError: If any parameter is invalid with detailed error message
        """
        errors = []
        
        # Validate SSO start URL (just check it's not empty)
        if not URLValidator.is_valid_sso_url(self.sso_start_url):
            errors.append(f"Invalid SSO start URL: '{self.sso_start_url}'. "
                         f"SSO start URL cannot be empty")
        
        # Validate AWS region
        if not RegionValidator.is_valid_aws_region(self.sso_region):
            example_regions = ", ".join(RegionValidator.get_example_regions()[:5])
            errors.append(f"Invalid AWS region: '{self.sso_region}'. "
                         f"Expected format like: {example_regions}")
        
        # Validate registration scopes (basic check)
        if not self.sso_registration_scopes or not isinstance(self.sso_registration_scopes, str):
            errors.append(f"Invalid registration scopes: '{self.sso_registration_scopes}'. "
                         f"Must be a non-empty string")
        
        if errors:
            raise ValueError("SessionConfig validation failed:\n" + "\n".join(f"- {error}" for error in errors))
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert SessionConfig to dictionary format
        
        Returns:
            dict: Configuration data as dictionary
        """
        return {
            'sso_start_url': self.sso_start_url,
            'sso_region': self.sso_region,
            'sso_registration_scopes': self.sso_registration_scopes
        }
    
    def to_aws_config_section(self, session_name: str) -> str:
        """
        Generate AWS config section content for this session
        
        Args:
            session_name: Name of the SSO session
            
        Returns:
            str: AWS config section content
        """
        return f"""[sso-session {session_name}]
sso_start_url = {self.sso_start_url}
sso_region = {self.sso_region}
sso_registration_scopes = {self.sso_registration_scopes}
"""
    
    def __str__(self) -> str:
        """String representation of SessionConfig"""
        return (f"SessionConfig(sso_start_url='{self.sso_start_url}', "
                f"sso_region='{self.sso_region}', "
                f"sso_registration_scopes='{self.sso_registration_scopes}')")
    
    def __repr__(self) -> str:
        """Detailed representation of SessionConfig"""
        return self.__str__()