# Kolja AWS CLI Tool 🚀

A powerful CLI tool that simplifies AWS SSO login management and AWS profile configuration. It automatically manages SSO sessions and generates AWS profiles, making it easier to work with multiple AWS accounts and roles.

## ✨ Features

- **Automatic Profile Generation**: Automatically create AWS profiles for all accessible accounts and roles
- **SSO Session Management**: Easy setup and management of multiple SSO sessions
- **Profile Switcher Integration**: Works seamlessly with AWS profile switcher tools like [Granted](https://granted.dev/)

## 🚀 Installation

```bash
git clone https://github.com/koljahuang/kolja_aws.git
cd kolja_aws
poetry install

# Setup Git hooks for security (recommended)
./scripts/setup-git-hooks.sh
```

## ⚙️ Configuration

### Initial Setup

**Replace placeholder URLs in `settings.toml`:**
```toml
AWS_CONFIG="~/.aws/config"

[sso_sessions.kolja-cn]
sso_start_url = "https://xxx.awsapps.cn/start#replace-with-your-sso-url"  # ← Replace this
sso_region = "cn-northwest-1"
sso_registration_scopes = "sso:account:access"
```

### 🔒 Security Features

- **Smart sensitive data detection**: Prevents committing real SSO URLs while allowing placeholder URLs
- **Pre-commit hooks**: Automatically scans for and blocks real credentials, tokens, and URLs
- **Safe configuration**: Use 'xxx' placeholders in committed files, replace locally with real URLs

## 📖 Usage

### Available Commands

```bash
kolja aws --help
```

```
Usage: kolja aws [OPTIONS] COMMAND [ARGS]...

Development commands.

Options:
  --help  Show this message and exit.

Commands:
  get       Get current SSO sessions
  login     Login to SSO sessions
  profiles  Generate AWS profiles
  set       Set SSO session configuration
```

### Step-by-Step Workflow

#### 1. Set SSO Sessions

Configure your SSO sessions in the AWS config file:

```bash
kolja aws get
```

This will show available sessions from your `settings.toml`:
```
Available SSO sessions:
  - kolja-cn
  - kolja

Usage: kolja aws set <session_name> [<session_name2> ...]
```

Set specific sessions:
```bash
kolja aws set kolja-cn kolja
```

#### 2. Login to SSO

```bash
kolja aws login
```

#### 3. Generate AWS Profiles

Automatically create profiles for all accessible accounts and roles:

```bash
kolja aws profiles
```

This generates profiles with the format `[profile AccountID-RoleName]`:
```ini
[profile 123456789012-AdminRole]
sso_session = kolja-cn
sso_account_id = 123456789012
sso_role_name = AdminRole
region = cn-northwest-1
output = text

[profile 123456789012-ReadOnlyRole]
sso_session = kolja-cn
sso_account_id = 123456789012
sso_role_name = ReadOnlyRole
region = cn-northwest-1
output = text
```

#### 4. Use with Profile Switchers

Now you can use your favorite AWS profile switcher. Example with [Granted](https://granted.dev/):

```bash
assume -c
```

```
? Please select the profile you would like to assume:  [Use arrows to move, type to filter]

> 123456789012-AdminRole
  123456789012-ReadOnlyRole
  987654321098-DeveloperRole
```

## 🏗️ Architecture

- **Dynamic Configuration**: SSO settings are managed in `settings.toml`
- **Template Generation**: Automatically generates SSO session templates
- **Profile Management**: Creates and updates AWS profiles with `AccountID-RoleName` format
- **Fallback Support**: Falls back to template files if dynamic configuration is unavailable

> 📖 **New Feature**: Profiles are now generated with the format `[profile AccountID-RoleName]` for better clarity and organization. See [Profile Naming Format Documentation](docs/profile-naming-format.md) for details.

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 🔐 Security

This project includes several security features to protect sensitive information:

### Protected Data Patterns
- Real SSO URLs (e.g., `https://d-xxxxxx.awsapps.com/start`)
- AWS directory IDs (e.g., `directory/d-xxxxxx`)
- Access tokens and secret keys
- Real passwords and credentials

### Security Scripts
- `scripts/setup-git-hooks.sh` - Sets up Git pre-commit hooks
- `scripts/sanitize-config.py` - Sanitizes configuration files

### Git Hooks
The pre-commit hook automatically:
- Prevents committing sensitive files
- Scans for sensitive patterns (URLs, tokens, keys)
- Provides clear error messages when sensitive data is detected

### Best Practices
1. Keep 'xxx' placeholders in committed files
2. Replace placeholders locally with your real SSO URLs
3. Run `./scripts/setup-git-hooks.sh` after cloning
4. Git hooks will automatically prevent committing real sensitive data

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.