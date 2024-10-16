import os
import subprocess
import shutil

def main():
    # Define the directory where the PNG files are located
    INPUT_DIR = os.path.join(os.getcwd(), 'decryption', 'input')

    if not os.path.exists(INPUT_DIR):
        print(f"The directory {INPUT_DIR} does not exist.")
        return

    # List all PNG files in the input directory
    png_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.png')]

    if png_files:
        # Delete each PNG file
        for file_name in png_files:
            file_path = os.path.join(INPUT_DIR, file_name)
            os.remove(file_path)
            print(f"Deleted {file_path}")
    else:
        print("No PNG files to delete.")

    # Delete the input directory itself
    try:
        shutil.rmtree(INPUT_DIR)
        print(f"Deleted directory: {INPUT_DIR}")
    except Exception as e:
        print(f"Failed to delete directory {INPUT_DIR}. Reason: {e}")
        return

    # Configure Git user details
    subprocess.run(['git', 'config', '--global', 'user.email', 'action@github.com'], check=True)
    subprocess.run(['git', 'config', '--global', 'user.name', 'GitHub Action'], check=True)

    # Stage the deleted files and directory
    subprocess.run(['git', 'add', '-u'], check=True)

    # Commit the changes
    commit_message = 'Delete uploaded PNG files and input directory'
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)

    # Push changes back to the repository
    subprocess.run(['git', 'push'], check=True)
    print("Deleted PNG files and input directory have been committed and pushed to the repository.")

if __name__ == '__main__':
    main()
