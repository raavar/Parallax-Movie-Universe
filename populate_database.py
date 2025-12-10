import os
import csv
from datetime import date, datetime

from dotenv import load_dotenv
from app import app, database
# Asigură-te că toate modelele necesare sunt importate
from app.models import Movie, Genre, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session 

# Load environment variables from .env file
load_dotenv()

def create_admin_user():
    """Creates a default admin user if it doesn't exist."""
    print("--- Checking Admin User ---")
    
    # We use app_context to access the database
    with app.app_context():
        # Ensure tables exist (Good practice to check here too)
        database.create_all()
        
        # Check if admin already exists
        if User.query.filter_by(email='admin@parallax.com').first():
            print("Admin user already exists. Skipping.")
            return

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
            
# Metodă pentru a popula baza de date cu filme din CSV
def populate_movies_from_csv(csv_file_path='movies.csv'):
    with app.app_context():
        # Asigură-te că tabelele sunt create (inclusiv Movie, Genre și tabela de asociere)
        database.create_all()

        # --- 1. Curățarea Datelor Existente ---
        print("Curățarea tabelelor Movie și Genre...")
        try:
            # Ștergem asocierile Mulți-la-Mulți (prin ștergerea tabelelor)
            database.session.query(Movie).delete()
            database.session.query(Genre).delete()
            
            # Resetarea secvențelor de ID (pentru PostgreSQL)
            # Notă: Dacă folosești SQLite sau MySQL, aceste comenzi trebuie ajustate sau șterse.
            database.session.execute(database.text("ALTER SEQUENCE movie_id_seq RESTART WITH 1"))
            database.session.execute(database.text("ALTER SEQUENCE genre_id_seq RESTART WITH 1"))
            database.session.commit()
            print("Curățare reușită.")
        except Exception as e:
            # Capturăm eroarea la resetarea secvențelor (ex: dacă secvența nu există încă sau nu e PostgreSQL)
            database.session.rollback()
            # Vom continua chiar dacă resetarea secvenței eșuează, presupunând că delete a funcționat.
            # print(f"Avertisment la curățarea secvențelor: {e}") 

        # --- 2. Procesul de Populare ---
        print(f"Populating database with movies and genres from CSV file: {csv_file_path}")

        try:
            # Dicționar pentru a stoca Genurile unice (Nume: Obiect Genre)
            existing_genres = {}
            movies_count = 0

            # CORECȚIA FINALĂ: Folosiți context manager-ul direct pe sesiunea bazei de date.
            with database.session.no_autoflush:
                with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(csv_file, delimiter=';')

                    for row in csv_reader:
                        movies_count += 1
                        
                        # --- PRELUARE DATE (ADĂUGARE CÂMPURI LIPSĂ) ---
                        release_year = int(row['release_year']) if row.get('release_year') else None
                        release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').date() if row.get('release_date') else None
                        
                        # 1. Crează obiectul Movie
                        movie = Movie(
                            title=row['title'],
                            description=row['description'],
                            release_year=release_year,
                            release_date=release_date
                        )
                        
                        # 2. PROCESARE GENURI:
                        # Extrage lista de genuri din string
                        genre_list = [g.strip() for g in row.get('genres', '').split(',') if g.strip()]
                        
                        for genre_name in genre_list:
                            if genre_name not in existing_genres:
                                # 3. Caută/Creează Genul (Avertismentul este rezolvat prin no_autoflush)
                                genre_obj = Genre.query.filter_by(name=genre_name).first() 
                                
                                if not genre_obj:
                                    genre_obj = Genre(name=genre_name)
                                    database.session.add(genre_obj)
                                
                                existing_genres[genre_name] = genre_obj
                            
                            # 4. Asociază Genul cu Filmul
                            movie.genres.append(existing_genres[genre_name])
                            
                        # Adaugă filmul la sesiune
                        database.session.add(movie)
            
            # --- 3. Salvare Finală ---
            database.session.commit()

            print(f"Successfully populated database with {movies_count} movies.")
            print(f"Total {len(existing_genres)} genuri unice create.")


        except FileNotFoundError:
            print(f"Eroare: Fișierul CSV '{csv_file_path}' nu a fost găsit.")
        except IntegrityError:
            database.session.rollback()
            print("Eroare: A apărut o eroare de integritate (date duplicate).")
        except Exception as e:
            database.session.rollback()
            print(f"A apărut o eroare neașteptată: {e}")
            
if __name__ == '__main__':
    # 1. First, create the users (Infrastructure)
    create_admin_user()
    
    # 2. Then, populate the content (Data)
    populate_movies_from_csv()