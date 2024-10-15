import os
import csv
from PIL import Image
import numpy as np

# Define the directories relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, 'data'))
INPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, 'input'))
PROCESS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, 'process'))

# Ensure the process directory exists
os.makedirs(PROCESS_DIR, exist_ok=True)

# Load DOT_COLORS and TOTAL_DOTS from the 'inventory.csv' file
def fetch_parameters_from_inventory(inventory_file_path):
    dot_colors = []
    total_dots = None
    with open(inventory_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Parameter'] == 'DOT_COLORS':
                color_tuple = tuple(map(int, row['Value'].strip('()').split(',')))
                dot_colors.append(color_tuple)
            elif row['Parameter'] == 'TOTAL_DOTS':
                total_dots = int(row['Value'])
    return dot_colors, total_dots

# Load dot positions from 'dot_positions.csv'
def load_dot_positions(dot_positions_file_path):
    dot_positions = []
    with open(dot_positions_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            x = int(row['x'])
            y = int(row['y'])
            dot_positions.append((x, y))
    return dot_positions

# Function to map color to bit
def color_to_bit(color, dot_colors):
    if color[:3] == dot_colors[0]:
        return '0'
    elif color[:3] == dot_colors[1]:
        return '1'
    else:
        # Handle color differences due to image processing
        distances = [np.linalg.norm(np.array(color[:3]) - np.array(dc[:3])) for dc in dot_colors]
        closest_color_index = distances.index(min(distances))
        return str(closest_color_index)

# Function to decrypt an image
def decrypt_image(image_path, dot_positions, dot_colors, total_dots):
    try:
        image = Image.open(image_path).convert('RGBA')
        print(f"Processing image: {image_path}")

        bit_string = ''
        for idx, (x, y) in enumerate(dot_positions):
            if idx >= total_dots:
                break  # Only read up to total_dots
            adjusted_y = y - 7  # Adjust y-coordinate if necessary
            color = image.getpixel((x, adjusted_y))
            bit = color_to_bit(color, dot_colors)
            bit_string += bit
        return bit_string
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

# Function to parse the bit string into original data
def parse_bit_string(bit_string):
    if len(bit_string) < 106:
        print("Bit string is shorter than expected.")
        return None
    # Extract bits according to their lengths
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

    original_latitude = (latitude / 100000) - 90
    original_longitude = (longitude / 100000) - 180

    return {
        'latitude': original_latitude,
        'longitude': original_longitude,
        'date_number': date_number,
        'impact_quantity': impact_quantity,
        'project_value': project_value,
        'impact_value': impact_value
    }

# Function to map project and impact values back to their names
def map_values_to_names(project_value, impact_value, creation_file_path):
    project_type = None
    impact_unit = None
    with open(creation_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')  # Assuming TSV format
        for row in reader:
            if 'Project Value' in row and int(row['Project Value']) == project_value:
                project_type = row.get('Project Type', 'Unknown Project Type')
            if 'Impact Value' in row and int(row['Impact Value']) == impact_value:
                impact_unit = row.get('Impact Unit', 'Unknown Impact Unit')
    return project_type or 'Unknown Project Type', impact_unit or 'Unknown Impact Unit'

# Function to save data to 'decrypted_data.csv'
def save_to_csv(data, output_file_path):
    # Define the headers, including the 'Binary Code' column
    headers = ['Latitude', 'Longitude', 'Serial Number', 'Impact Quantity', 'Project Type', 'Impact Unit', 'Binary Code']

    with open(output_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow({
                'Latitude': row['Latitude'],
                'Longitude': row['Longitude'],
                'Serial Number': row['Serial Number'],
                'Impact Quantity': row['Impact Quantity'],
                'Project Type': row['Project Type'],
                'Impact Unit': row['Impact Unit'],
                'Binary Code': row['Binary Code']  # Include the binary code (bit string)
            })

# Main decryption function
def main():
    # File paths
    inventory_file_path = os.path.join(DATA_DIR, 'inventory.csv')
    dot_positions_file_path = os.path.join(DATA_DIR, 'dot_positions.csv')
    creation_file_path = os.path.join(DATA_DIR, 'metadata.tsv')
    output_file_path = os.path.join(PROCESS_DIR, 'decrypted_data_with_binary.csv')

    # Fetch parameters
    DOT_COLORS, TOTAL_DOTS = fetch_parameters_from_inventory(inventory_file_path)
    dot_positions = load_dot_positions(dot_positions_file_path)

    # Check if there are images in the input directory
    input_images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
    if not input_images:
        print("No images found in the input directory.")
        return

    decrypted_data = []
    # Process each image
    for file_name in input_images:
        file_path = os.path.join(INPUT_DIR, file_name)
        bit_string = decrypt_image(file_path, dot_positions, DOT_COLORS, TOTAL_DOTS)
        if bit_string:
            data = parse_bit_string(bit_string)
            if data:
                project_type, impact_unit = map_values_to_names(data['project_value'], data['impact_value'], creation_file_path)
                decrypted_data.append({
    'Latitude': data['latitude'],
    'Longitude': data['longitude'],
    'Serial Number': data['date_number'],
    'Impact Quantity': data['impact_quantity'],
    'Project Type': project_type,
    'Impact Unit': impact_unit,
    'Binary Code': bit_string  # Add the binary code (bit string)
})

                print(f"Decrypted data for {file_name}: {data}")
            else:
                print(f"Failed to parse bit string for {file_name}")
        else:
            print(f"Failed to decrypt {file_name}")

    # Save decrypted data to 'decrypted_data.csv'
    if decrypted_data:
        save_to_csv(decrypted_data, output_file_path)
        print(f"Decrypted data saved to {output_file_path}")
    else:
        print("No data to save.")

# Run the main function
if __name__ == '__main__':
    main()
