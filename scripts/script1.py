import os
from PIL import Image
import numpy as np

# Directory paths
UPLOAD_FOLDER = './data/uploads/'
OUTPUT_FOLDER = './data/output/'

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Clear the upload directory to avoid old files
def clear_local_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# Clear the directory before starting
clear_local_directory(UPLOAD_FOLDER)

# Function to load parameters (in place of Google Sheets)
def load_parameters():
    dot_colors = [(0, 0, 0), (255, 255, 255)]  # Example DOT_COLORS
    total_dots = 100  # Example TOTAL_DOTS
    return dot_colors, total_dots

# Function to map color to bit
def color_to_bit(color, dot_colors):
    if color == dot_colors[0]:
        return '0'
    elif color == dot_colors[1]:
        return '1'
    else:
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
            adjusted_y = y - 7
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

    latitude_bits = bit_string[0:25]
    longitude_bits = bit_string[25:51]
    date_number_bits = bit_string[51:68]
    impact_quantity_bits = bit_string[68:98]
    project_value_bits = bit_string[98:102]
    impact_value_bits = bit_string[102:106]

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

# Save the decrypted data locally as CSV
def save_to_local_file(decrypted_data):
    output_file = os.path.join(OUTPUT_FOLDER, 'decrypted_data.csv')
    with open(output_file, 'w') as f:
        f.write('Latitude,Longitude,Serial Number,Impact Quantity,Project Type,Impact Unit\n')
        for row in decrypted_data:
            f.write(f"{row['Latitude']},{row['Longitude']},{row['Serial Number']},{row['Impact Quantity']},{row['Project Type']},{row['Impact Unit']}\n")
    print(f"Decrypted data saved to {output_file}")

# Main decryption function
def main():
    # Example parameters and dot positions
    DOT_COLORS, TOTAL_DOTS = load_parameters()
    dot_positions = [(10, 10), (20, 20), (30, 30)]  # Example positions

    # Simulate file upload (use a placeholder PNG in the folder)
    uploaded_files = [file for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.png')]

    if not uploaded_files:
        print("No PNG file uploaded.")
        return

    decrypted_data = []
    # Process each uploaded file
    for file_name in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        bit_string = decrypt_image(file_path, dot_positions, DOT_COLORS, TOTAL_DOTS)
        if bit_string:
            data = parse_bit_string(bit_string)
            if data:
                decrypted_data.append({
                    'Latitude': data['latitude'],
                    'Longitude': data['longitude'],
                    'Serial Number': data['date_number'],
                    'Impact Quantity': data['impact_quantity'],
                    'Project Type': "Sample Project",  # Placeholder
                    'Impact Unit': "Sample Unit"  # Placeholder
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
