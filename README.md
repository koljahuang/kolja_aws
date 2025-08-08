# Kolja AWS CLI Tool 🚀

A powerful CLI tool that simplifies AWS SSO login management and AWS profile configuration. It automatically manages SSO sessions, generates AWS profiles, and provides seamless shell integration for quick profile switching, making it easier to work with multiple AWS accounts and roles.

## ✨ Features

- **Automatic Profile Generation**: Automatically create AWS profiles for all accessible accounts and roles
- **SSO Session Management**: Easy setup and management of multiple SSO sessions
- **Shell Integration**: Built-in interactive AWS profile switcher with `sp` command
- **Profile Switcher Integration**: Works seamlessly with AWS profile switcher tools like [Granted](https://granted.dev/)

## 🚀 Installation

```bash
uv tool install kolja_aws
```

Or install from source:

```bash
git clone https://github.com/koljahuang/kolja_aws.git
cd kolja_aws
poetry install
```

### Shell Integration Setup

After installation, the shell integration is automatically configured during the installation process. If automatic setup fails, you can manually install it:

```bash
kolja-install-shell
```

This adds the `sp` command to your shell configuration file (`.bashrc`, `.zshrc`, or `.config/fish/config.fish`).

## ⚙️ Configuration

### Interactive Setup

No configuration files needed! The tool uses interactive prompts to gather all necessary information.

When you run `kolja aws set <session_name>`, you'll be prompted for:
- **SSO Start URL**: Your organization's SSO URL (e.g., `https://xxx.awsapps.com/start`)
- **SSO Region**: AWS region for your SSO (e.g., `ap-southeast-2`, `cn-northwest-1`)

The system automatically sets registration scopes to `sso:account:access`.

### 🔒 Security Features

- **No configuration files**: Eliminates risk of accidentally committing sensitive SSO URLs
- **Interactive input only**: All sensitive data entered through secure prompts, never stored in files
- **No sensitive data in repository**: Since all configuration is interactive, there's no risk of committing sensitive information

## 📖 Usage

### Available Commands

```bash
kolja aws --help
```

```
Usage: kolja aws [OPTIONS] COMMAND [ARGS]...

AWS SSO session and profile management commands.

Use these commands to interactively configure SSO sessions,
login to AWS, and generate profiles for your accounts.

Options:
  --help  Show this message and exit.

Commands:
  get       List all configured SSO sessions
  login     Login to all configured SSO sessions
  profiles  Generate AWS profile sections for all available accounts and roles
  set       Configure an SSO session through interactive prompts
```

### Shell Integration Commands

After installation, you can use these commands in your terminal:

```bash
# Interactive AWS profile switcher
sp

# Manual shell integration setup (if needed)
kolja-install-shell

# Diagnose shell integration issues
kolja-diagnose
```

### Step-by-Step Workflow

#### 1. Configure SSO Sessions

Set up your SSO sessions interactively:

```bash
kolja aws set my-company
```

You'll be prompted to enter:
- SSO start URL (e.g., `https://your-company.awsapps.com/start`)
- SSO region (e.g., `ap-southeast-2`)

The tool will guide you through each step with examples and validation.

Check your configured sessions:
```bash
kolja aws get
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

#### 4. Use the Built-in Profile Switcher

Use the integrated `sp` command for quick profile switching:

```bash
sp
```

This opens an interactive menu with smooth arrow key navigation:

```
🔄 AWS Profile Switcher
Use ↑↓ arrow keys to navigate, Enter to select, Ctrl+C to cancel

? Select AWS Profile:
❯ 🟢 123456789012-AdminRole (current)
     123456789012-ReadOnlyRole
     987654321098-DeveloperRole
```

After selection, the `AWS_PROFILE` environment variable is automatically set:

```bash
✅ Switched to profile: 123456789012-AdminRole
```

#### 5. Alternative: Use with External Profile Switchers

You can also use your favorite AWS profile switcher. Example with [Granted](https://granted.dev/):

```bash
assume -c
```

```
? Please select the profile you would like to assume:  [Use arrows to move, type to filter]

> 123456789012-AdminRole
  123456789012-ReadOnlyRole
  987654321098-DeveloperRole
```

## 🔄 Shell Integration

The shell integration feature provides a seamless way to switch between AWS profiles directly from your terminal.

### Features

- **Smooth Arrow Key Navigation**: Navigate through available profiles with ↑↓ arrow keys
- **Interactive Profile Selection**: Modern, user-friendly selection interface
- **Automatic Environment Setup**: Sets `AWS_PROFILE` environment variable automatically
- **Multi-Shell Support**: Works with Bash, Zsh, and Fish shells
- **Safe Installation**: Creates backups before modifying shell configuration files
- **Current Profile Highlighting**: Shows which profile is currently active with 🟢 indicator

### Supported Shells

| Shell | Configuration File | Status |
|-------|-------------------|--------|
| Bash  | `~/.bashrc`, `~/.bash_profile` | ✅ Supported |
| Zsh   | `~/.zshrc` | ✅ Supported |
| Fish  | `~/.config/fish/config.fish` | ✅ Supported |

### Installation Process

1. **Automatic Detection**: Detects your current shell environment
2. **Backup Creation**: Creates timestamped backups of configuration files
3. **Script Integration**: Adds the `sp` function to your shell configuration
4. **Validation**: Verifies the installation was successful

### Usage Examples

```bash
# Basic usage - opens interactive menu
sp

# Check current profile
echo $AWS_PROFILE

# Verify installation
kolja-install-shell --help

# Run demo (from source)
python examples/shell_integration_demo.py
```

For more comprehensive examples, see [EXAMPLES.md](EXAMPLES.md).

### Troubleshooting

If the shell integration doesn't work:

1. **Run diagnostics**: `kolja-diagnose` (comprehensive system check)
2. **Reload your shell**: `source ~/.zshrc` (for zsh) or `source ~/.bashrc` (for bash) or restart terminal
3. **Manual installation**: Run `kolja-install-shell`
4. **Check shell support**: Ensure you're using a supported shell
5. **Verify AWS profiles**: Run `kolja aws profiles` to generate profiles first

## 🏗️ Architecture

- **Interactive Configuration**: No configuration files needed - all settings gathered through interactive prompts
- **In-Memory Processing**: Configuration data is processed in memory and written directly to AWS config
- **Profile Management**: Creates and updates AWS profiles with `AccountID-RoleName` format
- **Shell Integration**: Seamless terminal integration with automatic environment variable management
- **Validation**: Built-in validation for SSO URLs and AWS regions

> 📖 **New Feature**: Built-in shell integration with the `sp` command provides instant AWS profile switching without external tools.

## 📚 Documentation

- **[Usage Examples](EXAMPLES.md)**: Comprehensive examples and use cases
- **[Troubleshooting Guide](TROUBLESHOOTING.md)**: Solutions to common issues
- **[Changelog](CHANGELOG.md)**: Version history and release notes

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 🔐 Security

With the new interactive configuration system, security is greatly simplified:

### Security Benefits
- **No sensitive data in repository**: All SSO URLs and configuration entered interactively
- **No configuration files to secure**: Eliminates the risk of accidentally committing sensitive information
- **Clean git history**: No need for sanitization scripts or git hooks
- **Simple and secure**: No complex security setup required

### Best Practices
1. Use the interactive prompts to configure SSO sessions - no files to manage
2. All sensitive data stays local in your `~/.aws/config` file
3. Review generated AWS profiles in `~/.aws/config` after running `kolja aws profiles`
4. The repository contains no sensitive information by design

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.