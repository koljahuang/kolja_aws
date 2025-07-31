"""
Custom exception classes for SSO configuration

This module defines various exception types that may occur during SSO configuration management,
each exception contains clear error messages and repair suggestions.
"""

from typing import List, Optional, Dict, Any


class SSOConfigError(Exception):
    """Base class for SSO configuration related errors
    
    All SSO configuration related exceptions should inherit from this base class.
    Provides basic error information and context management functionality.
    """
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, 
                 suggestions: Optional[List[str]] = None):
        """Initialize SSO configuration error
        
        Args:
            message: Error description message
            context: Error context information, containing related configuration data
            suggestions: List of repair suggestions
        """
        super().__init__(message)
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        """Return formatted error message"""
        error_msg = super().__str__()
        
        if self.context:
            error_msg += f"\nContext information: {self.context}"
        
        if self.suggestions:
            error_msg += "\nRepair suggestions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                error_msg += f"\n  {i}. {suggestion}"
        
        return error_msg


class InvalidSSOConfigError(SSOConfigError):
    """Invalid SSO configuration error
    
    This exception is thrown when SSO configuration format is incorrect or contains invalid values.
    """
    
    def __init__(self, session_name: str, field_name: str, field_value: Any, 
                 expected_format: str, context: Optional[Dict[str, Any]] = None):
        """Initialize invalid configuration error
        
        Args:
            session_name: SSO session name
            field_name: Invalid field name
            field_value: Invalid field value
            expected_format: Expected format description
            context: Additional context information
        """
        message = (f"Field '{field_name}' in SSO session '{session_name}' "
                  f"has invalid value '{field_value}'")
        
        error_context = {
            "session_name": session_name,
            "field_name": field_name,
            "field_value": field_value,
            "expected_format": expected_format
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            f"Ensure '{field_name}' field format conforms to: {expected_format}",
            f"Check configuration in [sso_sessions.{session_name}] section of settings.toml",
            "Refer to configuration examples in documentation for correction"
        ]
        
        super().__init__(message, error_context, suggestions)


class MissingSSOConfigError(SSOConfigError):
    """Missing SSO configuration error
    
    This exception is thrown when required SSO configuration fields or sessions do not exist.
    """
    
    def __init__(self, missing_item: str, item_type: str = "field", 
                 session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """Initialize missing configuration error
        
        Args:
            missing_item: Name of missing item
            item_type: Type of missing item ("field", "session", "section")
            session_name: Related SSO session name (if applicable)
            context: Additional context information
        """
        if item_type == "field" and session_name:
            message = f"SSO session '{session_name}' is missing required field '{missing_item}'"
        elif item_type == "session":
            message = f"SSO session configuration '{missing_item}' not found"
        elif item_type == "section":
            message = f"Missing '{missing_item}' configuration section in settings.toml"
        else:
            message = f"Missing required SSO configuration item '{missing_item}'"
        
        error_context = {
            "missing_item": missing_item,
            "item_type": item_type,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = []
        if item_type == "field":
            suggestions.extend([
                f"Add '{missing_item}' field in [sso_sessions.{session_name}] section of settings.toml",
                "Ensure all required fields are configured: sso_start_url, sso_region"
            ])
        elif item_type == "session":
            suggestions.extend([
                f"Add [sso_sessions.{missing_item}] configuration section in settings.toml",
                "Check if session name is spelled correctly"
            ])
        elif item_type == "section":
            suggestions.extend([
                "Add [sso_sessions] configuration section in settings.toml",
                "Ensure configuration file format is correct"
            ])
        
        suggestions.append("Refer to complete configuration examples in documentation")
        
        super().__init__(message, error_context, suggestions)


class InvalidURLError(SSOConfigError):
    """Invalid URL format error
    
    This exception is thrown when SSO start URL format is incorrect.
    """
    
    def __init__(self, url: str, session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """Initialize invalid URL error
        
        Args:
            url: Invalid URL
            session_name: Related SSO session name
            context: Additional context information
        """
        if session_name:
            message = f"Start URL '{url}' for SSO session '{session_name}' has invalid format"
        else:
            message = f"URL '{url}' has invalid format"
        
        error_context = {
            "invalid_url": url,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "Ensure URL starts with 'https://'",
            "Check if URL contains a valid domain name",
            "Ensure URL format conforms to standard format, e.g.: https://xxx.awsapps.cn/start#replace-with-your-sso-url",
            "Verify if URL can be accessed normally in browser"
        ]
        
        super().__init__(message, error_context, suggestions)


class InvalidRegionError(SSOConfigError):
    """Invalid AWS region error
    
    This exception is thrown when AWS region format is incorrect.
    """
    
    def __init__(self, region: str, session_name: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        """Initialize invalid region error
        
        Args:
            region: Invalid AWS region
            session_name: Related SSO session name
            context: Additional context information
        """
        if session_name:
            message = f"AWS region '{region}' for SSO session '{session_name}' has invalid format"
        else:
            message = f"AWS region '{region}' has invalid format"
        
        error_context = {
            "invalid_region": region,
            "session_name": session_name
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "Use valid AWS region codes, e.g.: us-east-1, ap-southeast-2, cn-northwest-1",
            "Check if region code spelling is correct",
            "Ensure region code conforms to AWS standard format: <region>-<availability-zone>-<number>",
            "Refer to AWS official documentation for complete region list"
        ]
        
        super().__init__(message, error_context, suggestions)


class SSOConfigFileError(SSOConfigError):
    """SSO configuration file related error
    
    This exception is thrown when configuration file reading, parsing or writing encounters problems.
    """
    
    def __init__(self, file_path: str, operation: str, original_error: Optional[Exception] = None,
                 context: Optional[Dict[str, Any]] = None):
        """Initialize configuration file error
        
        Args:
            file_path: Related file path
            operation: Operation being performed ("read", "write", "parse")
            original_error: Original exception object
            context: Additional context information
        """
        message = f"Configuration file '{file_path}' {operation} operation failed"
        if original_error:
            message += f": {str(original_error)}"
        
        error_context = {
            "file_path": file_path,
            "operation": operation,
            "original_error": str(original_error) if original_error else None
        }
        if context:
            error_context.update(context)
        
        suggestions = []
        if operation == "read":
            suggestions.extend([
                "Check if file exists",
                "Ensure sufficient file read permissions",
                "Verify if file path is correct"
            ])
        elif operation == "write":
            suggestions.extend([
                "Check if directory exists",
                "Ensure sufficient file write permissions",
                "Check if disk space is sufficient"
            ])
        elif operation == "parse":
            suggestions.extend([
                "Check if TOML file format is correct",
                "Ensure configuration file syntax conforms to TOML standard",
                "Use TOML validation tools to check file format"
            ])
        
        suggestions.append("View detailed error information for more diagnostic information")
        
        super().__init__(message, error_context, suggestions)


class SSOTemplateGenerationError(SSOConfigError):
    """SSO template generation error
    
    This exception is thrown when problems occur during template generation process.
    """
    
    def __init__(self, template_type: str, reason: str, 
                 context: Optional[Dict[str, Any]] = None):
        """Initialize template generation error
        
        Args:
            template_type: Template type ("session_block", "full_template")
            reason: Failure reason
            context: Additional context information
        """
        message = f"{template_type} template generation failed: {reason}"
        
        error_context = {
            "template_type": template_type,
            "failure_reason": reason
        }
        if context:
            error_context.update(context)
        
        suggestions = [
            "Check if SSO configuration is complete and valid",
            "Ensure all required configuration fields are provided",
            "Verify if configuration data format is correct",
            "View detailed error information to determine specific issues"
        ]
        
        super().__init__(message, error_context, suggestions)