import os
import shutil

def delete_and_recreate_process_directory():
    process_dir = os.path.join(os.getcwd(), 'process')  # Corrected to the root 'process' directory
    
    # Delete the 'process' directory if it exists
    if os.path.exists(process_dir):
        shutil.rmtree(process_dir)
        print(f"Deleted '{process_dir}' directory successfully.")
    
    # Recreate the 'process' directory
    os.makedirs(process_dir)
    print(f"Created '{process_dir}' directory successfully.")

if __name__ == '__main__':
    delete_and_recreate_process_directory()
