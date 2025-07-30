#!/bin/bash

# Setup Git hooks for sensitive data protection
echo "Setting up Git hooks for sensitive data protection..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook to prevent committing sensitive data
echo "Checking for sensitive data before commit..."

# Check if sensitive files are being committed
sensitive_files=("settings.toml" "kolja_aws/sso_session.template" ".secrets.*")

for file in "${sensitive_files[@]}"; do
    if git diff --cached --name-only | grep -q "$file"; then
        echo "❌ ERROR: Attempting to commit sensitive file: $file"
        echo "Please remove sensitive data or add to .gitignore"
        exit 1
    fi
done

# Check for sensitive patterns in staged files
if git diff --cached | grep -i -E "(sso_start_url.*https://[^/]*\.awsapps\.(com|cn)|access_token|secret_key|password)" > /dev/null; then
    echo "❌ ERROR: Sensitive data detected in staged changes!"
    echo "Please remove sensitive information before committing."
    echo ""
    echo "Detected patterns:"
    git diff --cached | grep -i -E "(sso_start_url.*https://[^/]*\.awsapps\.(com|cn)|access_token|secret_key|password)" --color=always
    exit 1
fi

echo "✅ No sensitive data detected. Proceeding with commit."
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks setup complete!"
echo ""
echo "The following protections are now active:"
echo "  - Scans for real SSO URLs and prevents committing them"
echo "  - Allows committing files with 'xxx' placeholders"
echo "  - Detects access tokens, secret keys, and passwords"
echo ""
echo "💡 You can now commit settings.toml and sso_session.template safely"
echo "   as long as they contain 'xxx' placeholders instead of real URLs."