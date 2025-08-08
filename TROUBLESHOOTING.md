# Troubleshooting Guide

This document provides solutions to common issues you might encounter when using kolja-aws, particularly with the shell integration feature.

## Shell Integration Issues

### Problem: `sp` command not found

**Symptoms:**
```bash
$ sp
bash: sp: command not found
```

**Solutions:**

1. **Run the diagnostic tool:**
   ```bash
   kolja-diagnose
   ```
   This will check your entire setup and provide specific recommendations.

2. **Reload your shell configuration:**
   ```bash
   # For Bash
   source ~/.bashrc
   
   # For Zsh (most common on macOS)
   source ~/.zshrc
   
   # For Fish
   source ~/.config/fish/config.fish
   
   # Or simply restart your terminal
   ```

2. **Run manual installation:**
   ```bash
   kolja-install-shell
   ```

3. **Check if shell integration is installed:**
   ```bash
   grep -n "kolja-aws profile switcher" ~/.bashrc ~/.zshrc ~/.config/fish/config.fish 2>/dev/null
   ```

### Problem: Shell integration installation fails

**Symptoms:**
```
❌ Automatic installation failed: Unsupported shell: <shell_name>
```

**Solutions:**

1. **Check supported shells:**
   - Bash (4.0+)
   - Zsh (5.0+)
   - Fish (3.0+)

2. **Verify your shell:**
   ```bash
   echo $SHELL
   ```

3. **Manual installation for unsupported shells:**
   Add this function to your shell configuration file:
   ```bash
   sp() {
       local selected_profile
       selected_profile=$(python -c "
   from kolja_aws.shell_integration import main
   main()
   ")
       
       if [ $? -eq 0 ] && [ -n "$selected_profile" ]; then
           export AWS_PROFILE="$selected_profile"
           echo "✅ Switched to profile: $selected_profile"
       fi
   }
   ```

### Problem: Permission denied when modifying shell configuration

**Symptoms:**
```
❌ Error: Permission denied: ~/.bashrc
```

**Solutions:**

1. **Check file permissions:**
   ```bash
   ls -la ~/.bashrc ~/.zshrc ~/.config/fish/config.fish
   ```

2. **Fix permissions:**
   ```bash
   chmod 644 ~/.bashrc  # or appropriate config file
   ```

3. **Check directory permissions:**
   ```bash
   # For Fish shell
   mkdir -p ~/.config/fish
   chmod 755 ~/.config/fish
   ```

### Problem: Backup files accumulating

**Symptoms:**
Multiple backup files in your home directory:
```
~/.bashrc.backup.20240101_120000
~/.bashrc.backup.20240102_130000
...
```

**Solutions:**

1. **Automatic cleanup** (keeps 5 most recent backups):
   ```bash
   kolja-install-shell  # Automatically cleans old backups
   ```

2. **Manual cleanup:**
   ```bash
   # Remove backups older than 30 days
   find ~ -name "*.backup.*" -mtime +30 -delete
   ```

## Profile Loading Issues

### Problem: No AWS profiles found

**Symptoms:**
```
❌ No AWS profiles found. Please run 'kolja aws profiles' first.
```

**Solutions:**

1. **Generate profiles:**
   ```bash
   kolja aws profiles
   ```

2. **Check AWS configuration:**
   ```bash
   ls -la ~/.aws/
   cat ~/.aws/config
   ```

3. **Verify SSO sessions:**
   ```bash
   kolja aws get
   kolja aws login
   ```

### Problem: Profile switching doesn't work

**Symptoms:**
- `sp` command runs but `AWS_PROFILE` is not set
- Selected profile doesn't appear in environment

**Solutions:**

1. **Check current environment:**
   ```bash
   echo $AWS_PROFILE
   env | grep AWS
   ```

2. **Verify profile exists:**
   ```bash
   aws configure list-profiles
   ```

3. **Test profile manually:**
   ```bash
   export AWS_PROFILE=your-profile-name
   aws sts get-caller-identity
   ```

### Problem: Interactive menu doesn't show profiles

**Symptoms:**
```
? Select AWS Profile:  [Use arrows to move, type to filter]
(empty list)
```

**Solutions:**

1. **Regenerate profiles:**
   ```bash
   kolja aws profiles
   ```

2. **Check AWS config format:**
   ```bash
   grep -A 5 "\[profile" ~/.aws/config
   ```

3. **Verify profile format:**
   Profiles should be in format: `[profile AccountID-RoleName]`

## Installation Issues

### Problem: Package installation fails

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solutions:**

1. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install kolja-aws
   ```

2. **Install with user flag:**
   ```bash
   pip install --user kolja-aws
   ```

3. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

### Problem: Command not found after installation

**Symptoms:**
```bash
$ kolja
bash: kolja: command not found
```

**Solutions:**

1. **Check installation location:**
   ```bash
   pip show kolja-aws
   ```

2. **Add to PATH:**
   ```bash
   # Add to your shell configuration file
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Use full path:**
   ```bash
   python -m kolja_aws.kolja_login --help
   ```

## AWS SSO Issues

### Problem: SSO login fails

**Symptoms:**
```
❌ SSO login failed for session: <session_name>
```

**Solutions:**

1. **Check SSO URL:**
   ```bash
   kolja aws get  # Verify SSO start URL
   ```

2. **Clear SSO cache:**
   ```bash
   rm -rf ~/.aws/sso/cache/
   ```

3. **Reconfigure session:**
   ```bash
   kolja aws set <session_name>
   ```

### Problem: SSO session expired

**Symptoms:**
```
❌ The SSO session associated with this profile has expired or is otherwise invalid
```

**Solutions:**

1. **Re-login:**
   ```bash
   kolja aws login
   ```

2. **Check session status:**
   ```bash
   aws sso login --profile <profile_name>
   ```

## Environment Issues

### Problem: Python version compatibility

**Symptoms:**
```
ERROR: kolja-aws requires Python '>=3.8' but the running Python is 3.7
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   python3 --version
   ```

2. **Use Python 3.8+:**
   ```bash
   python3.8 -m pip install kolja-aws
   ```

3. **Update Python:**
   - macOS: `brew install python@3.8`
   - Ubuntu: `sudo apt install python3.8`
   - Windows: Download from python.org

### Problem: Virtual environment issues

**Symptoms:**
- Commands work in one terminal but not another
- Inconsistent behavior across sessions

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install in system Python:**
   ```bash
   deactivate  # Exit virtual environment
   pip install --user kolja-aws
   ```

3. **Check which Python:**
   ```bash
   which python
   which kolja
   ```

## Getting Help

If you continue to experience issues:

1. **Enable debug logging:**
   ```bash
   export KOLJA_LOG_LEVEL=DEBUG
   sp  # or other command
   ```

2. **Check system information:**
   ```bash
   echo "OS: $(uname -s)"
   echo "Shell: $SHELL"
   echo "Python: $(python --version)"
   echo "Kolja version: $(kolja --version 2>/dev/null || echo 'Not found')"
   ```

3. **Create an issue:**
   Visit the project repository and create an issue with:
   - Your system information
   - Complete error messages
   - Steps to reproduce the problem
   - Debug logs (if applicable)

## Common Workarounds

### Alternative profile switching methods

If the shell integration doesn't work, you can still switch profiles manually:

```bash
# List available profiles
aws configure list-profiles

# Set profile manually
export AWS_PROFILE=your-profile-name

# Verify current profile
aws sts get-caller-identity
```

### Using with other tools

kolja-aws works well with other AWS tools:

```bash
# With AWS CLI
aws s3 ls --profile your-profile-name

# With Granted
assume your-profile-name

# With aws-vault
aws-vault exec your-profile-name -- aws s3 ls
```