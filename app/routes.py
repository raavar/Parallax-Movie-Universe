from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc, asc, distinct, and_, cast, Float
from app import app, database
from app.models import User, Movie, Rating, SeenList, ToWatchList, Genre
import random
from app.utility_modules.data_exporter import export_movie_list_to_csv
from app.utility_modules.qr_generator import generate_user_qr_code
from app.utility_modules.token_manager import confirm_token
from app.utility_modules.email_sender import send_confirmation_email
from app.utility_modules.recommendation_engine import get_recommendations
from datetime import datetime
from app.forms import UpdateProfileForm, ChangePasswordForm

# ==========================================================================================
# Main Routes
# ==========================================================================================

# Home route
@app.route('/')
@app.route('/home')
def home():
    # Logic for home page
    
    recommendations = []

    # 2. IF user is logged in, try to run the AI engine
    if current_user.is_authenticated:
        try:
            # CALL THE FUNCTION HERE using the user's ID
            recommendations = get_recommendations(current_user.id, 20)
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            recommendations = []

    # 3. If ML failed or user is logged out, just show 20 random movies
    if not recommendations:
        recommendations = Movie.query.order_by(func.random()).limit(20).all()
        
    movies = recommendations

    # Render the home template with movies and recommendations
    return render_template('index.html', title='Home', movies=recommendations)

# Catalog Route with Pagination, Filters, and Sorting
@app.route("/catalog", methods=['GET'])
def catalog():
    # Get parameters
    page = request.args.get('page', 1, type=int)
    
    # Get list of genres (from frontend buttons/checkboxes)
    selected_genres = request.args.getlist('genre') 
    
    # Get year range
    min_year = request.args.get('min_year', type=int)
    max_year = request.args.get('max_year', type=int)
    
    current_sort = request.args.get('sort_by', 'title_asc')
    
    PER_PAGE = 20
    
    # Base query selects Movie objects
    query = database.session.query(Movie)
    
    # 1. Get Available Genres (for tag buttons)
    # Query to fetch genres only from the Movie/Genre table
    available_genres = database.session.query(
        Genre.name, func.count(distinct(Movie.id)).label('movie_count')
    ).join(Movie.genres).group_by(Genre.name).order_by(Genre.name).all()


    # 2. Filtering
    
    # MULTI-GENRE FILTER (OR logic): Movies must have AT LEAST one of the selected genres
    if selected_genres:
        # Use join to link Movie to Genre and filter by selected genres
        query = query.join(Movie.genres).filter(Genre.name.in_(selected_genres))
        
    # YEAR RANGE FILTER
    year_filters = []
    if min_year:
        year_filters.append(Movie.release_year >= min_year)
    if max_year:
        year_filters.append(Movie.release_year <= max_year)
        
    if year_filters:
        # Apply year filters if they exist
        query = query.filter(and_(*year_filters)) 
    
    # 3. Sorting

    if current_sort == 'year_desc':
        query = query.order_by(Movie.release_year.desc())
    elif current_sort == 'year_asc':
        query = query.order_by(Movie.release_year.asc())
        
    elif current_sort == 'date_desc':
        query = query.order_by(Movie.release_date.desc())
    elif current_sort == 'date_asc':
        query = query.order_by(Movie.release_date.asc())
        
    elif current_sort == 'title_desc':
        query = query.order_by(Movie.title.desc())
    else: # title_asc (Default)
        query = query.order_by(Movie.title.asc())

    # 4. Pagination
    movies_paginated = query.paginate(
        page=page,
        per_page=PER_PAGE,
        error_out=False
    )
    
    # We no longer need to extract from tuples since we are not sorting by rating
    movies_to_display = movies_paginated.items

    return render_template('catalog.html',
                           movies=movies_to_display,
                           pagination=movies_paginated,
                           available_genres=available_genres,
                           selected_genres=selected_genres,  # List of selected genres
                           min_year=min_year,                # Minimum year
                           max_year=max_year,                # Maximum year
                           current_sort=current_sort)

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
            user = User(username=username, email=email, is_confirmed=False)
            user.set_password(password)

            # Add user to the database and commit
            database.session.add(user)
            database.session.commit()
            
            # Send mail
            send_confirmation_email(user.email)
            
            # Inform the user of successful registration and redirect to login page
            flash('A confirmation email has been sent via email.', 'success')
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

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
        
    user = User.query.filter_by(email=email).first_or_404()
    
    if user.is_confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        database.session.add(user)
        database.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
        
    return redirect(url_for('login'))

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
            # NEW: Check if confirmed
            if not user.is_confirmed:
                flash('Please confirm your account via the email link provided.', 'warning')
                return redirect(url_for('login'))
            
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

# ==========================================================================================
# Lists Routes
# ==========================================================================================

# Add to seen list route
@app.route('/toggle_seen/<int:movie_id>', methods=['POST'])
@login_required
def toggle_seen(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    seen_entry = SeenList.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    
    if seen_entry:
        # If seen, remove it from seen list
        database.session.delete(seen_entry)
        
        # CRITICAL: Delete the rating as well, since the movie is no longer considered seen
        Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).delete()
        
        flash(f'"{movie.title}" was deleted from Watch History and removed from ratings.', 'info')
        status = 'removed'
    else:
        # If not seen, add it to seen list
        new_entry = SeenList(user_id=current_user.id, movie_id=movie_id)
        database.session.add(new_entry)
        
        # Optional: Remove from Watchlist (if moved to seen)
        # ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie_id).delete()
        
        flash(f'"{movie.title}" was added to Watch History.', 'success')
        status = 'added'

    database.session.commit()
    return redirect(url_for('movie_details', movie_id=movie_id))

# Movie details route
@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    # Logic for displaying movie details

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # 1. GET GLOBAL RATINGS
    # Fetch ratings for the movie
    ratings = Rating.query.filter_by(movie_id=movie.id).all()

    # Calculate average rating
    avg_rating = None
    if ratings:
        avg_rating = sum(rating.score for rating in ratings) / len(ratings)

    # 2. GET USER STATE
    is_in_watchlist = False
    is_seen = False
    user_rating_score = None
    user_rating_obj = None

    if current_user.is_authenticated:
        # A. User rating
        user_rating_obj = Rating.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()
        if user_rating_obj:
            user_rating_score = user_rating_obj.score
            is_seen = True # Automatically marked as seen if rating exists
        
        # B. SeenList (Check SeenList only if no rating, for flexibility)
        elif SeenList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
             is_seen = True # Marked as seen (without rating)
        
        # C. Watchlist
        if ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
            is_in_watchlist = True


    # Render the movie details template
    return render_template('movie_details.html', 
                           title=movie.title, 
                           movie=movie, 
                           ratings=ratings, 
                           avg_rating=avg_rating, 
                           
                           # State variables newly sent to Frontend
                           is_in_watchlist=is_in_watchlist,
                           is_seen=is_seen,
                           user_rating=user_rating_score # Send only the score
                          )

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
    
    # Check if the rating already exists
    rating = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    movie = Movie.query.get_or_404(movie_id) # Fetch the movie for messages

    if rating:
        # Update existing rating
        rating.score = score
        flash(f'Updated your rating for "{movie.title}" to {score}.', 'success')
    else:
        # Create a new rating
        new_rating = Rating(user_id=current_user.id, movie_id=movie_id, score=score)
        database.session.add(new_rating)
        flash(f'You rated "{movie.title}" with a score of {score}.', 'success')
        
    # CRITICAL LOGIC: Ensure the movie is marked as seen
    seen_entry = SeenList.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    
    if not seen_entry:
        # Add movie to SeenList because it received a rating
        new_seen_entry = SeenList(user_id=current_user.id, movie_id=movie_id)
        database.session.add(new_seen_entry)
        
        # Optional: remove from ToWatchList if added
        # ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie_id).delete()
        
    # Final commit of all changes (rating, seenlist, towatchlist)
    database.session.commit()

    # Redirect back to the movie details page
    return redirect(url_for('movie_details', movie_id=movie_id))

# ==========================================================================================
# Utility Routes
# ==========================================================================================

# ROUTE: Export seen movie list (or to-watch) as CSV
@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    # Ensure the user is viewing their own profile
    if current_user.id != user_id:
        flash('You do not have permission to view this profile.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    
    # Generate QR Code (using application context)
    qr_data_uri = generate_user_qr_code(user_id)
    
    # Fetch movie lists (for display)
    seen_movies = SeenList.query.filter_by(user_id=user_id).all()
    to_watch_movies = ToWatchList.query.filter_by(user_id=user_id).all()

    return render_template('user_profile.html', 
                           title=f'Profile {user.username}', 
                           user=user,
                           qr_data_uri=qr_data_uri,
                           seen_movies=seen_movies,
                           to_watch_movies=to_watch_movies)

# Route for exporting the "To Watch" list as CSV
@app.route("/export_to_watch_list", methods=['GET'])
@login_required
def export_to_watch_list():
    """Export the current user's Watchlist to CSV."""
    
    # Fetch movies from the logged-in user's "To Watch" list
    to_watch_movies = ToWatchList.query.filter_by(user_id=current_user.id).all()
    
    if not to_watch_movies:
        flash('Watch History is empty. No data to export.', 'warning')
        # Redirect back to the profile page
        return redirect(url_for('user_profile', user_id=current_user.id))

    # Call the export module
    return export_movie_list_to_csv(to_watch_movies, filename="parallax_to_watch_list.csv")

# New Route: Export CSV Data

@app.route("/export_seen_list", methods=['GET'])
@login_required
def export_seen_list():
    """Export the current user's Watchlist to CSV."""
    
    # Fetch seen movies (Requires SeenList.movie relationship in models.py)
    seen_movies = SeenList.query.filter_by(user_id=current_user.id).all()
    
    if not seen_movies:
        flash('Watchlist is empty. No data to export.', 'warning')
        return redirect(url_for('user_profile', user_id=current_user.id))

    # Call the export module
    return export_movie_list_to_csv(seen_movies, filename="parallax_seen_list.csv")


# New Route: Movie Search

@app.route("/search", methods=['GET'])
def search():
    """
    Handles search requests by querying the database 
    for movies by title or description.
    """
    # Get search term from URL (e.g., /search?query=inception)
    query = request.args.get('query', '') 
    
    results = []
    
    if query:
        # Create search term for LIKE operator (e.g., "%interstellar%")
        search_term = f"%{query}%"
        
        # SQLAlchemy Query: Search by title OR description (case-insensitive)
        results = Movie.query.filter(
            (Movie.title.ilike(search_term)) | 
            (Movie.description.ilike(search_term))
        ).all()
        
        # Count of results
        count = len(results)
    else:
        count = 0

    return render_template('search_results.html', 
                           title=f"Search Results: {query}",
                           query=query,
                           results=results,
                           count=count)

@app.route("/search_autocomplete")
def search_autocomplete():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])

    try:
        search_term = f"%{query}%"
        suggestions = Movie.query.filter(
            Movie.title.ilike(search_term)
        ).limit(15).all()

        results = []
        for movie in suggestions:
            results.append({
                'id': movie.id,
                'title': f"{movie.title} ({movie.release_year})",
                'url': url_for('movie_details', movie_id=movie.id)
            })
            
        return jsonify(results)
        
    except Exception as e:
        # Log the full error
        current_app.logger.error(f"Autocomplete search error: {e}") 
        # Return an empty response for frontend (but error is in logs)
        return jsonify([]), 500 # Return error code 500

# User Settings Section

@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    # Initialize forms
    profile_form = UpdateProfileForm()
    password_form = ChangePasswordForm()

    # For unique profile validation, set the original user ID
    profile_form.original_user_id = current_user.id
    
    # PROFILE UPDATE FORM HANDLING
    if profile_form.validate_on_submit() and profile_form.submit.data:
        # 1. Check if entered data is different from current
        if (current_user.username != profile_form.username.data or 
            current_user.email != profile_form.email.data):
            
            # 2. Update user and save to database
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            database.session.commit()
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('settings'))

    # PASSWORD CHANGE FORM HANDLING
    if password_form.validate_on_submit() and password_form.submit.data:
        # 1. Verify old password
        if current_user.check_password(password_form.old_password.data):
            # 2. Change password
            current_user.set_password(password_form.new_password.data)
            database.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('settings'))
        else:
            flash('Current password is incorrect.', 'danger')
            
    # Populate profile form with current data if request is GET
    elif request.method == 'GET':
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email

    return render_template('settings.html', 
                           title='Account Settings',
                           profile_form=profile_form,
                           password_form=password_form)

# 1. MY RATINGS (New Page)
@app.route("/my_ratings")
@login_required
def my_ratings():
    # Fetch only ratings, ordered by date
    user_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.timestamp.desc()).all()
    
    return render_template('my_ratings.html', 
                           title='My Ratings', 
                           user_ratings=user_ratings)

# 2. WATCHLIST (Modified to send objects, not just movies)
@app.route("/watchlist")
@login_required
def watchlist():
    # Send ToWatchList objects to access the added date
    watchlist_items = ToWatchList.query.filter_by(user_id=current_user.id).order_by(ToWatchList.date_added.desc()).all()
    
    return render_template('watchlist.html', 
                           title='My Watchlist', 
                           watchlist_items=watchlist_items)

# 3. SEEN MOVIES (Modified to query SeenList)
@app.route("/seen_list")
@login_required
def seen_list():
    # Fetch entries from SeenList, ordered chronologically
    seen_entries = SeenList.query.filter_by(user_id=current_user.id).order_by(SeenList.date_added.desc()).all()
    
    return render_template('seen_list.html', 
                           title='Seen Movies', 
                           seen_entries=seen_entries)

# 4. TOGGLE WATCHLIST (Switch function)
@app.route('/toggle_watchlist/<int:movie_id>', methods=['POST'])
@login_required
def toggle_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    entry = ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first()
    
    if entry:
        # Remove
        database.session.delete(entry)
        flash(f'"{movie.title}" was removed from Watchlist.', 'info')
    else:
        # Add
        new_entry = ToWatchList(user_id=current_user.id, movie_id=movie.id)
        database.session.add(new_entry)
        flash(f'"{movie.title}" was added to Watchlist.', 'success')

    database.session.commit()
    return redirect(url_for('movie_details', movie_id=movie_id))
