import os
import sys
import pathlib
import logging
from WebApp import create_app, db, login_manager
from WebApp.models import User, Room, Booking, CheckIn, Invoice, ExtraService, BookingService, InvoiceItem

# Check if instance directory exists
instance_path = pathlib.Path('instance')
instance_path = instance_path.mkdir(exist_ok=True)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Check if database exists
db_path = pathlib.Path('instance/site.db')
if not db_path.exists() and not os.environ.get('FLASK_TESTING'):
    print("Database not found. Running database initialization...")
    try:
        from init_db import init_db
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)

try:
    app = create_app()
except Exception as e:
    print(f"Error creating Flask application: {e}")
    sys.exit(1)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Room': Room, 'Booking': Booking, 
            'CheckIn': CheckIn, 'Invoice': Invoice, 'ExtraService': ExtraService, 'BookingService': BookingService}
