from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

# Create Flask application instance
app = Flask(__name__)

# Load configuration from Config class
app.config.from_object(Config)

# Initialize extensions
database = SQLAlchemy(app)
login_manager = LoginManager(app)

# Set route for login page if user is not authenticated
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'   # Flash message category

# Register the user for Flask-Login
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes to register them with the application
from app import routes
