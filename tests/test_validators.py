"""
Tests for input validation functions

This module tests the URLValidator and RegionValidator classes
to ensure proper validation of SSO URLs and AWS regions.
"""

import pytest
from kolja_aws.validators import URLValidator, RegionValidator


class TestURLValidator:
    """Test cases for URLValidator class"""
    
    def test_is_valid_sso_url_with_url_pattern(self):
        """Test that strings matching URL pattern are accepted"""
        url_patterns = [
            "https://your-company.awsapps.com/start",
            "https://your-org.awsapps.cn/start", 
            "http://test.com",
            "https://my-sso.example.com/start",
            "https://your-test.awsapps.com/start#fragment",
            "https://your-test.awsapps.com/start?param=value",
            "http://localhost:8080",
            "https://subdomain.example.org/path"
        ]
        
        for url in url_patterns:
            assert URLValidator.is_valid_sso_url(url), f"URL pattern should be valid: {url}"
    
    def test_is_valid_sso_url_with_invalid_urls(self):
        """Test that invalid URLs are rejected"""
        invalid_urls = [
            "",  # Empty string
            "   ",  # Whitespace only
            None,  # None value
            123,  # Non-string type
            [],  # List
            {},  # Dict
            "not-a-url",  # Not a URL format
            "just-text",  # Plain text
            "ftp://example.com",  # FTP scheme - should be invalid for SSO URLs
            "example.com",  # Missing scheme
            "://example.com",  # Missing scheme
            "https://",  # Missing netloc
            "https:///path"  # Missing netloc
        ]
        
        for url in invalid_urls:
            assert not URLValidator.is_valid_sso_url(url), f"URL should be invalid: {url}"
    
    def test_is_valid_sso_url_strips_whitespace(self):
        """Test that URLs with leading/trailing whitespace are handled correctly"""
        assert URLValidator.is_valid_sso_url("  https://example.com  ")
        assert URLValidator.is_valid_sso_url("\thttps://example.com\n")
        assert not URLValidator.is_valid_sso_url("  \t\n  ")  # Only whitespace


class TestRegionValidator:
    """Test cases for RegionValidator class"""
    
    def test_is_valid_aws_region_with_valid_regions(self):
        """Test that current AWS legal regions are accepted"""
        valid_regions = [
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
        ]
        
        for region in valid_regions:
            assert RegionValidator.is_valid_aws_region(region), f"Region should be valid: {region}"
    
    def test_is_valid_aws_region_with_invalid_regions(self):
        """Test that invalid regions are rejected"""
        invalid_regions = [
            "",  # Empty string
            "   ",  # Whitespace only
            None,  # None value
            123,  # Non-string type
            "US-EAST-1",  # Uppercase (should be lowercase)
            "Us-East-1",  # Mixed case
            "us_east_1",  # Underscores instead of hyphens
            "us-east",  # Missing number
            "east-1",  # Missing region prefix
            "us-1",  # Missing direction
            "invalid-region-format",  # Invalid format
            "us-east-1-extra",  # Extra components
            "us--east-1",  # Double hyphen
            "us-east-",  # Trailing hyphen
            "-us-east-1",  # Leading hyphen
        ]
        
        for region in invalid_regions:
            assert not RegionValidator.is_valid_aws_region(region), f"Region should be invalid: {region}"
    
    def test_is_valid_aws_region_case_sensitive(self):
        """Test that region validation is case sensitive"""
        # Should be valid (lowercase)
        assert RegionValidator.is_valid_aws_region("us-east-1")
        
        # Should be invalid (uppercase/mixed case)
        assert not RegionValidator.is_valid_aws_region("US-EAST-1")
        assert not RegionValidator.is_valid_aws_region("Us-East-1")
        assert not RegionValidator.is_valid_aws_region("us-EAST-1")
    
    def test_is_valid_aws_region_pattern_matching(self):
        """Test that regions matching the pattern but not in known list are accepted"""
        # These follow the pattern but might not be in the known regions list
        pattern_valid_regions = [
            "xx-test-1",  # Follows pattern: region-direction-number
            "ab-north-2",
            "cd-south-3"
        ]
        
        for region in pattern_valid_regions:
            # These should be valid based on pattern matching
            assert RegionValidator.is_valid_aws_region(region), f"Pattern-valid region should be accepted: {region}"
    
    def test_get_example_regions(self):
        """Test that example regions are returned correctly"""
        examples = RegionValidator.get_example_regions()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are valid regions
        for region in examples:
            assert RegionValidator.is_valid_aws_region(region), f"Example region should be valid: {region}"
        
        # Check that common regions are included
        expected_examples = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'cn-north-1']
        for expected in expected_examples:
            assert expected in examples, f"Expected example region not found: {expected}"
    
    def test_valid_regions_constant(self):
        """Test that the VALID_REGIONS constant contains expected regions"""
        valid_regions = RegionValidator.VALID_REGIONS
        
        assert isinstance(valid_regions, set)
        assert len(valid_regions) > 0
        
        # Check some key regions are present
        key_regions = ['us-east-1', 'eu-west-1', 'ap-southeast-1', 'cn-north-1']
        for region in key_regions:
            assert region in valid_regions, f"Key region not found in VALID_REGIONS: {region}"