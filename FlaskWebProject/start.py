#!/usr/bin/env python
import os
import sys
import pathlib
import subprocess

def main():
    """Main entry point for setting up and running the application"""
    print("Starting HotelGuru application setup...")
    
    # Create instance directory if it doesn't exist
    instance_path = pathlib.Path('instance')
    instance_path.mkdir(exist_ok=True)
    
    # Check if database exists, if not initialize it
    db_path = pathlib.Path('instance/site.db')
    if not db_path.exists():
        print("Database not found. Running database initialization...")
        try:
            subprocess.run([sys.executable, 'init_db.py'], check=True)
        except subprocess.CalledProcessError:
            print("Error initializing database. Please check the logs.")
            sys.exit(1)
    
    # Set environment variables for Flask
    os.environ['FLASK_APP'] = 'app.py'
    if os.environ.get('FLASK_ENV') != 'production':
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
    
    # Run the application
    print("\nStarting the application...")
    from WebApp import create_app
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5555)

if __name__ == "__main__":
    main()
