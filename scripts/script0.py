Can we make our script fetch to the artifact instead of the CSV?

import os
import streamlit as st
import requests
import base64
import time
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# GitHub API URL to access artifacts
GITHUB_API_ARTIFACTS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts"

# Function to fetch the artifact URL and download the CSV file
def fetch_artifact():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of artifacts
    response = requests.get(GITHUB_API_ARTIFACTS_URL, headers=headers)
    
    if response.status_code == 200:
        artifacts = response.json().get("artifacts", [])
        
        # Find the most recent artifact (or you can match by name)
        for artifact in artifacts:
            if "processed-results" in artifact["name"]:
                artifact_url = artifact["archive_download_url"]

                # Download the artifact
                artifact_response = requests.get(artifact_url, headers=headers)
                if artifact_response.status_code == 200:
                    with open("artifact.zip", "wb") as file:
                        file.write(artifact_response.content)
                    st.write("Artifact downloaded successfully.")
                    return "artifact.zip"
                else:
                    st.error(f"Failed to download artifact. Response: {artifact_response.status_code}")
                    return None
    else:
        st.error(f"Failed to fetch artifacts. Response: {response.status_code}")
        return None

# Function to extract the CSV file from the downloaded artifact
def extract_csv_from_artifact(artifact_path):
    import zipfile

    # Extract the artifact
    with zipfile.ZipFile(artifact_path, 'r') as zip_ref:
        zip_ref.extractall("extracted_artifact")
    
    # Check if the CSV is extracted
    extracted_csv = os.path.join("extracted_artifact", "process", "merged_data_with_metadata.csv")
    if os.path.exists(extracted_csv):
        st.write("CSV extracted successfully.")
        return extracted_csv
    else:
        st.error("CSV file not found in the artifact.")
        return None

# Function to display token details from the artifact
def display_token_details(artifact_csv_path):
    if not os.path.exists(artifact_csv_path):
        st.error(f"CSV file not found: {artifact_csv_path}")
        return

    # Read the CSV file
    df = pd.read_csv(artifact_csv_path)

    # Get the last row of the dataframe
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

# Streamlit Page Layout
st.title("Upload and Process Your PNG File")

# File uploader widget in the right column
uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

if uploaded_file is not None:
    st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    st.write("Please wait for the processing to complete.")

# Fetch and display token details from artifact
if st.button("Fetch Token Details from Artifact"):
    artifact_path = fetch_artifact()
    if artifact_path:
        csv_path = extract_csv_from_artifact(artifact_path)
        if csv_path:
            display_token_details(csv_path)
