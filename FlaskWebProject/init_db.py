from WebApp import create_app, db
from WebApp.models import User, Room, Booking, ExtraService, Maintenance, Invoice
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Create admin user
        admin = User(
            username='admin',
            email='admin@hotel.com',
            password=generate_password_hash('admin123'),
            role='ADMIN',
            phone='1234567890',
            address='Hotel Address'
        )

        # Create sample rooms
        rooms = [
            Room(
                room_number=101,
                room_type='Standard',
                capacity=2,
                price_per_night=100.0,
                description='Comfortable standard room',
                amenities={'wifi': True, 'tv': True, 'minibar': False},
                floor=1
            ),
            Room(
                room_number=201,
                room_type='Deluxe',
                capacity=3,
                price_per_night=150.0,
                description='Spacious deluxe room',
                amenities={'wifi': True, 'tv': True, 'minibar': True},
                floor=2
            ),
            Room(
                room_number=301,
                room_type='Suite',
                capacity=4,
                price_per_night=250.0,
                description='Luxury suite',
                amenities={'wifi': True, 'tv': True, 'minibar': True, 'jacuzzi': True},
                floor=3
            )
        ]

        # Add sample data to database
        db.session.add(admin)
        db.session.add_all(rooms)
        db.session.commit()

if __name__ == '__main__':
    init_db()
