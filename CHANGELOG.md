# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Enhanced Profile Naming Format**: AWS profiles are now generated with the format `[profile AccountID-RoleName]` instead of `[profile AccountID]`
  - Provides clear identification of which role each profile uses
  - Supports multiple roles per AWS account automatically
  - Improves integration with AWS profile switcher tools like Granted
  - Maintains full backward compatibility with AWS CLI and other tools

### Changed
- Updated `construct_role_profile_section()` function to generate profiles with AccountID-RoleName format
- Modified `profiles` command in CLI to use the new naming convention
- Updated README documentation with examples of the new profile format

### Technical Details
- Modified `kolja_aws/utils.py`:
  - `construct_role_profile_section()` now creates profile names as `{account_id}-{role_name}`
  - Profile sections are properly managed with removal and replacement logic
- Modified `kolja_aws/kolja_login.py`:
  - Updated `profiles` command to pass correct section names to utility functions
- Added comprehensive tests in `tests/test_profile_generation.py`:
  - Tests for profile generation with new naming format
  - Tests for multiple roles in same account
  - Tests for profile replacement functionality
  - Tests for naming format consistency

### Documentation
- Added `docs/profile-naming-format.md` with detailed explanation of the new feature
- Updated README.md with examples showing the new profile format
- Created `examples/profile_generation_demo.py` to demonstrate the functionality

### Examples

**Before:**
```ini
[profile 555286235540]
sso_session = kolja-cn
sso_account_id = 555286235540
sso_role_name = AdminRole
region = cn-northwest-1
output = text
```

**After:**
```ini
[profile 555286235540-AdminRole]
sso_session = kolja-cn
sso_account_id = 555286235540
sso_role_name = AdminRole
region = cn-northwest-1
output = text

[profile 555286235540-ReadOnlyRole]
sso_session = kolja-cn
sso_account_id = 555286235540
sso_role_name = ReadOnlyRole
region = cn-northwest-1
output = text
```

### Migration
- Existing profiles in the old format will be automatically replaced when running `kolja aws profiles`
- No manual intervention required for migration
- All configuration settings are preserved during the transition

## Previous Versions

### [0.1.0] - Initial Release
- Basic SSO session management
- AWS profile generation
- CLI interface with `get`, `set`, `login`, and `profiles` commands
- Dynamic configuration support with settings.toml
- Custom exception handling
- Git hooks for sensitive data protection