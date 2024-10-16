import os

# Absolute path to the process directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
PROCESS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'process'))  # Process directory

# List of specific files to delete
files_to_delete = ['decrypted_data.csv', 'decrypted_data_with_binary.csv', 'merged_data_with_metadata.csv']

# Ensure the process directory exists
if os.path.exists(PROCESS_DIR):
    # Iterate over the list of specific files to delete
    for filename in files_to_delete:
        file_path = os.path.join(PROCESS_DIR, filename)
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
    print(f"Process directory does not exist: {PROCESS_DIR}")
