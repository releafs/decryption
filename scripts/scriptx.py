import os

# Define the process directory path
process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'process')

# List of specific files to delete
files_to_delete = ['decrypted_data.csv', 'decrypted_data_with_binary.csv', 'merged_data_with_metadata.csv']

# Ensure the process directory exists
if os.path.exists(process_dir):
    # Iterate over the list of specific files to delete
    for filename in files_to_delete:
        file_path = os.path.join(process_dir, filename)
        # Check if the file exists and delete it
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        else:
            print(f"File not found: {file_path}")
else:
    print(f"Process directory does not exist: {process_dir}")
