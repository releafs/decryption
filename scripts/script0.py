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

# Define directories in your GitHub repository
input_directory_in_github = "decryption/input/"
process_directory_in_github = "decryption/process/"
csv_file_path = 'process/merged_data_with_metadata.csv'

# Function to silently delete all files in the specified GitHub directory
def clear_directory(directory):
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{directory}"
    response = requests.get(GITHUB_API_URL, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    # If the directory does not exist or is empty, skip without any message
    if response.status_code == 404:
        return  # Silently skip

    if response.status_code == 200:
        files = response.json()
        for file in files:
            file_name = file['name']
            sha = file['sha']
            delete_response = delete_file_in_github(directory, file_name, sha)
            # Silent deletion without any message
    else:
        return  # Silently skip in case of any error

# Function to delete a file in the GitHub repository
def delete_file_in_github(directory, file_name, sha):
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{directory}"
    url = f"{GITHUB_API_URL}/{file_name}"
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

# Function to recreate an empty directory on GitHub by adding a placeholder file
def recreate_directory(directory):
    # Create a placeholder file in the directory to ensure it exists
    placeholder_file = "placeholder.txt"
    placeholder_content = "This is a placeholder file to recreate the directory."
    upload_file_to_github(f"{directory}/{placeholder_file}", placeholder_content.encode('utf-8'))

# Function to clear and recreate both input and process directories
def clear_and_recreate_directories():
    # Clear input and process directories
    clear_directory("decryption/input/")
    clear_directory("decryption/process/")
    
    # Recreate input and process directories
    recreate_directory("decryption/input")
    recreate_directory("decryption/process")

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content, sha=None):
    directory = file_name.split('/')[0]  # Assuming the directory is the first part of the file path
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{directory}"
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

    url = f"{GITHUB_API_URL}/{file_name}"  # GitHub API URL for the file

    # Send the request to upload the file to GitHub
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })

    return response

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
st.title("Scan Your Releafs' Token")

# Create two columns: left for the image, right for the file upload and info
col1, col2 = st.columns([1, 2])

# File uploader widget in the right column
with col2:
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        # Display the file name and size
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")

        # Clear and recreate directories before uploading a new file
        clear_and_recreate_directories()

        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()  # Get the content of the file

        # Upload the file to GitHub
        response = upload_file_to_github(f"decryption/input/{file_name}", file_content)

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
