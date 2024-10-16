import os

# Define the process directory path
process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'process')

# Ensure the process directory exists
if os.path.exists(process_dir):
    # Get the list of all files in the process directory
    for filename in os.listdir(process_dir):
        # If the file ends with .csv, remove it
        if filename.endswith(".csv"):
            file_path = os.path.join(process_dir, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
else:
    print(f"Process directory does not exist: {process_dir}")
