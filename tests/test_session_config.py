"""
Tests for SessionConfig data model using @mock.patch decorators
"""

import pytest
from kolja_aws.session_config import SessionConfig


class TestSessionConfig:
    """Test cases for SessionConfig class"""
    
    def test_session_config_creation(self):
        """Test basic SessionConfig creation"""
        config = SessionConfig(
            sso_start_url="https://your-company.awsapps.com/start",
            sso_region="us-east-1"
        )
        
        assert config.sso_start_url == "https://your-company.awsapps.com/start"
        assert config.sso_region == "us-east-1"
        assert config.sso_registration_scopes == "sso:account:access"
    
    def test_validate_with_valid_config(self):
        """Test validation with valid configuration"""
        config = SessionConfig(
            sso_start_url="https://your-company.awsapps.com/start",
            sso_region="us-east-1"
        )
        
        assert config.validate() is True
    
    def test_validate_with_invalid_url(self):
        """Test validation fails with invalid URL"""
        config = SessionConfig(
            sso_start_url="",
            sso_region="us-east-1"
        )
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "Invalid SSO start URL" in str(exc_info.value)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        config = SessionConfig(
            sso_start_url="https://your-company.awsapps.com/start",
            sso_region="us-east-1"
        )
        
        result = config.to_dict()
        expected = {
            'sso_start_url': "https://your-company.awsapps.com/start",
            'sso_region': "us-east-1",
            'sso_registration_scopes': "sso:account:access"
        }
        
        assert result == expected