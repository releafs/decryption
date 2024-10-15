import os
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Your GitHub repository
GITHUB_BRANCH = "main"  # Branch you're using
GITHUB_TOKEN = "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"  # Your GitHub PAT

# Define the input directory in your GitHub repository
input_directory_in_github = "input/"

# GitHub API URL to upload files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"

# Title of the Streamlit App
st.title("Image Uploader to GitHub Repository")

# File uploader widget
uploaded_files = st.file_uploader("Choose PNG images to upload", type="png", accept_multiple_files=True)

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content):
    # Prepare the data for the GitHub API request
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    commit_message = f"Upload {file_name}"

    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    url = f"{GITHUB_API_URL}{file_name}"

    # Send the request to upload the file
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

# Save the uploaded files to the GitHub repository
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()

        # Upload the file to GitHub
        response = upload_file_to_github(file_name, file_content)

        if response.status_code == 201:
            st.success(f"Successfully uploaded {file_name} to GitHub.")
        else:
            st.error(f"Failed to upload {file_name}. Response: {response.text}")
