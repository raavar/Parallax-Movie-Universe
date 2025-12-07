from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, database
from app.models import User, Movie, Rating, SeenList, ToWatchList
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app.utility_modules.qr_generator import generate_user_qr_code
from app.utility_modules.data_exporter import export_movie_list_to_csv
from app import app

# Home route
@app.route('/')
@app.route('/home')
def home():
    # Logic for home page

    # Fetch some movies to display on the home page
    movies = Movie.query.order_by(Movie.id).limit(10).all()

    # Get some recommendations for the current user
    recommendations = []    # Placeholder

    # Render the home template with movies and recommendations
    return render_template('index.html', title='Home', movies=movies, recommendations=recommendations)

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Logic for user registration

    # Redirect authenticated users to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check data validity and if not valid return with error and redirect to registration page
        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

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
            return redirect(url_for('login'))
        
        except IntegrityError:
            # Handle duplicate username or email

            # Rollback the session to avoid issues
            database.session.rollback()

            # Inform the user of the error and redirect to registration page
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))

    # Render the registration template
    return render_template('register.html', title='Register')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for user login

    # Redirect authenticated users to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    
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
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            # Inform the user of invalid credentials
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    # Render the login template
    return render_template('login.html', title='Login')

# User logout route
@app.route('/logout')
@login_required     # Ensure user is logged in to access this route
def logout():
    # Logic for user logout

    # Log the user out
    logout_user()
    flash('You have been logged out.', 'success')

    # Redirect to home page
    return redirect(url_for('home'))

# Add to seen list route
@app.route('/add_to_seen/<int:movie_id>', methods=['POST'])
@login_required     # Ensure user is logged in to access this route
def add_to_seen(movie_id):
    # Logic for adding a movie to the seen list

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # Check if the movie is already in the user's seen list
    if SeenList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
        flash(f'"{movie.title}" is already in your seen list.', 'warning')
        return redirect(request.referrer or url_for('home'))

    # Add the movie to the current user's seen list
    new_entry = SeenList(user_id=current_user.id, movie_id=movie.id)
    database.session.add(new_entry)

    # Delete from to-watch list if it exists there
    ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).delete()

    # Commit the changes to the database
    database.session.commit()

    # Inform the user and redirect back
    flash(f'Added "{movie.title}" to your seen list.', 'success')
    return redirect(request.referrer or url_for('home'))

# Add to to-watch list route
@app.route('/add_to_watch/<int:movie_id>', methods=['POST'])
@login_required     # Ensure user is logged in to access this route
def add_to_watch(movie_id):
    # Logic for adding a movie to the to-watch list

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # Check if the movie is already in the user's to-watch list
    if ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
        flash(f'"{movie.title}" is already in your to-watch list.', 'warning')
        return redirect(request.referrer or url_for('home'))

    # Add the movie to the current user's to-watch list
    new_entry = ToWatchList(user_id=current_user.id, movie_id=movie.id)
    database.session.add(new_entry)

    # Commit the changes to the database
    database.session.commit()

    # Inform the user and redirect back
    flash(f'Added "{movie.title}" to your to-watch list.', 'success')
    return redirect(request.referrer or url_for('home'))

# Movie details route
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    # Logic for displaying movie details

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # Fetch ratings for the movie
    ratings = Rating.query.filter_by(movie_id=movie.id).all()

    # Calculate average rating
    avg_rating = None
    if ratings:
        avg_rating = sum(rating.score for rating in ratings) / len(ratings)

    # Render the movie details template
    return render_template('movie_details.html', title=movie.title, movie=movie, ratings=ratings, avg_rating=avg_rating)

# Rate movie route
@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
@login_required     # Ensure user is logged in to access this route
def rate_movie(movie_id):
    # Logic for rating a movie

    # Get the rating score from the form
    score_string = request.form.get('score')

    # Try to convert score to integer
    try:
        # Convert score to integer
        score = int(score_string)

    except (ValueError, TypeError):
        # Handle invalid score input and redirect to movie details
        flash('The rating must be a number.', 'danger')
        return redirect(url_for('movie_details', movie_id=movie_id))

    # Check if score is valid and redirect to movie details if not
    if not 1 <= score <= 10:
        flash('Please provide a valid rating between 1 and 10.', 'danger')
        return redirect(url_for('movie_details', movie_id=movie_id))
    
    # Verify if there is already a rating by the user for this movie
    rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()

    if rating:
        # Update existing rating
        rating.score = score

        # Commit the changes to the database
        database.session.commit()

        # Inform the user of the update
        flash(f'Updated your rating for "{rating.movie.title}" to {score}.', 'success')
    else:
        # Create a new rating
        new_rating = Rating(user_id=current_user.id, movie_id=movie_id, score=score)
        database.session.add(new_rating)

        # Commit the new rating to the database
        database.session.commit()

        # Inform the user of the new rating
        flash(f'You rated "{new_rating.movie.title}" with a score of {score}.', 'success')

    # Redirect back to the movie details page
    return redirect(url_for('movie_details', movie_id=movie_id))


# --- Rută nouă: Pagina Profilului Utilizatorului (pentru QR Code) ---

@app.route("/profile/<int:user_id>")
@login_required
def user_profile(user_id):
    # Asigură-te că utilizatorul își vizualizează propriul profil
    if current_user.id != user_id:
        flash('Nu aveți permisiunea de a vizualiza acest profil.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    
    # Generare QR Code (folosind contextul aplicației)
    qr_data_uri = generate_user_qr_code(app.app_context(), user_id)
    
    # Preluare liste de filme (pentru afișare)
    seen_movies = SeenList.query.filter_by(user_id=user_id).all()
    to_watch_movies = ToWatchList.query.filter_by(user_id=user_id).all()

    return render_template('user_profile.html', 
                           title=f'Profil {user.username}', 
                           user=user,
                           qr_data_uri=qr_data_uri,
                           seen_movies=seen_movies,
                           to_watch_movies=to_watch_movies)

# --- Rută nouă: Export date CSV ---

@app.route("/export_seen_list", methods=['GET'])
@login_required
def export_seen_list():
    """Exportă lista 'Văzute' a utilizatorului curent în CSV."""
    
    # Preluare filme văzute (Necesită ca models.py să aibă relația SeenList.movie)
    seen_movies = SeenList.query.filter_by(user_id=current_user.id).all()
    
    if not seen_movies:
        flash('Lista "Văzute" este goală. Nu există date de exportat.', 'warning')
        return redirect(url_for('user_profile', user_id=current_user.id))

    # Apelează modulul de export
    return export_movie_list_to_csv(seen_movies, filename="parallax_seen_list.csv")