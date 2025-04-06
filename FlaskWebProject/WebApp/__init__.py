from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import pathlib
from dotenv import load_dotenv
import logging
import sys
from logging.handlers import RotatingFileHandler
from .api_keys import APIKeys

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.login_message_category = 'info'

# Load environment variables
load_dotenv()

def _fk_pragma_on_connect(dbapi_con, con_record):
    """Enable foreign key support on SQLite connections"""
    dbapi_con.execute('pragma foreign_keys=ON')
    # Set journal mode to WAL for better concurrency
    dbapi_con.execute('PRAGMA journal_mode=WAL')
    dbapi_con.execute('PRAGMA busy_timeout=5000')

def create_app(config_name=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # Create instance directory if it doesn't exist
    instance_path = pathlib.Path('instance')
    instance_path.mkdir(exist_ok=True)
    
    # Use absolute path for database URI to avoid path resolution issues
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "site.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Configure SQLite for better performance - after db is initialized
    with app.app_context():
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            event.listen(db.engine, 'connect', _fk_pragma_on_connect)
    
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Setup logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/hotel.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('HotelGuru startup')
    
    # Register user_loader for login_manager
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Validate API keys on startup
    with app.app_context():
        from .api_keys import APIKeys
        app.logger.info('Validating API keys...')
        keys_valid = APIKeys.validate_all_keys()
        if not keys_valid:
            app.logger.warning('Some API keys are missing or invalid. Some features may not work correctly.')
            app.logger.warning('Check your .env file and ensure all required API keys are set.')
            app.logger.warning('Required keys: MAPS_API_KEY, WEATHER_API_KEY, STRIPE_API_KEY, STRIPE_PUBLIC_KEY')
        else:
            app.logger.info('All API keys validated successfully.')
    
    # Register blueprint
    from .routes import routes
    app.register_blueprint(routes)
    
    return app
