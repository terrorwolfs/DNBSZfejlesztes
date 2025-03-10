from WebApp import create_app, db
from WebApp.models import User, Room, Booking
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Add admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )

        # Add sample rooms
        rooms = [
            Room(room_number='101', room_type='Single', price_per_night=100.0, capacity=1),
            Room(room_number='102', room_type='Double', price_per_night=150.0, capacity=2),
            Room(room_number='103', room_type='Suite', price_per_night=250.0, capacity=4)
        ]

        # Add to session and commit
        db.session.add(admin)
        for room in rooms:
            db.session.add(room)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
