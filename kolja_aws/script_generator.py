"""
Shell script generator

This module provides functionality to generate shell-specific integration scripts
for the profile switcher functionality.
"""

import os
import sys
from typing import Dict, Optional
from kolja_aws.shell_exceptions import UnsupportedShellError


class ScriptGenerator:
    """Shell 脚本生成器"""
    
    def __init__(self):
        self.install_marker_start = "# kolja-aws profile switcher - START"
        self.install_marker_end = "# kolja-aws profile switcher - END"
    
    def generate_bash_script(self) -> str:
        """生成 Bash/Zsh 兼容脚本"""
        # Determine the correct Python executable
        python_cmd = self._get_python_command()
        
        script = f"""{self.install_marker_start}
sp() {{
    # Create a temporary file to store the selected profile
    local temp_file=$(mktemp)
    
    # Run Python script with proper terminal I/O
    {python_cmd} -c "
import sys
import os
from kolja_aws.shell_integration import show_interactive_menu

# Ensure we're using the terminal for input/output
if not os.isatty(0):
    # Reopen stdin from terminal
    sys.stdin = open('/dev/tty', 'r')

try:
    selected_profile = show_interactive_menu()
    if selected_profile:
        # Write the selected profile to the temp file
        with open('$temp_file', 'w') as f:
            f.write(selected_profile)
        sys.exit(0)
    else:
        sys.exit(1)
except KeyboardInterrupt:
    sys.exit(1)
except Exception as e:
    print(f'Error: {{e}}', file=sys.stderr)
    sys.exit(1)
"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ] && [ -f "$temp_file" ]; then
        local selected_profile=$(cat "$temp_file")
        if [ -n "$selected_profile" ]; then
            export AWS_PROFILE="$selected_profile"
            echo "✅ Switched to profile: $selected_profile"
        fi
    fi
    
    # Clean up
    rm -f "$temp_file"
}}
{self.install_marker_end}"""
        
        return script
    
    def generate_zsh_script(self) -> str:
        """生成 Zsh 专用脚本（与 Bash 相同）"""
        return self.generate_bash_script()
    
    def generate_fish_script(self) -> str:
        """生成 Fish shell 脚本"""
        # Determine the correct Python executable
        python_cmd = self._get_python_command()
        
        script = f"""{self.install_marker_start}
function sp
    # Create a temporary file to store the selected profile
    set temp_file (mktemp)
    
    # Run Python script with proper terminal I/O
    {python_cmd} -c "
import sys
import os
from kolja_aws.shell_integration import show_interactive_menu

# Ensure we're using the terminal for input/output
if not os.isatty(0):
    # Reopen stdin from terminal
    sys.stdin = open('/dev/tty', 'r')

try:
    selected_profile = show_interactive_menu()
    if selected_profile:
        # Write the selected profile to the temp file
        with open('$temp_file', 'w') as f:
            f.write(selected_profile)
        sys.exit(0)
    else:
        sys.exit(1)
except KeyboardInterrupt:
    sys.exit(1)
except Exception as e:
    print(f'Error: {{e}}', file=sys.stderr)
    sys.exit(1)
"
    
    set exit_code $status
    
    if test $exit_code -eq 0 -a -f $temp_file
        set selected_profile (cat $temp_file)
        if test -n "$selected_profile"
            set -gx AWS_PROFILE $selected_profile
            echo "✅ Switched to profile: $selected_profile"
        end
    end
    
    # Clean up
    rm -f $temp_file
end
{self.install_marker_end}"""
        
        return script
    
    def get_script_for_shell(self, shell_type: str) -> str:
        """根据 shell 类型生成对应脚本"""
        if shell_type == 'bash':
            return self.generate_bash_script()
        elif shell_type == 'zsh':
            return self.generate_zsh_script()
        elif shell_type == 'fish':
            return self.generate_fish_script()
        else:
            supported_shells = ['bash', 'zsh', 'fish']
            raise UnsupportedShellError(shell_type, supported_shells)
    
    def get_uninstall_script_for_shell(self, shell_type: str) -> str:
        """生成卸载脚本（移除函数定义）"""
        if shell_type in ['bash', 'zsh']:
            return f"""{self.install_marker_start}
# Profile switcher function has been removed
# You can reinstall it by running: kolja aws sp
{self.install_marker_end}"""
        elif shell_type == 'fish':
            return f"""{self.install_marker_start}
# Profile switcher function has been removed
# You can reinstall it by running: kolja aws sp
{self.install_marker_end}"""
        else:
            supported_shells = ['bash', 'zsh', 'fish']
            raise UnsupportedShellError(shell_type, supported_shells)
    
    def extract_existing_script(self, config_content: str) -> Optional[str]:
        """从配置文件内容中提取现有的脚本"""
        start_marker = self.install_marker_start
        end_marker = self.install_marker_end
        
        start_index = config_content.find(start_marker)
        if start_index == -1:
            return None
        
        end_index = config_content.find(end_marker, start_index)
        if end_index == -1:
            return None
        
        # Include the end marker in the extracted script
        end_index += len(end_marker)
        
        return config_content[start_index:end_index]
    
    def remove_existing_script(self, config_content: str) -> str:
        """从配置文件内容中移除现有的脚本"""
        existing_script = self.extract_existing_script(config_content)
        if existing_script:
            # Remove the existing script and any surrounding empty lines
            updated_content = config_content.replace(existing_script, "")
            
            # Clean up multiple consecutive newlines
            while "\n\n\n" in updated_content:
                updated_content = updated_content.replace("\n\n\n", "\n\n")
            
            return updated_content.strip()
        
        return config_content
    
    def insert_script_into_config(self, config_content: str, script: str, shell_type: str) -> str:
        """将脚本插入到配置文件内容中"""
        # First remove any existing script
        clean_content = self.remove_existing_script(config_content)
        
        # Add the new script at the end
        if clean_content and not clean_content.endswith('\n'):
            clean_content += '\n'
        
        clean_content += '\n' + script + '\n'
        
        return clean_content
    
    def is_script_installed(self, config_content: str) -> bool:
        """检查脚本是否已安装"""
        return self.install_marker_start in config_content and self.install_marker_end in config_content
    
    def validate_script_syntax(self, script: str, shell_type: str) -> bool:
        """验证生成的脚本语法是否正确"""
        try:
            # Basic syntax validation
            if shell_type in ['bash', 'zsh']:
                # Check for basic bash/zsh syntax elements
                required_elements = ['sp()', 'export AWS_PROFILE', 'if [']
                return all(element in script for element in required_elements)
            elif shell_type == 'fish':
                # Check for basic fish syntax elements
                required_elements = ['function sp', 'set -gx AWS_PROFILE']
                return all(element in script for element in required_elements)
            
            return False
        except Exception:
            return False
    
    def get_installation_instructions(self, shell_type: str, config_file: str) -> str:
        """获取安装后的使用说明"""
        instructions = f"""
🎉 Shell integration installed successfully!

Configuration updated: {config_file}

To activate the changes, run:
  source {config_file}

Or restart your terminal.

Usage:
  sp    # Launch interactive AWS profile switcher

The 'sp' command will show you all available AWS profiles with a nice
interactive menu. Use arrow keys to navigate and Enter to select.
"""
        
        if shell_type == 'fish':
            instructions = instructions.replace('source', '.')
        
        return instructions.strip()
    
    def _get_python_command(self) -> str:
        """获取正确的 Python 命令"""
        try:
            # Try to detect if we're running from a uv tool installation
            import kolja_aws
            kolja_path = kolja_aws.__file__
            
            # Check if this is a uv tool installation
            if '.local/share/uv/tools/' in kolja_path:
                # Extract the tool name and construct the Python path
                import re
                match = re.search(r'\.local/share/uv/tools/([^/]+)/', kolja_path)
                if match:
                    tool_name = match.group(1)
                    home_dir = os.path.expanduser('~')
                    python_path = f"{home_dir}/.local/share/uv/tools/{tool_name}/bin/python"
                    if os.path.exists(python_path):
                        return python_path
            
            # Fallback to system python
            return "python3"
            
        except ImportError:
            # Development environment fallback
            return "python3"
    
    def _get_kolja_aws_path(self) -> str:
        """获取 kolja_aws 模块的路径"""
        try:
            import kolja_aws
            # Return the parent directory of kolja_aws module (project root)
            kolja_aws_dir = os.path.dirname(kolja_aws.__file__)
            return os.path.dirname(kolja_aws_dir)
        except ImportError:
            # Fallback: try to determine from current file location
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to get project root
            return os.path.dirname(current_dir)
    
    def _escape_path_for_shell(self, path: str, shell_type: str) -> str:
        """为 shell 脚本转义路径"""
        if shell_type in ['bash', 'zsh']:
            # Escape single quotes and backslashes for bash/zsh
            return path.replace("'", "\\'").replace("\\", "\\\\")
        elif shell_type == 'fish':
            # Fish has different escaping rules
            return path.replace("'", "\\'")
        
        return path