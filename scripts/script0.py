import os
import streamlit as st
import requests
import time
import zipfile
import io

# Define GitHub repository and token
GITHUB_REPO = "releafs/decryption"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
WORKFLOW_RUN_ID = st.secrets["WORKFLOW_RUN_ID"]

# GitHub API URLs
ARTIFACTS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{WORKFLOW_RUN_ID}/artifacts"

# Function to fetch the artifact
def fetch_artifact():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of artifacts
    response = requests.get(ARTIFACTS_URL, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to list artifacts: {response.text}")
        return None
    
    artifacts = response.json()["artifacts"]
    if not artifacts:
        st.write("No artifacts found.")
        return None
    
    # Find the artifact by name (assumed "processed-results")
    for artifact in artifacts:
        if artifact["name"] == "processed-results":
            # Download the artifact
            download_url = artifact["archive_download_url"]
            response = requests.get(download_url, headers=headers)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    # Extract the CSV file from the artifact zip
                    for file in z.namelist():
                        if file.endswith("merged_data_with_metadata.csv"):
                            return z.read(file).decode("utf-8")
            else:
                st.error(f"Failed to download artifact: {response.text}")
                return None
    return None

# Streamlit File Uploader
st.title("Image Uploader and Processing")
uploaded_file = st.file_uploader("Choose a PNG image", type="png")

# Process the file and check for artifact
if uploaded_file is not None:
    st.image(uploaded_file)

    # Save the uploaded file locally to trigger GitHub Actions
    with open(f"input/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("File uploaded successfully! Processing...")

    # Poll to check for the artifact every 10 seconds
    result = None
    with st.spinner("Waiting for the processed artifact..."):
        while result is None:
            time.sleep(10)
            result = fetch_artifact()

    if result:
        st.success("Processing complete! Displaying the result below:")
        st.write(result)  # Display the CSV content or processed data
    else:
        st.error("Could not retrieve the processed result.")
