from app import create_app
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

app = create_app()

if __name__ == "__main__":
    create_app(config_name=Config).run('localhost', 5555)
    app.run(debug=True)
