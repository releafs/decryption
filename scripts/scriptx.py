import os
import requests
from requests.auth import HTTPBasicAuth

# Define the directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
PROCESS_DIR = os.path.join(ROOT_DIR, 'process')

# GitHub API information
GITHUB_REPO = "releafs/decryption"  # Replace with your repository details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Token should be provided via environment variables
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts"

# Print statements for debugging
print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"ROOT_DIR: {ROOT_DIR}")
print(f"PROCESS_DIR: {PROCESS_DIR}")

# List of specific files to delete
files_to_delete = ['decrypted_data.csv', 'decrypted_data_with_binary.csv', 'merged_data_with_metadata.csv']

# Function to delete local CSV files
def delete_local_files():
    if os.path.exists(PROCESS_DIR):
        # Iterate over the list of specific files to delete
        for filename in files_to_delete:
            file_path = os.path.join(PROCESS_DIR, filename)
            print(f"Checking for file: {file_path}")
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

# Function to delete artifacts from GitHub
def delete_github_artifacts():
    if not GITHUB_TOKEN:
        print("GitHub token is not set.")
        return
    
    # Fetch all artifacts from the repository
    response = requests.get(GITHUB_API_URL, auth=HTTPBasicAuth('username', GITHUB_TOKEN))  # Replace 'username' with your GitHub username
    if response.status_code == 200:
        artifacts = response.json().get('artifacts', [])
        if not artifacts:
            print("No artifacts found.")
            return
        
        # Iterate over the artifacts and delete them
        for artifact in artifacts:
            artifact_id = artifact['id']
            delete_url = f"{GITHUB_API_URL}/{artifact_id}"
            print(f"Deleting artifact: {artifact['name']} (ID: {artifact_id})")
            delete_response = requests.delete(delete_url, auth=HTTPBasicAuth('username', GITHUB_TOKEN))  # Replace 'username'
            if delete_response.status_code == 204:
                print(f"Artifact {artifact['name']} deleted successfully.")
            else:
                print(f"Failed to delete artifact {artifact['name']}. Status code: {delete_response.status_code}")
    else:
        print(f"Failed to fetch artifacts. Status code: {response.status_code}")

# Main script logic
if __name__ == "__main__":
    # First, delete the local CSV files
    delete_local_files()

    # Then, delete the artifacts from GitHub
    delete_github_artifacts()
