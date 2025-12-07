import os

class Config:
    # Get the APP_SECRET_KEY from environment variables (.env)
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')

    # Get the Database URL from environment variables (.env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Disable SQLAlchemy modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
