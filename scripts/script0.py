import os
import streamlit as st
import requests
import base64
import time
import zipfile
import io
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"  # Change if you're using a different branch
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Define the input directory in your GitHub repository
input_directory_in_github = "decryption/input/"

# GitHub API URL to upload files
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

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

# Function to get the latest workflow run ID
def get_latest_workflow_run_id():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the list of workflow runs
    WORKFLOW_RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
    response = requests.get(WORKFLOW_RUNS_URL, headers=headers)
    if response.status_code == 200:
        workflow_runs = response.json()["workflow_runs"]
        if workflow_runs:
            return workflow_runs[0]["id"]  # Return the latest run ID
    else:
        st.error(f"Failed to fetch workflow runs: {response.text}")
        return None

# Function to fetch the artifact
def fetch_artifact(run_id, retries=5, delay=10):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    ARTIFACTS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/artifacts"

    for _ in range(retries):
        response = requests.get(ARTIFACTS_URL, headers=headers)
        if response.status_code == 200:
            artifacts = response.json()["artifacts"]
            if not artifacts:
                st.write("No artifacts found. Retrying...")
                time.sleep(delay)
            else:
                for artifact in artifacts:
                    if artifact["name"] == "processed-results":
                        download_url = artifact["archive_download_url"]
                        artifact_response = requests.get(download_url, headers=headers)
                        if artifact_response.status_code == 200:
                            with zipfile.ZipFile(io.BytesIO(artifact_response.content)) as z:
                                for file in z.namelist():
                                    if file.endswith("merged_data_with_metadata.csv"):
                                        return z.read(file).decode("utf-8")
                        else:
                            st.error(f"Failed to download artifact: {artifact_response.text}")
                            return None
        else:
            st.error(f"Failed to fetch artifact: {response.text}")
            return None

    st.error("Artifact could not be fetched after multiple retries.")
    return None

# Function to display the selected parameters in a two-column table
def display_selected_parameters(csv_data):
    from io import StringIO
    data = StringIO(csv_data)
    df = pd.read_csv(data)

    # Filter the DataFrame to only include the required parameters
    filtered_data = df[required_parameters].iloc[0]  # Take the first row of the filtered columns

    # Create a two-column table with 'Parameters' and 'Values'
    parameters_df = pd.DataFrame({
        "Parameters": filtered_data.index,
        "Values": filtered_data.values
    })

    # Display the DataFrame as a table in Streamlit
    st.table(parameters_df)

# Streamlit File Uploader
st.title("Scan your Releafs Token")

# Add the instruction text below the title
st.markdown(
    """
Your Releafs Token empowers real-world climate action. Track your token to discover the tangible, positive impact you're contributing to. Together, we’re making a sustainable future possible.
Powered by [Releafs](https://www.releafs.co)
    """
)

uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    # Create two columns: left for the image, right for the table
    col1, col2 = st.columns([1, 2])

    # Display the image in the left column
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Get the file content
    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()

    # Check if the file already exists in the repository
    sha = check_if_file_exists(file_name)

    # Upload the file to GitHub
    response = upload_file_to_github(file_name, file_content, sha)

    if response.status_code == 201 or response.status_code == 200:
        st.write("File uploaded successfully! Processing...")

        # Wait for the workflow to process and fetch the artifact
        run_id = get_latest_workflow_run_id()

        if run_id:
            result = None
            with st.spinner("Waiting for the processed artifact..."):
                result = fetch_artifact(run_id)

            if result:
                st.success("Processing complete! Displaying the result below:")
                with col2:
                    display_selected_parameters(result)
            else:
                st.error("Could not retrieve the processed result.")
        else:
            st.error("Failed to retrieve workflow run ID.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
