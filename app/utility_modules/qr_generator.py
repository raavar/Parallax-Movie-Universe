# From app/utility_modules/qr_generator.py (Function generate_user_qr_code)
import qrcode
from io import BytesIO
import base64
from flask import url_for # Import remains

# The function no longer requires app_context as an argument
def generate_user_qr_code(user_id):
    """
    Generates a QR code that encodes the URL of the user's profile.
    This function must be executed within an active Flask request context.
    """
    
    # Generate the absolute URL for the user profile using the current request context
    profile_url = url_for('user_profile', user_id=user_id, _external=True)

    # Initialize the QR code object with specific sizing parameters
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(profile_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to an in-memory buffer and convert it to a Base64 string
    buffer = BytesIO()
    img.save(buffer)
    img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_b64}"
