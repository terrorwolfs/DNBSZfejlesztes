from datetime import datetime
from . import db
from sqlalchemy.orm import validates
from enum import Enum

class UserRole(Enum):
    GUEST = 'GUEST'
    RECEPTIONIST = 'RECEPTIONIST'
    ADMIN = 'ADMIN'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    role = db.Column(db.Enum(UserRole), default=UserRole.GUEST, nullable=False)
    bookings = db.relationship('Booking', backref='guest', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    amenities = db.Column(db.JSON)
    status = db.Column(db.String(20), default='available')
    floor = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='room', lazy='dynamic')
    maintenance_records = db.relationship('Maintenance', backref='room', lazy='dynamic')

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.capacity}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')
    total_price = db.Column(db.Float, nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    special_requests = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    extra_services = db.relationship('ExtraService', backref='booking', lazy='dynamic')

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
        return f"Booking('{self.start_date}', '{self.end_date}', '{self.guest.username}', '{self.room.room_number}')"

class ExtraService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    service_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f"ExtraService('{self.name}', '{self.price}')"

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')
    maintenance_type = db.Column(db.String(50))
    technician = db.Column(db.String(100))

    def __repr__(self):
        return f"Maintenance(Room {self.room.room_number}, '{self.status}')"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))

    def __repr__(self):
        return f"Invoice(Booking {self.booking_id}, Amount: {self.amount})"
