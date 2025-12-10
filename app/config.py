import os

class Config:
    # Get the APP_SECRET_KEY from environment variables (.env)
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')

    # Get the Database URL from environment variables (.env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Disable SQLAlchemy modification tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
