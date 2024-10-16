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

# Function to fetch the processed result after a delay
def wait_for_process_completion(delay=60):
    # Sleep for 60 seconds to wait for the GitHub Actions process to complete
    st.write(f"Waiting for {delay} seconds for the process to complete...")
    time.sleep(delay)

    # Now, try fetching the processed result
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(GITHUB_PROCESS_RESULT_URL, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info["content"]).decode("utf-8")
        return content
    else:
        st.error("Processed result could not be fetched after waiting.")
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
        st.write("File uploaded successfully! Waiting for 1 minute...")

        # Wait for 1 minute and then check for the processed CSV result
        result = wait_for_process_completion()

        if result:
            st.success("Processing complete! Displaying the result below:")
            display_selected_parameters(result)
        else:
            st.error("Could not retrieve the processed result.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
