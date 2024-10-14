import os
import csv

# Function to load the Metadata from 'metadata.csv' in the 'data' folder
def load_metadata():
    metadata_file_path = os.path.join('data', 'metadata.csv')
    with open(metadata_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to load data from 'decrypted_data_with_binary.csv' in the 'process' folder
def load_decrypted_data_with_binary():
    decrypted_data_file_path = os.path.join('process', 'decrypted_data_with_binary.csv')
    with open(decrypted_data_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to clean and compare strings safely, preserving leading zeros
def clean_string(s):
    if not isinstance(s, str):
        s = str(s)  # Convert to string if not already a string
    return s.strip().replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")

# Function to find the matching profile by Serial Number and Bit String in metadata
def find_metadata_by_serial(serial_number, bit_string, metadata_data):
    bit_string_cleaned = clean_string(bit_string)

    for row in metadata_data:
        # Ensure tokenID is treated as a string and stripped of spaces
        token_id = clean_string(row.get('tokenID', ''))

        # Fetch the Bit String and ensure it is treated as a string to preserve leading zeros
        row_bit_string = clean_string(row.get('Bit String', '').zfill(len(bit_string_cleaned)))

        # Check if both Serial Number and Bit String match
        if token_id == str(serial_number).strip() and row_bit_string == bit_string_cleaned:
            return row

    # Return None if no match is found
    return None

# Function to save the merged data into 'merged_data_with_metadata.csv' in the 'process' folder
def save_merged_data_to_csv(data, file_name):
    file_path = os.path.join('process', file_name)
    
    # Define the headers
    headers = ['Latitude', 'Longitude', 'Serial Number', 'Impact Quantity', 'Project Type', 'Impact Unit', 'Binary Code'] + list(data[0].keys())[7:]

    # Save the data to the CSV
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

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
                'Project Type': metadata_row.get('Project Type', 'N/A'),  # From Metadata
                'Impact Unit': metadata_row.get('Impact Unit', 'N/A'),    # From Metadata
                'Binary Code': bit_string
            }

            # Add other metadata fields (skip the first 7 columns to avoid duplication)
            merged_row.update({k: v for k, v in metadata_row.items() if k not in ['tokenID', 'Bit String', 'Project Type', 'Impact Unit']})

            merged_data.append(merged_row)
            matched_count += 1  # Increment the match count
        else:
            print(f"No matching Metadata found for Serial Number: {serial_number} and Bit String: {bit_string}")

    # Save the merged data to 'merged_data_with_metadata.csv' in the 'process' folder
    if matched_count > 0:
        print(f"Successfully matched and merged {matched_count} entries.")
        save_merged_data_to_csv(merged_data, 'merged_data_with_metadata.csv')
    else:
        print("No successful matches found to save.")

# Run the main function
if __name__ == '__main__':
    main()
