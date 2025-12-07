from flask import Blueprint, send_file, url_for, request, abort, current_app
from flask_login import login_required, current_user
# Importați funcțiile necesare pentru generarea QR și export
# from app.utils import generate_qr_code, export_to_csv # Presupunem că aceste funcții sunt în app/utils.py

# Definește Blueprint-ul
utility = Blueprint('utility', __name__)

# RUTA: Exportă lista de filme văzute (sau de vizionat) ca CSV
@utility.route('/export/seen_list', methods=['GET'])
@login_required
def user_profile(user_id):
    # Asigură-te că utilizatorul își vizualizează propriul profil
    if current_user.id != user_id:
        flash('Nu aveți permisiunea de a vizualiza acest profil.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    
    # Generare QR Code (folosind contextul aplicației)
    qr_data_uri = generate_user_qr_code(app.app_context(), user_id)
    
    # Preluare liste de filme (pentru afișare)
    seen_movies = SeenList.query.filter_by(user_id=user_id).all()
    to_watch_movies = ToWatchList.query.filter_by(user_id=user_id).all()

    return render_template('user_profile.html', 
                           title=f'Profil {user.username}', 
                           user=user,
                           qr_data_uri=qr_data_uri,
                           seen_movies=seen_movies,
                           to_watch_movies=to_watch_movies)

# --- Rută nouă: Export date CSV ---

@app.route("/export_seen_list", methods=['GET'])
@login_required
def export_seen_list():
    """Exportă lista 'Văzute' a utilizatorului curent în CSV."""
    
    # Preluare filme văzute (Necesită ca models.py să aibă relația SeenList.movie)
    seen_movies = SeenList.query.filter_by(user_id=current_user.id).all()
    
    if not seen_movies:
        flash('Lista "Văzute" este goală. Nu există date de exportat.', 'warning')
        return redirect(url_for('user_profile', user_id=current_user.id))

    # Apelează modulul de export
    return export_movie_list_to_csv(seen_movies, filename="parallax_seen_list.csv")