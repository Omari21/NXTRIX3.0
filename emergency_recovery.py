#!/usr/bin/env python3
"""
NXTRIX 3.0 - Emergency Recovery System
Automated code restoration and integrity verification
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path
import hashlib

class EmergencyRecovery:
    def __init__(self):
        self.backup_dir = Path("BACKUPS")
        self.archive_dir = Path("ARCHIVE") 
        self.recovery_log = "recovery_log.txt"
        
    def find_latest_backup(self, filename):
        """Find the most recent backup of a file"""
        if not self.backup_dir.exists():
            return None
            
        file_stem = Path(filename).stem
        file_ext = Path(filename).suffix
        
        backups = list(self.backup_dir.glob(f"{file_stem}_*{file_ext}"))
        if not backups:
            return None
            
        # Sort by modification time, return newest
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return backups[0]
    
    def find_latest_archive(self):
        """Find the most recent complete archive"""
        if not self.archive_dir.exists():
            return None
            
        archives = list(self.archive_dir.glob("NXTRIX_COMPLETE_BACKUP_*.zip"))
        if not archives:
            return None
            
        archives.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return archives[0]
    
    def restore_file(self, filename):
        """Restore a single file from backup"""
        backup_file = self.find_latest_backup(filename)
        if not backup_file:
            return False, f"No backup found for {filename}"
            
        try:
            shutil.copy2(backup_file, filename)
            self.log_recovery(f"RESTORED: {filename} from {backup_file.name}")
            return True, f"File restored from {backup_file.name}"
        except Exception as e:
            return False, f"Failed to restore: {e}"
    
    def restore_from_archive(self, archive_path=None):
        """Restore all files from complete archive"""
        if not archive_path:
            archive_path = self.find_latest_archive()
            
        if not archive_path:
            return False, "No archive found"
            
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall('.')
                
            self.log_recovery(f"FULL_RESTORE: All files restored from {archive_path.name}")
            return True, f"Complete restore from {archive_path.name}"
        except Exception as e:
            return False, f"Failed to restore from archive: {e}"
    
    def verify_critical_files(self):
        """Check if critical NXTRIX files exist"""
        critical_files = [
            'nxtrix_saas_app.py',
            'enhanced_crm.py', 
            'requirements.txt',
            'Procfile'
        ]
        
        missing_files = []
        for file in critical_files:
            if not os.path.exists(file):
                missing_files.append(file)
                
        return missing_files
    
    def emergency_restore(self):
        """Perform emergency restoration of missing critical files"""
        print("🚨 NXTRIX 3.0 Emergency Recovery System")
        print("=" * 50)
        
        missing = self.verify_critical_files()
        
        if not missing:
            print("✅ All critical files present - no recovery needed")
            return True
            
        print(f"⚠️  Missing files detected: {missing}")
        print("\n🔧 Attempting recovery...")
        
        recovered = []
        failed = []
        
        for filename in missing:
            success, message = self.restore_file(filename)
            if success:
                recovered.append(filename)
                print(f"  ✅ {filename}: {message}")
            else:
                failed.append(filename)
                print(f"  ❌ {filename}: {message}")
        
        # If individual restores failed, try archive restore
        if failed:
            print("\n🗃️  Attempting full archive restoration...")
            success, message = self.restore_from_archive()
            if success:
                print(f"  ✅ {message}")
            else:
                print(f"  ❌ {message}")
        
        print(f"\n📊 Recovery Summary:")
        print(f"   ✅ Recovered: {len(recovered)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if not failed:
            print("🎉 Emergency recovery completed successfully!")
        else:
            print("⚠️  Some files could not be recovered")
            
        return len(failed) == 0
    
    def log_recovery(self, message):
        """Log recovery operations"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.recovery_log, 'a') as f:
            f.write(log_entry)

if __name__ == "__main__":
    recovery = EmergencyRecovery()
    recovery.emergency_restore()