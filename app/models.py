from app import database
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import UniqueConstraint

# 1. Tabelă de asociere (Fără clasă Model)
# Aceasta este legătura fizică dintre filme și genuri
movie_genre_association = database.Table('movie_genre_association', database.metadata,
    database.Column('movie_id', database.Integer, database.ForeignKey('movie.id'), primary_key=True),
    database.Column('genre_id', database.Integer, database.ForeignKey('genre.id'), primary_key=True)
)

# 2. Modelul Genre (Genul propriu-zis)
class Genre(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"Genre: {self.name}"

# Define User model
class User(database.Model, UserMixin):
    # Get user credentials
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(255), unique=True, nullable=False)
    email = database.Column(database.String(255), unique=True, nullable=False)
    password = database.Column(database.String(255), nullable=False)
    
    # NEW: Confirmation flag (default to False)
    is_confirmed = database.Column(database.Boolean, default=False)
    confirmed_on = database.Column(database.DateTime, nullable=True)
    
    # NOU: Coloană pentru a marca utilizatorii ca administratori
    is_admin = database.Column(database.Boolean, default=False)

    # Corecție Relații: Trecem la back_populates pentru Rating
    # Relația din User către Rating
    ratings = database.relationship('Rating', back_populates='user', lazy=True)
    
    # Relațiile SeenList și ToWatchList pot folosi backref simplu pentru a evita conflictele complexe
    seen_list = database.relationship("SeenList", backref='user', lazy=True)
    to_watch_list = database.relationship("ToWatchList", backref='user', lazy=True)

    # Password hashing method
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Password verification method
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # String representation of the User model (CRUCIAL pentru Flask-Admin)
    def __repr__(self):
        return f"User: {self.username}"
    
# Define Movie model
class Movie(database.Model):
    # Get movie details
    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(255), nullable=False)
    description = database.Column(database.Text, nullable=True)
    release_year = database.Column(database.Integer, nullable=True)
    release_date = database.Column(database.Date, nullable=True)
    poster_url = database.Column(database.String(500), nullable=True)
    imdb_rating = database.Column(database.String(10), nullable=True)
    
    # --- NEW ML FEATURES ---
    runtime_minutes = database.Column(database.Integer, nullable=True)  # e.g., 120
    meta_score = database.Column(database.Integer, nullable=True)       # e.g., 85
    imdb_votes = database.Column(database.BigInteger, nullable=True)    # e.g., 1500000
    box_office = database.Column(database.BigInteger, nullable=True)    # e.g., 500000000
    rated = database.Column(database.String(10), nullable=True)         # e.g., "PG-13"

    # Relația Mulți-la-Mulți (pentru a accesa Movie.genres)
    genres = database.relationship(
        'Genre', 
        secondary=movie_genre_association, # Folosește tabela de asociere
        backref=database.backref('movies', lazy='dynamic'), 
        lazy='select'
    )

    # Corecție Relații: Trecem la back_populates
    # Relația din Movie către Rating
    ratings = database.relationship('Rating', back_populates='movie', lazy=True)

    # String representation of the Movie model (CRUCIAL pentru Flask-Admin)
    def __repr__(self):
        return f"Movie: {self.title} ({self.release_year})"

# Define Rating model
class Rating(database.Model):
    # Get rating details
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)
    movie_id = database.Column(database.Integer, database.ForeignKey('movie.id'), nullable=False)
    
    # CORECȚIE: Relația inversă către User (rezolvă AttributeError)
    user = database.relationship('User', back_populates='ratings', lazy=True) 
    
    # CORECȚIE: Relația inversă către Movie (rezolvă conflictele)
    movie = database.relationship('Movie', back_populates='ratings', lazy=True)
    
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