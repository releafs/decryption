import os
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

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
        return response.json().get('sha')  # Return the SHA of the existing file
    return None

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content, sha=None):
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    commit_message = f"Upload {file_name}"

    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    if sha:
        data["sha"] = sha

    url = f"{GITHUB_API_URL}{file_name}"

    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

# Streamlit File Uploader for Uploading File
st.title("Upload Releafs Token")

uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    st.write("Uploading your file. Please wait...")

    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()

    sha = check_if_file_exists(file_name)

    # Upload the file to GitHub
    response = upload_file_to_github(file_name, file_content, sha)

    if response.status_code in [201, 200]:
        st.success("File uploaded successfully! Please wait for the result.")
        st.write("Wait for about 1 minute, then proceed to the next step.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
