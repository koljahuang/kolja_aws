"""
Configuration file backup manager

This module provides functionality to create, restore, and manage backups
of shell configuration files.
"""

import os
import shutil
import glob
from datetime import datetime
from typing import List, Optional
from kolja_aws.shell_exceptions import BackupError


class BackupManager:
    """配置文件备份管理器"""
    
    def __init__(self, backup_suffix: str = ".kolja-backup"):
        self.backup_suffix = backup_suffix
    
    def create_backup(self, file_path: str) -> str:
        """创建配置文件备份"""
        expanded_path = os.path.expanduser(file_path)
        
        if not os.path.exists(expanded_path):
            raise BackupError(
                "create",
                file_path,
                f"Source file does not exist: {expanded_path}"
            )
        
        if not os.access(expanded_path, os.R_OK):
            raise BackupError(
                "create",
                file_path,
                f"No read permission for source file: {expanded_path}"
            )
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{expanded_path}{self.backup_suffix}_{timestamp}"
        
        try:
            # Create backup
            shutil.copy2(expanded_path, backup_path)
            
            # Verify backup was created successfully
            if not os.path.exists(backup_path):
                raise BackupError(
                    "create",
                    file_path,
                    f"Backup file was not created: {backup_path}"
                )
            
            return backup_path
            
        except (OSError, IOError) as e:
            raise BackupError(
                "create",
                file_path,
                f"Failed to create backup: {e}"
            )
    
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None) -> bool:
        """恢复配置文件备份"""
        expanded_backup = os.path.expanduser(backup_path)
        
        if not os.path.exists(expanded_backup):
            raise BackupError(
                "restore",
                backup_path,
                f"Backup file does not exist: {expanded_backup}"
            )
        
        # Determine target path
        if target_path is None:
            # Extract original path from backup filename
            target_path = self._extract_original_path(backup_path)
        
        expanded_target = os.path.expanduser(target_path)
        
        try:
            # Create target directory if it doesn't exist
            target_dir = os.path.dirname(expanded_target)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
            
            # Restore backup
            shutil.copy2(expanded_backup, expanded_target)
            
            # Verify restoration
            if not os.path.exists(expanded_target):
                raise BackupError(
                    "restore",
                    backup_path,
                    f"Target file was not restored: {expanded_target}"
                )
            
            return True
            
        except (OSError, IOError) as e:
            raise BackupError(
                "restore",
                backup_path,
                f"Failed to restore backup: {e}"
            )
    
    def cleanup_old_backups(self, file_path: str, keep_count: int = 5) -> None:
        """清理旧备份文件"""
        expanded_path = os.path.expanduser(file_path)
        
        # Find all backup files for this config file
        backup_pattern = f"{expanded_path}{self.backup_suffix}_*"
        backup_files = glob.glob(backup_pattern)
        
        if len(backup_files) <= keep_count:
            return  # No cleanup needed
        
        try:
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remove old backups (keep only the newest keep_count files)
            files_to_remove = backup_files[keep_count:]
            
            for backup_file in files_to_remove:
                try:
                    os.remove(backup_file)
                except OSError as e:
                    # Log warning but don't fail the entire operation
                    print(f"Warning: Failed to remove old backup {backup_file}: {e}")
                    
        except Exception as e:
            raise BackupError(
                "cleanup",
                file_path,
                f"Failed to cleanup old backups: {e}"
            )
    
    def list_backups(self, file_path: str) -> List[str]:
        """列出指定文件的所有备份"""
        expanded_path = os.path.expanduser(file_path)
        backup_pattern = f"{expanded_path}{self.backup_suffix}_*"
        backup_files = glob.glob(backup_pattern)
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return backup_files
    
    def get_latest_backup(self, file_path: str) -> Optional[str]:
        """获取最新的备份文件"""
        backups = self.list_backups(file_path)
        return backups[0] if backups else None
    
    def delete_backup(self, backup_path: str) -> bool:
        """删除指定的备份文件"""
        expanded_backup = os.path.expanduser(backup_path)
        
        if not os.path.exists(expanded_backup):
            return False  # Already deleted or never existed
        
        try:
            os.remove(expanded_backup)
            return True
        except OSError as e:
            raise BackupError(
                "delete",
                backup_path,
                f"Failed to delete backup: {e}"
            )
    
    def get_backup_info(self, backup_path: str) -> dict:
        """获取备份文件信息"""
        expanded_backup = os.path.expanduser(backup_path)
        
        if not os.path.exists(expanded_backup):
            raise BackupError(
                "info",
                backup_path,
                f"Backup file does not exist: {expanded_backup}"
            )
        
        try:
            stat = os.stat(expanded_backup)
            
            return {
                "path": backup_path,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "original_path": self._extract_original_path(backup_path)
            }
            
        except OSError as e:
            raise BackupError(
                "info",
                backup_path,
                f"Failed to get backup info: {e}"
            )
    
    def _extract_original_path(self, backup_path: str) -> str:
        """从备份文件路径提取原始文件路径"""
        # Remove backup suffix and timestamp
        # Format: /path/to/file.kolja-backup_20240115_143022
        if self.backup_suffix in backup_path:
            # Find the last occurrence of backup_suffix
            suffix_index = backup_path.rfind(self.backup_suffix)
            return backup_path[:suffix_index]
        
        # Fallback: just remove the backup suffix if present
        return backup_path.replace(self.backup_suffix, "")
    
    def is_backup_file(self, file_path: str) -> bool:
        """检查文件是否为备份文件"""
        return self.backup_suffix in file_path
    
    def validate_backup_integrity(self, backup_path: str) -> bool:
        """验证备份文件完整性"""
        expanded_backup = os.path.expanduser(backup_path)
        
        if not os.path.exists(expanded_backup):
            return False
        
        try:
            # Basic integrity check: file is readable and not empty
            with open(expanded_backup, 'r') as f:
                # Try to read first line
                f.readline()
            return True
        except (OSError, IOError, UnicodeDecodeError):
            return False