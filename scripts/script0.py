import os
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Replace with your repository name
GITHUB_BRANCH = "main"  # Replace with your branch name
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Use Streamlit secrets to store your GitHub token securely

# Define the input directory in your GitHub repository
input_directory_in_github = "decryption/input/"

# GitHub API URL to upload files and check for existing files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"

# Function to check if the file exists in the GitHub repository
def check_if_file_exists(file_name):
    url = f"{GITHUB_API_URL}{file_name}"
    response = requests.get(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    if response.status_code == 200:
        return response.json().get('sha')  # Return the SHA of the existing file if found
    return None

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content, sha=None):
    encoded_content = base64.b64encode(file_content).decode("utf-8")  # Base64 encode the file content
    commit_message = f"Upload {file_name}"  # Commit message

    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    # If the file already exists, include the SHA to update it
    if sha:
        data["sha"] = sha

    url = f"{GITHUB_API_URL}{file_name}"  # GitHub API URL for the file

    # Send the request to upload the file to GitHub
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

# Streamlit File Uploader
st.title("Upload a PNG File to GitHub")

# File uploader widget in Streamlit
uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

if uploaded_file is not None:
    # Display the file name and size
    st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    
    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()  # Get the content of the file

    # Check if the file already exists in the GitHub repository
    sha = check_if_file_exists(file_name)

    if sha:
        st.warning(f"The file {file_name} already exists in the repository. It will be updated.")
    else:
        st.info(f"The file {file_name} does not exist in the repository. It will be uploaded.")

    # Upload the file to GitHub (update or create)
    response = upload_file_to_github(file_name, file_content, sha)

    if response.status_code in [201, 200]:
        st.success(f"File {file_name} uploaded/updated successfully!")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.status_code}, {response.text}")
