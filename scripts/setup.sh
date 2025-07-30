#!/bin/bash

echo "🚀 Setting up Kolja AWS CLI Tool..."
echo

# Setup Git hooks first
echo "🔒 Setting up Git security hooks..."
./scripts/setup-git-hooks.sh

# Check if user needs to configure SSO URLs
echo
echo "📋 Configuration Check:"
if grep -q "xxx.awsapps" settings.toml; then
    echo "⚠️  Please replace placeholder URLs in settings.toml with your actual SSO URLs"
    echo "   Current placeholders: xxx.awsapps.com/start#replace-with-your-sso-url"
    echo "   Replace with your real SSO start URLs"
else
    echo "✅ settings.toml appears to be configured"
fi

if grep -q "xxx.awsapps" kolja_aws/sso_session.template; then
    echo "⚠️  Please replace placeholder URLs in kolja_aws/sso_session.template with your actual SSO URLs"
    echo "   Current placeholders: xxx.awsapps.com/start#replace-with-your-sso-url"
    echo "   Replace with your real SSO start URLs"
else
    echo "✅ sso_session.template appears to be configured"
fi

echo
echo "🎉 Setup complete!"
echo
echo "Next steps:"
echo "1. Replace 'xxx' placeholders in settings.toml with your real SSO URLs"
echo "2. Replace 'xxx' placeholders in kolja_aws/sso_session.template if needed"
echo "3. Run: kolja aws set"
echo "4. Run: kolja aws login"
echo "5. Run: kolja aws profiles"
echo
echo "💡 Note: Git hooks will prevent committing real SSO URLs to protect your credentials"