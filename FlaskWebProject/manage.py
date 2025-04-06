from flask.cli import FlaskGroup
from WebApp import create_app, db
from WebApp.models import User, Room, Booking
from flask_migrate import init, migrate, upgrade

cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("init_db")
def init_db():
    """Initialize the database with migrations"""
    init()
    migrate()
    upgrade()

@cli.command("seed_db")
def seed_db():
    # Add some sample rooms
    rooms = [
        Room(room_number="101", room_type="Single", price_per_night=100.0, capacity=1),
        Room(room_number="102", room_type="Double", price_per_night=150.0, capacity=2),
        Room(room_number="103", room_type="Suite", price_per_night=250.0, capacity=4)
    ]
    db.session.bulk_save_objects(rooms)
    db.session.commit()

if __name__ == "__main__":
    cli()
