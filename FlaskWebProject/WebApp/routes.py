from flask import render_template, url_for, flash, redirect, request
from WebApp import app, db, bcrypt
from WebApp.forms import RegistrationForm, LoginForm
from WebApp.models import User, Room, Booking
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/index")
def index():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route("/book_room/<int:room_id>", methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        booking = Booking(start_date=start_date, end_date=end_date, guest=current_user, room=room)
        db.session.add(booking)
        db.session.commit()
        flash('Your booking has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('booking.html', title='Book Room', room=room)
