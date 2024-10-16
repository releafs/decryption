import os
import streamlit as st
import requests
import base64
import time

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Your GitHub repository
GITHUB_BRANCH = "main"  # Branch you're using
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Get the GitHub PAT from Streamlit Secrets

# Define the input and process directories in your GitHub repository
input_directory_in_github = "decryption/input/"
process_directory_in_github = "decryption/process/"

# GitHub API URLs
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
RESULT_FILE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{process_directory_in_github}merged_data_with_metadata.csv"

# Title of the Streamlit App
st.title("Image Uploader to GitHub Repository")

# File uploader widget
uploaded_files = st.file_uploader("Choose PNG images to upload", type="png", accept_multiple_files=True)

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

# Function to check if the result file is ready
def check_for_result():
    response = requests.get(RESULT_FILE_URL)
    if response.status_code == 200:
        return response.text  # Return the CSV data if available
    else:
        return None

# Save the uploaded files to the GitHub repository
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()

        # Check if the file already exists in the repository
        sha = check_if_file_exists(file_name)

        # Upload the file to GitHub
        response = upload_file_to_github(file_name, file_content, sha)

        if response.status_code == 201 or response.status_code == 200:
            st.success(f"Successfully uploaded {file_name} to GitHub.")
            
            # Once uploaded, check for the result every 10 seconds
            st.write("Processing the image. This may take a few minutes...")

            result = None
            with st.spinner("Waiting for the processed result..."):
                while result is None:
                    time.sleep(10)  # Wait 10 seconds before checking again
                    result = check_for_result()

            if result:
                st.success("Processing complete! Displaying the result below:")
                st.write(result)  # Display the CSV content or processed data
            else:
                st.error("Could not retrieve the processed result.")
        else:
            st.error(f"Failed to upload {file_name}. Response: {response.text}")
