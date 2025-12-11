import os
import sys
import csv
from datetime import date, datetime

# Add the project root to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from dotenv import load_dotenv
from app import app, database
from app.models import Movie, Genre, User
from sqlalchemy.exc import IntegrityError

# Load environment variables from .env file
load_dotenv()

def create_admin_user():
    # Log the process of checking and creating the admin user
    print("--- Creating Admin User ---")
    
    # We use app_context to access the database
    with app.app_context():
        # Ensure tables exist (Good practice to check here too)
        database.create_all()
        
        # Check if admin already exists
        print("Checking Admin User...")
        if User.query.filter_by(email='admin@parallax.com').first():
            print("Admin user already exists. Skipping.")
            print("Done creating Admin User.")
            return

        # Create the admin user if not exists
        print("Creating default Admin user...")
        try:
            admin_user = User(
                username='admin',
                email='admin@parallax.com',
                is_admin=True,       # Grant Admin Access
                is_confirmed=True    # <--- CRITICAL: Skip email verification
            )
            # Set the password (hashing happens automatically via the model method)
            admin_user.set_password('admin123') 
            
            database.session.add(admin_user)
            database.session.commit()
            print("Successfully created user: admin@parallax.com / admin123")
            
        except Exception as e:
            database.session.rollback()
            print(f"Error creating admin: {e}")
    
    print("Done creating Admin User.")
            
# Method to populate the database with movies from CSV
def populate_movies_from_csv():
    # Log the process of populating the database
    print("--- Populating Movies and Genres from CSV ---")

    # Construct full path to the CSV file
    csv_file_path = os.path.join(current_dir, 'csv', 'movies.csv')

    with app.app_context():
        # Ensure tables are created (including Movie, Genre, and the association table)
        database.create_all()

        # --- 1. Cleaning Existing Data ---
        print("Cleaning Movie and Genre tables...")
        try:
            # Delete Many-to-Many associations (by deleting the tables)
            database.session.query(Movie).delete()
            database.session.query(Genre).delete()
            
            # Resetting ID sequences (for PostgreSQL)
            # Note: If using SQLite or MySQL, these commands need to be adjusted or removed.
            database.session.execute(database.text("ALTER SEQUENCE movie_id_seq RESTART WITH 1"))
            database.session.execute(database.text("ALTER SEQUENCE genre_id_seq RESTART WITH 1"))
            database.session.commit()
            print("Cleanup successful.")
        except Exception as e:
            # Capture error when resetting sequences (e.g., if the sequence doesn't exist yet or not PostgreSQL)
            database.session.rollback()
            # We will continue even if sequence reset fails, assuming delete worked.
            # print(f"Warning during sequence cleanup: {e}") 

        # --- 2. Population Process ---
        print(f"Populating database with movies and genres from CSV file: {csv_file_path}")

        try:
            # Dictionary to store unique Genres (Name: Genre Object)
            existing_genres = {}
            movies_count = 0

            # FINAL CORRECTION: Use the context manager directly on the database session.
            with database.session.no_autoflush:
                with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')

                    for row in csv_reader:
                        movies_count += 1
                        
                        # --- FETCH DATA (ADD MISSING FIELDS) ---
                        release_year = int(row['release_year']) if row.get('release_year') else None
                        release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date() if row.get('release_date') else None
                        
                        # 1. Create the Movie object
                        movie = Movie(
                            title=row['title'],
                            description=row['description'],
                            release_year=release_year,
                            release_date=release_date
                        )
                        
                        # 2. GENRE PROCESSING:
                        # Extract genre list from string
                        genre_list = [g.strip() for g in row.get('genres', '').split(',') if g.strip()]
                        
                        for genre_name in genre_list:
                            if genre_name not in existing_genres:
                                # 3. Search/Create Genre (Warning resolved by no_autoflush)
                                genre_obj = Genre.query.filter_by(name=genre_name).first() 
                                
                                if not genre_obj:
                                    genre_obj = Genre(name=genre_name)
                                    database.session.add(genre_obj)
                                
                                existing_genres[genre_name] = genre_obj
                            
                            # 4. Associate Genre with Movie
                            movie.genres.append(existing_genres[genre_name])
                            
                        # Add movie to session
                        database.session.add(movie)
            
            # --- 3. Final Save ---
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
    
    # Final log message
    print("Done populating Movies and Genres from CSV.")
            
if __name__ == '__main__':
    # 1. First, create the users (Infrastructure)
    create_admin_user()
    
    # 2. Then, populate the content (Data)
    populate_movies_from_csv()
