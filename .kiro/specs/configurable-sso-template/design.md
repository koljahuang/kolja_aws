# Design Document

## Overview

This design aims to refactor the current SSO configuration management approach that is hardcoded in the `sso_session.template` file, migrating configuration information to the `settings.toml` file and implementing dynamic template generation functionality. This will improve system configurability and maintainability, allowing users to manage different SSO environments by modifying configuration files.

## Architecture

### Current Architecture Issues
- SSO configuration is hardcoded in template files
- Manual maintenance required for multiple environment configurations
- Configuration changes require modifying code files

### New Architecture Design
```
settings.toml (Configuration Source) 
    ↓
SSO Configuration Manager (Read and Validate)
    ↓  
Template Generator (Dynamic Generation)
    ↓
AWS Configuration File (Final Output)
```

## Components and Interfaces

### 1. Configuration Structure Design

Add SSO configuration blocks in `settings.toml`:

```toml
[sso_sessions.kolja-cn]
sso_start_url = "https://start.home.awsapps.cn/directory/xxx"
sso_region = "cn-northwest-1"
sso_registration_scopes = "sso:account:access"

[sso_sessions.kolja]
sso_start_url = "https://xxx/start"
sso_region = "ap-southeast-2"
sso_registration_scopes = "sso:account:access"
```

### 2. SSO Configuration Manager (`sso_config_manager.py`)

**Core Class: `SSOConfigManager`**

```python
class SSOConfigManager:
    def __init__(self, settings_instance)
    def get_sso_sessions() -> Dict[str, Dict[str, str]]
    def validate_sso_config(session_name: str, config: Dict) -> bool
    def get_session_config(session_name: str) -> Dict[str, str]
```

**Responsibilities:**
- Read SSO configuration from settings.toml
- Validate configuration completeness and correctness
- Provide configuration access interface

### 3. Template Generator (`sso_template_generator.py`)

**Core Class: `SSOTemplateGenerator`**

```python
class SSOTemplateGenerator:
    def __init__(self, config_manager: SSOConfigManager)
    def generate_session_block(session_name: str, config: Dict) -> str
    def generate_full_template() -> str
    def write_template_to_file(file_path: str) -> None
```

**Responsibilities:**
- Generate SSO session template content based on configuration
- Maintain template format consistency
- Support writing to file or returning string

### 4. Configuration Validator (`sso_validator.py`)

**Core Functions:**
```python
def validate_url(url: str) -> bool
def validate_aws_region(region: str) -> bool
def validate_sso_session_config(config: Dict) -> Tuple[bool, List[str]]
```

**Responsibilities:**
- URL format validation
- AWS region format validation
- Configuration completeness checking

## Data Models

### SSOSessionConfig
```python
@dataclass
class SSOSessionConfig:
    session_name: str
    sso_start_url: str
    sso_region: str
    sso_registration_scopes: str = "sso:account:access"
    
    def validate(self) -> Tuple[bool, List[str]]
    def to_template_block(self) -> str
```

### SSOConfigCollection
```python
@dataclass
class SSOConfigCollection:
    sessions: Dict[str, SSOSessionConfig]
    
    def add_session(self, session: SSOSessionConfig) -> None
    def get_session(self, name: str) -> SSOSessionConfig
    def generate_template(self) -> str
```

## Error Handling

### Exception Type Definitions
```python
class SSOConfigError(Exception):
    """Base class for SSO configuration related errors"""
    pass

class InvalidSSOConfigError(SSOConfigError):
    """Invalid SSO configuration error"""
    pass

class MissingSSOConfigError(SSOConfigError):
    """Missing SSO configuration error"""
    pass

class InvalidURLError(SSOConfigError):
    """Invalid URL format error"""
    pass

class InvalidRegionError(SSOConfigError):
    """Invalid AWS region error"""
    pass
```

### Error Handling Strategy
1. **Configuration Read Errors**: Provide clear error messages and repair suggestions
2. **Validation Errors**: Detail which field has issues and expected format
3. **File Operation Errors**: Handle file permission and path issues
4. **Backward Compatibility**: Fall back to original template file approach if configuration doesn't exist

## Integration Plan

### 1. Modify Existing Code
- Update `set` command in `kolja_login.py` to use new configuration manager
- Modify `get_section_metadata_from_template` function in `utils.py` to support dynamically generated templates
- Keep existing CLI interface unchanged to ensure backward compatibility

### 2. Configuration Migration Strategy
- Provide migration tools to convert existing template file configurations to settings.toml format
- Support hybrid mode: prioritize settings.toml, fall back to template files if not available
- Add configuration validation command to help users check configuration correctness

### 3. Progressive Deployment
1. Phase 1: Implement configuration reading and validation functionality
2. Phase 2: Implement template generation functionality
3. Phase 3: Integrate into existing CLI commands
4. Phase 4: Add migration tools and backward compatibility support

## Testing Strategy

### Unit Tests
- **Configuration Manager Tests**: Test configuration reading, validation, and access functionality
- **Template Generator Tests**: Test template generation correctness and format
- **Validator Tests**: Test various validation rules and edge cases
- **Data Model Tests**: Test data class behavior and validation logic

### Integration Tests
- **End-to-End Configuration Flow Tests**: From settings.toml reading to final template generation
- **CLI Integration Tests**: Test modified CLI command functionality
- **File Operation Tests**: Test template file read/write operations
- **Error Scenario Tests**: Test handling of various error conditions

### Compatibility Tests
- **Backward Compatibility Tests**: Ensure existing functionality is not affected
- **Configuration Format Tests**: Test handling of different configuration formats
- **Environment Compatibility Tests**: Test behavior on different operating systems and Python versions

## Performance Considerations

### Configuration Caching
- Implement configuration caching mechanism to avoid repeated settings.toml reads
- Monitor configuration file changes and automatically refresh cache

### Template Generation Optimization
- Lazy generation: Generate template content only when needed
- Template caching: Cache generated template content until configuration changes

### Memory Usage
- Use generator patterns to handle large amounts of configuration
- Promptly release unnecessary configuration objects