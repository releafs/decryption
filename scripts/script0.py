import os
import streamlit as st
import requests
import base64
import time
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"  # Replace with your repository name
GITHUB_BRANCH = "main"  # Replace with your branch name
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]  # Use Streamlit secrets to store your GitHub token securely

# Define the input directory in your GitHub repository
input_directory_in_github = "decryption/input/"
csv_file_path = 'process/merged_data_with_metadata.csv'

# Function to delete all files in the input directory
def clear_input_directory():
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
    response = requests.get(GITHUB_API_URL, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    if response.status_code == 200:
        files = response.json()
        if len(files) == 0:
            st.write("Directory is already empty.")
        else:
            for file in files:
                file_name = file['name']
                sha = file['sha']
                delete_response = delete_file_in_github(file_name, sha)
                if delete_response.status_code == 200:
                    st.write(f"Deleted {file_name} successfully.")
                else:
                    st.error(f"Failed to delete {file_name}. Response: {delete_response.status_code}, {delete_response.text}")
    elif response.status_code == 404:
        st.warning(f"Directory {input_directory_in_github} not found, creating it...")
        create_placeholder_file()
    else:
        st.error(f"Failed to list files in directory. Response: {response.status_code}, {response.text}")

# Function to create a placeholder file if the directory does not exist
def create_placeholder_file():
    file_name = ".gitkeep"  # Placeholder file
    content = base64.b64encode(b'').decode('utf-8')  # Empty file content
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}{file_name}"
    data = {
        "message": "Create input directory with placeholder file",
        "content": content,
        "branch": GITHUB_BRANCH
    }
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    if response.status_code in [201, 200]:
        st.write(f"Created {file_name} in {input_directory_in_github}.")
    else:
        st.error(f"Failed to create directory. Response: {response.status_code}, {response.text}")

# Function to delete a file in the GitHub repository
def delete_file_in_github(file_name, sha):
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
    url = f"{GITHUB_API_URL}{file_name}"
    data = {
        "message": f"Delete {file_name}",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }
    response = requests.delete(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return response

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content, sha=None):
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
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

import requests
import zipfile
import io

# Function to fetch the artifact and display token details
def display_token_details():
    # GitHub API URL for fetching artifacts
    GITHUB_API_ARTIFACT_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts"
    
    # Step 1: Fetch the artifact list
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(GITHUB_API_ARTIFACT_URL, headers=headers)

    if response.status_code == 200:
        artifacts = response.json().get("artifacts", [])
        if not artifacts:
            st.error("No artifacts found.")
            return
        
        # Step 2: Get the latest artifact
        latest_artifact = artifacts[0]  # Assuming the first artifact is the latest
        artifact_download_url = latest_artifact["archive_download_url"]
        
        # Step 3: Download the artifact
        artifact_response = requests.get(artifact_download_url, headers=headers)
        if artifact_response.status_code != 200:
            st.error(f"Failed to download artifact. Status code: {artifact_response.status_code}")
            return
        
        # Step 4: Extract the artifact (assumed to be a ZIP file)
        zip_file = zipfile.ZipFile(io.BytesIO(artifact_response.content))
        zip_file.extractall()  # Extracting the files
        
        # Step 5: Look for the CSV file in the extracted artifact
        extracted_csv_file = 'process/merged_data_with_metadata.csv'  # Replace with the correct path if needed
        
        if not os.path.exists(extracted_csv_file):
            st.error(f"CSV file not found in the artifact: {extracted_csv_file}")
            return
        
        # Step 6: Read the CSV and display token details
        df = pd.read_csv(extracted_csv_file)
        last_row = df.iloc[-1]

        # Extract the required parameters
        required_parameters = [
            "Latitude", "Longitude", "Type of Token", "description", "external_url",
            "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
            "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
        ]

        parameters = {param: last_row[param] for param in required_parameters if param in last_row}

        # Display content in Streamlit
        st.write("### Token Information:")
        st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))
    else:
        st.error(f"Failed to fetch artifacts. Status code: {response.status_code}, {response.text}")



# Display the uploaded image on the left column
if uploaded_file is not None:
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# Section to display the token details once the fetch.py script completes processing
st.write("## Token Details")
if st.button("Fetch Token Details"):
    # Simulate delay for processing to be completed
    st.write("Fetching token details after processing...")
    time.sleep(60)  # Assuming the fetch happens after 1 minute (adjust as needed)
    display_token_details()
