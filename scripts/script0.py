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

# Function to upload the file to GitHub and return the commit SHA
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

    if response.status_code in [200, 201]:
        commit_sha = response.json().get('commit', {}).get('sha')
        return response, commit_sha
    else:
        return response, None

# Function to get the workflow run ID associated with a commit SHA
def get_workflow_run_by_commit(commit_sha, retries=10, delay=10):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for attempt in range(retries):
        WORKFLOW_RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"
        params = {
            "event": "push",
            "per_page": 100
        }
        response = requests.get(WORKFLOW_RUNS_URL, headers=headers, params=params)
        if response.status_code == 200:
            workflow_runs = response.json()["workflow_runs"]
            # Look for the workflow run with the matching head_sha
            for run in workflow_runs:
                if run["head_sha"] == commit_sha:
                    return run["id"]
            else:
                st.write(f"Workflow run not found for commit {commit_sha}. Retrying in {delay} seconds...")
                time.sleep(delay)
        else:
            st.error(f"Failed to fetch workflow runs: {response.text}")
            return None
    st.error("Workflow run not found after multiple retries.")
    return None

# Function to poll workflow completion
def wait_for_workflow_completion(run_id, retries=20, delay=10):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    WORKFLOW_RUN_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}"

    for attempt in range(retries):
        response = requests.get(WORKFLOW_RUN_URL, headers=headers)
        if response.status_code == 200:
            run_data = response.json()
            status = run_data["status"]
            if status == "completed":
                conclusion = run_data["conclusion"]
                if conclusion == "success":
                    st.success("Workflow completed successfully.")
                    return True
                else:
                    st.error(f"Workflow completed with conclusion: {conclusion}")
                    return False
            else:
                st.write(f"Workflow status: {status}. Retrying in {delay} seconds...")
                time.sleep(delay)
        else:
            st.error(f"Failed to fetch workflow status: {response.text}")
            return False

    st.error("Workflow did not complete in time.")
    return False

# Function to fetch the artifact
def fetch_artifact(run_id, retries=10, delay=10):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    ARTIFACTS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/artifacts"

    for attempt in range(retries):
        response = requests.get(ARTIFACTS_URL, headers=headers)
        if response.status_code == 200:
            artifacts = response.json()["artifacts"]
            if artifacts:
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
                st.write(f"Artifacts not found. Retrying {attempt+1}/{retries}...")
                time.sleep(delay)
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

st.markdown(
    """
Your Releafs Token empowers real-world climate action. Track your token to discover the tangible, positive impact you're contributing to. Together, we’re making a sustainable future possible.
Powered by [Releafs](https://www.releafs.co)
    """
)

uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    st.write("Uploading and processing your file. Please wait...")

    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()

    sha = check_if_file_exists(file_name)

    # Upload the file to GitHub and get the commit SHA
    response, commit_sha = upload_file_to_github(file_name, file_content, sha)

    if response.status_code in [201, 200] and commit_sha:
        st.write("File uploaded successfully! Processing...")

        # Get the workflow run ID associated with the commit SHA
        run_id = get_workflow_run_by_commit(commit_sha)

        if run_id:
            st.write("Waiting for the workflow to complete...")
            completed = wait_for_workflow_completion(run_id)
            if completed:
                result = None
                with st.spinner("Fetching the processed artifact..."):
                    result = fetch_artifact(run_id)
                if result:
                    st.success("Processing complete! Displaying the result below:")
                    display_selected_parameters(result)
                else:
                    st.error("Could not retrieve the processed result.")
            else:
                st.error("Workflow did not complete successfully.")
        else:
            st.error("Failed to find the workflow run associated with the file upload.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
