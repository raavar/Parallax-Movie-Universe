import time
import requests
from app import app, database
from app.models import Movie

# ==============================================================================
# 🔑 INTRODU CHEIA TA API AICI (Obligatoriu!)
# ==============================================================================
OMDB_API_KEY = "5e3d2d73"  # Ex: "b2b6df35"
# ==============================================================================

def parse_int(value):
    """Helper pentru conversia numerelor (ex: '$50M' -> 50000000)"""
    if not value or value == 'N/A':
        return None
    clean_val = ''.join(filter(str.isdigit, value))
    return int(clean_val) if clean_val else None

def fetch_movie_data_local(title, year=None):
    """
    Funcție locală care folosește cheia hardcodată pentru a evita problemele de mediu.
    """
    if OMDB_API_KEY == "PUNE_CHEIA_TA_AICI":
        print("❌ EROARE: Nu ai pus cheia API în script la linia 9!")
        return None

    params = {'apikey': OMDB_API_KEY, 't': title}
    if year:
        params['y'] = year

    try:
        response = requests.get('http://www.omdbapi.com/', params=params)
        
        if response.status_code != 200:
            print(f"   -> Eroare HTTP: {response.status_code}")
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
        print(f"   -> Excepție: {e}")
        
    return None

def update_all_movies():
    with app.app_context():
        # Căutăm filmele care nu au poster
        movies = Movie.query.filter(
            (Movie.poster_url == None) | (Movie.poster_url == '')
        ).all()
        
        total = len(movies)
        print(f"--- Începere actualizare pentru {total} filme fără poster ---")
        
        updated_count = 0

        for index, movie in enumerate(movies):
            print(f"[{index + 1}/{total}] Procesez: {movie.title} ({movie.release_year})...")
            
            data = fetch_movie_data_local(movie.title, movie.release_year)
            
            if data:
                # Actualizăm datele
                if data['poster']: movie.poster_url = data['poster']
                if data['rating']: movie.imdb_rating = data['rating']
                if data['rated']: movie.rated = data['rated']
                if data['runtime']: movie.runtime_minutes = data['runtime']
                if data['metascore']: movie.meta_score = data['metascore']
                if data['imdb_votes']: movie.imdb_votes = data['imdb_votes']
                if data['box_office']: movie.box_office = data['box_office']
                
                updated_count += 1
                
                # Salvăm la fiecare 5 filme
                if updated_count % 5 == 0:
                    database.session.commit()
                    print("   -> Salvat (lot intermediar).")
            else:
                print("   -> Nu s-au găsit date.")

            # Pauză mică pentru a nu bloca cheia API
            time.sleep(0.3)

        database.session.commit()
        print(f"--- FINALIZAT! {updated_count} filme actualizate. ---")

if __name__ == "__main__":
    update_all_movies()