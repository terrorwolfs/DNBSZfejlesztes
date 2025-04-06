#!/usr/bin/env python
"""
Utility script to check database health and integrity
"""
import os
import sys
import sqlite3
import pathlib
from WebApp import create_app, db
from WebApp.models import User, Room, Booking, CheckIn, Invoice, ExtraService, BookingService, InvoiceItem

def check_database():
    """Check database health and integrity"""
    print("Checking database health...")
    
    # Check if database file exists
    db_path = pathlib.Path('instance/site.db')
    if not db_path.exists():
        print("Error: Database file not found at instance/site.db")
        return 1
    
    # Check if database file is valid SQLite database
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] != "ok":
            print(f"SQLite integrity check failed: {result[0]}")
            return 1
        print("SQLite integrity check: OK")
        
        # Check foreign key constraints
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            print(f"Foreign key constraint violations found: {len(fk_violations)}")
            for violation in fk_violations:
                print(f"  Table: {violation[0]}, Row ID: {violation[1]}, Parent: {violation[2]}, Foreign Key: {violation[3]}")
            return 1
        print("Foreign key constraints: OK")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return 1
    
    # Check ORM models
    try:
        app = create_app()
        with app.app_context():
            # Check User table
            user_count = User.query.count()
            print(f"Users: {user_count}")
            
            # Check Room table
            room_count = Room.query.count()
            print(f"Rooms: {room_count}")
            
            # Check Booking table
            booking_count = Booking.query.count()
            print(f"Bookings: {booking_count}")
            
            # Check CheckIn table
            checkin_count = CheckIn.query.count()
            print(f"Check-ins: {checkin_count}")
            
            # Check Invoice table
            invoice_count = Invoice.query.count()
            print(f"Invoices: {invoice_count}")
            
            # Check ExtraService table
            service_count = ExtraService.query.count()
            print(f"Extra Services: {service_count}")
            
            # Check BookingService table
            booking_service_count = BookingService.query.count()
            print(f"Booking Services: {booking_service_count}")
            
            # Check InvoiceItem table
            invoice_item_count = InvoiceItem.query.count()
            print(f"Invoice Items: {invoice_item_count}")
            
            print("\nDatabase check completed successfully!")
    except Exception as e:
        print(f"Error checking ORM models: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(check_database())
