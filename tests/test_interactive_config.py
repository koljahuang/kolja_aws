"""
Tests for InteractiveConfig class using @mock.patch decorators
"""

import pytest
from unittest.mock import patch
import click
from kolja_aws.interactive_config import InteractiveConfig
from kolja_aws.session_config import SessionConfig


class TestInteractiveConfig:
    """Test cases for InteractiveConfig class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.interactive_config = InteractiveConfig()
    
    @patch('click.echo')
    @patch('click.prompt')
    def test_prompt_sso_config_success(self, mock_prompt, mock_echo):
        """Test successful SSO configuration prompting"""
        mock_prompt.side_effect = [
            "https://your-company.awsapps.com/start",
            "us-east-1"
        ]
        
        result = self.interactive_config.prompt_sso_config("test-session")
        
        assert isinstance(result, SessionConfig)
        assert result.sso_start_url == "https://your-company.awsapps.com/start"
        assert result.sso_region == "us-east-1"
        assert mock_prompt.call_count == 2
    
    @patch('click.echo')
    @patch('click.prompt')
    def test_prompt_sso_url_success(self, mock_prompt, mock_echo):
        """Test successful SSO URL prompting"""
        mock_prompt.return_value = "https://your-company.awsapps.com/start"
        
        result = self.interactive_config._prompt_sso_url()
        
        assert result == "https://your-company.awsapps.com/start"
        mock_prompt.assert_called_once_with("Enter SSO start URL", type=str)
    
    @patch('click.echo')
    @patch('click.prompt')
    def test_prompt_sso_region_success(self, mock_prompt, mock_echo):
        """Test successful region prompting"""
        mock_prompt.return_value = "us-east-1"
        
        result = self.interactive_config._prompt_sso_region()
        
        assert result == "us-east-1"
        mock_prompt.assert_called_once_with("Enter AWS region", type=str)
    
    def test_validate_sso_url_valid(self):
        """Test SSO URL validation with valid URLs"""
        valid_urls = [
            "https://your-company.awsapps.com/start",
            "http://localhost:8080"
        ]
        
        for url in valid_urls:
            assert self.interactive_config.validate_sso_url(url)
    
    def test_validate_aws_region_valid(self):
        """Test AWS region validation with valid regions"""
        valid_regions = ["us-east-1", "eu-west-1", "ap-southeast-2"]
        
        for region in valid_regions:
            assert self.interactive_config.validate_aws_region(region)