from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin                       # NOU
from flask_admin.contrib.sqla import ModelView      # NOU
from flask_admin import AdminIndexView              # NOU: Import necesar
from flask_mail import Mail
from app.config import Config


# --- 2. Inițializarea Aplicației și Extensiilor ---
app = Flask(__name__)
app.config.from_object(Config)
database = SQLAlchemy(app)
login_manager = LoginManager(app)

# Initialize Mail
mail = Mail(app)


# --- 1. Definirea Clasei Rădăcină (Index View) ---
# Aceasta restricționează accesul la /admin
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))


# --- 1. Definirea Claselor de Vizualizare Restricționată ---
class RestrictedModelView(ModelView):
    def is_accessible(self):
        # Aplică logica de restricție (folosită de toate vizualizările)
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

    # Adăugăm _handle_view pentru a forța verificarea is_accessible la orice acțiune de model (inclusiv root)
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return self.inaccessible_callback(name, **kwargs)


class RatingView(RestrictedModelView):
    # Coloanele de listare (folosesc relațiile 'user' și 'movie' unificate)
    column_list = ('id', 'user', 'movie', 'score', 'timestamp') 
    # Filtru simplificat pentru a evita AttributeErrors la inițializare
    column_filters = ('score',) 


class ListView(RestrictedModelView):
    # Coloanele de listare (folosesc relațiile 'user' și 'movie' unificate)
    column_list = ('id', 'user', 'movie', 'date_added') 
    # Filtru simplificat
    column_filters = ()


# --- 3. Inițializarea Flask-Admin ---
# CORECȚIE CRITICĂ: Inițializăm cu clasa MyAdminIndexView
admin = Admin(app, 
              name='Parallax Admin', 
              template_mode='bootstrap3',
              index_view=MyAdminIndexView())


# --- 4. Import Modele & Adăugare Vizualizări ---
# MUTĂ Importul AICI (după ce 'app' și 'database' sunt definite)
from app.models import User, Movie, Rating, SeenList, ToWatchList 

# Adaugă Vizualizările Modelelor (folosind clasele personalizate)
admin.add_view(RestrictedModelView(User, database.session, name="1. Utilizatori"))
admin.add_view(RestrictedModelView(Movie, database.session, name="2. Catalog Filme"))
admin.add_view(RatingView(Rating, database.session, name="3. Ratinguri"))
admin.add_view(ListView(SeenList, database.session, name="4. Liste Văzute"))
admin.add_view(ListView(ToWatchList, database.session, name="5. Liste De Văzut"))


# --- 5. User Loader & Routes ---
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    # User este acum disponibil
    return User.query.get(int(user_id))

# Import routes to register them with the application (ULTIMA LINIE)
from app import routes