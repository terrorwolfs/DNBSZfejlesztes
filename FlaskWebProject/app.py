import os
import sys
import pathlib
from WebApp import create_app, db, login_manager
from WebApp.models import User, Room, Booking, CheckIn, Invoice, ExtraService, BookingService, InvoiceItem

# Check if instance directory exists
instance_path = pathlib.Path('instance')
instance_path.mkdir(exist_ok=True)

# Check if database exists
db_path = pathlib.Path('instance/site.db')
if not db_path.exists():
    print("Database not found. Please run init_db.py first.")
    print("Example: python init_db.py")
    sys.exit(1)

try:
    app = create_app()
except Exception as e:
    print(f"Error creating Flask application: {e}")
    sys.exit(1)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Room': Room, 'Booking': Booking, 
            'CheckIn': CheckIn, 'Invoice': Invoice, 'ExtraService': ExtraService}
