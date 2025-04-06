from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField, IntegerField, SelectField, FloatField, RadioField, DateTimeField, TimeField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange, URL
from datetime import datetime, timedelta
from WebApp.models import User, ExtraService, Room, Booking

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone = StringField('Phone Number')
    address = TextAreaField('Address')
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ProfileUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    address = TextAreaField('Address')
    submit = SubmitField('Update')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class BookingForm(FlaskForm):
    start_date = StringField('Check-in Date (YYYY-MM-DD)', validators=[DataRequired()])
    end_date = StringField('Check-out Date (YYYY-MM-DD)', validators=[DataRequired()])
    submit = SubmitField('Book Room')

    def validate_start_date(self, start_date):
        try:
            date = datetime.strptime(start_date.data, '%Y-%m-%d')
            if date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                raise ValidationError('Start date cannot be in the past')
        except ValueError:
            raise ValidationError('Invalid date format. Please use YYYY-MM-DD')

class RoomManagementForm(FlaskForm):
    room_number = IntegerField('Room Number', validators=[DataRequired()])
    room_type = StringField('Room Type', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    price_per_night = FloatField('Price per Night', validators=[DataRequired()])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[('Available', 'Available'), ('Maintenance', 'Maintenance'), ('Cleaning', 'Cleaning')])
    amenities = TextAreaField('Amenities (comma separated)', validators=[Optional()])
    image_url = StringField('Image URL', validators=[URL()])
    is_available_flag = BooleanField('Available for Booking')
    submit = SubmitField('Save Room')

class ExtraServiceForm(FlaskForm):
    service = SelectField('Service', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=1)
    submit = SubmitField('Add Service')
    
    def __init__(self, *args, **kwargs):
        super(ExtraServiceForm, self).__init__(*args, **kwargs)
        self.service.choices = [(s.id, f"{s.name} - ${s.price}") for s in ExtraService.query.all()]

class BookingStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class CheckInForm(FlaskForm):
    room_key_issued = BooleanField('Room Key Issued')
    special_requests = TextAreaField('Special Requests')
    id_verified = BooleanField('ID Verified')
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer')
    ])
    submit = SubmitField('Complete Check-In')

class CheckOutForm(FlaskForm):
    check_out_time = DateTimeField('Check-out Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    room_condition = SelectField('Room Condition', choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('needs_cleaning', 'Needs Cleaning'),
        ('damaged', 'Damaged')
    ])
    key_returned = BooleanField('Room Key Returned')
    submit = SubmitField('Complete Check-Out')

class InvoiceForm(FlaskForm):
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer')
    ])
    additional_charges = FloatField('Additional Charges', default=0.0)
    discount = FloatField('Discount', default=0.0)
    notes = TextAreaField('Notes')
    submit = SubmitField('Generate Invoice')

class BookingManagementForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Pending', 'Pending'), 
        ('Confirmed', 'Confirmed'), 
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    start_date = StringField('Check-in Date (YYYY-MM-DD)', validators=[DataRequired()])
    end_date = StringField('Check-out Date (YYYY-MM-DD)', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Update Booking')
