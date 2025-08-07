# Design Document

## Overview

This design transforms the kolja tool from a configuration-file-based system to a fully interactive system. The key changes include:

1. **Removing all configuration file dependencies** - Eliminate settings.toml, config.py, and sso_session.template
2. **Implementing interactive prompts** - Replace static configuration with dynamic user input
3. **Simplifying the codebase** - Remove complex configuration loading and template generation logic
4. **Maintaining core functionality** - Preserve all existing AWS SSO operations while changing how configuration is obtained

## Architecture

### Current Architecture Issues
- Heavy dependency on Dynaconf and settings.toml
- Complex template generation and configuration parsing
- Multiple fallback mechanisms for configuration loading
- Static configuration files that need manual editing

### New Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Interactive     │───▶│   AWS SSO       │
│   (Terminal)    │    │  Prompt System   │    │   Operations    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   In-Memory      │
                       │   Configuration  │
                       └──────────────────┘
```

## Components and Interfaces

### 1. Interactive Prompt System

**Purpose**: Replace configuration file reading with interactive user input

**Interface**:
```python
class InteractiveConfig:
    def prompt_sso_config(self, session_name: str) -> dict:
        """Prompt user for SSO configuration parameters"""
        pass
    
    def validate_sso_url(self, url: str) -> bool:
        """Validate SSO start URL format"""
        pass
    
    def validate_aws_region(self, region: str) -> bool:
        """Validate AWS region format"""
        pass
```

**Implementation Details**:
- Use `click.prompt()` for user input
- Implement validation functions for each input type
- Provide clear examples and error messages
- Set default value for sso_registration_scopes

### 2. Simplified Configuration Management

**Purpose**: Replace complex configuration loading with simple in-memory storage

**Interface**:
```python
class SessionConfig:
    def __init__(self, sso_start_url: str, sso_region: str, 
                 sso_registration_scopes: str = "sso:account:access"):
        pass
    
    def to_aws_config_section(self, session_name: str) -> str:
        """Generate AWS config section content"""
        pass
```

### 3. Refactored Command Handlers

**Purpose**: Update existing commands to use interactive configuration

**Changes**:
- `kolja aws set <session_name>`: Prompt for configuration instead of reading from files
- Remove dependency on `get_available_sso_sessions()` 
- Simplify `get_sso_session_config()` to work with in-memory data
- Update all utility functions to work without configuration files

## Data Models

### SessionConfig Class
```python
@dataclass
class SessionConfig:
    sso_start_url: str
    sso_region: str
    sso_registration_scopes: str = "sso:account:access"
    
    def validate(self) -> bool:
        """Validate all configuration parameters"""
        pass
    
    def to_dict(self) -> dict:
        """Convert to dictionary for AWS operations"""
        pass
```

### Input Validation Models
```python
class URLValidator:
    @staticmethod
    def is_valid_sso_url(url: str) -> bool:
        """Validate SSO URL format (https://xxx.awsapps.com/start or .cn)"""
        pass

class RegionValidator:
    @staticmethod
    def is_valid_aws_region(region: str) -> bool:
        """Validate AWS region format"""
        pass
```

## Error Handling

### Input Validation Errors
- **Invalid URL Format**: Clear error message with expected format examples
- **Invalid Region**: List of common AWS regions with examples
- **Empty Input**: Re-prompt with guidance
- **Keyboard Interrupt**: Graceful exit with cleanup

### AWS Operation Errors
- **SSO Login Failures**: Maintain existing error handling
- **Token Retrieval Issues**: Preserve current error messages
- **Profile Generation Errors**: Keep existing error handling logic

## Testing Strategy

### Remove Configuration-Related Tests
The following test files need to be deleted as they test configuration file functionality that will be removed:

1. **tests/test_utils_dynamic_config.py** - Tests dynamic configuration loading from settings.toml
2. **Configuration-related parts of tests/test_sso_exceptions.py** - Tests for configuration file errors and template generation errors

### Keep Core Functionality Tests
1. **tests/test_profile_generation.py** - Keep profile generation tests as this functionality remains
2. **Core SSO exception tests** - Keep URL and region validation exception tests

### New Unit Tests
1. **Interactive Prompt Tests**
   - Mock user input scenarios using `click.testing.CliRunner`
   - Test validation functions for URLs and regions
   - Test error handling and re-prompting
   - Test default value assignment for registration scopes

2. **SessionConfig Tests**
   - Test SessionConfig class methods
   - Test AWS config section generation
   - Test data validation and serialization

3. **Command Integration Tests**
   - Test complete `kolja aws set` workflow with mocked prompts
   - Test interaction with AWS SSO operations
   - Test error scenarios end-to-end

### Manual Testing
1. **User Experience Testing**
   - Test prompt clarity and examples
   - Test error message helpfulness
   - Test workflow efficiency

2. **AWS Integration Testing**
   - Test with real AWS SSO endpoints
   - Test profile generation
   - Test login workflows

## Implementation Plan

### Phase 1: Remove Configuration Dependencies
- Delete settings.toml, config.py, sso_session.template
- Remove Dynaconf dependency from pyproject.toml
- Update imports to remove configuration references

### Phase 2: Implement Interactive System
- Create InteractiveConfig class
- Implement input validation functions
- Create SessionConfig data model

### Phase 3: Refactor Command Handlers
- Update `kolja aws set` command to use interactive prompts
- Simplify utility functions in utils.py
- Remove template generation logic

### Phase 4: Testing and Validation
- Implement comprehensive test suite
- Perform manual testing with various scenarios
- Validate AWS integration still works correctly

## Migration Considerations

### Breaking Changes
- Users can no longer use settings.toml for configuration
- All configuration must be entered interactively
- No more batch configuration of multiple sessions

### User Communication
- Update README with new usage instructions
- Provide migration guide for existing users
- Update CLI help text to reflect new workflow

### Backward Compatibility
- None - this is a breaking change by design
- Users must adapt to new interactive workflow
- Existing AWS configurations in ~/.aws/config remain unchanged