from datetime import datetime
from . import db
from sqlalchemy.orm import validates

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy='dynamic')

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.capacity}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    @validates('start_date', 'end_date')
    def validate_dates(self, key, date):
        if key == 'start_date':
            if date > self.end_date:
                raise ValueError('Start date must be before end date')
        if key == 'end_date':
            if date < self.start_date:
                raise ValueError('End date must be after start date')
        return date

    def __repr__(self):
        return f"Booking('{self.start_date}', '{self.end_date}', '{self.customer.username}', '{self.room.room_number}')"
