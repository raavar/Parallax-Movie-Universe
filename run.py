import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Import the main application and database from the app module
from app import app, database

if __name__ == '__main__':
    # Local running logic
    # It runs only with python run.py

    with app.app_context():
        # Create database tables
        database.create_all()
        print("Database tables were created successfully.")     # Log success message
    
    # Run the Flask application
    app.run(debug=True)
    print("Application is running locally.")
