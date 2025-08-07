# Requirements Document

## Introduction

This feature transforms the kolja tool to use an interactive prompt system for SSO configuration, completely eliminating the need for configuration files. When users execute `kolja set kolja`, the system will guide them through entering the necessary SSO parameters dynamically, making the tool more user-friendly and removing dependency on static configuration files.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to be prompted for SSO configuration parameters when I run `kolja set kolja`, so that I can configure SSO sessions interactively without any configuration files.

#### Acceptance Criteria

1. WHEN I run `kolja set kolja` THEN the system SHALL prompt me to enter the SSO start URL
2. WHEN I enter a valid SSO start URL THEN the system SHALL prompt me to enter the SSO region
3. WHEN I enter a valid SSO region THEN the system SHALL automatically use "sso:account:access" as the default registration scopes
4. WHEN I complete all prompts THEN the system SHALL proceed with the SSO configuration using only the provided values

### Requirement 2

**User Story:** As a developer, I want the interactive prompts to provide clear guidance and examples, so that I know what format of input is expected.

#### Acceptance Criteria

1. WHEN the system prompts for SSO start URL THEN it SHALL display an example format like "https://xxx.awsapps.com/start"
2. WHEN the system prompts for SSO region THEN it SHALL display example regions like "ap-southeast-2" or "cn-northwest-1"
3. WHEN I enter an invalid format THEN the system SHALL display an error message and re-prompt for the correct input
4. WHEN I enter valid input THEN the system SHALL proceed to the next prompt without error

### Requirement 3

**User Story:** As a developer, I want to validate my input during the interactive session, so that I can correct mistakes immediately.

#### Acceptance Criteria

1. WHEN I enter an invalid SSO start URL format THEN the system SHALL display a validation error and prompt again
2. WHEN I enter an invalid AWS region format THEN the system SHALL display a validation error and prompt again
3. WHEN I enter a valid SSO start URL THEN the system SHALL accept it and move to the next prompt
4. WHEN I enter a valid AWS region THEN the system SHALL accept it and proceed with configuration

### Requirement 4

**User Story:** As a developer, I want the system to use default values for sso_registration_scopes, so that I don't need to manually enter this common configuration.

#### Acceptance Criteria

1. WHEN the system processes SSO configuration THEN it SHALL automatically set sso_registration_scopes to "sso:account:access"
2. WHEN I complete the interactive prompts THEN the system SHALL not prompt me for registration scopes
3. WHEN the SSO configuration is applied THEN it SHALL include the default registration scopes value

### Requirement 5

**User Story:** As a developer, I want all configuration file dependencies removed from the project, so that the tool operates purely through interactive input.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL not attempt to read any configuration files
2. WHEN I run any kolja command THEN it SHALL not depend on settings.toml or any other configuration file
3. WHEN the project is deployed THEN it SHALL not include any configuration file templates or examples
4. WHEN the system needs configuration data THEN it SHALL obtain it only through interactive prompts or command-line arguments

### Requirement 6

**User Story:** As a developer, I want all configuration-related tests removed from the test suite, so that the test suite only covers the new interactive functionality.

#### Acceptance Criteria

1. WHEN the test suite runs THEN it SHALL not include any tests that depend on configuration files
2. WHEN I run tests THEN they SHALL not test settings.toml loading or template generation functionality
3. WHEN configuration-related test files exist THEN they SHALL be deleted from the project
4. WHEN new tests are written THEN they SHALL focus on interactive prompt functionality and validation