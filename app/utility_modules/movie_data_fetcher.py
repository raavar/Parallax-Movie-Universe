import requests
import os

def parse_int(value):
    """Helper to turn '1,500,000' or '$50M' into integers"""
    if not value or value == 'N/A':
        return None
    # Remove non-numeric characters except digits
    clean_val = ''.join(filter(str.isdigit, value))
    return int(clean_val) if clean_val else None

def fetch_movie_data(title, year=None):
    api_key = os.environ.get('OMDB_API_KEY')
    if not api_key:
        return None

    params = {'apikey': api_key, 't': title}
    if year: params['y'] = year

    try:
        response = requests.get('http://www.omdbapi.com/', params=params)
        data = response.json()

        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster') if data.get('Poster') != 'N/A' else None,
                'rating': data.get('imdbRating') if data.get('imdbRating') != 'N/A' else None,
                
                # --- NEW PARSING LOGIC ---
                'rated': data.get('Rated') if data.get('Rated') != 'N/A' else None,
                'runtime': parse_int(data.get('Runtime')),   # "120 min" -> 120
                'metascore': parse_int(data.get('Metascore')), # "85" -> 85
                'imdb_votes': parse_int(data.get('imdbVotes')), # "1,200,000" -> 1200000
                'box_office': parse_int(data.get('BoxOffice'))  # "$50,000,000" -> 50000000
            }
            
    except Exception as e:
        print(f"Error fetching OMDb data: {e}")
        
    return None