from flask import render_template, url_for, flash, redirect, request, Blueprint, session, jsonify, abort
from . import db
from datetime import datetime, timedelta
from WebApp.auth import get_current_user, login_required, admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import RegistrationForm, LoginForm, BookingForm, ProfileUpdateForm, ExtraServiceForm, RoomManagementForm, BookingManagementForm, CheckInForm, CheckOutForm, InvoiceForm, BookingStatusForm
from .models import User, Room, Booking, ExtraService, BookingService, CheckIn, Invoice, InvoiceItem
import uuid

routes = Blueprint('routes', __name__)

# Home and general routes
@routes.route("/")
@routes.route("/index")
def index():
    """Home page showing available rooms"""
    current_user = get_current_user() 
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms, current_user=current_user)

# Authentication routes
@routes.route("/register", methods=['GET', 'POST'])
def register():  
    if 'user_id' in session:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, 
                   password=hashed_password, is_admin=False,
                   phone=form.phone.data, address=form.address.data)
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

# User account routes
@routes.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    user = User.query.get(session['user_id'])
    current_user = get_current_user()
    form = ProfileUpdateForm(original_username=user.username, original_email=user.email)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.address = form.address.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('routes.account'))
    
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.phone.data = user.phone
        form.address.data = user.address
    
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template('account.html', title='My Account', user=user, form=form, bookings=bookings, current_user=current_user)

# Admin routes
@routes.route("/admin")
@admin_required
def admin():
    current_user = get_current_user()
    # Get counts for dashboard
    room_count = Room.query.count()
    booking_count = Booking.query.count()
    user_count = User.query.count()
    users = User.query.all()
    pending_bookings = Booking.query.filter_by(status='Pending').count()
    active_check_ins = CheckIn.query.filter_by(status='Active').count()
    
    return render_template('admin.html', room_count=room_count, booking_count=booking_count, user_count=user_count, users=users, pending_bookings=pending_bookings, active_check_ins=active_check_ins, current_user=current_user)

# Booking routes
@routes.route("/book_room/<int:room_id>", methods=['GET', 'POST']) 
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    current_user = get_current_user()
    form = BookingForm()
    
    if form.validate_on_submit():
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d')
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d') 
        
        # Check if room is available for these dates
        if not room.is_available:
            flash('Room is not available for these dates.', 'error')
            return render_template('booking.html', title='Book a Room', form=form, room=room, current_user=current_user)
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
    return render_template('booking.html', title='Book a Room', form=form, room=room, current_user=current_user)

# Room routes
@routes.route("/rooms")
def rooms():
    """Public view of all rooms, no login required"""
    rooms = Room.query.all()
    return render_template('rooms.html', title='Our Rooms', rooms=rooms)

@routes.route("/room/<int:room_id>")
def room_detail(room_id):
    """Detailed view of a specific room"""
    room = Room.query.get_or_404(room_id)
    return render_template('room_detail.html', title=f'Room {room.room_number}', room=room)

# Booking management routes
@routes.route("/cancel_booking/<int:booking_id>", methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != session['user_id']:
        flash('You can only cancel your own bookings!', 'danger')
        return redirect(url_for('routes.account'))
    
    if not booking.can_cancel():
        flash('Sorry, this booking can no longer be cancelled as it is past the 48-hour cancellation window.', 'danger')
        return redirect(url_for('routes.account'))
    
    booking.status = 'Cancelled'
    db.session.commit()
    flash('Your booking has been cancelled successfully.', 'success')
    return redirect(url_for('routes.account'))

# Services routes
@routes.route("/extra_services", methods=['GET'])
def extra_services():
    """View all available extra services"""
    services = ExtraService.query.all()
    return render_template('extra_services.html', title='Extra Services', services=services)

@routes.route("/request_service/<int:booking_id>", methods=['GET', 'POST'])
@login_required
def request_service(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != session['user_id']:
        flash('You can only request services for your own bookings!', 'danger')
        return redirect(url_for('routes.account'))
    
    form = ExtraServiceForm()
    if form.validate_on_submit():
        service = ExtraService.query.get(form.service.data)
        booking_service = BookingService(
            booking_id=booking.id,
            service_id=service.id,
            quantity=form.quantity.data
        )
        db.session.add(booking_service)
        db.session.commit()
        flash(f'Service "{service.name}" has been added to your booking!', 'success')
        return redirect(url_for('routes.account'))
    
    return render_template('request_service.html', title='Request Extra Service', form=form, booking=booking)

# Room management routes
@routes.route("/admin/rooms")
@admin_required
def manage_rooms():
    """View all rooms with management options"""
    rooms = Room.query.order_by(Room.room_number).all()
    return render_template('manage_rooms.html', title='Manage Rooms', rooms=rooms)

@routes.route("/admin/room/delete/<int:room_id>", methods=['POST'])
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('routes.manage_rooms'))

@routes.route("/admin/room/add", methods=['GET', 'POST'])
@admin_required
def add_room():
    """Add a new room"""
    form = RoomManagementForm()
    
    if form.validate_on_submit():
        room = Room(
            room_number=form.room_number.data,
            room_type=form.room_type.data,
            capacity=form.capacity.data,
            price_per_night=form.price_per_night.data,
            description=form.description.data,
            status=form.status.data,
            amenities=form.amenities.data,
            image_url=form.image_url.data,
            is_available=form.is_available.data
        )
        db.session.add(room)
        db.session.commit()
        flash('Room has been added successfully!', 'success')
        return redirect(url_for('routes.manage_rooms'))
    
    return render_template('room_form.html', title='Add Room', form=form, is_edit=False)

@routes.route("/admin/room/edit/<int:room_id>", methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    """Edit an existing room"""
    room = Room.query.get_or_404(room_id)
    form = RoomManagementForm(obj=room)
    
    if form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        flash('Room has been updated successfully!', 'success')
        return redirect(url_for('routes.manage_rooms'))
    
    return render_template('room_form.html', title='Edit Room', form=form, is_edit=True, room=room)

@routes.route("/admin/room/toggle_availability/<int:room_id>", methods=['POST'])
@admin_required
def toggle_room_availability(room_id):
    """Toggle a room's availability status"""
    room = Room.query.get_or_404(room_id)
    room.is_available = not room.is_available
    db.session.commit()
    flash(f'Room {room.room_number} is now {"available" if room.is_available else "unavailable"} for booking.', 'success')
    return redirect(url_for('routes.manage_rooms'))

# API routes
@routes.route("/api/user_bookings")
@login_required
def user_bookings_api():
    """API endpoint to get user's active bookings for the services page"""
    user_id = session.get('user_id')
    bookings = Booking.query.filter_by(
        user_id=user_id, 
        status='Confirmed'
    ).all()
    
    booking_data = [{
        'id': booking.id,
        'room_number': booking.room.room_number,
        'dates': f"{booking.start_date.strftime('%m/%d')} - {booking.end_date.strftime('%m/%d')}"
    } for booking in bookings]
    
    return jsonify(booking_data)

# Booking management routes
@routes.route("/admin/bookings")
@admin_required
def manage_bookings():
    """View all bookings with management options"""
    bookings = Booking.query.order_by(Booking.start_date.desc()).all()
    current_user = get_current_user()
    return render_template('manage_bookings.html', title='Manage Bookings', bookings=bookings, current_user=current_user)

@routes.route("/admin/booking/delete/<int:booking_id>", methods=['POST'])
@admin_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('routes.manage_bookings'))

@routes.route("/admin/booking/<int:booking_id>", methods=['GET', 'POST'])
@admin_required
def edit_booking(booking_id):
    """Edit an existing booking"""
    booking = Booking.query.get_or_404(booking_id)
    form = BookingManagementForm()
    
    if form.validate_on_submit():
        booking.status = form.status.data
        booking.start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d')
        booking.end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d')
        
        # Recalculate total price if dates changed
        days = (booking.end_date - booking.start_date).days
        booking.total_price = days * booking.room.price_per_night
        
        db.session.commit()
        flash('Booking has been updated successfully!', 'success')
        return redirect(url_for('routes.manage_bookings'))
    
    elif request.method == 'GET':
        form.status.data = booking.status
        form.start_date.data = booking.start_date.strftime('%Y-%m-%d')
        form.end_date.data = booking.end_date.strftime('%Y-%m-%d')
    
    current_user = get_current_user()
    return render_template('manage_booking.html', title='Edit Booking', form=form, booking=booking, current_user=current_user)

@routes.route("/admin/booking/confirm/<int:booking_id>", methods=['POST'])
@admin_required
def confirm_booking(booking_id):
    """Confirm a pending booking"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'Pending':
        booking.status = 'Confirmed'
        db.session.commit()
        flash(f'Booking #{booking.id} has been confirmed!', 'success')
    else:
        flash('Only pending bookings can be confirmed.', 'warning')
    return redirect(url_for('routes.manage_bookings'))

@routes.route("/admin/booking/cancel/<int:booking_id>", methods=['POST'])
@admin_required
def admin_cancel_booking(booking_id):
    """Cancel a booking (admin)"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.status not in ['Completed', 'Cancelled']:
        booking.status = 'Cancelled'
        db.session.commit()
        flash(f'Booking #{booking.id} has been cancelled!', 'success')
    else:
        flash('This booking cannot be cancelled.', 'warning')
    return redirect(url_for('routes.manage_bookings'))

# Check-in/Check-out routes
@routes.route("/admin/checkins")
@admin_required
def manage_checkins():
    """View all check-ins"""
    active_checkins = CheckIn.query.filter_by(status='Active').all()
    completed_checkins = CheckIn.query.filter_by(status='Completed').order_by(CheckIn.check_out_time.desc()).limit(10).all()
    current_user = get_current_user()
    
    # Get confirmed bookings that don't have check-ins yet
    pending_checkins = Booking.query.filter_by(status='Confirmed')\
        .outerjoin(CheckIn)\
        .filter(CheckIn.id == None)\
        .filter(Booking.start_date <= datetime.now())\
        .all()
    
    return render_template('checkin_list.html', title='Manage Check-ins', 
                          active_checkins=active_checkins, 
                          completed_checkins=completed_checkins,
                          pending_checkins=pending_checkins,
                          current_user=current_user)

@routes.route("/admin/checkin/<int:booking_id>", methods=['GET', 'POST'])
@admin_required
def checkin_guest(booking_id):
    """Check in a guest for their booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify booking is confirmed and doesn't already have a check-in
    if booking.status != 'Confirmed':
        flash('Only confirmed bookings can be checked in.', 'warning')
        return redirect(url_for('routes.manage_checkins'))
    
    if booking.check_in:
        flash('This booking already has a check-in record.', 'warning')
        return redirect(url_for('routes.manage_checkins'))
    
    form = CheckInForm()
    
    if form.validate_on_submit():
        checkin = CheckIn(
            booking_id=booking.id,
            user_id=booking.user_id,
            room_key_issued=form.room_key_issued.data,
            special_requests=form.special_requests.data,
            status='Active'
        )
        db.session.add(checkin)
        db.session.commit()
        flash(f'Check-in completed for booking #{booking.id}!', 'success')
        return redirect(url_for('routes.manage_checkins'))
    
    current_user = get_current_user()
    return render_template('checkin.html', title='Check-in Guest', form=form, booking=booking, current_user=current_user)

@routes.route("/admin/checkout/<int:checkin_id>", methods=['GET', 'POST'])
@admin_required
def checkout_guest(checkin_id):
    """Check out a guest"""
    checkin = CheckIn.query.get_or_404(checkin_id)
    
    # Verify check-in is active
    if checkin.status != 'Active':
        flash('This check-in is already completed.', 'warning')
        return redirect(url_for('routes.manage_checkins'))
    
    form = CheckOutForm()
    
    if form.validate_on_submit():
        checkin.check_out_time = form.check_out_time.data
        checkin.status = 'Completed'
        
        # Update booking status
        booking = checkin.booking
        booking.status = 'Completed'
        
        db.session.commit()
        flash(f'Check-out completed for booking #{booking.id}!', 'success')
        
        # Redirect to invoice creation
        return redirect(url_for('routes.create_invoice', booking_id=booking.id))
    
    elif request.method == 'GET':
        form.check_out_time.data = datetime.now()
    
    current_user = get_current_user()
    return render_template('checkout.html', title='Check-out Guest', form=form, checkin=checkin, current_user=current_user)

# Invoice routes
@routes.route("/admin/invoices")
@admin_required
def manage_invoices():
    """View all invoices"""
    invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
    current_user = get_current_user()
    return render_template('manage_invoices.html', title='Manage Invoices', invoices=invoices, current_user=current_user)

@routes.route("/admin/invoice/delete/<int:invoice_id>", methods=['POST'])
@admin_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    return redirect(url_for('routes.manage_invoices'))

@routes.route("/admin/invoice/create/<int:booking_id>", methods=['GET', 'POST'])
@admin_required
def create_invoice(booking_id):
    """Create an invoice for a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if invoice already exists
    if booking.invoice:
        flash('An invoice already exists for this booking.', 'info')
        return redirect(url_for('routes.view_invoice', invoice_id=booking.invoice.id))
        
    form = InvoiceForm()
    
    if form.validate_on_submit():
        # Calculate due date (7 days from now)
        due_date = datetime.now() + timedelta(days=7)
        
        # Calculate total amount
        room_charge = booking.total_price
        additional_charges = form.additional_charges.data
        discount = form.discount.data if form.discount.data else 0
        total_amount = room_charge + additional_charges - discount
        
        # Create invoice
        invoice = Invoice(
            booking_id=booking.id,
            due_date=due_date,
            total_amount=total_amount,
            payment_method=form.payment_method.data,
            notes=form.notes.data
        )
        db.session.add(invoice)
        
        # Create invoice items
        # Room charge
        room_item = InvoiceItem(
            invoice=invoice,
            description=f"Room {booking.room.room_number} - {booking.start_date.strftime('%Y-%m-%d')} to {booking.end_date.strftime('%Y-%m-%d')}",
            quantity=(booking.end_date - booking.start_date).days,
            unit_price=booking.room.price_per_night
        )
        db.session.add(room_item)
        
        # Add extra services
        for service in booking.services:
            service_item = InvoiceItem(
                invoice=invoice,
                description=f"Extra Service: {service.service.name}",
                quantity=service.quantity,
                unit_price=service.service.price
            )
            db.session.add(service_item)
        
        # Add additional charges if any
        if additional_charges > 0:
            additional_item = InvoiceItem(
                invoice=invoice,
                description=f"Additional charges: {form.notes.data or 'N/A'}",
                quantity=1,
                unit_price=additional_charges
            )
            db.session.add(additional_item)
        
        db.session.commit()
        flash('Invoice has been created successfully!', 'success')
        return redirect(url_for('routes.view_invoice', invoice_id=invoice.id))
    
    current_user = get_current_user()
    return render_template('create_invoice.html', title='Create Invoice', form=form, booking=booking, current_user=current_user)

@routes.route("/admin/invoice/<int:invoice_id>")
@admin_required
def view_invoice(invoice_id):
    """View an invoice"""
    invoice = Invoice.query.get_or_404(invoice_id)
    current_user = get_current_user()
    return render_template('invoice.html', title='View Invoice', invoice=invoice, current_user=current_user)

@routes.route("/admin/invoice/mark_paid/<int:invoice_id>", methods=['POST'])
@admin_required
def mark_invoice_paid(invoice_id):
    """Mark an invoice as paid"""
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.is_paid = True
    invoice.paid_amount = invoice.total_amount
    invoice.payment_date = datetime.now()
    db.session.commit()
    flash(f'Invoice #{invoice.id} has been marked as paid!', 'success')
    return redirect(url_for('routes.view_invoice', invoice_id=invoice.id))

@routes.route("/invoice/<int:public_id>")
def public_invoice(public_id):
    """Public view of an invoice (accessible without login)"""
    invoice = Invoice.query.filter_by(public_id=public_id).first_or_404()
    return render_template('public_invoice.html', title='Invoice', invoice=invoice)

@routes.route("/admin/room_status")
@admin_required
def room_status_dashboard():
    """Dashboard showing current status of all rooms"""
    rooms = Room.query.order_by(Room.room_number).all()
    current_user = get_current_user()
    return render_template('room_status.html', title='Room Status', rooms=rooms, current_user=current_user)
