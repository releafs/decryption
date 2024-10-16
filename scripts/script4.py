import os

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")

    # Get the absolute path to the root directory (one level up from the script directory)
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    print(f"Root directory: {root_dir}")

    # Get the absolute path to the process directory
    process_dir = os.path.join(root_dir, 'process')
    print(f"Process directory: {process_dir}")

    # List of specific files to delete
    files_to_delete = [
        'decrypted_data.csv',
        'decrypted_data_with_binary.csv',
        'merged_data_with_metadata.csv'
    ]

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
                print(f"File not found (cannot delete): {file_path}")
    else:
        print(f"Process directory does not exist: {process_dir}")

if __name__ == '__main__':
    main()
