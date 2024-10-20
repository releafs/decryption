import os
import csv
import requests
from io import StringIO
from PIL import Image
import numpy as np

# Function to fetch CSV content from a URL
def fetch_csv_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_content = response.content.decode('utf-8')
        return csv_content
    else:
        print(f"Failed to fetch CSV from {url}. Status code: {response.status_code}")
        return None

# URLs of the CSV files (Replace 'your-username' and 'your-repo' with your actual GitHub username and repository)
INVENTORY_CSV_URL = 'https://raw.githubusercontent.com/releafs/decryption/main/data/inventory.csv'
DOT_POSITIONS_CSV_URL = 'https://raw.githubusercontent.com/releafs/decryption/main/data/dot_positions.csv'
CREATION_TSV_URL = 'https://raw.githubusercontent.com/releafs/decryption/main/data/metadata.tsv'

# Define the directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Adjusted directory paths
INPUT_DIR = os.path.join(ROOT_DIR, 'decryption', 'input')  # Adjusted to match script1.py
PROCESS_DIR = os.path.join(ROOT_DIR, 'process')

# Check the paths
print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"ROOT_DIR: {ROOT_DIR}")
print(f"INPUT_DIR: {INPUT_DIR}")
print(f"PROCESS_DIR: {PROCESS_DIR}")

# Ensure the process directory exists
os.makedirs(PROCESS_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)  # Ensure input directory exists

# Load DOT_COLORS and TOTAL_DOTS from the 'inventory.csv' file
def fetch_parameters_from_inventory(inventory_csv_url):
    dot_colors = []
    total_dots = None
    csv_content = fetch_csv_from_url(inventory_csv_url)
    if csv_content is None:
        return dot_colors, total_dots
    csvfile = StringIO(csv_content)
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Parameter'] == 'DOT_COLORS':
            color_tuple = tuple(map(int, row['Value'].strip('()').split(',')))
            dot_colors.append(color_tuple)
        elif row['Parameter'] == 'TOTAL_DOTS':
            total_dots = int(row['Value'])
    return dot_colors, total_dots

# Load dot positions from 'dot_positions.csv'
def load_dot_positions(dot_positions_csv_url):
    dot_positions = []
    csv_content = fetch_csv_from_url(dot_positions_csv_url)
    if csv_content is None:
        return dot_positions
    csvfile = StringIO(csv_content)
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
def map_values_to_names(project_value, impact_value, creation_tsv_url):
    project_type = None
    impact_unit = None
    csv_content = fetch_csv_from_url(creation_tsv_url)
    if csv_content is None:
        return 'Unknown Project Type', 'Unknown Impact Unit'
    csvfile = StringIO(csv_content)
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
        if 'Project Value' in row and int(row['Project Value']) == project_value:
            project_type = row.get('Project Type', 'Unknown Project Type')
        if 'Impact Value' in row and int(row['Impact Value']) == impact_value:
            impact_unit = row.get('Impact Unit', 'Unknown Impact Unit')
    return project_type or 'Unknown Project Type', impact_unit or 'Unknown Impact Unit'

# Function to save data to 'decrypted_data_with_binary.csv'
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
    # URLs of the data files
    inventory_csv_url = INVENTORY_CSV_URL
    dot_positions_csv_url = DOT_POSITIONS_CSV_URL
    creation_tsv_url = CREATION_TSV_URL
    output_file_path = os.path.join(PROCESS_DIR, 'decrypted_data_with_binary.csv')

    # Fetch parameters
    DOT_COLORS, TOTAL_DOTS = fetch_parameters_from_inventory(inventory_csv_url)
    dot_positions = load_dot_positions(dot_positions_csv_url)

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
                project_type, impact_unit = map_values_to_names(data['project_value'], data['impact_value'], creation_tsv_url)
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

    # Save decrypted data to 'decrypted_data_with_binary.csv'
    if decrypted_data:
        save_to_csv(decrypted_data, output_file_path)
        print(f"Decrypted data saved to {output_file_path}")
    else:
        print("No data to save.")

# Run the main function
if __name__ == '__main__':
    main()
