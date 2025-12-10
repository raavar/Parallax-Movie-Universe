import os
import sys
import time
import requests
import csv

# Add the project root to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app import app, database
from app.models import Movie

# Setup paths for CSV files
CSV_FILE_PATH = os.path.join(current_dir, 'movies.csv')
REMOVED_CSV_PATH = os.path.join(current_dir, 'movies_without_poster.csv')

# Get OMDB API key from environment variable
OMDB_API_KEY = os.environ.get('OMDB_API_KEY')

def parse_int(value):
    # Helper function for number conversion (e.g., '$50M' -> 50000000).
    if not value or value == 'N/A':
        return None
    clean_val = ''.join(filter(str.isdigit, value))
    return int(clean_val) if clean_val else None

def fetch_movie_data_local(title, year=None):
    if not OMDB_API_KEY or OMDB_API_KEY == "your_omdb_api_key":
        print("❌ ERROR: OMDB_API_KEY is missing!")
        return None

    params = {'apikey': OMDB_API_KEY, 't': title}
    if year:
        params['y'] = year

    try:
        response = requests.get('http://www.omdbapi.com/', params=params)
        if response.status_code != 200:
            print(f"   -> HTTP Error: {response.status_code}")
            return None
            
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                'rating': data.get('imdbRating') if data.get('imdbRating') != 'N/A' else None,
                'rated': data.get('Rated') if data.get('Rated') != 'N/A' else None,
                'runtime': parse_int(data.get('Runtime')),
                'metascore': parse_int(data.get('Metascore')),
                'imdb_votes': parse_int(data.get('imdbVotes')),
                'box_office': parse_int(data.get('BoxOffice'))
            }
        else:
            print(f"   -> OMDb Error: {data.get('Error')}")
            return None
    except Exception as e:
        print(f"   -> Exception: {e}")
    return None

def handle_csv_changes(titles_to_remove):
    """
    Reads the main CSV, removes the specified titles, 
    writes them to a new CSV, and updates the main CSV.
    """
    if not titles_to_remove:
        return

    print(f"\n--- Processing CSV files for {len(titles_to_remove)} removed movies ---")
    
    kept_rows = []
    removed_rows = []
    fieldnames = []

    # 1. Read the source file
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';') 
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row['title'] in titles_to_remove:
                    removed_rows.append(row)
                else:
                    kept_rows.append(row)
    except FileNotFoundError:
        print("Error: movies.csv not found. Cannot update CSV files.")
        return

    # 2. Append removed movies to movies_without_poster.csv
    file_exists = os.path.isfile(REMOVED_CSV_PATH)
    with open(REMOVED_CSV_PATH, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        if not file_exists:
            writer.writeheader() # Write header only if file is new
        writer.writerows(removed_rows)
    print(f"   -> Added {len(removed_rows)} rows to {os.path.basename(REMOVED_CSV_PATH)}")

    # 3. Overwrite movies.csv with kept rows
    with open(CSV_FILE_PATH, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(kept_rows)
    print(f"   -> Updated {os.path.basename(CSV_FILE_PATH)}")


def update_and_clean_movies():
    titles_to_remove = set() # Store titles to remove from CSV

    with app.app_context():
        movies = Movie.query.filter(
            (Movie.poster_url == None) | (Movie.poster_url == '')
        ).all()
        
        total = len(movies)
        print(f"--- Starting cleanup for {total} movies without posters ---")
        
        updated_count = 0
        deleted_count = 0

        for index, movie in enumerate(movies):
            print(f"[{index + 1}/{total}] Processing: {movie.title} ({movie.release_year})...")
            
            data = fetch_movie_data_local(movie.title, movie.release_year)
            got_poster = False

            if data and data.get('poster'):
                movie.poster_url = data['poster']
                if data['rating']: movie.imdb_rating = data['rating']
                if data['rated']: movie.rated = data['rated']
                if data['runtime']: movie.runtime_minutes = data['runtime']
                if data['metascore']: movie.meta_score = data['metascore']
                if data['imdb_votes']: movie.imdb_votes = data['imdb_votes']
                if data['box_office']: movie.box_office = data['box_office']
                
                updated_count += 1
                got_poster = True
                print("   -> Updated.")
            
            if not got_poster:
                print(f"   -> No poster. Deleting '{movie.title}' from DB & moving to removed list.")
                # Add to set for CSV processing later
                titles_to_remove.add(movie.title)
                # Delete from DB
                database.session.delete(movie)
                deleted_count += 1

            if (index + 1) % 10 == 0:
                database.session.commit()

            time.sleep(0.3)

        database.session.commit()
        print(f"--- DB FINISHED! Updated: {updated_count} | Deleted from DB: {deleted_count} ---")
        
        # After DB operations are done, handle the CSV files
        if deleted_count > 0:
            handle_csv_changes(titles_to_remove)

if __name__ == "__main__":
    update_and_clean_movies()
