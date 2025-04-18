from datetime import datetime
from multiprocessing import set_start_method
from sqlalchemy import desc
from WebApp import db
from sqlalchemy.orm import validates

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='guest', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(20), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy=True)

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.room_type}', '{self.price_per_night}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    total_price = db.Column(db.Float, nullable=False)

    @validates('start_date', 'end_date')
    def validate_dates(self, key, date):
        if key == 'end_date' and date <= self.start_date:
            raise ValueError('End date must be after start date')
        return date

    @validates('status')
    def validate_status(self, key, status):
        if status not in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
            raise ValueError('Invalid booking status')
        return status

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
            raise ValueError('Invalid booking status')
        return status
    
    def __repr__(self):
        return f"Invoice('{self.id}', '{self.amount}', '{self.status}', {self.payment_date})"

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_method = db.Column(db.DateTime)
    end_method = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    maintenance_type = db.Column(db.String(50), nullable=False)
    technician = db.Column(db.String(100), nullable=False)

    @validates('start_method', 'end_method')
    def validate_dates(self, key, date):
        if key == 'end_method' and date <= self.start_method:
            raise ValueError('End date must be after start date')
        return date

    @validates('status')
    def validate_status(self, key, status):
        if status not in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
            raise ValueError('Invalid booking status')
        return status

    def __repr__(self):
        return f"Maintenance('{self.id}', '{self.room_id}', '{self.start_method}-{self.end_method}', '{self.status}', '{self.maintenance_type}')"

class Extra_Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    service_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
            raise ValueError('Invalid booking status')
        return status

    def __repr__(self):
        return f"Extra_Service('{self.id}', '{self.name}', '{self.price}', '{self.service_date}', '{self.status}')"
