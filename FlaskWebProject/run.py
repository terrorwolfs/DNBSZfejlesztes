#!/usr/bin/env python
import os
import sys
import logging
import pathlib
from WebApp import create_app, db, login_manager

def main():
    """Main entry point for running the application with proper setup"""
    print("Setting up the HotelGuru application...")
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create instance directory if it doesn't exist
    instance_path = pathlib.Path('instance')
    instance_path.mkdir(exist_ok=True)
    
    # Check if database exists, if not initialize it
    db_path = pathlib.Path('instance/site.db')
    if not db_path.exists() and not os.environ.get('FLASK_TESTING'):
        print("Database not found. Running database initialization...")
        try:
            from init_db import init_db
            init_db()
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)
    
    # Create the Flask application
    app = create_app()
    
    # Set environment variables for Flask
    os.environ['FLASK_APP'] = 'app.py'
    if os.environ.get('FLASK_ENV') != 'production':
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
    
    # Run the application
    print("\nStarting the application...")
    app.run(debug=True, host='0.0.0.0', port=5555, use_reloader=True)

if __name__ == "__main__":
    main()
