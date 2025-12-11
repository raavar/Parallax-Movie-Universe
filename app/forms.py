from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User # Asigură-te că User este importat corect

# --- Formular de Actualizare Profil ---
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
    # Metoda de validare personalizată pentru a evita duplicarea numelui de utilizator/email
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.original_user_id:
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.original_user_id:
            raise ValidationError('This email is already taken.')

# --- Change Password Form ---
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', 
                                 validators=[DataRequired()])
    new_password = PasswordField('New Password', 
                                 validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')