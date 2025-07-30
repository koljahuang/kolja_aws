#!/usr/bin/env python3
"""
Test dynamic configuration support for updated utility functions
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add project root directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kolja_aws.utils import (
    get_section_metadata_from_template,
    get_available_sso_sessions,
    get_sso_session_config,
    write_dynamic_sso_template_to_file,
    _generate_dynamic_sso_template
)


class TestUtilsDynamicConfig(unittest.TestCase):
    """Test dynamic configuration support for utility functions"""
    
    def setUp(self):
        """Setup before tests"""
        self.test_sso_sessions = {
            'kolja-cn': {
                'sso_start_url': 'https://start.home.awsapps.cn/directory/xxx',
                'sso_region': 'cn-northwest-1',
                'sso_registration_scopes': 'sso:account:access'
            },
            'kolja': {
                'sso_start_url': 'https://xxx/start',
                'sso_region': 'ap-southeast-2',
                'sso_registration_scopes': 'sso:account:access'
            }
        }
    
    @patch('kolja_aws.utils.settings')
    def test_generate_dynamic_sso_template(self, mock_settings):
        """Test dynamic SSO template generation"""
        # Set mock settings
        mock_settings.sso_sessions = self.test_sso_sessions
        
        # Generate template
        template_content = _generate_dynamic_sso_template()
        
        # Verify template content
        self.assertIn('[sso-session kolja-cn]', template_content)
        self.assertIn('[sso-session kolja]', template_content)
        self.assertIn('sso_start_url = https://start.home.awsapps.cn/directory/xxx', template_content)
        self.assertIn('sso_region = cn-northwest-1', template_content)
        self.assertIn('sso_registration_scopes = sso:account:access', template_content)
    
    @patch('kolja_aws.utils.settings')
    def test_get_available_sso_sessions(self, mock_settings):
        """Test getting available SSO sessions"""
        # Set mock settings
        mock_settings.sso_sessions = self.test_sso_sessions
        
        # Get session list
        sessions = get_available_sso_sessions()
        
        # Verify results
        self.assertEqual(set(sessions), {'kolja-cn', 'kolja'})
    
    @patch('kolja_aws.utils.settings')
    def test_get_sso_session_config(self, mock_settings):
        """Test getting SSO session configuration"""
        # Set mock settings
        mock_settings.sso_sessions = self.test_sso_sessions
        
        # Get configuration
        config = get_sso_session_config('kolja-cn')
        
        # Verify configuration
        expected_config = {
            'sso_start_url': 'https://start.home.awsapps.cn/directory/xxx',
            'sso_region': 'cn-northwest-1',
            'sso_registration_scopes': 'sso:account:access'
        }
        self.assertEqual(config, expected_config)
    
    @patch('kolja_aws.utils.settings')
    def test_get_sso_session_config_with_default_scopes(self, mock_settings):
        """Test getting SSO session configuration with default scopes"""
        # Set configuration without registration_scopes
        test_sessions = {
            'test-session': {
                'sso_start_url': 'https://test.example.com',
                'sso_region': 'us-east-1'
            }
        }
        mock_settings.sso_sessions = test_sessions
        
        # Get configuration
        config = get_sso_session_config('test-session')
        
        # Verify default scopes are added
        self.assertEqual(config['sso_registration_scopes'], 'sso:account:access')
    
    @patch('kolja_aws.utils.settings')
    def test_get_section_metadata_from_template_dynamic(self, mock_settings):
        """Test getting section metadata from dynamic template"""
        # Set mock settings
        mock_settings.sso_sessions = self.test_sso_sessions
        
        # Create a non-existent configuration file path
        non_existent_file = '/tmp/non_existent_config.conf'
        
        # Get section metadata
        section_content, section_dict = get_section_metadata_from_template(
            non_existent_file, 'sso-session kolja-cn'
        )
        
        # Verify results
        self.assertIn('[sso-session kolja-cn]', section_content)
        self.assertEqual(section_dict['sso_start_url'], 'https://start.home.awsapps.cn/directory/xxx')
        self.assertEqual(section_dict['sso_region'], 'cn-northwest-1')
        self.assertEqual(section_dict['sso_registration_scopes'], 'sso:account:access')
    
    @patch('kolja_aws.utils.settings')
    def test_write_dynamic_sso_template_to_file(self, mock_settings):
        """Test writing dynamic template to file"""
        # Set mock settings
        mock_settings.sso_sessions = self.test_sso_sessions
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.template', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Write template
            result_path = write_dynamic_sso_template_to_file(temp_path)
            
            # Verify file path
            self.assertEqual(result_path, temp_path)
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
            
            self.assertIn('[sso-session kolja-cn]', content)
            self.assertIn('[sso-session kolja]', content)
            self.assertIn('sso_start_url = https://start.home.awsapps.cn/directory/xxx', content)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def test_fallback_to_template_file(self):
        """Test fallback to template file functionality"""
        # When settings doesn't have sso_sessions, should fallback to template file
        with patch('kolja_aws.utils.settings') as mock_settings:
            # Set settings without sso_sessions attribute
            del mock_settings.sso_sessions
            
            # Get session list (should read from template file)
            sessions = get_available_sso_sessions()
            
            # Verify sessions can be obtained (from template file)
            self.assertIsInstance(sessions, list)


if __name__ == '__main__':
    unittest.main()