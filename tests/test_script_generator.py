"""
Tests for shell script generator
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from kolja_aws.script_generator import ScriptGenerator
from kolja_aws.shell_exceptions import UnsupportedShellError


class TestScriptGenerator:
    """Test ScriptGenerator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ScriptGenerator()
    
    def test_init_default_markers(self):
        """Test ScriptGenerator initialization with default markers"""
        assert self.generator.install_marker_start == "# kolja-aws profile switcher - START"
        assert self.generator.install_marker_end == "# kolja-aws profile switcher - END"
    
    def test_generate_bash_script(self):
        """Test Bash script generation"""
        script = self.generator.generate_bash_script()
        
        # Check for required elements
        assert "sp()" in script
        assert "export AWS_PROFILE" in script
        assert "python3 -c" in script
        assert "ProfileSwitcher" in script
        assert self.generator.install_marker_start in script
        assert self.generator.install_marker_end in script
        
        # Check bash-specific syntax
        assert "if [ $? -eq 0 ]" in script
        assert "fi" in script
    
    def test_generate_zsh_script(self):
        """Test Zsh script generation (should be same as bash)"""
        bash_script = self.generator.generate_bash_script()
        zsh_script = self.generator.generate_zsh_script()
        
        assert bash_script == zsh_script
    
    def test_generate_fish_script(self):
        """Test Fish script generation"""
        script = self.generator.generate_fish_script()
        
        # Check for required elements
        assert "function sp" in script
        assert "set -gx AWS_PROFILE" in script
        assert "python3 -c" in script
        assert "ProfileSwitcher" in script
        assert self.generator.install_marker_start in script
        assert self.generator.install_marker_end in script
        
        # Check fish-specific syntax
        assert "if test $status -eq 0" in script
        assert "end" in script
    
    def test_get_script_for_shell_bash(self):
        """Test getting script for bash shell"""
        script = self.generator.get_script_for_shell('bash')
        assert "sp()" in script
        assert "export AWS_PROFILE" in script
    
    def test_get_script_for_shell_zsh(self):
        """Test getting script for zsh shell"""
        script = self.generator.get_script_for_shell('zsh')
        assert "sp()" in script
        assert "export AWS_PROFILE" in script
    
    def test_get_script_for_shell_fish(self):
        """Test getting script for fish shell"""
        script = self.generator.get_script_for_shell('fish')
        assert "function sp" in script
        assert "set -gx AWS_PROFILE" in script
    
    def test_get_script_for_shell_unsupported(self):
        """Test getting script for unsupported shell"""
        with pytest.raises(UnsupportedShellError) as exc_info:
            self.generator.get_script_for_shell('tcsh')
        
        assert exc_info.value.context['shell_type'] == 'tcsh'
        assert 'bash' in exc_info.value.context['supported_shells']
    
    def test_get_uninstall_script_bash(self):
        """Test getting uninstall script for bash"""
        script = self.generator.get_uninstall_script_for_shell('bash')
        
        assert self.generator.install_marker_start in script
        assert self.generator.install_marker_end in script
        assert "removed" in script.lower()
        assert "kolja aws sp" in script
    
    def test_get_uninstall_script_fish(self):
        """Test getting uninstall script for fish"""
        script = self.generator.get_uninstall_script_for_shell('fish')
        
        assert self.generator.install_marker_start in script
        assert self.generator.install_marker_end in script
        assert "removed" in script.lower()
    
    def test_get_uninstall_script_unsupported(self):
        """Test getting uninstall script for unsupported shell"""
        with pytest.raises(UnsupportedShellError):
            self.generator.get_uninstall_script_for_shell('tcsh')
    
    def test_extract_existing_script_present(self):
        """Test extracting existing script when present"""
        config_content = f"""# Some config
export PATH=/usr/bin

{self.generator.install_marker_start}
sp() {{
    echo "old script"
}}
{self.generator.install_marker_end}

# More config
alias ll='ls -la'
"""
        
        extracted = self.generator.extract_existing_script(config_content)
        
        assert extracted is not None
        assert self.generator.install_marker_start in extracted
        assert self.generator.install_marker_end in extracted
        assert "old script" in extracted
    
    def test_extract_existing_script_not_present(self):
        """Test extracting existing script when not present"""
        config_content = """# Some config
export PATH=/usr/bin
alias ll='ls -la'
"""
        
        extracted = self.generator.extract_existing_script(config_content)
        assert extracted is None
    
    def test_extract_existing_script_incomplete_markers(self):
        """Test extracting script with incomplete markers"""
        config_content = f"""# Some config
{self.generator.install_marker_start}
sp() {{
    echo "incomplete script"
}}
# Missing end marker
"""
        
        extracted = self.generator.extract_existing_script(config_content)
        assert extracted is None
    
    def test_remove_existing_script_present(self):
        """Test removing existing script when present"""
        config_content = f"""# Some config
export PATH=/usr/bin

{self.generator.install_marker_start}
sp() {{
    echo "old script"
}}
{self.generator.install_marker_end}

# More config
alias ll='ls -la'
"""
        
        cleaned = self.generator.remove_existing_script(config_content)
        
        assert self.generator.install_marker_start not in cleaned
        assert self.generator.install_marker_end not in cleaned
        assert "old script" not in cleaned
        assert "export PATH=/usr/bin" in cleaned
        assert "alias ll='ls -la'" in cleaned
    
    def test_remove_existing_script_not_present(self):
        """Test removing existing script when not present"""
        config_content = """# Some config
export PATH=/usr/bin
alias ll='ls -la'
"""
        
        cleaned = self.generator.remove_existing_script(config_content)
        assert cleaned == config_content
    
    def test_insert_script_into_config_empty(self):
        """Test inserting script into empty config"""
        config_content = ""
        script = "sp() { echo 'test'; }"
        
        result = self.generator.insert_script_into_config(config_content, script, 'bash')
        
        assert script in result
        assert result.strip().endswith(script)
    
    def test_insert_script_into_config_existing_content(self):
        """Test inserting script into config with existing content"""
        config_content = "# Existing config\nexport PATH=/usr/bin"
        script = "sp() { echo 'test'; }"
        
        result = self.generator.insert_script_into_config(config_content, script, 'bash')
        
        assert "# Existing config" in result
        assert "export PATH=/usr/bin" in result
        assert script in result
    
    def test_insert_script_replace_existing(self):
        """Test inserting script replaces existing script"""
        old_script = f"""{self.generator.install_marker_start}
sp() {{ echo "old"; }}
{self.generator.install_marker_end}"""
        
        config_content = f"# Config\n{old_script}\n# More config"
        new_script = f"""{self.generator.install_marker_start}
sp() {{ echo "new"; }}
{self.generator.install_marker_end}"""
        
        result = self.generator.insert_script_into_config(config_content, new_script, 'bash')
        
        assert "old" not in result
        assert "new" in result
        assert result.count(self.generator.install_marker_start) == 1
    
    def test_is_script_installed_true(self):
        """Test script installation detection - installed"""
        config_content = f"""# Config
{self.generator.install_marker_start}
sp() {{ echo "test"; }}
{self.generator.install_marker_end}
"""
        
        assert self.generator.is_script_installed(config_content) is True
    
    def test_is_script_installed_false(self):
        """Test script installation detection - not installed"""
        config_content = "# Config\nexport PATH=/usr/bin"
        
        assert self.generator.is_script_installed(config_content) is False
    
    def test_is_script_installed_partial(self):
        """Test script installation detection - partial markers"""
        config_content = f"# Config\n{self.generator.install_marker_start}\nsp() {{ echo 'test'; }}"
        
        assert self.generator.is_script_installed(config_content) is False
    
    def test_validate_script_syntax_bash_valid(self):
        """Test script syntax validation for bash - valid"""
        script = self.generator.generate_bash_script()
        
        is_valid = self.generator.validate_script_syntax(script, 'bash')
        assert is_valid is True
    
    def test_validate_script_syntax_fish_valid(self):
        """Test script syntax validation for fish - valid"""
        script = self.generator.generate_fish_script()
        
        is_valid = self.generator.validate_script_syntax(script, 'fish')
        assert is_valid is True
    
    def test_validate_script_syntax_bash_invalid(self):
        """Test script syntax validation for bash - invalid"""
        invalid_script = "echo 'not a proper function'"
        
        is_valid = self.generator.validate_script_syntax(invalid_script, 'bash')
        assert is_valid is False
    
    def test_validate_script_syntax_fish_invalid(self):
        """Test script syntax validation for fish - invalid"""
        invalid_script = "echo 'not a proper function'"
        
        is_valid = self.generator.validate_script_syntax(invalid_script, 'fish')
        assert is_valid is False
    
    def test_get_installation_instructions_bash(self):
        """Test getting installation instructions for bash"""
        instructions = self.generator.get_installation_instructions('bash', '~/.bashrc')
        
        assert "source ~/.bashrc" in instructions
        assert "sp" in instructions
        assert "interactive" in instructions.lower()
    
    def test_get_installation_instructions_fish(self):
        """Test getting installation instructions for fish"""
        instructions = self.generator.get_installation_instructions('fish', '~/.config/fish/config.fish')
        
        # Fish uses '.' instead of 'source'
        assert ". ~/.config/fish/config.fish" in instructions
        assert "sp" in instructions
    
    def test_get_kolja_aws_path_success(self):
        """Test getting kolja_aws path - success"""
        # This should work since we're in the kolja_aws package
        path = self.generator._get_kolja_aws_path()
        assert path is not None
        assert isinstance(path, str)
        assert len(path) > 0
    
    @patch('kolja_aws.script_generator.ScriptGenerator._get_kolja_aws_path')
    def test_get_kolja_aws_path_in_script(self, mock_get_path):
        """Test that the path is used in generated scripts"""
        mock_get_path.return_value = '/test/path/kolja_aws'
        
        script = self.generator.generate_bash_script()
        assert '/test/path/kolja_aws' in script
    
    def test_escape_path_for_shell_bash(self):
        """Test path escaping for bash"""
        path = "/path/with'quotes/and\\backslashes"
        escaped = self.generator._escape_path_for_shell(path, 'bash')
        
        assert "\\'" in escaped
        assert "\\\\" in escaped
    
    def test_escape_path_for_shell_fish(self):
        """Test path escaping for fish"""
        path = "/path/with'quotes"
        escaped = self.generator._escape_path_for_shell(path, 'fish')
        
        assert "\\'" in escaped
    
    def test_escape_path_for_shell_no_special_chars(self):
        """Test path escaping with no special characters"""
        path = "/simple/path"
        
        bash_escaped = self.generator._escape_path_for_shell(path, 'bash')
        fish_escaped = self.generator._escape_path_for_shell(path, 'fish')
        
        assert bash_escaped == path
        assert fish_escaped == path