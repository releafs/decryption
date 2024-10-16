import os
import shutil

def delete_and_recreate_process_directory():
    # Navigate to the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))  # Get the root directory of the script
    
    # Set the correct 'process' directory under the root
    process_dir = os.path.join(root_dir, 'process')
    
    # Delete the 'process' directory if it exists
    if os.path.exists(process_dir):
        shutil.rmtree(process_dir)
        print(f"Deleted '{process_dir}' directory successfully.")
    
    # Recreate the 'process' directory
    os.makedirs(process_dir)
    print(f"Created '{process_dir}' directory successfully.")

if __name__ == '__main__':
    delete_and_recreate_process_directory()
