import os
import streamlit as st
import requests
import base64
import time
import zipfile
import io
import pandas as pd

# (Other imports and initial setup remain the same)

# Function to fetch the artifact with the specific name
def fetch_artifact(run_id, artifact_name, retries=20, delay=10):
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
                    if artifact["name"] == artifact_name:
                        download_url = artifact["archive_download_url"]
                        artifact_response = requests.get(download_url, headers=headers)
                        if artifact_response.status_code == 200:
                            with zipfile.ZipFile(io.BytesIO(artifact_response.content)) as z:
                                for file in z.namelist():
                                    if file.endswith("merged_data_with_metadata.csv"):
                                        return z.read(file).decode("utf-8")
                            else:
                                st.error(f"File not found in the artifact.")
                                return None
                        else:
                            st.error(f"Failed to download artifact: {artifact_response.text}")
                            return None
                else:
                    st.write(f"Artifact '{artifact_name}' not found. Retrying {attempt+1}/{retries}...")
                    time.sleep(delay)
            else:
                st.write(f"No artifacts found. Retrying {attempt+1}/{retries}...")
                time.sleep(delay)
        else:
            st.error(f"Failed to fetch artifacts: {response.text}")
            return None

    st.error(f"Artifact '{artifact_name}' could not be fetched after multiple retries.")
    return None

# Main application logic
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
                artifact_name = f"processed-results-{commit_sha}"
                with st.spinner("Fetching the processed artifact..."):
                    result = fetch_artifact(run_id, artifact_name)
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
