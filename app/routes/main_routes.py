from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from app.models import User, Movie
from app import database
from sqlalchemy.exc import IntegrityError

# Define a Blueprint for main routes
main = Blueprint('main', __name__)

# Home route
@main.route('/')
@main.route('/home')
def home():
    # Logic for home page
    
    # Fetch some movies to display on the home page
    movies = Movie.query.order_by(Movie.id).limit(10).all()

    # Get some recommendations for the current user
    recommendations = []    # Placeholder

    # Render the home template with movies and recommendations
    return render_template('index.html', title='Home', movies=movies, recommendations=recommendations)

# User registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    # Logic for user registration

    # Redirect authenticated users to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check data validity and if not valid return with error and redirect to registration page
        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('main.register'))

        # Try to create a new user
        try:
            # Create user and hash password
            user = User(username=username, email=email)
            user.set_password(password)

            # Add user to the database and commit
            database.session.add(user)
            database.session.commit()

            # Inform the user of successful registration and redirect to login page
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('main.login'))
        
        except IntegrityError:
            # Handle duplicate username or email

            # Rollback the session to avoid issues
            database.session.rollback()

            # Inform the user of the error and redirect to registration page
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('main.register'))

    # Render the registration template
    return render_template('register.html', title='Register')

# User login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for user login

    # Redirect authenticated users to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Log the user in and log a success message
            login_user(user, remember=remember)
            flash('Login successful!', 'success')

            # Redirect to next page if exists, else to home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            # Inform the user of invalid credentials
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('main.login'))
    # Render the login template
    return render_template('login.html', title='Login')

# User logout route
@main.route('/logout')
@login_required     # Ensure user is logged in to access this route
def logout():
    # Logic for user logout

    # Log the user out
    logout_user()
    flash('You have been logged out.', 'success')

    # Redirect to home page
    return redirect(url_for('main.home'))
