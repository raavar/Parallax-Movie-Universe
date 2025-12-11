import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from app.models import Movie, Rating, SeenList

def get_recommendations(user_id, num_recommendations=4):
    movies = Movie.query.all()
    if not movies: return []

    # Configure weights for the recommendation algorithm
    # These weights prioritize IMDb rating and Genre over description and general stats
    W_IMDB  = 0.40   # Highest priority given to movie quality/rating
    W_GENRE = 0.30   # High priority given to movie category
    W_STATS = 0.20   # Medium priority given to budget, runtime, and metascore
    W_DESC  = 0.10   # Lower priority given to specific keywords in the description

    movie_data = []
    for m in movies:
        # Prepare text data by combining title and description
        desc_text = f"{m.title} {m.description}"
        # Create a string of genres separated by spaces
        genre_text = " ".join([g.name for g in m.genres])
        
        # Prepare statistical data, setting defaults if values are missing
        runtime = m.runtime_minutes if m.runtime_minutes else 90
        metascore = m.meta_score if m.meta_score else 50
        budget = m.box_office if m.box_office else 0
        
        # Handle IMDb ratings carefully, defaulting to a neutral score if unavailable
        try:
            imdb_val = float(m.imdb_rating) if m.imdb_rating and m.imdb_rating != 'N/A' else 5.0
        except:
            imdb_val = 5.0

        # Map MPAA ratings to numerical values for processing
        rating_map = {'R': 3, 'PG-13': 2, 'PG': 1, 'G': 0}
        rated_val = rating_map.get(m.rated, 1)

        movie_data.append({
            'id': m.id,
            'desc': desc_text,
            'genres': genre_text,
            'imdb': imdb_val,
            'stats': [runtime, metascore, budget, rated_val],
            'obj': m
        })
    
    df = pd.DataFrame(movie_data)

    # Convert movie descriptions into numerical vectors using TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    desc_matrix = tfidf.fit_transform(df['desc'])
    desc_tensor = torch.tensor(desc_matrix.toarray(), dtype=torch.float32)

    # Convert movie genres into numerical vectors using Count Vectorizer
    # Count Vectorizer is used here because genres are distinct categories
    count_vec = CountVectorizer()
    genre_matrix = count_vec.fit_transform(df['genres'])
    genre_tensor = torch.tensor(genre_matrix.toarray(), dtype=torch.float32)

    # Normalize statistical data columns to a 0-1 range
    stats_tensor = torch.tensor(list(df['stats']), dtype=torch.float32)
    for i in range(stats_tensor.shape[1]):
        col = stats_tensor[:, i]
        min_v, max_v = col.min(), col.max()
        if max_v > min_v:
            stats_tensor[:, i] = (col - min_v) / (max_v - min_v)

    # Normalize IMDb ratings to a 0-1 range
    imdb_tensor = torch.tensor(list(df['imdb']), dtype=torch.float32).unsqueeze(1)
    imdb_tensor = imdb_tensor / 10.0

    # Normalize the description and genre tensors before applying weights
    desc_tensor = F.normalize(desc_tensor, p=2, dim=1)
    genre_tensor = F.normalize(genre_tensor, p=2, dim=1)
    # Stats and IMDb tensors are not re-normalized here to preserve their magnitude after initial scaling
    
    # Combine all feature tensors into a single matrix, applying the configured weights
    combined_tensor = torch.cat((
        desc_tensor * W_DESC, 
        genre_tensor * W_GENRE, 
        imdb_tensor * W_IMDB, 
        stats_tensor * W_STATS
    ), dim=1)

    # Normalize the final combined matrix to facilitate cosine similarity calculations
    final_movie_matrix = F.normalize(combined_tensor, p=2, dim=1)

    # Construct the user profile based on their highly rated movies
    user_ratings = Rating.query.filter(Rating.user_id == user_id, Rating.score >= 7).all()
    liked_ids = [r.movie_id for r in user_ratings]

    # If no ratings exist, use the seen list as a fallback
    if not liked_ids:
        seen = SeenList.query.filter_by(user_id=user_id).limit(5).all()
        liked_ids = [s.movie_id for s in seen]

    if not liked_ids:
        return [] # Return empty if no user history exists to base recommendations on

    # Create the user vector by finding the indices of movies the user liked
    liked_indices = df.index[df['id'].isin(liked_ids)].tolist()
    
    if not liked_indices:
        return []

    # Calculate the average vector of all movies the user liked to create a dynamic preference profile
    user_profile_vector = torch.mean(final_movie_matrix[liked_indices], dim=0, keepdim=True)

    # Calculate similarity scores by comparing the user profile vector against all movie vectors
    similarity_scores = torch.mm(final_movie_matrix, user_profile_vector.t()).flatten()

    # Sort movies by similarity score in descending order
    top_indices = torch.topk(similarity_scores, k=len(movies)).indices.tolist()
    
    recommended = []
    # Fetch lists of movies the user has already seen or rated to exclude them
    seen_ids = [s.movie_id for s in SeenList.query.filter_by(user_id=user_id).all()]
    all_rated_ids = [r.movie_id for r in Rating.query.filter_by(user_id=user_id).all()]
    
    excluded_ids = set(seen_ids + all_rated_ids)

    # Iterate through the top matches and select recommendations that haven't been seen yet
    for idx in top_indices:
        movie_obj = df.iloc[idx]['obj']
        if movie_obj.id not in excluded_ids:
            recommended.append(movie_obj)
        if len(recommended) >= num_recommendations:
            break
            
    return recommended
