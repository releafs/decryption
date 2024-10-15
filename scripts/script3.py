import os
import csv

# Define the directories relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
PROCESS_DIR = os.path.join(SCRIPT_DIR, 'process')

# Ensure the process directory exists
os.makedirs(PROCESS_DIR, exist_ok=True)

# Function to load the Metadata from 'metadata.tsv'
def load_metadata():
    metadata_file_path = os.path.join(DATA_DIR, 'metadata.tsv')
    metadata_data = []
    with open(metadata_file_path, mode='r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            metadata_data.append(row)
    return metadata_data

# Function to load data from 'decrypted_data_with_binary.csv'
def load_decrypted_data_with_binary():
    decrypted_data_file_path = os.path.join(PROCESS_DIR, 'decrypted_data_with_binary.csv')
    decrypted_data = []
    with open(decrypted_data_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            decrypted_data.append(row)
    return decrypted_data

# Function to clean and compare strings safely, preserving leading zeros
def clean_string(s):
    if not isinstance(s, str):
        s = str(s)  # Convert to string if not already a string
    return s.strip().replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")

# Function to find the matching profile by Serial Number and Bit String
def find_metadata_by_serial(serial_number, bit_string, metadata_data):
    bit_string_cleaned = clean_string(bit_string)
    
    for row in metadata_data:
        # Ensure tokenID is treated as a string and stripped of spaces
        token_id = str(row.get('tokenID', '')).strip()

        # Fetch the Bit String from the 'Bit String' column and ensure it is treated as a string to preserve leading zeros
        row_bit_string = clean_string(str(row.get('Bit String', '')).zfill(len(bit_string_cleaned)))
        
        # Check if both the Serial Number and Bit String match
        if token_id == str(serial_number).strip() and row_bit_string == bit_string_cleaned:
            return row
        
    # Return None if no match is found
    return None

# Function to save the merged data to 'merged_data_with_metadata.csv'
def save_to_csv(data):
    output_file_path = os.path.join(PROCESS_DIR, 'merged_data_with_metadata.csv')
    # Define the headers
    if not data:
        print("No data to save.")
        return
    headers = ['Latitude', 'Longitude', 'Serial Number', 'Impact Quantity', 'Project Type', 'Impact Unit', 'Binary Code'] + [k for k in data[0].keys() if k not in ['Latitude', 'Longitude', 'Serial Number', 'Impact Quantity', 'Project Type', 'Impact Unit', 'Binary Code']]

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Merged data saved to {output_file_path}")

# Main function to load data, match with Metadata, and save the result
def main():
    # Load the Metadata
    metadata_data = load_metadata()
    
    # Load the data from 'decrypted_data_with_binary.csv'
    decrypted_data = load_decrypted_data_with_binary()
    merged_data = []
    matched_count = 0
    
    for row in decrypted_data:
        bit_string = row['Binary Code']
        serial_number = row['Serial Number']
        
        # Search for matching metadata using Serial Number and Bit String
        metadata_row = find_metadata_by_serial(serial_number, bit_string, metadata_data)
        if metadata_row:
            # Merge the row data with the corresponding metadata
            merged_row = {
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude'],
                'Serial Number': serial_number,
                'Impact Quantity': row['Impact Quantity'],
                'Project Type': row.get('Project Type', 'Unknown Project Type'),
                'Impact Unit': row.get('Impact Unit', 'Unknown Impact Unit'),
                'Binary Code': bit_string
            }
            
            # Add other metadata fields (excluding duplicates)
            for k, v in metadata_row.items():
                if k not in merged_row:
                    merged_row[k] = v
            
            merged_data.append(merged_row)
            matched_count += 1  # Increment the match count
        else:
            print(f"No matching metadata found for Serial Number: {serial_number} and Bit String: {bit_string}")
    
    # Save the merged data to 'merged_data_with_metadata.csv'
    if matched_count > 0:
        print(f"Successfully matched and merged {matched_count} entries.")
        save_to_csv(merged_data)
    else:
        print("No successful matches found to save.")

# Run the main function
if __name__ == '__main__':
    main()
