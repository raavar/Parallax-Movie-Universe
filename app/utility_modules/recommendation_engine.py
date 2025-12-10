import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from app.models import Movie, Rating, SeenList

def get_recommendations(user_id, num_recommendations=4):
    movies = Movie.query.all()
    if not movies: return []

    # --- CONFIGURATION: THE RECIPE ---
    # You wanted IMDb to be "really relevant" and Genres > Description
    W_IMDB  = 0.40   # Huge weight on quality
    W_GENRE = 0.30   # High weight on category
    W_STATS = 0.20   # Medium weight on Budget/Runtime/Meta
    W_DESC  = 0.10   # Low weight on specific words
    # ---------------------------------

    movie_data = []
    for m in movies:
        # 1. Clean Text (Description vs Genre)
        desc_text = f"{m.title} {m.description}"
        genre_text = " ".join([g.name for g in m.genres])
        
        # 2. Clean Stats
        runtime = m.runtime_minutes if m.runtime_minutes else 90
        metascore = m.meta_score if m.meta_score else 50
        budget = m.box_office if m.box_office else 0
        
        # 3. Clean IMDb (Crucial Step)
        try:
            imdb_val = float(m.imdb_rating) if m.imdb_rating and m.imdb_rating != 'N/A' else 5.0
        except:
            # If a score is not found we default to 5.0(neutral)
            imdb_val = 5.0

        # Categorical Rated
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

    # --- A. VECTORIZE DESCRIPTION (TF-IDF) ---
    tfidf = TfidfVectorizer(stop_words='english')
    desc_matrix = tfidf.fit_transform(df['desc'])
    desc_tensor = torch.tensor(desc_matrix.toarray(), dtype=torch.float32)

    # --- B. VECTORIZE GENRES (Count Vectorizer) ---
    # We use Count instead of TF-IDF because genres are absolute categories
    count_vec = CountVectorizer()
    genre_matrix = count_vec.fit_transform(df['genres'])
    genre_tensor = torch.tensor(genre_matrix.toarray(), dtype=torch.float32)

    # --- C. NORMALIZE STATS ---
    stats_tensor = torch.tensor(list(df['stats']), dtype=torch.float32)
    # Normalize columns (0-1)
    for i in range(stats_tensor.shape[1]):
        col = stats_tensor[:, i]
        min_v, max_v = col.min(), col.max()
        if max_v > min_v:
            stats_tensor[:, i] = (col - min_v) / (max_v - min_v)

    # --- D. NORMALIZE IMDB (The Heavy Hitter) ---
    imdb_tensor = torch.tensor(list(df['imdb']), dtype=torch.float32).unsqueeze(1)
    # Normalize (0-10 -> 0-1)
    imdb_tensor = imdb_tensor / 10.0

    # --- E. THE ASSEMBLY (Applying Weights) ---
    # Normalize each block first so they are mathematically fair
    desc_tensor = F.normalize(desc_tensor, p=2, dim=1)
    genre_tensor = F.normalize(genre_tensor, p=2, dim=1)
    # Stats and IMDb are already 0-1, so we skip L2 norm for them to keep magnitude
    
    combined_tensor = torch.cat((
        desc_tensor * W_DESC, 
        genre_tensor * W_GENRE, 
        imdb_tensor * W_IMDB, 
        stats_tensor * W_STATS
    ), dim=1)

    # Final Unit Normalization (Crucial for Cosine Similarity)
    final_movie_matrix = F.normalize(combined_tensor, p=2, dim=1)

    # --- F. DYNAMIC USER PROFILE ---
    # 1. Get user's high rated movies
    user_ratings = Rating.query.filter(Rating.user_id == user_id, Rating.score >= 7).all()
    liked_ids = [r.movie_id for r in user_ratings]

    # Fallback to seen list
    if not liked_ids:
        seen = SeenList.query.filter_by(user_id=user_id).limit(5).all()
        liked_ids = [s.movie_id for s in seen]

    if not liked_ids:
        return [] # Cold start handled by route

    # 2. Build the "User Vector"
    # Find the indices of movies the user likes
    liked_indices = df.index[df['id'].isin(liked_ids)].tolist()
    
    if not liked_indices:
        return []

    # Calculate the AVERAGE vector of all liked movies
    # This is the "Dynamic" part. If you like 3 Horror movies, this vector moves to Horror land.
    user_profile_vector = torch.mean(final_movie_matrix[liked_indices], dim=0, keepdim=True)

    # --- G. CALCULATE SIMILARITY ---
    # Compare the User Vector vs All Movies
    # Result is a list of scores: How close is every movie to YOUR specific taste?
    similarity_scores = torch.mm(final_movie_matrix, user_profile_vector.t()).flatten()

    # --- H. FILTER & RETURN ---
    top_indices = torch.topk(similarity_scores, k=len(movies)).indices.tolist()
    
    recommended = []
    seen_ids = [s.movie_id for s in SeenList.query.filter_by(user_id=user_id).all()]
    all_rated_ids = [r.movie_id for r in Rating.query.filter_by(user_id=user_id).all()]
    
    excluded_ids = set(seen_ids + all_rated_ids)

    for idx in top_indices:
        movie_obj = df.iloc[idx]['obj']
        if movie_obj.id not in excluded_ids:
            recommended.append(movie_obj)
        if len(recommended) >= num_recommendations:
            break
            
    return recommended