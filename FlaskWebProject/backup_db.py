#!/usr/bin/env python
"""
Utility script to backup the database
"""
import os
import sys
import shutil
import datetime
import pathlib

def backup_database():
    """Create a backup of the database"""
    # Get the current date and time for the backup filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # Create backups directory if it doesn't exist
    backup_dir = pathlib.Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Source database path
    db_path = pathlib.Path('instance/site.db')
    
    if not db_path.exists():
        print("Error: Database file not found at instance/site.db")
        return 1
    
    # Destination backup path
    backup_path = backup_dir / f"site_db_backup_{timestamp}.db"
    
    try:
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        print(f"Database backup created successfully: {backup_path}")
        return 0
    except Exception as e:
        print(f"Error creating database backup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(backup_database())
