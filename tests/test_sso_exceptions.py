"""
Unit tests for SSO exception classes

Test all custom exception class functionality, including error message formatting,
context information management, and repair suggestion provision.
"""

import pytest
from kolja_aws.sso_exceptions import (
    SSOConfigError,
    InvalidSSOConfigError,
    MissingSSOConfigError,
    InvalidURLError,
    InvalidRegionError,
    SSOConfigFileError,
    SSOTemplateGenerationError
)


class TestSSOConfigError:
    """Test base exception class SSOConfigError"""
    
    def test_basic_error_creation(self):
        """Test basic error creation"""
        error = SSOConfigError("Test error message")
        assert str(error) == "Test error message"
        assert error.context == {}
        assert error.suggestions == []
    
    def test_error_with_context(self):
        """Test error with context information"""
        context = {"key": "value", "number": 42}
        error = SSOConfigError("Test error", context=context)
        
        error_str = str(error)
        assert "Test error" in error_str
        assert "Context information" in error_str
        assert "key" in error_str
        assert "value" in error_str
    
    def test_error_with_suggestions(self):
        """Test error with repair suggestions"""
        suggestions = ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        error = SSOConfigError("Test error", suggestions=suggestions)
        
        error_str = str(error)
        assert "Test error" in error_str
        assert "Repair suggestions" in error_str
        assert "1. Suggestion 1" in error_str
        assert "2. Suggestion 2" in error_str
        assert "3. Suggestion 3" in error_str
    
    def test_error_with_context_and_suggestions(self):
        """Test error with both context and suggestions"""
        context = {"session": "test-session"}
        suggestions = ["Check configuration", "Retry"]
        error = SSOConfigError("Complete error", context=context, suggestions=suggestions)
        
        error_str = str(error)
        assert "Complete error" in error_str
        assert "Context information" in error_str
        assert "Repair suggestions" in error_str
        assert "session" in error_str
        assert "Check configuration" in error_str


class TestInvalidSSOConfigError:
    """Test invalid SSO configuration error"""
    
    def test_invalid_config_error_creation(self):
        """Test invalid configuration error creation"""
        error = InvalidSSOConfigError(
            session_name="test-session",
            field_name="sso_start_url",
            field_value="invalid-url",
            expected_format="https://..."
        )
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "sso_start_url" in error_str
        assert "invalid-url" in error_str
        assert "invalid" in error_str
        
        # Check context information
        assert error.context["session_name"] == "test-session"
        assert error.context["field_name"] == "sso_start_url"
        assert error.context["field_value"] == "invalid-url"
        assert error.context["expected_format"] == "https://..."
        
        # Check repair suggestions
        assert len(error.suggestions) > 0
        assert any("format conforms" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_config_error_with_additional_context(self):
        """Test invalid configuration error with additional context"""
        additional_context = {"config_file": "settings.toml"}
        error = InvalidSSOConfigError(
            session_name="prod",
            field_name="sso_region",
            field_value="invalid-region",
            expected_format="AWS region format",
            context=additional_context
        )
        
        assert error.context["config_file"] == "settings.toml"
        assert error.context["session_name"] == "prod"


class TestMissingSSOConfigError:
    """Test missing SSO configuration error"""
    
    def test_missing_field_error(self):
        """Test missing field error"""
        error = MissingSSOConfigError(
            missing_item="sso_start_url",
            item_type="field",
            session_name="test-session"
        )
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "sso_start_url" in error_str
        assert "missing required field" in error_str
        
        # Check repair suggestions contain field addition guidance
        assert any("Add" in suggestion and "sso_start_url" in suggestion 
                  for suggestion in error.suggestions)
    
    def test_missing_session_error(self):
        """Test missing session error"""
        error = MissingSSOConfigError(
            missing_item="prod-session",
            item_type="session"
        )
        
        error_str = str(error)
        assert "prod-session" in error_str
        assert "SSO session configuration" in error_str and "not found" in error_str
        
        # Check repair suggestions contain session addition guidance
        assert any("Add" in suggestion and "sso_sessions.prod-session" in suggestion 
                  for suggestion in error.suggestions)
    
    def test_missing_section_error(self):
        """Test missing configuration section error"""
        error = MissingSSOConfigError(
            missing_item="sso_sessions",
            item_type="section"
        )
        
        error_str = str(error)
        assert "sso_sessions" in error_str
        assert "Missing" in error_str and "configuration section" in error_str
        
        # Check repair suggestions contain section addition guidance
        assert any("[sso_sessions]" in suggestion for suggestion in error.suggestions)
    
    def test_missing_config_with_context(self):
        """Test missing configuration error with context"""
        context = {"config_path": "/path/to/settings.toml"}
        error = MissingSSOConfigError(
            missing_item="sso_region",
            item_type="field",
            session_name="dev",
            context=context
        )
        
        assert error.context["config_path"] == "/path/to/settings.toml"
        assert error.context["missing_item"] == "sso_region"


class TestInvalidURLError:
    """Test invalid URL error"""
    
    def test_invalid_url_error_basic(self):
        """Test basic invalid URL error"""
        error = InvalidURLError("not-a-url")
        
        error_str = str(error)
        assert "not-a-url" in error_str
        assert "invalid format" in error_str
        
        # Check repair suggestions contain URL format guidance
        assert any("https://" in suggestion for suggestion in error.suggestions)
        assert any("domain name" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_url_error_with_session(self):
        """Test invalid URL error with session name"""
        error = InvalidURLError("invalid-url", session_name="test-session")
        
        error_str = str(error)
        assert "test-session" in error_str
        assert "invalid-url" in error_str
        assert "Start URL" in error_str
        
        assert error.context["invalid_url"] == "invalid-url"
        assert error.context["session_name"] == "test-session"
    
    def test_invalid_url_error_with_context(self):
        """Test invalid URL error with additional context"""
        context = {"validation_step": "initial_check"}
        error = InvalidURLError("bad-url", context=context)
        
        assert error.context["validation_step"] == "initial_check"
        assert error.context["invalid_url"] == "bad-url"


class TestInvalidRegionError:
    """Test invalid AWS region error"""
    
    def test_invalid_region_error_basic(self):
        """Test basic invalid region error"""
        error = InvalidRegionError("invalid-region")
        
        error_str = str(error)
        assert "invalid-region" in error_str
        assert "invalid format" in error_str
        
        # Check repair suggestions contain region format guidance
        assert any("us-east-1" in suggestion for suggestion in error.suggestions)
        assert any("AWS region codes" in suggestion for suggestion in error.suggestions)
    
    def test_invalid_region_error_with_session(self):
        """Test invalid region error with session name"""
        error = InvalidRegionError("bad-region", session_name="prod")
        
        error_str = str(error)
        assert "prod" in error_str
        assert "bad-region" in error_str
        assert "AWS region" in error_str
        
        assert error.context["invalid_region"] == "bad-region"
        assert error.context["session_name"] == "prod"
    
    def test_invalid_region_error_suggestions(self):
        """Test invalid region error repair suggestions"""
        error = InvalidRegionError("wrong")
        
        suggestions_text = " ".join(error.suggestions)
        assert "ap-southeast-2" in suggestions_text
        assert "cn-northwest-1" in suggestions_text
        assert "spelling" in suggestions_text
        assert "AWS standard format" in suggestions_text


class TestSSOConfigFileError:
    """Test SSO configuration file error"""
    
    def test_file_read_error(self):
        """Test file read error"""
        original_error = FileNotFoundError("File not found")
        error = SSOConfigFileError(
            file_path="/path/to/settings.toml",
            operation="read",
            original_error=original_error
        )
        
        error_str = str(error)
        assert "/path/to/settings.toml" in error_str
        assert "read operation failed" in error_str
        assert "File not found" in error_str
        
        # Check read operation repair suggestions
        assert any("file exists" in suggestion for suggestion in error.suggestions)
        assert any("read permissions" in suggestion for suggestion in error.suggestions)
    
    def test_file_write_error(self):
        """Test file write error"""
        error = SSOConfigFileError(
            file_path="/readonly/settings.toml",
            operation="write"
        )
        
        error_str = str(error)
        assert "write operation failed" in error_str
        
        # Check write operation repair suggestions
        assert any("write permissions" in suggestion for suggestion in error.suggestions)
        assert any("disk space" in suggestion for suggestion in error.suggestions)
    
    def test_file_parse_error(self):
        """Test file parse error"""
        parse_error = ValueError("TOML format error")
        error = SSOConfigFileError(
            file_path="settings.toml",
            operation="parse",
            original_error=parse_error
        )
        
        error_str = str(error)
        assert "parse operation failed" in error_str
        assert "TOML format error" in error_str
        
        # Check parse operation repair suggestions
        assert any("TOML file format" in suggestion for suggestion in error.suggestions)
        assert any("TOML standard" in suggestion for suggestion in error.suggestions)
    
    def test_file_error_with_context(self):
        """Test file error with context"""
        context = {"line_number": 15, "column": 8}
        error = SSOConfigFileError(
            file_path="config.toml",
            operation="parse",
            context=context
        )
        
        assert error.context["line_number"] == 15
        assert error.context["column"] == 8
        assert error.context["file_path"] == "config.toml"


class TestSSOTemplateGenerationError:
    """Test SSO template generation error"""
    
    def test_session_block_generation_error(self):
        """Test session block generation error"""
        error = SSOTemplateGenerationError(
            template_type="session_block",
            reason="Missing required configuration fields"
        )
        
        error_str = str(error)
        assert "session_block template generation failed" in error_str
        assert "Missing required configuration fields" in error_str
        
        # Check template generation repair suggestions
        assert any("SSO configuration is complete" in suggestion for suggestion in error.suggestions)
        assert any("required configuration fields" in suggestion for suggestion in error.suggestions)
    
    def test_full_template_generation_error(self):
        """Test full template generation error"""
        error = SSOTemplateGenerationError(
            template_type="full_template",
            reason="Configuration data format is incorrect"
        )
        
        error_str = str(error)
        assert "full_template template generation failed" in error_str
        assert "Configuration data format is incorrect" in error_str
        
        assert error.context["template_type"] == "full_template"
        assert error.context["failure_reason"] == "Configuration data format is incorrect"
    
    def test_template_generation_error_with_context(self):
        """Test template generation error with context"""
        context = {
            "session_name": "prod",
            "missing_fields": ["sso_start_url", "sso_region"]
        }
        error = SSOTemplateGenerationError(
            template_type="session_block",
            reason="Field validation failed",
            context=context
        )
        
        assert error.context["session_name"] == "prod"
        assert error.context["missing_fields"] == ["sso_start_url", "sso_region"]
        assert error.context["template_type"] == "session_block"


class TestExceptionInheritance:
    """Test exception inheritance relationships"""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test all exceptions inherit from base class"""
        exceptions = [
            InvalidSSOConfigError("test", "field", "value", "format"),
            MissingSSOConfigError("item", "field"),
            InvalidURLError("url"),
            InvalidRegionError("region"),
            SSOConfigFileError("path", "read"),
            SSOTemplateGenerationError("type", "reason")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, SSOConfigError)
            assert isinstance(exception, Exception)
    
    def test_exception_context_and_suggestions_available(self):
        """Test all exceptions have context and suggestion attributes"""
        exceptions = [
            InvalidSSOConfigError("test", "field", "value", "format"),
            MissingSSOConfigError("item", "field"),
            InvalidURLError("url"),
            InvalidRegionError("region"),
            SSOConfigFileError("path", "read"),
            SSOTemplateGenerationError("type", "reason")
        ]
        
        for exception in exceptions:
            assert hasattr(exception, 'context')
            assert hasattr(exception, 'suggestions')
            assert isinstance(exception.context, dict)
            assert isinstance(exception.suggestions, list)
            assert len(exception.suggestions) > 0  # All exceptions should have suggestions


if __name__ == "__main__":
    pytest.main([__file__])