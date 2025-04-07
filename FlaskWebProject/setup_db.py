import os
import sys
import pathlib
import shutil
from flask import Flask
from WebApp import db, create_app
from WebApp.models import User, Room, Booking, ExtraService, CheckIn, Invoice, InvoiceItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def setup_database():
    """Set up the database with initial data"""
    print("Setting up the database...")
    
    # Create instance directory if it doesn't exist
    instance_path = pathlib.Path('instance')
    instance_path.mkdir(exist_ok=True)

    # Check if site.db exists and rename it to backup if it does
    db_path = instance_path / 'site.db'
    if db_path.exists():
        backup_path = instance_path / 'site.db.backup'
        print(f"Existing database found. Creating backup at {backup_path}")
        try:
            shutil.copy2(db_path, backup_path)
            # Remove the existing database to create a fresh one
            os.remove(db_path)
            print("Removed existing database to create a fresh one.")
        except Exception as e:
            print(f"Error backing up database: {e}")
    
    # Create the Flask application
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if we need to seed the database
        if User.query.count() == 0:
            print("Seeding database with initial data...")
            
            # Add admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            
            # Add test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password=generate_password_hash('password123')
            )
            
            # Add sample rooms
            rooms = [
                Room(room_number=101, room_type='Single', price_per_night=100.0, capacity=1, 
                     description='Cozy single room with a view of the garden.',
                     amenities='Wi-Fi, TV, Air conditioning, Mini fridge'),
                Room(room_number=102, room_type='Double', price_per_night=150.0, capacity=2, status='Available',
                     description='Spacious double room with a comfortable queen-sized bed.',
                     amenities='Wi-Fi, TV, Air conditioning, Mini fridge, Coffee maker'),
                Room(room_number=103, room_type='Suite', price_per_night=250.0, capacity=4,
                     description='Luxurious suite with separate living area and bedroom.',
                     amenities='Wi-Fi, TV, Air conditioning, Mini bar, Coffee maker, Jacuzzi')
            ]
            
            # Add sample extra services
            services = [
                ExtraService(name='Breakfast', price=15.0, 
                             description='Continental breakfast served in your room or in our dining area.'),
                ExtraService(name='Spa Treatment', price=80.0,
                             description='60-minute relaxing massage or facial treatment.'),
                ExtraService(name='Airport Transfer', price=50.0,
                             description='Private transportation to or from the airport.'),
                ExtraService(name='Room Cleaning', price=20.0,
                             description='Additional room cleaning service during your stay.')
            ]
            
            db.session.add(admin)
            db.session.add(test_user)
            for room in rooms:
                db.session.add(room)
            for service in services:
                db.session.add(service)
            
            db.session.commit()
            print("Database seeded successfully!")
        else:
            print("Database already contains data, skipping seed.")
        
        print("Database setup complete!")

if __name__ == '__main__':
    setup_database()
