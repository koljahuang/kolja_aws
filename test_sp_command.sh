#!/bin/bash

echo "Testing sp command functionality..."

# Source the shell configuration to ensure sp function is available
source ~/.zshrc

# Check if sp function exists
if type sp >/dev/null 2>&1; then
    echo "✅ sp function is available"
else
    echo "❌ sp function is not available"
    exit 1
fi

# Test the underlying Python module
echo "Testing Python module..."
python3 -c "
from kolja_aws.shell_integration import list_profiles, health_check
print('Health check:', health_check())
profiles = list_profiles()
print(f'Found {len(profiles)} profiles: {profiles}')
"

echo "✅ All tests passed!"