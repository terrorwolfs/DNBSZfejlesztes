from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, BookingForm
from models import User, Room, Booking
from auth import login_required, admin_required

routes = Blueprint('routes', __name__)

@routes.route("/")
@routes.route("/index")
def index():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)

@routes.route("/register", methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@routes.route("/login", methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@routes.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('routes.index'))

@routes.route("/account")
@login_required
def account():
    user = User.query.get(session['user_id'])
    return render_template('account.html', title='Account', user=user)

@routes.route("/admin")
@admin_required
def admin():
    rooms = Room.query.all()
    bookings = Booking.query.all()
    users = User.query.all()
    return render_template('admin.html', rooms=rooms, bookings=bookings, users=users)

@routes.route("/book_room/<int:room_id>", methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = BookingForm()
    
    if form.validate_on_submit():
        # Convert string dates to datetime objects
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d')
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d')
        
        # Check if room is available for these dates
        existing_booking = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.status != 'Cancelled',
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).first()
        
        if existing_booking:
            flash('Room is not available for these dates.', 'error')
            return render_template('booking.html', form=form, room=room)
        
        # Calculate total price
        days = (end_date - start_date).days
        total_price = days * room.price_per_night
        
        booking = Booking(
            start_date=start_date,
            end_date=end_date,
            user_id=session['user_id'],
            room_id=room.id,
            status='Pending',
            total_price=total_price
        )
        
        db.session.add(booking)
        db.session.commit()
        flash('Your booking has been created!', 'success')
        return redirect(url_for('routes.index'))
    return render_template('booking.html', form=form, room=room)
