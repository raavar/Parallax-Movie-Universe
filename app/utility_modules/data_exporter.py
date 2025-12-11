import pandas as pd
from io import StringIO
from flask import make_response

def export_movie_list_to_csv(data_list, filename="movie_export.csv"):
    """
    Converts a list of ORM objects (e.g., SeenList, ToWatchList) into a CSV response.
    The data is formatted into a downloadable file.
    
    :param data_list: List of objects (usually SeenList or ToWatchList)
    :param filename: The name of the file to download
    :return: Flask Response object with CSV data
    """
    if not data_list:
        data = [{"Message": "Nu au fost găsite date pentru export."}]
    else:
        data = []
        for item in data_list:
            # Ensure the 'movie' relationship is available (define 'backref' in models.py)
            movie = item.movie # Assume a defined relationship or try accessing item.movie
            
            movie_data = {
                'ID Film': item.movie_id,
                'Titlu': movie.title,
                'An Lansare': movie.release_year,
                'Data Adaugarii': item.date_added.strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(movie_data)

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Save to CSV in an in-memory buffer (StringIO)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Create the Flask response for download
    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    return response
