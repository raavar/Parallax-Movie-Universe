# Din app/utility_modules/qr_generator.py (Funcția generate_user_qr_code)
import qrcode
from io import BytesIO
import base64
from flask import url_for # Rămâne importul

# Funcția nu mai primește app_context
def generate_user_qr_code(user_id):
    """
    Generează un QR code care codifică URL-ul profilului utilizatorului.
    Funcția trebuie rulată ÎN INTERIORUL unui context de cerere (request context).
    """
    
    # Acum url_for rulează în contextul cererii existente, nu creează unul nou.
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
    img.save(buffer)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_b64}"