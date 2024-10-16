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

    # If the directory does not exist or is empty, skip without error
    if response.status_code == 404:
        st.info("Input directory does not exist or is empty. Skipping directory clearing.")
        return

    if response.status_code == 200:
        files = response.json()
        for file in files:
            file_name = file['name']
            sha = file['sha']
            delete_response = delete_file_in_github(file_name, sha)
            if delete_response.status_code == 200:
                st.write(f"Deleted {file_name} successfully.")
            else:
                st.error(f"Failed to delete {file_name}. Response: {delete_response.status_code}, {delete_response.text}")
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

# Function to display token details from the CSV file after the processing is done
# Function to display token details from the CSV file after the processing is done
def display_token_details():
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        st.error(f"CSV file not found: {csv_file_path}")
        return

    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Get the first row of the dataframe (changed from last row to first row)
    first_row = df.iloc[0]

    # Extract the required parameters
    required_parameters = [
        "Latitude", "Longitude", "Type of Token", "description", "external_url",
        "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
        "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
    ]

    parameters = {param: first_row[param] for param in required_parameters if param in first_row}

    # Display content in Streamlit
    st.write("### Token Information:")
    st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))


# Streamlit Page Layout
st.title("Upload and Process Your PNG File")

# Create two columns: left for the image, right for the file upload and info
col1, col2 = st.columns([1, 2])

# File uploader widget in the right column
with col2:
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        # Display the file name and size
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

        # Clear the input directory before uploading a new file
        st.write("Clearing input directory...")
        clear_input_directory()

        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()  # Get the content of the file

        # Upload the file to GitHub (no need to check for existence because we cleared the directory)
        response = upload_file_to_github(file_name, file_content)

        if response.status_code in [201, 200]:
            st.success(f"File {file_name} uploaded/updated successfully!")
        else:
            st.error(f"Failed to upload {file_name}. Response: {response.status_code}, {response.text}")

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
