import os
import shutil

# Define the 'process' directory path
process_dir = os.path.join(os.getcwd(), 'process')

# Function to delete and recreate the 'process' directory
def reset_process_directory():
    # Check if the 'process' directory exists
    if os.path.exists(process_dir):
        # Delete the 'process' directory and its contents
        shutil.rmtree(process_dir)
        print(f"Deleted '{process_dir}' directory successfully.")
    
    # Recreate the 'process' directory
    os.makedirs(process_dir)
    print(f"Created '{process_dir}' directory successfully.")

if __name__ == "__main__":
    reset_process_directory()
