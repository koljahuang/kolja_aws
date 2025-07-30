#!/bin/bash

# Setup Git hooks for sensitive data protection
echo "Setting up Git hooks for sensitive data protection..."

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Pre-commit hook to automatically sanitize sensitive data
echo "Checking for sensitive data before commit..."

# Function to sanitize a file
sanitize_file() {
    local file="$1"
    local changed=false
    
    if [[ ! -f "$file" ]]; then
        return 0
    fi
    
    # Create a temporary file for modifications
    local temp_file=$(mktemp)
    cp "$file" "$temp_file"
    
    # Replace AWS SSO URLs with placeholders
    if sed -i.bak 's|sso_start_url = "https://[^"]*\.awsapps\.\(com\|cn\)[^"]*"|sso_start_url = "https://xxx.awsapps.\1/start#replace-with-your-sso-url"|g' "$temp_file" 2>/dev/null; then
        if ! cmp -s "$file" "$temp_file"; then
            changed=true
        fi
    fi
    
    # Replace other sensitive patterns
    if sed -i.bak 's|access_token = "[^"]*"|access_token = "xxx-your-access-token"|g' "$temp_file" 2>/dev/null; then
        if ! cmp -s "$file" "$temp_file"; then
            changed=true
        fi
    fi
    
    if sed -i.bak 's|secret_key = "[^"]*"|secret_key = "xxx-your-secret-key"|g' "$temp_file" 2>/dev/null; then
        if ! cmp -s "$file" "$temp_file"; then
            changed=true
        fi
    fi
    
    # If changes were made, update the original file and re-stage it
    if [[ "$changed" == true ]]; then
        cp "$temp_file" "$file"
        git add "$file"
        echo "🔧 Auto-sanitized: $file"
    fi
    
    # Clean up
    rm -f "$temp_file" "${temp_file}.bak"
    
    return 0
}

# Get list of staged files
staged_files=$(git diff --cached --name-only)

# Check each staged file for sensitive data
auto_fixed=false
for file in $staged_files; do
    if [[ -f "$file" ]]; then
        # Check if file contains sensitive patterns
        if grep -q -E "(sso_start_url.*https://[^/]*\.awsapps\.(com|cn)|access_token.*['\"][^'\"]*['\"]|secret_key.*['\"][^'\"]*['\"])" "$file" 2>/dev/null; then
            # Skip if already using placeholders
            if grep -q "xxx" "$file" 2>/dev/null; then
                continue
            fi
            
            echo "🔍 Found sensitive data in: $file"
            sanitize_file "$file"
            auto_fixed=true
        fi
    fi
done

# Final check for any remaining sensitive data
remaining_sensitive=$(git diff --cached | grep -E "(sso_start_url.*https://[^/]*\.awsapps\.(com|cn)/[^#]|access_token.*['\"][^'\"x][^'\"]*['\"]|secret_key.*['\"][^'\"x][^'\"]*['\"])" || true)

if [[ -n "$remaining_sensitive" ]]; then
    echo "❌ ERROR: Real sensitive data detected in staged changes!"
    echo "Please replace with placeholders (xxx) before committing."
    echo ""
    echo "Detected sensitive patterns:"
    echo "$remaining_sensitive" | head -10
    echo ""
    echo "💡 Tip: Replace real URLs with placeholders like:"
    echo "https://xxx.awsapps.com/start#replace-with-your-sso-url"
    exit 1
fi

if [[ "$auto_fixed" == true ]]; then
    echo "✅ Auto-sanitized sensitive data. Please review the changes and commit again."
    echo "💡 The following files were automatically sanitized:"
    git diff --cached --name-only
    exit 1
fi

echo "✅ No sensitive data detected. Proceeding with commit."
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks setup complete!"
echo ""
echo "The following protections are now active:"
echo "  - 🔧 Automatically replaces real SSO URLs with placeholders"
echo "  - 🔧 Automatically sanitizes access tokens and secret keys"
echo "  - ✅ Allows committing files with 'xxx' placeholders"
echo "  - ❌ Blocks commits if sensitive data can't be auto-sanitized"
echo ""
echo "💡 How it works:"
echo "   1. When you commit, the hook scans for sensitive data"
echo "   2. Real URLs/tokens are automatically replaced with 'xxx' placeholders"
echo "   3. Files are re-staged with sanitized content"
echo "   4. You'll need to commit again to proceed"
echo ""
echo "🎯 You can now commit normally - sensitive data will be auto-sanitized!"