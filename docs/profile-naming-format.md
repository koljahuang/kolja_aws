# Profile Naming Format: AccountID-RoleName

## Overview

The Kolja AWS CLI tool now generates AWS profiles using the format `[profile AccountID-RoleName]` instead of the previous `[profile AccountID]` format. This enhancement provides better clarity and organization when working with multiple AWS accounts and roles.

## Benefits

### 1. **Clear Role Identification**
- **Before**: `[profile 555286235540]` - unclear which role this profile uses
- **After**: `[profile 555286235540-AdminRole]` - immediately clear this is the AdminRole

### 2. **Multiple Roles per Account**
- **Before**: Only one profile per account, requiring manual management for different roles
- **After**: Automatic generation of separate profiles for each role:
  ```ini
  [profile 555286235540-AdminRole]
  [profile 555286235540-ReadOnlyRole]
  [profile 555286235540-DeveloperRole]
  ```

### 3. **Better Profile Switcher Integration**
When using tools like [Granted](https://granted.dev/), you get clearer options:
```
? Please select the profile you would like to assume:
> 555286235540-AdminRole
  555286235540-ReadOnlyRole
  555286235540-DeveloperRole
  987654321098-AdminRole
  987654321098-ReadOnlyRole
```

### 4. **Consistent Naming Convention**
All profiles follow the same predictable pattern: `AccountID-RoleName`

## Example Output

When you run `kolja aws profiles`, the generated AWS config will look like:

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

[profile 987654321098-DeveloperRole]
sso_session = kolja
sso_account_id = 987654321098
sso_role_name = DeveloperRole
region = ap-southeast-2
output = text
```

## Usage Examples

### With AWS CLI
```bash
# Use specific role for S3 operations
aws --profile 555286235540-AdminRole s3 ls

# Use read-only role for viewing resources
aws --profile 555286235540-ReadOnlyRole ec2 describe-instances

# Use developer role for application deployment
aws --profile 987654321098-DeveloperRole lambda list-functions
```

### With Profile Switchers

#### Granted
```bash
# Interactive selection
assume -c

# Direct assumption
assume 555286235540-AdminRole
```

#### AWS Vault
```bash
aws-vault exec 555286235540-AdminRole -- aws s3 ls
```

#### AWS Profile Switcher
```bash
asp 555286235540-AdminRole
```

## Migration from Old Format

If you have existing profiles in the old format (`[profile AccountID]`), they will be automatically replaced when you run `kolja aws profiles` again. The tool will:

1. Remove the old profile section
2. Create a new profile with the AccountID-RoleName format
3. Preserve all configuration settings (SSO session, region, etc.)

## Technical Implementation

The profile generation logic has been updated in two key areas:

1. **Profile Name Generation**: `construct_role_profile_section()` now creates profiles with the format `AccountID-RoleName`
2. **Section Management**: The tool properly handles removal and replacement of existing profiles

## Backward Compatibility

- **AWS CLI**: Fully compatible - AWS CLI works with any profile name format
- **Profile Switchers**: Enhanced compatibility - most tools work better with descriptive profile names
- **Scripts**: May need updates if they reference profiles by the old naming convention

## Best Practices

1. **Use descriptive role names** in your AWS SSO setup for clearer profile identification
2. **Regularly regenerate profiles** after role changes in AWS SSO
3. **Update scripts and documentation** to reference the new profile naming format
4. **Use profile switchers** to take full advantage of the improved naming clarity