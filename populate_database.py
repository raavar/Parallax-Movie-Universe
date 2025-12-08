import os
import csv
from datetime import date, datetime

from dotenv import load_dotenv
from app import app, database
from app.models import Movie
from sqlalchemy.exc import IntegrityError

# Load environment variables from .env file
load_dotenv()

# Method to populate the database with movies from a CSV file
def populate_movies_from_csv(csv_file_path='movies.csv'):
    # Read movies from CSV file and insert them into the database
    with app.app_context():
        # Make sure the database tables are created
        database.create_all()

        # Check if the database is already populated
        if Movie.query.count() > 0:
            print("Database already populated with movies. Exiting.")
            return
        
        # Log message indicating the start of the population process
        print(f"Populating database with movies from CSV file: {csv_file_path}")

        # Try to populate the database
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                # We are using DictReader to read the CSV file rows as dictionaries
                csv_reader = csv.DictReader(csv_file, delimiter=';')

                # Movies list to be added to the database
                movies_to_add = []

                # Iterate through each row in the CSV file
                for row in csv_reader:
                    # Convert data types as necessary
                    release_year = int(row['release_year']) if row['release_year'] else None
                    release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date() if row['release_date'] else None

                    # Create a Movie instance
                    movie = Movie(
                        title=row['title'],
                        description=row['description'],
                        release_year=release_year,
                        release_date=release_date
                    )
                    movies_to_add.append(movie)

            # Insert all movies at once into the database for efficiency
            database.session.bulk_save_objects(movies_to_add)

            # Commit the session to save changes
            database.session.commit()

            # Log success message
            print(f"Successfully populated database with {len(movies_to_add)} movies.")

        except FileNotFoundError:
            # Log error if the CSV file is not found
            print(f"Error: CSV file '{csv_file_path}' not found.")
        except IntegrityError:
            # Rollback the session in case of integrity error
            database.session.rollback()

            # Log integrity error message
            print("Error: Integrity error occurred while inserting movies into the database.")
        except Exception as e:
            # Rollback the session in case of any other exceptions
            database.session.rollback()

            # Log any other exceptions that occur
            print(f"An unexpected error occurred: {e}")
            
if __name__ == '__main__':
    populate_movies_from_csv()
