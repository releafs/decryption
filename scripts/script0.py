import os
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Replace with your repository name
GITHUB_BRANCH = "main"  # Replace with your branch name
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Use Streamlit secrets to store your GitHub token securely

# Define the input and process directories in your GitHub repository
input_directory_in_github = "decryption/input/"
process_file_path = "decryption/process/merged_data_with_metadata.csv"

# GitHub API URL to upload files and check for existing files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/"
input_dir_url = f"{GITHUB_API_URL}{input_directory_in_github}"
process_file_url = f"{GITHUB_API_URL}{process_file_path}"

# Function to check if a file exists in the GitHub repository
def check_if_file_exists(file_url):
    response = requests.get(file_url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    if response.status_code == 200:
        return response.json().get('sha')  # Return the SHA of the existing file if found
    return None

# Function to delete a file in the GitHub repository
def delete_file_in_github(file_url, sha):
    data = {
        "message": "Delete old file",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }
    response = requests.delete(file_url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return response

# Function to list and delete all existing files in the input directory on GitHub
def clear_input_directory():
    response = requests.get(input_dir_url, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    if response.status_code == 200:
        files = response.json()
        for file in files:
            file_name = file['name']
            sha = file['sha']
            delete_response = delete_file_in_github(f"{input_dir_url}{file_name}", sha)
            if delete_response.status_code == 200 or delete_response.status_code == 204:
                st.write(f"Deleted {file_name} successfully.")
            else:
                st.error(f"Failed to delete {file_name}. Response: {delete_response.status_code}, {delete_response.text}")
    else:
        st.error(f"Failed to list files in directory. Response: {response.status_code}, {response.text}")

# Function to delete the process/merged_data_with_metadata.csv file from the repository
def delete_process_file():
    sha = check_if_file_exists(process_file_url)
    if sha:
        delete_response = delete_file_in_github(process_file_url, sha)
        if delete_response.status_code == 200 or delete_response.status_code == 204:
            st.write(f"Deleted {process_file_path} successfully.")
        else:
            st.error(f"Failed to delete {process_file_path}. Response: {delete_response.status_code}, {delete_response.text}")
    else:
        st.write(f"{process_file_path} does not exist.")

# Function to upload a file to GitHub
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

    url = f"{input_dir_url}{file_name}"  # GitHub API URL for the file

    # Send the request to upload the file to GitHub
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

# Streamlit File Uploader
st.title("Upload a PNG File to GitHub")

# Create two columns: left for the image, right for the file upload and info
col1, col2 = st.columns([1, 2])

# File uploader widget in the right column
with col2:
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        # Display the file name and size
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
        
        # Clear the input directory before uploading a new file
        st.write("Clearing input directory...")
        clear_input_directory()

        # Delete the process/merged_data_with_metadata.csv before proceeding
        st.write("Deleting the existing process/merged_data_with_metadata.csv file...")
        delete_process_file()

        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()  # Get the content of the file

        # Check if the file already exists in the GitHub repository
        sha = check_if_file_exists(f"{input_dir_url}{file_name}")

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

# Display the uploaded image on the left column
if uploaded_file is not None:
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
