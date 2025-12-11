import os
import csv

# Determine the directory where this script is located to handle file paths correctly
current_dir = os.path.dirname(os.path.abspath(__file__))

def clean_csv_duplicates(filename, unique_column='title', delimiter=';'):
    """
    Scans a CSV file and removes rows that have duplicate values in a specified column.
    The function retains the first instance found and discards any subsequent duplicates.
    """
    file_path = os.path.join(current_dir, filename)
    
    # Verify if the target file exists before proceeding
    if not os.path.exists(file_path):
        print(f"  File not found: {filename}. Skipping.")
        return

    print(f"\n--- Processing {filename} ---")
    
    # Initialize lists and sets to track unique data and duplicates
    unique_rows = []
    seen_keys = set()
    duplicates_count = 0
    total_rows = 0
    fieldnames = []

    try:
        # Open the source CSV file for reading
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            fieldnames = reader.fieldnames
            
            # Check if the file is empty or missing headers
            if not fieldnames:
                print(f"Error: {filename} is empty or has no header.")
                return

            # Confirm that the column used for identifying duplicates exists in the headers
            if unique_column not in fieldnames:
                print(f"Error: Column '{unique_column}' not found in {filename}.")
                return

            # Iterate through every row in the file to identify duplicates
            for row in reader:
                total_rows += 1
                # Normalize the data in the unique column by trimming spaces and converting to lowercase
                key = row[unique_column].strip().lower()
                
                # Check if this key has already been processed
                if key in seen_keys:
                    duplicates_count += 1
                else:
                    seen_keys.add(key)
                    unique_rows.append(row)

        # If duplicates were found overwrite the file with the cleaned list of unique rows
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
    # Run the duplicate cleanup function on the main movies database file
    clean_csv_duplicates('csv/movies.csv', unique_column='title')
    
    # Run the duplicate cleanup function on the blacklist file
    clean_csv_duplicates('csv/blacklist.csv', unique_column='title')
