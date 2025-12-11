from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_mail import Mail
from app.config import Config


# Initialize Application and Extensions
app = Flask(__name__)
app.config.from_object(Config)
database = SQLAlchemy(app)
login_manager = LoginManager(app)

# Initialize Mail
mail = Mail(app)


# Definition of Root Class (Index View)
# This restricts access to the /admin route
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin
        
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))


# Definition of Restricted View Classes
class RestrictedModelView(ModelView):
    def is_accessible(self):
        # Applies restriction logic (used by all views)
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

    # Add _handle_view to force is_accessible check on any model action (including root)
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return self.inaccessible_callback(name, **kwargs)


class RatingView(RestrictedModelView):
    # Listing columns (uses unified 'user' and 'movie' relationships)
    column_list = ('id', 'user', 'movie', 'score', 'timestamp') 
    # Simplified filter to avoid AttributeErrors during initialization
    column_filters = ('score',) 


class ListView(RestrictedModelView):
    # Listing columns (uses unified 'user' and 'movie' relationships)
    column_list = ('id', 'user', 'movie', 'date_added') 
    # Simplified filter
    column_filters = ()


# Initialize Flask-Admin
# We initialize with the MyAdminIndexView class
admin = Admin(app, 
              name='Parallax Admin', 
              template_mode='bootstrap3',
              index_view=MyAdminIndexView())


# Import Models and Add Views
# Import moved here (after 'app' and 'database' are defined)
from app.models import User, Movie, Rating, SeenList, ToWatchList 

# Add Model Views (using custom classes)
admin.add_view(RestrictedModelView(User, database.session, name="1. Users"))
admin.add_view(RestrictedModelView(Movie, database.session, name="2. Movie Catalog"))
admin.add_view(RatingView(Rating, database.session, name="3. Ratings"))
admin.add_view(ListView(SeenList, database.session, name="4. Seen Lists"))
admin.add_view(ListView(ToWatchList, database.session, name="5. To Watch Lists"))


# User Loader and Routes
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    # User is now available
    return User.query.get(int(user_id))

# Import routes to register them with the application (Last line)
from app import routes
