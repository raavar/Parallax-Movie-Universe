from itsdangerous import URLSafeTimedSerializer
from app import app

def generate_confirmation_token(email):
    # Create a serializer instance using the application's secret key
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    # Generate a secure token based on the email address and a specific salt
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    # Create a serializer instance to attempt decoding the token
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        # Attempt to retrieve the email from the token ensuring it has not expired
        # The expiration default is set to 3600 seconds which equals one hour
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
    except Exception:
        # Return False if the token is invalid, tampered with, or expired
        return False
    # Return the extracted email address if the token is valid
    return email
