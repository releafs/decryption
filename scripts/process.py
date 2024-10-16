import os
import shutil

def delete_and_recreate_process_directory():
    # Use the GITHUB_WORKSPACE environment variable to ensure the path is absolute
    root_dir = os.environ.get('GITHUB_WORKSPACE', os.getcwd())  # GITHUB_WORKSPACE gives the absolute path to the root of the repository
    
    # Set the absolute 'process' directory path
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
