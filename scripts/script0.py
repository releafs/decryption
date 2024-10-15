import os
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Your GitHub repository
GITHUB_BRANCH = "main"  # Branch you're using
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Get the GitHub PAT from the environment variable

# Define the input directory in your GitHub repository
input_directory_in_github = "decryption/input/"

# GitHub API URL to upload files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"

# Function to check if the file exists in the GitHub repository
def check_if_file_exists(file_name):
    url = f"{GITHUB_API_URL}{file_name}"
    response = requests.get(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    if response.status_code == 200:
        return response.json().get('sha')  # Return the sha of the existing file
    return None

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content, sha=None):
    # Prepare the data for the GitHub API request
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    commit_message = f"Upload {file_name}"

    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    # If the file exists, add the SHA to update it
    if sha:
        data["sha"] = sha

    url = f"{GITHUB_API_URL}{file_name}"

    # Send the request to upload the file
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

# Example usage (this can be adapted based on how your workflow triggers)
file_name = "example.png"
file_content = b"binary content of the image"
sha = check_if_file_exists(file_name)
response = upload_file_to_github(file_name, file_content, sha)

if response.status_code == 201 or response.status_code == 200:
    print(f"Successfully uploaded {file_name} to GitHub.")
else:
    print(f"Failed to upload {file_name}. Response: {response.text}")
