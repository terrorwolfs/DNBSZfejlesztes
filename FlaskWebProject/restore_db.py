#!/usr/bin/env python
"""
Utility script to restore the database from a backup
"""
import os
import sys
import shutil
import pathlib
from glob import glob

def restore_database():
    """Restore the database from a backup"""
    # Get list of available backups
    backup_dir = pathlib.Path('backups')
    
    if not backup_dir.exists() or not os.listdir(backup_dir):
        print("Error: No backups found in the backups directory")
        return 1
    
    # List all backup files
    backup_files = sorted(glob(str(backup_dir / "site_db_backup_*.db")), reverse=True)
    
    if not backup_files:
        print("Error: No backup files found matching the expected pattern")
        return 1
    
    # Show available backups
    print("Available backups:")
    for i, backup in enumerate(backup_files):
        filename = os.path.basename(backup)
        print(f"{i+1}. {filename}")
    
    # Ask user to select a backup
    try:
        selection = int(input("\nEnter the number of the backup to restore (or 0 to cancel): "))
        if selection == 0:
            print("Restore cancelled")
            return 0
        if selection < 1 or selection > len(backup_files):
            print("Invalid selection")
            return 1
        
        selected_backup = backup_files[selection-1]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return 1
    
    # Destination database path
    db_path = pathlib.Path('instance/site.db')
    
    # Backup current database if it exists
    if db_path.exists():
        current_backup = pathlib.Path('instance/site.db.before_restore')
        try:
            shutil.copy2(db_path, current_backup)
            print(f"Current database backed up to {current_backup}")
        except Exception as e:
            print(f"Warning: Could not backup current database: {e}")
    
    try:
        # Copy the backup file to the database location
        shutil.copy2(selected_backup, db_path)
        print(f"Database restored successfully from {os.path.basename(selected_backup)}")
        return 0
    except Exception as e:
        print(f"Error restoring database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(restore_database())
