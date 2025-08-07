# Kolja AWS CLI Tool 🚀

A powerful CLI tool that simplifies AWS SSO login management and AWS profile configuration. It automatically manages SSO sessions and generates AWS profiles, making it easier to work with multiple AWS accounts and roles.

## ✨ Features

- **Automatic Profile Generation**: Automatically create AWS profiles for all accessible accounts and roles
- **SSO Session Management**: Easy setup and management of multiple SSO sessions
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

- **Interactive Configuration**: No configuration files needed - all settings gathered through interactive prompts
- **In-Memory Processing**: Configuration data is processed in memory and written directly to AWS config
- **Profile Management**: Creates and updates AWS profiles with `AccountID-RoleName` format
- **Validation**: Built-in validation for SSO URLs and AWS regions

> 📖 **New Feature**: Profiles are now generated with the format `[profile AccountID-RoleName]` for better clarity and organization. See [Profile Naming Format Documentation](docs/profile-naming-format.md) for details.

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