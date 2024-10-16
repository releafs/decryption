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

# Define the input directory and process result paths in your GitHub repository
input_directory_in_github = "decryption/input/"
process_result_path = "decryption/process/merged_data_with_metadata.csv"

# GitHub API URL to upload files and fetch results
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
GITHUB_PROCESS_RESULT_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{process_result_path}"

# GitHub Actions API URL to check workflow status
GITHUB_WORKFLOW_RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs"

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

# Replace time.sleep(delay) with st.experimental_sleep(delay)

# Function to check the latest workflow status
def check_workflow_status(retries=20, delay=15):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    for attempt in range(retries):
        response = requests.get(GITHUB_WORKFLOW_RUNS_URL, headers=headers)
        if response.status_code == 200:
            workflow_runs = response.json().get("workflow_runs", [])
            if workflow_runs:
                latest_run = workflow_runs[0]
                status = latest_run.get("status")
                conclusion = latest_run.get("conclusion")
                st.write(f"Workflow status: {status}, Conclusion: {conclusion}")

                if status == "completed" and conclusion == "success":
                    return True
                elif status == "completed" and conclusion != "success":
                    st.error("Workflow completed but failed. Please check the logs.")
                    return False
            else:
                st.write(f"No workflow runs found. Retrying {attempt+1}/{retries}...")
        else:
            st.error(f"Failed to check workflow status. Retrying {attempt+1}/{retries}...")

        st.experimental_sleep(delay)  # Use st.experimental_sleep here

    st.error("Workflow did not complete within the expected time.")
    return False

# Function to wait for the process result by polling for the presence of the processed result
def wait_for_process_completion(retries=20, delay=15):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for attempt in range(retries):
        response = requests.get(GITHUB_PROCESS_RESULT_URL, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            content = base64.b64decode(file_info["content"]).decode("utf-8")
            return content
        else:
            st.write(f"Processed result not found. Retrying {attempt+1}/{retries}...")
            st.experimental_sleep(delay)  # Use st.experimental_sleep here

    st.error("Processed result could not be fetched after multiple retries.")
    return None


# Function to display the selected parameters in a two-column table
def display_selected_parameters(csv_data):
    from io import StringIO
    data = StringIO(csv_data)
    df = pd.read_csv(data)

    filtered_data = df[required_parameters].iloc[0]

    parameters_df = pd.DataFrame({
        "Parameters": filtered_data.index,
        "Values": filtered_data.values
    })

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

    # Upload the file to GitHub
    response = upload_file_to_github(file_name, file_content, sha)

    if response.status_code in [201, 200]:
        st.write("File uploaded successfully! Checking workflow status...")

        # Wait for the workflow to complete by checking its status
        workflow_completed = check_workflow_status()

        if workflow_completed:
            # Wait for the result to be available after workflow completion
            result = None
            with st.spinner("Fetching the processed result..."):
                result = wait_for_process_completion()

            if result:
                st.success("Processing complete! Displaying the result below:")
                display_selected_parameters(result)
            else:
                st.error("Could not retrieve the processed result.")
        else:
            st.error("Workflow did not complete successfully.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
