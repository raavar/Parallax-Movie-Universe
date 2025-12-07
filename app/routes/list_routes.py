from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Movie, Rating, SeenList, ToWatchList
from app import database

# Define a Blueprint for list routes
lists = Blueprint('lists', __name__)

# Add to seen list route
@lists.route('/add_to_seen/<int:movie_id>', methods=['POST'])
@login_required     # Ensure user is logged in to access this route
def add_to_seen(movie_id):
    # Logic for adding a movie to the seen list

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # Check if the movie is already in the user's seen list
    if SeenList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
        flash(f'"{movie.title}" is already in your seen list.', 'warning')
        return redirect(request.referrer or url_for('lists.home'))

    # Add the movie to the current user's seen list
    new_entry = SeenList(user_id=current_user.id, movie_id=movie.id)
    database.session.add(new_entry)

    # Delete from to-watch list if it exists there
    ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).delete()

    # Commit the changes to the database
    database.session.commit()

    # Inform the user and redirect back
    flash(f'Added "{movie.title}" to your seen list.', 'success')
    return redirect(request.referrer or url_for('lists.home'))

# Add to to-watch list route
@lists.route('/add_to_watch/<int:movie_id>', methods=['POST'])
@login_required     # Ensure user is logged in to access this route
def add_to_watch(movie_id):
    # Logic for adding a movie to the to-watch list

    # Find the movie by ID
    movie = Movie.query.get_or_404(movie_id)

    # Check if the movie is already in the user's to-watch list
    if ToWatchList.query.filter_by(user_id=current_user.id, movie_id=movie.id).first():
        flash(f'"{movie.title}" is already in your to-watch list.', 'warning')
        return redirect(request.referrer or url_for('lists.home'))

    # Add the movie to the current user's to-watch list
    new_entry = ToWatchList(user_id=current_user.id, movie_id=movie.id)
    database.session.add(new_entry)

    # Commit the changes to the database
    database.session.commit()

    # Inform the user and redirect back
    flash(f'Added "{movie.title}" to your to-watch list.', 'success')
    return redirect(request.referrer or url_for('lists.home'))

# Movie details route
@lists.route('/movie/<int:movie_id>')
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
@lists.route('/rate_movie/<int:movie_id>', methods=['POST'])
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
        return redirect(url_for('lists.movie_details', movie_id=movie_id))

    # Check if score is valid and redirect to movie details if not
    if not 1 <= score <= 10:
        flash('Please provide a valid rating between 1 and 10.', 'danger')
        return redirect(url_for('lists.movie_details', movie_id=movie_id))
    
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
    return redirect(url_for('lists.movie_details', movie_id=movie_id))
