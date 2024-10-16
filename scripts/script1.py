Check Script1.py

import os
import csv
from PIL import Image
import numpy as np

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Corrected directory paths
UPLOAD_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, 'decryption', 'input'))    # Where PNGs are uploaded (ROOT_DIR, 'decryption', 'input')
OUTPUT_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'process'))  # Where the output CSV will be saved
DATA_FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'data')) 

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to load parameters from 'data/inventory.csv'
def load_parameters():
    dot_colors = []
    total_dots = None
    inventory_file = os.path.join(DATA_FOLDER, 'inventory.csv')
    with open(inventory_file, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Parameter'] == 'DOT_COLORS':
                # Handle multiple color tuples
                colors = row['Value'].split(';')
                for color_str in colors:
                    color_tuple = tuple(map(int, color_str.strip('() ').split(',')))
                    dot_colors.append(color_tuple)
            elif row['Parameter'] == 'TOTAL_DOTS':
                total_dots = int(row['Value'])
    return dot_colors, total_dots

# Function to load dot positions from 'data/dot_positions.csv'
def load_dot_positions():
    dot_positions = []
    dot_positions_file = os.path.join(DATA_FOLDER, 'dot_positions.csv')
    with open(dot_positions_file, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            x = int(row['x'])
            y = int(row['y'])
            dot_positions.append((x, y))
    return dot_positions

# Function to load mappings from 'data/creation.csv'
def load_mappings():
    project_type_map = {}
    impact_unit_map = {}
    creation_file = os.path.join(DATA_FOLDER, 'creation.csv')
    with open(creation_file, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'Project Value' in row and row['Project Value']:
                project_value = int(row['Project Value'])
                project_type = row['PROJECT_TYPE_MAP']
                project_type_map[project_value] = project_type
            if 'Impact Value' in row and row['Impact Value']:
                impact_value = int(row['Impact Value'])
                impact_unit = row['IMPACT_UNIT_MAP']
                impact_unit_map[impact_value] = impact_unit
    return project_type_map, impact_unit_map

# Function to map color to bit
def color_to_bit(color, dot_colors):
    if color[:3] == dot_colors[0]:
        return '0'
    elif color[:3] == dot_colors[1]:
        return '1'
    else:
        # Handle cases where the color isn't exactly matching by finding the closest color
        distances = [np.linalg.norm(np.array(color[:3]) - np.array(dc)) for dc in dot_colors]
        closest_color_index = distances.index(min(distances))
        return str(closest_color_index)

# Function to decrypt an image
def decrypt_image(image_path, dot_positions, dot_colors, total_dots):
    try:
        image = Image.open(image_path).convert('RGBA')  # Ensure the image is in RGBA format
        print(f"Processing image: {image_path}")

        bit_string = ''
        for idx, (x, y) in enumerate(dot_positions):
            if idx >= total_dots:
                break  # Only process up to total_dots
            adjusted_y = y - 7  # Adjust for any potential offset
            color = image.getpixel((x, adjusted_y))
            bit = color_to_bit(color, dot_colors)
            bit_string += bit

        # Ensure bit string is padded to the correct length (106 bits)
        if len(bit_string) < 106:
            bit_string = bit_string.zfill(106)  # Pad with leading zeros if necessary
        return bit_string
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

# Function to parse the bit string into original data
def parse_bit_string(bit_string):
    if len(bit_string) < 106:
        print("Bit string is shorter than expected after padding.")
        return None

    # Extract bits according to the expected lengths
    latitude_bits = bit_string[0:25]
    longitude_bits = bit_string[25:51]
    date_number_bits = bit_string[51:68]
    impact_quantity_bits = bit_string[68:98]
    project_value_bits = bit_string[98:102]
    impact_value_bits = bit_string[102:106]

    # Convert binary strings to integers
    latitude = int(latitude_bits, 2)
    longitude = int(longitude_bits, 2)
    date_number = int(date_number_bits, 2)
    impact_quantity = int(impact_quantity_bits, 2)
    project_value = int(project_value_bits, 2)
    impact_value = int(impact_value_bits, 2)

    original_latitude = (latitude / 100000) - 90  # Decode latitude
    original_longitude = (longitude / 100000) - 180  # Decode longitude

    return {
        'latitude': original_latitude,
        'longitude': original_longitude,
        'date_number': date_number,
        'impact_quantity': impact_quantity,
        'project_value': project_value,
        'impact_value': impact_value
    }

# Function to save the decrypted data locally as a CSV file
def save_to_local_file(decrypted_data):
    output_file = os.path.join(OUTPUT_FOLDER, 'decrypted_data.csv')
    with open(output_file, 'w', newline='') as f:
        # Write the headers
        f.write('Latitude,Longitude,Serial Number,Impact Quantity,Project Type,Impact Unit\n')
        # Write each row of data
        for row in decrypted_data:
            f.write(f"{row['latitude']},{row['longitude']},{row['date_number']},{row['impact_quantity']},{row['project_type']},{row['impact_unit']}\n")
    print(f"Decrypted data saved to: {output_file}")

# Main decryption function
def main():
    # Load parameters and mappings
    DOT_COLORS, TOTAL_DOTS = load_parameters()
    dot_positions = load_dot_positions()
    project_type_map, impact_unit_map = load_mappings()

    # Check for uploaded PNG files in the input folder
    uploaded_files = [file for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.png')]

    if not uploaded_files:
        print(f"No PNG files found in {UPLOAD_FOLDER}.")
        return

    decrypted_data = []
    # Process each uploaded file
    for file_name in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        bit_string = decrypt_image(file_path, dot_positions, DOT_COLORS, TOTAL_DOTS)
        if bit_string:
            data = parse_bit_string(bit_string)
            if data:
                project_type = project_type_map.get(data['project_value'], 'Unknown Project Type')
                impact_unit = impact_unit_map.get(data['impact_value'], 'Unknown Impact Unit')
                decrypted_data.append({
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'date_number': data['date_number'],
                    'impact_quantity': data['impact_quantity'],
                    'project_type': project_type,
                    'impact_unit': impact_unit
                })
                print(f"Decrypted data for {file_name}: {data}")
            else:
                print(f"Failed to parse bit string for {file_name}")
        else:
            print(f"Failed to decrypt {file_name}")

    # Save decrypted data locally
    if decrypted_data:
        save_to_local_file(decrypted_data)

# Run the main function
if __name__ == '__main__':
    main()

