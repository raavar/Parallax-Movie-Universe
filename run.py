import os
from dotenv import load_dotenv

# Load environment variables from the .env file to configure the application
load_dotenv()

# Import the Flask application instance and the database object from the app package
from app import app, database

if __name__ == '__main__':
    # Check if the script is executed directly rather than being imported as a module
    # This ensures the server only starts when running this specific file
    
    with app.app_context():
        # Establish an application context to allow access to the database configuration
        # Create the database tables defined in the models if they do not already exist
        database.create_all()
        print("Database tables were created successfully.")     # Print a confirmation message to the console
    
    # Start the Flask development server with debugging enabled
    app.run(debug=True)
    print("Application is running locally.")
