from app import database
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Define User model
class User(database.Model, UserMixin):
    # Get user credentials
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(255), unique=True, nullable=False)
    email = database.Column(database.String(255), unique=True, nullable=False)
    password = database.Column(database.String(255), nullable=False)

    # Get user relationships
    ratings = database.relationship('Rating', backref='user_ratings', lazy=True)
    seen_list = database.relationship("SeenList", backref='user_seen_list', lazy=True)
    to_watch_list = database.relationship("ToWatchList", backref='user_to_watch_list', lazy=True)

    # Password hashing method
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Password verification method
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # String representation of the User model
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
# Define Movie model
class Movie(database.Model):
    # Get movie details
    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(255), nullable=False)
    description = database.Column(database.Text, nullable=True)
    release_year = database.Column(database.Integer, nullable=True)
    release_date = database.Column(database.Date, nullable=True)

    # Inverse relationships
    ratings = database.relationship('Rating', backref='movie_ratings', lazy=True)

    # String representation of the Movie model
    def __repr__(self):
        return f"Movie('{self.title}', '{self.release_date}')"

# Define Rating model
class Rating(database.Model):
    # Get rating details
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    movie_id = database.Column(database.Integer, database.ForeignKey('movie.id'), nullable=False)
    movie = database.relationship('Movie', backref='ratings_rel', lazy=True)
    score = database.Column(database.Integer, nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    # Make sure that an user can rate a movie only once
    __table_args__ = (database.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),)

# Define SeenList model
class SeenList(database.Model):
    # Get seen list details
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    movie_id = database.Column(database.Integer, database.ForeignKey('movie.id'), nullable=False)
    # Adaugă relația explicită pentru a permite accesul item.movie
    movie = database.relationship('Movie', backref='seen_by_users', lazy=True)
    date_added = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    # Make sure that an user can add a movie to seen list only once
    __table_args__ = (database.UniqueConstraint('user_id', 'movie_id', name='unique_user_seen_movie'),)

# Define ToWatchList model
class ToWatchList(database.Model):
    # Get to-watch list details
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    movie_id = database.Column(database.Integer, database.ForeignKey('movie.id'), nullable=False)
    # Adaugă relația explicită pentru a permite accesul item.movie
    movie = database.relationship('Movie', backref='towatch_by_users', lazy=True)
    date_added = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

    # Make sure that an user can add a movie to to-watch list only once
    __table_args__ = (database.UniqueConstraint('user_id', 'movie_id', name='unique_user_to_watch_movie'),)
