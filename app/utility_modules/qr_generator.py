import qrcode
from io import BytesIO
import base64
from flask import url_for

def generate_user_qr_code(app_context, user_id):
    """
    Generează un QR code care codifică URL-ul profilului utilizatorului.
    Returnează datele imaginii în format Base64 pentru afișare inline în HTML.
    
    :param app_context: Contextul aplicației Flask (necesar pentru url_for)
    :param user_id: ID-ul unic al utilizatorului
    :return: String Base64 gata de afișat în tag-ul <img>
    """
    # url_for() necesită contextul aplicației. Rulăm în interiorul contextului.
    with app_context:
        # Presupunem că vom avea o rută /profile/<user_id>
        # _external=True asigură că URL-ul este complet (ex: http://localhost:5000/profile/1)
        profile_url = url_for('user_profile', user_id=user_id, _external=True)

    # Creare obiect QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(profile_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salvare în buffer in-memory și conversie la Base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Returnează formatul de date specific HTML <img>
    return f"data:image/png;base64,{img_b64}"