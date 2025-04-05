#!/usr/bin/env python
import os
import sys
import pathlib
from WebApp import create_app, db

def main():
    """Main entry point for running the application with proper setup"""
    print("Setting up the HotelGuru application...")
    
    # Create instance directory if it doesn't exist
    instance_path = pathlib.Path('instance')
    instance_path.mkdir(exist_ok=True)
    
    # Check if database exists, if not initialize it
    db_path = pathlib.Path('instance/site.db')
    if not db_path.exists():
        print("Database not found. Please run init_db.py or setup_db.py first.")
        print("Example: python init_db.py")
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
    app.run(debug=True, host='0.0.0.0', port=5555)

if __name__ == "__main__":
    main()
