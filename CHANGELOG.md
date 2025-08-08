# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-01-08

### Added
- **Shell Integration Feature**: Complete shell integration system for interactive AWS profile switching
  - Interactive `sp` command with smooth arrow key navigation (↑↓)
  - Modern questionary-based interface for better user experience
  - Support for Bash, Zsh, and Fish shells
  - Automatic installation during package setup
  - Manual installation option with `kolja-install-shell` command
  - Safe configuration file modification with automatic backups
  - Environment variable management for `AWS_PROFILE`
  - Current profile highlighting with 🟢 indicator
  - Comprehensive error handling and user feedback

### New Components
- `ShellInstaller`: Coordinates shell integration installation process
- `ShellDetector`: Detects current shell type and configuration files
- `ProfileSwitcher`: Handles interactive profile selection and switching
- `ScriptGenerator`: Generates shell-specific integration scripts
- `BackupManager`: Manages configuration file backups and restoration
- `ProfileLoader`: Loads and validates AWS profiles from configuration
- `UserExperienceManager`: Provides rich terminal UI and user feedback
- Shell integration module with standalone functionality

### Enhanced
- Post-installation hook for automatic shell integration setup
- Rich terminal UI with progress indicators and colored output
- Comprehensive error handling with user-friendly messages
- Backup and restoration system for configuration files
- Cross-platform shell support with platform-specific optimizations

### Documentation
- Updated README with shell integration usage instructions
- Added troubleshooting guide for common issues
- Created comprehensive changelog
- Added shell integration examples and use cases

### Technical Improvements
- Modular architecture with clear separation of concerns
- Comprehensive test suite for all shell integration components
- Type hints and documentation for all new modules
- Logging system for debugging and monitoring
- Safe file operations with atomic writes and rollback capability
- Migrated from `inquirer` to `questionary` for better Python 3.12+ compatibility
- Enhanced arrow key navigation with modern terminal UI library

## [0.3.0] - 2023-12-15

### Added
- Interactive SSO session configuration
- Automatic profile generation with AccountID-RoleName format
- Support for multiple SSO sessions
- Enhanced security with no configuration files

### Changed
- Moved from configuration files to interactive prompts
- Improved profile naming convention
- Enhanced error handling and user feedback

### Security
- Eliminated risk of committing sensitive SSO URLs
- All configuration data entered through secure prompts
- No sensitive data stored in repository

## [0.2.0] - 2023-11-20

### Added
- SSO session management
- Profile generation from SSO accounts
- Basic CLI interface

### Changed
- Improved AWS profile handling
- Enhanced error messages

## [0.1.0] - 2023-10-15

### Added
- Initial release
- Basic AWS SSO login functionality
- Profile management capabilities
- CLI interface with Click framework

### Features
- AWS SSO authentication
- Profile configuration
- Session management