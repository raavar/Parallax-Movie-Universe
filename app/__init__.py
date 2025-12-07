from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

# Initialize extensions
database = SQLAlchemy()
login_manager = LoginManager()

# Set route for login page if user is not authenticated
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'   # Flash message category

def create_app(config_class=Config):
    # Create Flask application instance
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.from_object(config_class)

    # Initialize extensions with the app
    database.init_app(app)
    login_manager.init_app(app)

    # Import and register blueprints
    from app import models, routes

    # Register the user for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Return the Flask application instance
    return app
