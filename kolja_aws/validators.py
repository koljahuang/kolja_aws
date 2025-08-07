"""
Input validation functions for SSO configuration

This module provides validation classes for SSO start URLs and AWS regions
to ensure user input meets the required format and standards.
"""

import re
from typing import Optional
from urllib.parse import urlparse


class URLValidator:
    """Validator for SSO start URLs"""
    
    # URL pattern regex - matches http/https URLs with domain
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:'  # start of domain group
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*'  # domain parts
        r'[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?'  # final domain part
        r'|'  # or
        r'localhost'  # localhost
        r')'  # end of domain group
        r'(?::\d+)?'  # optional port
        r'(?:/[^\s]*)?$',  # optional path
        re.IGNORECASE
    )
    
    @staticmethod
    def is_valid_sso_url(url: str) -> bool:
        """
        Validate SSO start URL format using regex pattern
        
        Args:
            url: The URL to validate
            
        Returns:
            bool: True if URL matches valid URL pattern, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        url = url.strip()
        if not url:
            return False
            
        return bool(URLValidator.URL_PATTERN.match(url))


class RegionValidator:
    """Validator for AWS regions"""
    
    # Common AWS regions for validation
    VALID_REGIONS = {
        # US regions
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        # Europe regions
        'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-north-1',
        'eu-south-1', 'eu-central-2', 'eu-south-2',
        # Asia Pacific regions
        'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ap-southeast-4',
        'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
        'ap-south-1', 'ap-south-2', 'ap-east-1',
        # China regions
        'cn-north-1', 'cn-northwest-1',
        # Canada
        'ca-central-1', 'ca-west-1',
        # South America
        'sa-east-1',
        # Africa
        'af-south-1',
        # Middle East
        'me-south-1', 'me-central-1',
        # Israel
        'il-central-1'
    }
    
    @staticmethod
    def is_valid_aws_region(region: str) -> bool:
        """
        Validate AWS region format
        
        Args:
            region: The region to validate
            
        Returns:
            bool: True if region is valid, False otherwise
            
        Valid format: <region>-<direction>-<number> (e.g., us-east-1, ap-southeast-2)
        """
        if not region or not isinstance(region, str):
            return False
            
        original_region = region.strip()
        region_lower = original_region.lower()
        
        # Reject if not already lowercase (strict validation)
        if original_region != region_lower:
            return False
        
        # Check if it's in our known valid regions list
        if region_lower in RegionValidator.VALID_REGIONS:
            return True
            
        # Check format pattern: region-direction-number
        pattern = r'^[a-z]{2,3}-[a-z]+-\d+$'
        if re.match(pattern, region_lower):
            return True
            
        return False
    
    @staticmethod
    def get_example_regions() -> list[str]:
        """
        Get a list of example regions for user guidance
        
        Returns:
            list: List of example region strings
        """
        return [
            'us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1',
            'cn-north-1', 'cn-northwest-1'
        ]