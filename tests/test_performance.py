"""
Performance and stress tests for shell profile switcher

These tests verify the performance characteristics and stress tolerance
of the shell profile switcher system.
"""

import os
import time
import tempfile
import pytest
from unittest.mock import Mock, patch
from kolja_aws.profile_loader import ProfileLoader
from kolja_aws.shell_models import ProfileInfo
from kolja_aws.backup_manager import BackupManager
from kolja_aws.script_generator import ScriptGenerator


class TestPerformance:
    """Performance tests"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.large_aws_config = os.path.join(self.temp_dir, 'large_aws_config')
        
        # Create a large AWS config file with many profiles
        self._create_large_aws_config(100)  # 100 profiles
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_large_aws_config(self, profile_count: int):
        """Create a large AWS config file with many profiles"""
        content = '''[default]
region = us-east-1
output = json

'''
        
        for i in range(profile_count):
            content += f'''[profile test-profile-{i:03d}]
sso_session = test-sso-{i % 10}
sso_account_id = {123456789 + i}
sso_role_name = Role{i % 5}
region = us-{['east', 'west'][i % 2]}-{(i % 3) + 1}

'''
        
        # Add SSO sessions
        for i in range(10):
            content += f'''[sso-session test-sso-{i}]
sso_start_url = https://test{i}.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access

'''
        
        with open(self.large_aws_config, 'w') as f:
            f.write(content)
    
    def test_large_profile_loading_performance(self):
        """Test performance with large number of profiles"""
        loader = ProfileLoader(self.large_aws_config)
        
        # Measure loading time
        start_time = time.time()
        profiles = loader.load_profiles()
        end_time = time.time()
        
        loading_time = end_time - start_time
        
        # Should load 101 profiles (100 + default) in reasonable time
        assert len(profiles) == 101
        assert loading_time < 1.0  # Should load in less than 1 second
        
        # Verify profile details are correctly parsed
        test_profile = next((p for p in profiles if p.name == 'test-profile-050'), None)
        assert test_profile is not None
        assert test_profile.account_id == '123456839'  # 123456789 + 50
        assert test_profile.role_name == 'Role0'  # 50 % 5 = 0
    
    def test_profile_validation_performance(self):
        """Test performance of profile validation with many profiles"""
        loader = ProfileLoader(self.large_aws_config)
        
        # Test validation performance
        start_time = time.time()
        
        # Validate multiple profiles
        for i in range(0, 100, 10):  # Test every 10th profile
            profile_name = f'test-profile-{i:03d}'
            result = loader.validate_profile(profile_name)
            assert result is True
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should validate 10 profiles quickly
        assert validation_time < 0.5  # Should validate in less than 0.5 seconds
    
    def test_backup_performance_with_large_files(self):
        """Test backup performance with large configuration files"""
        # Create a large shell config file
        large_config = os.path.join(self.temp_dir, 'large_bashrc')
        
        # Create 10KB of configuration content
        large_content = '# Large configuration file\n' * 500
        with open(large_config, 'w') as f:
            f.write(large_content)
        
        backup_manager = BackupManager()
        
        # Measure backup time
        start_time = time.time()
        backup_path = backup_manager.create_backup(large_config)
        end_time = time.time()
        
        backup_time = end_time - start_time
        
        # Should backup quickly even for large files
        assert backup_time < 0.1  # Should backup in less than 0.1 seconds
        assert os.path.exists(backup_path)
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        
        assert len(backup_content) == len(large_content)
        
        # Clean up
        backup_manager.delete_backup(backup_path)
    
    def test_script_generation_performance(self):
        """Test script generation performance"""
        generator = ScriptGenerator()
        
        # Measure script generation time for different shells
        shells = ['bash', 'zsh', 'fish']
        
        for shell in shells:
            start_time = time.time()
            
            # Generate script multiple times
            for _ in range(100):
                script = generator.get_script_for_shell(shell)
                assert len(script) > 0
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            # Should generate 100 scripts quickly
            assert generation_time < 0.1  # Should generate in less than 0.1 seconds
    
    def test_concurrent_operations(self):
        """Test concurrent operations performance"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def load_profiles_worker():
            try:
                loader = ProfileLoader(self.large_aws_config)
                profiles = loader.load_profiles()
                results.put(len(profiles))
            except Exception as e:
                errors.put(e)
        
        # Start multiple threads
        threads = []
        thread_count = 5
        
        start_time = time.time()
        
        for _ in range(thread_count):
            thread = threading.Thread(target=load_profiles_worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check results
        assert errors.empty(), f"Errors occurred: {list(errors.queue)}"
        assert results.qsize() == thread_count
        
        # All threads should return same profile count
        profile_counts = []
        while not results.empty():
            profile_counts.append(results.get())
        
        assert all(count == 101 for count in profile_counts)
        
        # Concurrent operations should complete in reasonable time
        assert total_time < 2.0  # Should complete in less than 2 seconds
    
    def test_repeated_operations_performance(self):
        """Test performance of repeated operations"""
        loader = ProfileLoader(self.large_aws_config)
        
        # Measure time for repeated profile loading
        start_time = time.time()
        
        for _ in range(10):
            profiles = loader.load_profiles()
            assert len(profiles) == 101
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Repeated operations should be efficient
        assert total_time < 2.0  # 10 loads in less than 2 seconds
        
        # Average time per load should be reasonable
        avg_time_per_load = total_time / 10
        assert avg_time_per_load < 0.2  # Less than 0.2 seconds per load