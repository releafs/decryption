import os
from PIL import Image
import numpy as np
import csv

# Clear the content directory to avoid processing old files
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# Clear /process directory before starting
clear_directory('/process')

# Load DOT_COLORS and TOTAL_DOTS from the 'inventory_sheet.csv'
def fetch_parameters_from_inventory():
    dot_colors = []
    total_dots = None
    with open('/data/inventory_sheet.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['
