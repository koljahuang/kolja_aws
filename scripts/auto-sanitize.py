#!/usr/bin/env python3
"""
Auto-sanitize sensitive data in files before git commit
"""

import re
import sys
import os


def sanitize_file(filepath):
    """Sanitize a single file by replacing sensitive patterns"""
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False
    
    original_content = content
    changed = False
    
    # Replace AWS SSO URLs with placeholders
    patterns = [
        # SSO URLs
        (r'sso_start_url = "https://[^"]*\.awsapps\.com[^"]*"', 
         'sso_start_url = "https://xxx.awsapps.com/start#replace-with-your-sso-url"'),
        (r'sso_start_url = "https://[^"]*\.awsapps\.cn[^"]*"', 
         'sso_start_url = "https://xxx.awsapps.cn/start#replace-with-your-sso-url"'),
        
        # Access tokens and secret keys
        (r'access_token = "[^"x][^"]*"', 'access_token = "xxx-your-access-token"'),
        (r'secret_key = "[^"x][^"]*"', 'secret_key = "xxx-your-secret-key"'),
        (r'password = "[^"x][^"]*"', 'password = "xxx-your-password"'),
    ]
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            changed = True
    
    if changed:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔧 Auto-sanitized: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error writing {filepath}: {e}")
            return False
    
    return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: auto-sanitize.py <file1> [file2] ...")
        sys.exit(1)
    
    files_changed = []
    
    for filepath in sys.argv[1:]:
        if sanitize_file(filepath):
            files_changed.append(filepath)
    
    if files_changed:
        print(f"✅ Auto-sanitized {len(files_changed)} file(s)")
        return True
    else:
        return False


if __name__ == "__main__":
    changed = main()
    sys.exit(0 if changed else 1)