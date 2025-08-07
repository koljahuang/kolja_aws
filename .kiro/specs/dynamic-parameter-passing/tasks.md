# Implementation Plan

- [x] 1. Remove configuration file dependencies
  - Delete settings.toml, config.py, and sso_session.template files
  - Remove Dynaconf dependency from pyproject.toml
  - Update imports to remove configuration references
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 2. Remove configuration-related tests
  - Delete tests/test_utils_dynamic_config.py file
  - Remove configuration-related test cases from tests/test_sso_exceptions.py
  - Keep only core functionality tests (profile generation, URL/region validation)
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 3. Create interactive prompt system
- [x] 3.1 Implement input validation functions
  - Create URLValidator class with is_valid_sso_url method
  - Create RegionValidator class with is_valid_aws_region method
  - Write unit tests for validation functions
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.2 Create SessionConfig data model
  - Implement SessionConfig dataclass with sso_start_url, sso_region, and default sso_registration_scopes
  - Add validate() method to SessionConfig class
  - Add to_dict() and to_aws_config_section() methods
  - Write unit tests for SessionConfig class
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 3.3 Implement InteractiveConfig class
  - Create prompt_sso_config method using click.prompt()
  - Integrate validation functions with user prompts
  - Implement error handling and re-prompting logic
  - Add clear examples and guidance in prompts
  - Write unit tests using click.testing.CliRunner
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_

- [x] 4. Refactor command handlers
- [x] 4.1 Update kolja aws set command
  - Replace configuration file reading with interactive prompts
  - Remove dependency on get_available_sso_sessions()
  - Use SessionConfig for in-memory configuration storage
  - Update command to work with single session at a time
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 4.2 Simplify utility functions
  - Remove _generate_dynamic_sso_template() function
  - Remove get_available_sso_sessions() function
  - Simplify get_sso_session_config() to work with in-memory data
  - Remove get_section_metadata_from_template() function
  - Update construct_role_profile_section() to work without templates
  - _Requirements: 5.1, 5.4_

- [x] 4.3 Update remaining command handlers
  - Modify profiles command to work with interactive configuration
  - Update login command to handle new configuration approach
  - Ensure get command works with simplified session management
  - _Requirements: 5.4_

- [x] 5. Write new test suite
  - 使用pytest风格，包括pytest的装饰器用法，比如@mock.patch
  - test_is_valid_sso_url_with_valid_urls，只要保证是网址就可以
  - region是目前aws合法的region
- [x] 6. Update documentation and cleanup
- [x] 6.1 Update CLI help text
  - Update command descriptions to reflect interactive workflow
  - Remove references to configuration files in help text
  - Add examples of interactive usage
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 6.2 Clean up project structure
  - Remove any remaining configuration file references
  - Update .gitignore if needed
  - Verify no dead code remains
  - _Requirements: 5.3_