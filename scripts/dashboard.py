import os
import time
import pandas as pd
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

input_directory_in_github = "decryption/input/"

# Function to create a placeholder file if the directory does not exist
def create_placeholder_file():
    file_name = ".gitkeep"  # Placeholder file name
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
        st.error(f"Failed to create placeholder file. Response: {response.status_code}, {response.text}")

# Function to clear the input directory
def clear_input_directory():
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}"
    response = requests.get(GITHUB_API_URL, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    if response.status_code == 200:
        files = response.json()
        if len(files) == 0:
            st.write("Directory is already empty.")
        else:
            for file in files:
                file_name = file['name']
                sha = file['sha']
                delete_response = delete_file_in_github(file_name, sha)
                if delete_response.status_code == 200:
                    st.write(f"Deleted {file_name} successfully.")
                else:
                    st.error(f"Failed to delete {file_name}. Response: {delete_response.status_code}")
    elif response.status_code == 404:
        st.warning(f"Directory {input_directory_in_github} not found, creating it...")
        create_placeholder_file()
    else:
        st.error(f"Failed to list files in directory. Response: {response.status_code}")

# Function to delete a file in the GitHub repository
def delete_file_in_github(file_name, sha):
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}{file_name}"
    data = {
        "message": f"Delete {file_name}",
        "sha": sha,
        "branch": GITHUB_BRANCH
    }
    response = requests.delete(GITHUB_API_URL, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return response

# Function to upload the file to GitHub
def upload_file_to_github(file_name, file_content):
    encoded_content = base64.b64encode(file_content).decode("utf-8")  # Base64 encode the file content
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{input_directory_in_github}{file_name}"
    data = {
        "message": f"Upload {file_name}",
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }
    response = requests.put(url, json=data, headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    })
    return response

# Function to display token details using the fetched CSV
# Function to display token details using the direct URL of the CSV
def display_token_details():
    try:
        # Directly read the CSV data from the URL using Pandas
        df = pd.read_csv(CSV_URL)

        if df.empty:
            st.error("CSV file is empty.")
            return

        last_row = df.iloc[-1]
        parameters = {
            "Latitude": last_row["Latitude"],
            "Longitude": last_row["Longitude"],
            "Type of Token": last_row["Type of Token"],
            "Description": last_row["description"],
            "External URL": last_row["external_url"],
            "Starting Project": last_row["Starting Project"],
            "Unit": last_row["Unit"],
            "Deleverable": last_row["Deleverable"],
            "Years Duration": last_row["Years_Duration"],
            "Impact Type": last_row["Impact Type"],
            "SDGs": last_row["SDGs"],
            "Implementer Partner": last_row["Implementer Partner"],
            "Internal Verification": last_row["Internal Verification"],
            "Local Verification": last_row["Local Verification"],
            "Imv Document": last_row["Imv_Document"]
        }

        st.write("### Token Information:")
        st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Streamlit Page Layout
st.title("Scan Your Releafs' Token")

# Add the message at the top
st.write("""
    Each token represents a climate action impact on the ground. 
    When you scan, you will find out the status of your token. 
    Thanks for holding a Releafs token.
""")

# Create tabs for Upload and Display
tab1, tab2 = st.tabs(["Upload Image", "Display Token Details"])

# Upload Image Tab
with tab1:
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
        st.write("Clearing input directory...")
        clear_input_directory()
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()

        response = upload_file_to_github(file_name, file_content)

        if response.status_code in [201, 200]:
            st.success(f"File {file_name} uploaded/updated successfully!")
        else:
            st.error(f"Failed to upload {file_name}. Response: {response.status_code}, {response.text}")

# Display Token Details Tab
with tab2:
    if st.button("Show Token Details"):
        with st.spinner("Showing Your Token Details..."):
            time.sleep(60)  # Adjust this based on your processing time
            display_token_details()
