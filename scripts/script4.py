# scripts/script4.py

import os
import subprocess

def main():
    # Define the directory where the PNG files are located
    INPUT_DIR = os.path.join(os.getcwd(), 'decryption', 'input')

    # List all PNG files in the input directory
    png_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.png')]

    if not png_files:
        print("No PNG files to delete.")
        return

    # Delete each PNG file
    for file_name in png_files:
        file_path = os.path.join(INPUT_DIR, file_name)
        os.remove(file_path)
        print(f"Deleted {file_path}")

    # Configure Git user details
    subprocess.run(['git', 'config', '--global', 'user.email', '"action@github.com"'], check=True)
    subprocess.run(['git', 'config', '--global', 'user.name', '"GitHub Action"'], check=True)

    # Stage the deleted files
    subprocess.run(['git', 'add', '-u', INPUT_DIR], check=True)

    # Commit the changes
    commit_message = 'Delete uploaded PNG files from input directory'
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)

    # Push changes back to the repository
    subprocess.run(['git', 'push'], check=True)
    print("Deleted PNG files have been committed and pushed to the repository.")

if __name__ == '__main__':
    main()
