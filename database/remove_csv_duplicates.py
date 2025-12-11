import os
import csv

# Defines the current directory (database folder)
current_dir = os.path.dirname(os.path.abspath(__file__))

def clean_csv_duplicates(filename, unique_column='title', delimiter=';'):
    """
    Removes duplicate rows from a CSV file based on a specific unique column.
    It keeps the first occurrence and removes subsequent duplicates.
    """
    file_path = os.path.join(current_dir, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"  File not found: {filename}. Skipping.")
        return

    print(f"\n--- Processing {filename} ---")
    
    unique_rows = []
    seen_keys = set()
    duplicates_count = 0
    total_rows = 0
    fieldnames = []

    try:
        # 1. Read the file
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            fieldnames = reader.fieldnames
            
            if not fieldnames:
                print(f"Error: {filename} is empty or has no header.")
                return

            # Check if the unique column exists in the CSV
            if unique_column not in fieldnames:
                print(f"Error: Column '{unique_column}' not found in {filename}.")
                return

            for row in reader:
                total_rows += 1
                # Normalize key (strip spaces and convert to lowercase for comparison)
                key = row[unique_column].strip().lower()
                
                if key in seen_keys:
                    duplicates_count += 1
                else:
                    seen_keys.add(key)
                    unique_rows.append(row)

        # 2. Write back only if there were duplicates
        if duplicates_count > 0:
            with open(file_path, mode='w', encoding='utf-8', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(unique_rows)
            
            print(f"Cleaned {filename}.")
            print(f"   - Total rows scanned: {total_rows}")
            print(f"   - Duplicates removed: {duplicates_count}")
            print(f"   - Unique rows remaining: {len(unique_rows)}")
        else:
            print(f"No duplicates found in {filename}.")

    except Exception as e:
        print(f"An error occurred while processing {filename}: {e}")

if __name__ == "__main__":
    # Clean the main movie database file
    clean_csv_duplicates('csv/movies.csv', unique_column='title')
    
    # Clean the list of removed movies (if it exists)
    clean_csv_duplicates('csv/blacklist.csv', unique_column='title')
