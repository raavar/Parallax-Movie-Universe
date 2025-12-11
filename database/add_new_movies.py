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
    Merges new movies from movies_to_add.csv into movies.csv,
    ensuring uniqueness and skipping movies found in blacklist.csv.
    """
    print("--- Adding New Movies to the Database ---\n")
    
    # Validate Source File
    if not os.path.exists(NEW_MOVIES_CSV_PATH):
        print(f"ERROR: Source file not found: {NEW_MOVIES_CSV_PATH}")
        print("Please create movies_to_add.csv with the new movie data.")
        return

    # --- Load Existing Data & Blacklist ---
    
    # Load the titles that are blacklisted (movies without a good poster)
    blacklist = set()
    if os.path.exists(BLACKLIST_CSV_PATH):
        with open(BLACKLIST_CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=DELIMITER)
            for row in reader:
                blacklist.add(row[UNIQUE_KEY].strip().lower())
        print(f"Loaded {len(blacklist)} titles from the blacklist.")
    else:
        print("blacklist.csv not found. No blacklist applied.")

    # Load existing titles from the database file (movies.csv)
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

    # --- Process New Movies ---
    
    new_rows_to_add = []
    skipped_count = 0
    duplicate_count = 0
    blacklisted_count = 0
    total_new_movies = 0
    
    with open(NEW_MOVIES_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=DELIMITER)
        
        # Ensure the fieldnames match the database file if provided
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
                # The movie is new and not blacklisted, add it
                new_rows_to_add.append(row)
                existing_titles.add(title_key)
    
    # Write Database File (Overwrite) ---
    
    final_rows = database_rows + new_rows_to_add
    
    if new_rows_to_add:
        print(f"\nAdding {len(new_rows_to_add)} new unique movies to the database file.")
        
        # Overwrite movies.csv with the combined list
        with open(DATABASE_CSV_PATH, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=DELIMITER)
            writer.writeheader()
            writer.writerows(final_rows)
            
        print(f"SUCCESS: {os.path.basename(DATABASE_CSV_PATH)} updated with {len(new_rows_to_add)} movies.")
        print(f"   - Total movies remaining: {len(final_rows)}")
    else:
        print("\nNo new unique movies to add.")

    # --- Consume Source File ---
    
    # Empty the movies_to_add.csv file after consuming its content
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
