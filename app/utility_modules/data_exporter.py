import pandas as pd
from io import StringIO
from flask import make_response

def export_movie_list_to_csv(data_list, filename="movie_export.csv"):
    """
    Converște o listă de obiecte ORM (ex: SeenList, ToWatchList) într-un răspuns CSV.
    Datele sunt formatate într-un fișier descărcabil.
    
    :param data_list: Lista de obiecte (de obicei SeenList sau ToWatchList)
    :param filename: Numele fișierului de descărcat
    :return: Răspuns Flask (Response object) cu datele CSV
    """
    if not data_list:
        data = [{"Message": "Nu au fost găsite date pentru export."}]
    else:
        data = []
        for item in data_list:
            # Asigurăm că relația 'movie' este disponibilă (definiți relația 'backref' în models.py)
            movie = item.movie # Presupunem o relație definită sau încercăm item.movie
            
            movie_data = {
                'ID Film': item.movie_id,
                'Titlu': movie.title,
                'An Lansare': movie.release_year,
                'Data Adaugarii': item.date_added.strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(movie_data)

    # Creează un DataFrame Pandas
    df = pd.DataFrame(data)

    # Salvează în CSV într-un buffer in-memory (StringIO)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Creează răspunsul Flask pentru descărcare
    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    return response