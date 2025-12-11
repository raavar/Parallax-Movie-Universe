import os
import csv

# Define the directory where the CSV files are located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define file paths
DATABASE_CSV_PATH = os.path.join(CURRENT_DIR, 'csv', 'movies.csv')
NEW_MOVIES_CSV_PATH = os.path.join(CURRENT_DIR, 'csv', 'movies_to_add.csv')
BLACKLIST_CSV_PATH = os.path.join(CURRENT_DIR, 'csv', 'blacklist.csv')

# Define the column used for identifying duplicates
UNIQUE_KEY = 'title'
DELIMITER = ';'

def add_new_movies():
    """
    Reads the file containing new movies and merges them into the main movies CSV file.
    This process ensures no duplicates are added and respects the blacklist file.
    """
    print("--- Adding New Movies to the Database ---\n")
    
    # Check if the source file for new movies exists before proceeding
    if not os.path.exists(NEW_MOVIES_CSV_PATH):
        print(f"ERROR: Source file not found: {NEW_MOVIES_CSV_PATH}")
        print("Please create movies_to_add.csv with the new movie data.")
        return

    # Load the list of blacklisted titles which are movies previously removed or flagged
    blacklist = set()
    if os.path.exists(BLACKLIST_CSV_PATH):
        with open(BLACKLIST_CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=DELIMITER)
            for row in reader:
                blacklist.add(row[UNIQUE_KEY].strip().lower())
        print(f"Loaded {len(blacklist)} titles from the blacklist.")
    else:
        print("blacklist.csv not found. No blacklist applied.")

    # Load the existing movies from the main database file to prevent duplicates
    database_rows = []
    existing_titles = set()
    fieldnames = None
    
    with open(DATABASE_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        fieldnames = reader.fieldnames
        for row in reader:
            database_rows.append(row)
            existing_titles.add(row[UNIQUE_KEY].strip().lower())
    
    print(f"Loaded {len(database_rows)} existing movies from {os.path.basename(DATABASE_CSV_PATH)}.")

    # Process the new movies file and filter out duplicates or blacklisted items
    new_rows_to_add = []
    skipped_count = 0
    duplicate_count = 0
    blacklisted_count = 0
    total_new_movies = 0
    
    with open(NEW_MOVIES_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        
        # If the main database file was empty or missing, use headers from the new file
        if fieldnames is None:
             fieldnames = reader.fieldnames 
             
        for row in reader:
            total_new_movies += 1
            title_key = row[UNIQUE_KEY].strip().lower()
            
            if title_key in existing_titles:
                duplicate_count += 1
                skipped_count += 1
            elif title_key in blacklist:
                blacklisted_count += 1
                skipped_count += 1
            else:
                # The movie is unique and safe to add so append it to the list
                new_rows_to_add.append(row)
                existing_titles.add(title_key)
    
    # Combine the existing movies with the valid new movies and overwrite the database file
    final_rows = database_rows + new_rows_to_add
    
    if new_rows_to_add:
        print(f"\nAdding {len(new_rows_to_add)} new unique movies to the database file.")
        
        with open(DATABASE_CSV_PATH, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=DELIMITER)
            writer.writeheader()
            writer.writerows(final_rows)
            
        print(f"SUCCESS: {os.path.basename(DATABASE_CSV_PATH)} updated with {len(new_rows_to_add)} movies.")
        print(f"   - Total movies remaining: {len(final_rows)}")
    else:
        print("\nNo new unique movies to add.")

    # Clear the contents of the source file to indicate processing is complete
    with open(NEW_MOVIES_CSV_PATH, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=DELIMITER)
        writer.writeheader()
    
    print(f"Source file {os.path.basename(NEW_MOVIES_CSV_PATH)} has been consumed and reset.")

    print("\n--- Summary ---")
    print(f"Total movies processed for addition: {total_new_movies}")
    print(f"Skipped (Already in movies.csv): {duplicate_count}")
    print(f"Skipped (Blacklisted): {blacklisted_count}")
    print(f"Successfully Added to Database: {len(new_rows_to_add)}")

if __name__ == "__main__":
    add_new_movies()
