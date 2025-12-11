import os
import sys
import csv
from datetime import date, datetime

# Adjust the system path to include the parent directory so we can import the app module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from app import app, database
from app.models import Movie, Genre, User
from sqlalchemy.exc import IntegrityError

# Load environment variables from the .env file
load_dotenv()

def create_admin_user():
    # Log the start of the admin user creation process
    print("--- Creating Admin User ---")
    
    # Use the application context to access the database session
    with app.app_context():
        # Ensure all database tables exist before proceeding
        database.create_all()
        
        # Check if an admin user with the specified email already exists
        print("Checking Admin User...")
        if User.query.filter_by(email='admin@parallax.com').first():
            print("Admin user already exists. Skipping.")
            print("Done creating Admin User.")
            return

        # Create the default admin user since one does not exist
        print("Creating default Admin user...")
        try:
            admin_user = User(
                username='admin',
                email='admin@parallax.com',
                is_admin=True,       # Grant administrative access privileges
                is_confirmed=True    # Set the account as confirmed immediately to bypass email verification
            )
            # Set the password which will be hashed automatically by the model
            admin_user.set_password('admin123') 
            
            database.session.add(admin_user)
            database.session.commit()
            print("Successfully created user: admin@parallax.com / admin123")
            
        except Exception as e:
            database.session.rollback()
            print(f"Error creating admin: {e}")
    
    print("Done creating Admin User.")
            
# Function to read movies from a CSV file and populate the database
def populate_movies_from_csv():
    # Log the start of the movie and genre population process
    print("--- Populating Movies and Genres from CSV ---")

    # Define the full path to the source CSV file
    csv_file_path = os.path.join(current_dir, 'csv', 'movies.csv')

    with app.app_context():
        # Ensure the Movie, Genre, and association tables are created
        database.create_all()

        # Clear existing data from the Movie and Genre tables to start fresh
        print("Cleaning Movie and Genre tables...")
        try:
            # Delete all records from the Movie and Genre tables
            database.session.query(Movie).delete()
            database.session.query(Genre).delete()
            
            # Reset the primary key ID sequences for PostgreSQL databases to ensure IDs start from 1
            # Note that these commands may need adjustment if using SQLite or MySQL
            database.session.execute(database.text("ALTER SEQUENCE movie_id_seq RESTART WITH 1"))
            database.session.execute(database.text("ALTER SEQUENCE genre_id_seq RESTART WITH 1"))
            database.session.commit()
            print("Cleanup successful.")
        except Exception as e:
            # If resetting the sequence fails (e.g., non-PostgreSQL DB), rollback but continue assuming the delete worked
            database.session.rollback()

        # Begin populating the database with data from the CSV file
        print(f"Populating database with movies and genres from CSV file: {csv_file_path}")

        try:
            # Initialize a dictionary to track unique Genre objects by name to avoid duplicates
            existing_genres = {}
            movies_count = 0

            # Disable autoflush on the session to prevent premature database writes while processing the CSV data
            with database.session.no_autoflush:
                with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')

                    for row in csv_reader:
                        movies_count += 1
                        
                        # Parse the release year and date from the CSV row, handling missing values
                        release_year = int(row['release_year']) if row.get('release_year') else None
                        release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date() if row.get('release_date') else None
                        
                        # Instantiate a new Movie object using data from the current CSV row
                        movie = Movie(
                            title=row['title'],
                            description=row['description'],
                            release_year=release_year,
                            release_date=release_date
                        )
                        
                        # Process the genre information associated with the movie
                        genre_list = [g.strip() for g in row.get('genres', '').split(',') if g.strip()]
                        
                        for genre_name in genre_list:
                            if genre_name not in existing_genres:
                                # Check if the genre already exists in the database
                                genre_obj = Genre.query.filter_by(name=genre_name).first() 
                                
                                if not genre_obj:
                                    # Create a new Genre object if it does not exist
                                    genre_obj = Genre(name=genre_name)
                                    database.session.add(genre_obj)
                                
                                # Add the genre to the local tracking dictionary
                                existing_genres[genre_name] = genre_obj
                            
                            # Associate the genre object with the current movie
                            movie.genres.append(existing_genres[genre_name])
                            
                        # Add the fully constructed movie object to the database session
                        database.session.add(movie)
            
            # Commit all changes to the database in a single transaction
            database.session.commit()

            print(f"Successfully populated database with {movies_count} movies.")
            print(f"Total {len(existing_genres)} unique genres created.")


        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file_path}' not found.")
        except IntegrityError:
            database.session.rollback()
            print("Error: Integrity error occurred (duplicate data).")
        except Exception as e:
            database.session.rollback()
            print(f"An unexpected error occurred: {e}")
    
    # Log the completion of the population process
    print("Done populating Movies and Genres from CSV.")
            
if __name__ == '__main__':
    # First ensure the admin user exists
    create_admin_user()
    
    # Then populate the database with movie and genre content
    populate_movies_from_csv()
