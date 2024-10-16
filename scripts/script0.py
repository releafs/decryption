import os
import streamlit as st
import requests
import base64
import time
import zipfile
import io
import pandas as pd  # Ensure pandas is imported for handling tables

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# GitHub API URLs
WORKFLOW_RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
ARTIFACTS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{{run_id}}/artifacts"

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to get the latest workflow run ID
def get_latest_workflow_run_id():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of workflow runs
    response = requests.get(WORKFLOW_RUNS_URL, headers=headers)
    if response.status_code == 200:
        workflow_runs = response.json()["workflow_runs"]
        if workflow_runs:
            return workflow_runs[0]["id"]  # Return the latest run ID
    else:
        st.error(f"Failed to fetch workflow runs: {response.text}")
        return None

# Function to fetch the artifact
def fetch_artifact(run_id):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of artifacts for the run
    response = requests.get(ARTIFACTS_URL.format(run_id=run_id), headers=headers)
    if response.status_code == 200:
        artifacts = response.json()["artifacts"]
        if not artifacts:
            st.write("No artifacts found.")
            return None
        
        # Find the artifact by name (assumed "processed-results")
        for artifact in artifacts:
            if artifact["name"] == "processed-results":
                download_url = artifact["archive_download_url"]
                response = requests.get(download_url, headers=headers)
                if response.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                        for file in z.namelist():
                            if file.endswith("merged_data_with_metadata.csv"):
                                return z.read(file).decode("utf-8")
                else:
                    st.error(f"Failed to download artifact: {response.text}")
                    return None
    return None

# Function to display the selected parameters in a two-column table
def display_selected_parameters(csv_data):
    # Convert the CSV string into a Pandas DataFrame
    from io import StringIO
    data = StringIO(csv_data)
    df = pd.read_csv(data)

    # Filter the DataFrame to only include the required parameters
    filtered_df = df[required_parameters].transpose()

    # Create a two-column table with 'Parameters' and 'Values'
    parameters_df = pd.DataFrame({
        "Parameters": filtered_df.index,
        "Values": filtered_df.iloc[:, 0]  # Assuming you want the first row's values
    })

    # Display the DataFrame as a table in Streamlit
    st.table(parameters_df)

# Streamlit File Uploader
st.title("Image Uploader and Processing")
uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    st.image(uploaded_file)

    with open(f"input/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("File uploaded successfully! Processing...")

    # Dynamically get the latest workflow run ID
    run_id = get_latest_workflow_run_id()

    if run_id:
        result = None
        with st.spinner("Waiting for the processed artifact..."):
            while result is None:
                time.sleep(10)
                result = fetch_artifact(run_id)

        if result:
            st.success("Processing complete! Displaying the result below:")
            display_selected_parameters(result)  # Display the selected parameters
        else:
            st.error("Could not retrieve the processed result.")
    else:
        st.error("Failed to retrieve workflow run ID.")
