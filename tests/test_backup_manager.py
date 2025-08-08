"""
Tests for configuration file backup manager
"""

import os
import tempfile
import time
import pytest
from unittest.mock import patch, mock_open
from kolja_aws.backup_manager import BackupManager
from kolja_aws.shell_exceptions import BackupError


class TestBackupManager:
    """Test BackupManager class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.backup_manager = BackupManager()
        
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write("# Test configuration file\nexport TEST=value\n")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Clean up temp file
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
        
        # Clean up any backup files
        backups = self.backup_manager.list_backups(self.temp_file_path)
        for backup in backups:
            try:
                os.unlink(backup)
            except OSError:
                pass
    
    def test_init_default_suffix(self):
        """Test BackupManager initialization with default suffix"""
        manager = BackupManager()
        assert manager.backup_suffix == ".kolja-backup"
    
    def test_init_custom_suffix(self):
        """Test BackupManager initialization with custom suffix"""
        manager = BackupManager(".custom-backup")
        assert manager.backup_suffix == ".custom-backup"
    
    def test_create_backup_success(self):
        """Test successful backup creation"""
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        # Backup file should exist
        assert os.path.exists(backup_path)
        
        # Backup should contain same content as original
        with open(self.temp_file_path, 'r') as original:
            original_content = original.read()
        
        with open(backup_path, 'r') as backup:
            backup_content = backup.read()
        
        assert original_content == backup_content
        
        # Backup filename should contain timestamp and suffix
        assert ".kolja-backup_" in backup_path
        assert backup_path.startswith(self.temp_file_path)
    
    def test_create_backup_nonexistent_file(self):
        """Test backup creation with non-existent source file"""
        nonexistent_path = "/tmp/nonexistent_file"
        
        with pytest.raises(BackupError) as exc_info:
            self.backup_manager.create_backup(nonexistent_path)
        
        assert exc_info.value.context['operation'] == 'create'
        assert "does not exist" in exc_info.value.context['details']
    
    @patch('os.access')
    def test_create_backup_no_read_permission(self, mock_access):
        """Test backup creation with no read permission"""
        # Mock os.access to return False for read permission
        mock_access.return_value = False
        
        with pytest.raises(BackupError) as exc_info:
            self.backup_manager.create_backup(self.temp_file_path)
        
        assert exc_info.value.context['operation'] == 'create'
        assert "No read permission" in exc_info.value.context['details']
    
    def test_restore_backup_success(self):
        """Test successful backup restoration"""
        # Create backup first
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        # Modify original file
        with open(self.temp_file_path, 'w') as f:
            f.write("# Modified content\n")
        
        # Restore backup
        result = self.backup_manager.restore_backup(backup_path)
        assert result is True
        
        # Original content should be restored
        with open(self.temp_file_path, 'r') as f:
            restored_content = f.read()
        
        assert "# Test configuration file" in restored_content
        assert "export TEST=value" in restored_content
    
    def test_restore_backup_with_target_path(self):
        """Test backup restoration with custom target path"""
        # Create backup
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        # Create new target file
        target_file = tempfile.NamedTemporaryFile(delete=False)
        target_path = target_file.name
        target_file.close()
        
        try:
            # Restore to different target
            result = self.backup_manager.restore_backup(backup_path, target_path)
            assert result is True
            
            # Target should have backup content
            with open(target_path, 'r') as f:
                content = f.read()
            
            assert "# Test configuration file" in content
        finally:
            os.unlink(target_path)
    
    def test_restore_backup_nonexistent_backup(self):
        """Test restoration with non-existent backup file"""
        nonexistent_backup = "/tmp/nonexistent_backup"
        
        with pytest.raises(BackupError) as exc_info:
            self.backup_manager.restore_backup(nonexistent_backup)
        
        assert exc_info.value.context['operation'] == 'restore'
        assert "does not exist" in exc_info.value.context['details']
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist"""
        backups = self.backup_manager.list_backups(self.temp_file_path)
        assert backups == []
    
    def test_list_backups_multiple(self):
        """Test listing multiple backups"""
        # Create multiple backups with longer delays to ensure different timestamps
        backup1 = self.backup_manager.create_backup(self.temp_file_path)
        time.sleep(1.1)  # Increase delay to ensure different timestamps
        backup2 = self.backup_manager.create_backup(self.temp_file_path)
        time.sleep(1.1)
        backup3 = self.backup_manager.create_backup(self.temp_file_path)
        
        backups = self.backup_manager.list_backups(self.temp_file_path)
        
        # Should have 3 backups
        assert len(backups) == 3
        
        # Should be sorted by modification time (newest first)
        assert backup3 in backups
        assert backup2 in backups
        assert backup1 in backups
        
        # Newest should be first
        assert backups[0] == backup3
    
    def test_get_latest_backup_exists(self):
        """Test getting latest backup when backups exist"""
        backup1 = self.backup_manager.create_backup(self.temp_file_path)
        time.sleep(0.1)
        backup2 = self.backup_manager.create_backup(self.temp_file_path)
        
        latest = self.backup_manager.get_latest_backup(self.temp_file_path)
        assert latest == backup2
    
    def test_get_latest_backup_none(self):
        """Test getting latest backup when none exist"""
        latest = self.backup_manager.get_latest_backup(self.temp_file_path)
        assert latest is None
    
    def test_delete_backup_success(self):
        """Test successful backup deletion"""
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        # Backup should exist
        assert os.path.exists(backup_path)
        
        # Delete backup
        result = self.backup_manager.delete_backup(backup_path)
        assert result is True
        
        # Backup should no longer exist
        assert not os.path.exists(backup_path)
    
    def test_delete_backup_nonexistent(self):
        """Test deleting non-existent backup"""
        nonexistent_backup = "/tmp/nonexistent_backup"
        
        result = self.backup_manager.delete_backup(nonexistent_backup)
        assert result is False
    
    def test_cleanup_old_backups_no_cleanup_needed(self):
        """Test cleanup when no cleanup is needed"""
        # Create 3 backups (less than default keep_count of 5)
        for i in range(3):
            self.backup_manager.create_backup(self.temp_file_path)
            time.sleep(1.1)  # Increase delay
        
        # Should not raise any exception
        self.backup_manager.cleanup_old_backups(self.temp_file_path)
        
        # All backups should still exist
        backups = self.backup_manager.list_backups(self.temp_file_path)
        assert len(backups) == 3
    
    def test_cleanup_old_backups_cleanup_needed(self):
        """Test cleanup when cleanup is needed"""
        # Create 7 backups (more than default keep_count of 5)
        for i in range(7):
            self.backup_manager.create_backup(self.temp_file_path)
            time.sleep(1.1)  # Increase delay
        
        # Cleanup old backups
        self.backup_manager.cleanup_old_backups(self.temp_file_path, keep_count=3)
        
        # Should have only 3 backups remaining
        backups = self.backup_manager.list_backups(self.temp_file_path)
        assert len(backups) == 3
    
    def test_get_backup_info_success(self):
        """Test getting backup information"""
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        info = self.backup_manager.get_backup_info(backup_path)
        
        assert info['path'] == backup_path
        assert info['size'] > 0
        assert 'created' in info
        assert 'modified' in info
        assert info['original_path'] == self.temp_file_path
    
    def test_get_backup_info_nonexistent(self):
        """Test getting info for non-existent backup"""
        nonexistent_backup = "/tmp/nonexistent_backup"
        
        with pytest.raises(BackupError) as exc_info:
            self.backup_manager.get_backup_info(nonexistent_backup)
        
        assert exc_info.value.context['operation'] == 'info'
    
    def test_extract_original_path(self):
        """Test extracting original path from backup path"""
        backup_path = "/home/user/.bashrc.kolja-backup_20240115_143022"
        original = self.backup_manager._extract_original_path(backup_path)
        assert original == "/home/user/.bashrc"
    
    def test_extract_original_path_no_suffix(self):
        """Test extracting original path when no suffix present"""
        path = "/home/user/.bashrc"
        original = self.backup_manager._extract_original_path(path)
        assert original == "/home/user/.bashrc"
    
    def test_is_backup_file_true(self):
        """Test backup file detection - positive case"""
        backup_path = "/home/user/.bashrc.kolja-backup_20240115_143022"
        assert self.backup_manager.is_backup_file(backup_path) is True
    
    def test_is_backup_file_false(self):
        """Test backup file detection - negative case"""
        regular_path = "/home/user/.bashrc"
        assert self.backup_manager.is_backup_file(regular_path) is False
    
    def test_validate_backup_integrity_valid(self):
        """Test backup integrity validation - valid backup"""
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        is_valid = self.backup_manager.validate_backup_integrity(backup_path)
        assert is_valid is True
    
    def test_validate_backup_integrity_nonexistent(self):
        """Test backup integrity validation - non-existent file"""
        nonexistent_backup = "/tmp/nonexistent_backup"
        
        is_valid = self.backup_manager.validate_backup_integrity(nonexistent_backup)
        assert is_valid is False
    
    def test_validate_backup_integrity_unreadable(self):
        """Test backup integrity validation - unreadable file"""
        # Create backup first
        backup_path = self.backup_manager.create_backup(self.temp_file_path)
        
        # Now patch the open function for validation only
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            is_valid = self.backup_manager.validate_backup_integrity(backup_path)
            assert is_valid is False