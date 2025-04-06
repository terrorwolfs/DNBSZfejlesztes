from datetime import datetime
from flask_login import UserMixin, current_user
from WebApp import db
import uuid

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')
    check_ins = db.relationship('CheckIn', backref='guest', lazy='dynamic')
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def get_id(self):
        return str(self.id)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy='dynamic', cascade="all, delete-orphan")
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Available')  # Available, Maintenance, Cleaning
    amenities = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True, default='default_room.jpg')
    is_available_flag = db.Column(db.Boolean, default=True)

    def __init__(self, **kwargs):
        super(Room, self).__init__(**kwargs)

    def is_available(self, start_date, end_date):
        """Check if room is available for the given date range"""
        # First check if room is marked as available
        if not self.is_available_flag:
            return False
        overlapping_bookings = Booking.query.filter(
            Booking.room_id == self.id,
            Booking.status.in_(['Pending', 'Confirmed', 'Active']),
            Booking.start_date < end_date, Booking.end_date > start_date).count()
        return overlapping_bookings == 0

    def current_status(self):
        """Return the current status of the room considering bookings and maintenance"""
        if not self.is_available_flag:
            return "Unavailable"
        if self.status != 'Available':
            return self.status
        return "Available"

    def calculate_nights(self, start_date, end_date):
        """Calculate number of nights for a given date range"""
        return (end_date - start_date).days

    def __repr__(self):
        return f"Room('{self.room_number}', '{self.room_type}', '${self.price_per_night}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_price = db.Column(db.Float, nullable=True)
    check_in = db.relationship('CheckIn', backref='booking', uselist=False, cascade="all, delete-orphan")
    invoice = db.relationship('Invoice', backref='booking', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Booking('{self.start_date}', '{self.end_date}', '{self.status}')"

    def can_cancel(self):
        """Check if booking can be cancelled (within 48 hours of creation)"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.total_seconds() < 48 * 3600  # 48 hours in seconds

    def calculate_nights(self, start_date=None, end_date=None):
        """Calculate number of nights for this booking"""
        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date
        return (end_date - start_date).days

class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    room_key_issued = db.Column(db.Boolean, default=False)
    id_verified = db.Column(db.Boolean, default=False)
    special_requests = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Completed

    def __repr__(self):
        return f"CheckIn('{self.check_in_time}', '{self.status}')"

class Invoice(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    invoice_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, nullable=True, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    invoice_items = db.relationship('InvoiceItem', backref='invoice', lazy=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Invoice('{self.invoice_date}', '${self.total_amount}', Paid: {self.is_paid})"

class ExtraService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"ExtraService('{self.name}', '${self.price}')"

class BookingService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('extra_service.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    booking = db.relationship('Booking', backref=db.backref('services', lazy=True))
    service = db.relationship('ExtraService')

    @property
    def total_price(self):
        return self.service.price * self.quantity

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)

    @property
    def total_price(self):
        return self.quantity * self.unit_price
