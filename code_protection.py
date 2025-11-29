"""
NXTRIX 3.0 Code Protection System
Comprehensive protection for your 7,730+ line enterprise CRM codebase
"""

import os
import hashlib
import json
import time
import sqlite3
from datetime import datetime
from pathlib import Path
import zipfile
import shutil

class CodeProtectionSystem:
    def __init__(self):
        self.protected_files = [
            'nxtrix_saas_app.py',
            'enhanced_crm.py',
            'nxtrix_billing_integrated.py',
            'nxtrix_main_app.py',
            'nxtrix_saas_app_billing.py',
            'trial_billing_manager.py',
            'signup_with_billing.py',
            'auth_system.py',
            'requirements.txt',
            'Procfile',
            '.env.example'
        ]
        self.backup_dir = Path("BACKUPS")
        self.archive_dir = Path("ARCHIVE")
        self.protection_log = "protection_log.db"
        
        # Ensure backup directories exist
        self.backup_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        self.init_protection_database()
    
    def init_protection_database(self):
        """Initialize protection tracking database"""
        conn = sqlite3.connect(self.protection_log)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_checksums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                checksum TEXT NOT NULL,
                file_size INTEGER,
                line_count INTEGER,
                backup_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS protection_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                filename TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_file_hash(self, filepath):
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.log_event("ERROR", filepath, f"Failed to hash file: {e}")
            return None
    
    def count_lines(self, filepath):
        """Count lines in file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for line in f)
        except:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return sum(1 for line in f)
            except:
                return 0
    
    def create_backup(self, filename):
        """Create timestamped backup of file"""
        if not os.path.exists(filename):
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(filename).stem}_{timestamp}{Path(filename).suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(filename, backup_path)
            
            # Log backup
            file_hash = self.calculate_file_hash(filename)
            file_size = os.path.getsize(filename)
            line_count = self.count_lines(filename)
            
            conn = sqlite3.connect(self.protection_log)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO file_checksums (filename, checksum, file_size, line_count, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, file_hash, file_size, line_count, f"Backup: {backup_name}"))
            conn.commit()
            conn.close()
            
            self.log_event("BACKUP_CREATED", filename, f"Backup saved as {backup_name}")
            return True
        except Exception as e:
            self.log_event("BACKUP_FAILED", filename, f"Failed to create backup: {e}")
            return False
    
    def create_complete_archive(self):
        """Create complete archive of all protected files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"NXTRIX_COMPLETE_BACKUP_{timestamp}.zip"
        archive_path = self.archive_dir / archive_name
        
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in self.protected_files:
                    if os.path.exists(filename):
                        zipf.write(filename, filename)
                        print(f"✅ Added {filename} to archive")
                
                # Add protection log
                if os.path.exists(self.protection_log):
                    zipf.write(self.protection_log, self.protection_log)
            
            self.log_event("ARCHIVE_CREATED", "ALL_FILES", f"Complete archive: {archive_name}")
            print(f"🎉 Complete archive created: {archive_path}")
            return str(archive_path)
        except Exception as e:
            self.log_event("ARCHIVE_FAILED", "ALL_FILES", f"Failed to create archive: {e}")
            return None
    
    def verify_file_integrity(self, filename):
        """Verify file hasn't been tampered with"""
        if not os.path.exists(filename):
            return False, "File does not exist"
        
        current_hash = self.calculate_file_hash(filename)
        if not current_hash:
            return False, "Could not calculate hash"
        
        # Get latest known hash
        conn = sqlite3.connect(self.protection_log)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT checksum, line_count, file_size FROM file_checksums 
            WHERE filename = ? ORDER BY backup_created DESC LIMIT 1
        ''', (filename,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return True, "No previous hash found - first verification"
        
        stored_hash, stored_lines, stored_size = result
        current_size = os.path.getsize(filename)
        current_lines = self.count_lines(filename)
        
        if current_hash != stored_hash:
            change_details = f"Size: {stored_size}→{current_size}, Lines: {stored_lines}→{current_lines}"
            self.log_event("FILE_CHANGED", filename, f"Hash mismatch detected. {change_details}")
            return False, f"File has been modified! {change_details}"
        
        return True, "File integrity verified"
    
    def protect_all_files(self):
        """Comprehensive protection for all files"""
        print("🛡️  NXTRIX 3.0 Code Protection System")
        print("=" * 50)
        
        total_lines = 0
        protected_count = 0
        
        for filename in self.protected_files:
            if os.path.exists(filename):
                print(f"\n🔒 Protecting: {filename}")
                
                # Create backup
                if self.create_backup(filename):
                    print(f"  ✅ Backup created")
                else:
                    print(f"  ❌ Backup failed")
                
                # Verify integrity
                is_valid, message = self.verify_file_integrity(filename)
                if is_valid:
                    print(f"  ✅ Integrity verified")
                else:
                    print(f"  ⚠️  {message}")
                
                # Count lines
                lines = self.count_lines(filename)
                total_lines += lines
                protected_count += 1
                
                print(f"  📊 Lines: {lines:,}")
            else:
                print(f"⚠️  File not found: {filename}")
        
        print(f"\n" + "=" * 50)
        print(f"🎯 PROTECTION SUMMARY:")
        print(f"   📁 Files Protected: {protected_count}")
        print(f"   📝 Total Lines: {total_lines:,}")
        print(f"   🗓️  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create complete archive
        archive_path = self.create_complete_archive()
        if archive_path:
            print(f"   📦 Archive: {Path(archive_path).name}")
        
        self.log_event("PROTECTION_COMPLETE", "SYSTEM", f"Protected {protected_count} files, {total_lines:,} total lines")
        
        return {
            "files_protected": protected_count,
            "total_lines": total_lines,
            "archive_created": bool(archive_path),
            "archive_path": archive_path
        }
    
    def log_event(self, event_type, filename, details):
        """Log protection events"""
        conn = sqlite3.connect(self.protection_log)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO protection_events (event_type, filename, details)
            VALUES (?, ?, ?)
        ''', (event_type, filename, details))
        conn.commit()
        conn.close()
    
    def get_protection_report(self):
        """Generate protection status report"""
        conn = sqlite3.connect(self.protection_log)
        
        # Get recent events
        events = pd.read_sql('''
            SELECT * FROM protection_events 
            ORDER BY timestamp DESC LIMIT 10
        ''', conn)
        
        # Get file status
        files = pd.read_sql('''
            SELECT filename, checksum, line_count, backup_created 
            FROM file_checksums 
            ORDER BY backup_created DESC
        ''', conn)
        
        conn.close()
        
        return {
            "recent_events": events,
            "file_status": files,
            "total_backups": len(files),
            "last_backup": files['backup_created'].max() if not files.empty else None
        }

def main():
    """Run code protection system"""
    protection = CodeProtectionSystem()
    result = protection.protect_all_files()
    
    print(f"\n🚀 NXTRIX 3.0 codebase is now PROTECTED!")
    print(f"💎 Your {result['total_lines']:,} lines of code are secure!")

if __name__ == "__main__":
    main()