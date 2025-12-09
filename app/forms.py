from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User # Asigură-te că User este importat corect

# --- Formular de Actualizare Profil ---
class UpdateProfileForm(FlaskForm):
    username = StringField('Nume Utilizator', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Actualizează Profilul')

    # Metoda de validare personalizată pentru a evita duplicarea numelui de utilizator/email
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.original_user_id:
            raise ValidationError('Acest nume de utilizator este deja folosit.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.original_user_id:
            raise ValidationError('Acest email este deja folosit.')

# --- Formular de Schimbare Parolă ---
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Parola Actuală', 
                                 validators=[DataRequired()])
    new_password = PasswordField('Parola Nouă', 
                                 validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirmă Parola Nouă', 
                                         validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Schimbă Parola')