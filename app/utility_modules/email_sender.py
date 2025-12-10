from flask_mail import Message
from flask import url_for, render_template_string
from app import mail

def send_confirmation_email(user_email):
    from app.utility_modules.token_manager import generate_confirmation_token
    
    token = generate_confirmation_token(user_email)
    
    # Create the verification link (points to the 'confirm_email' route we will make next)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    
    html = f"""
    <p>Welcome! Thanks for signing up for parallax.</p>
    <p>Please follow this link to activate your account:</p>
    <p><a href="{confirm_url}">{confirm_url}</a></p>
    <br>
    <p>If you did not sign up, please ignore this email.</p>
    """
    
    msg = Message(
        subject='Confirm your email (PARALLAX)',
        recipients=[user_email],
        html=html
    )
    
    mail.send(msg)