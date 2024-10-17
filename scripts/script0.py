import os
import streamlit as st
import requests
import base64
import time
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"

# Ensure GITHUB_TOKEN is available
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    st.write("GitHub token loaded successfully.")
except KeyError:
    st.error("GITHUB_TOKEN not found in Streamlit secrets.")
    st.stop()  # Stop execution if the token is not found

input_directory_in_github = "decryption/input/"
csv_file_path = 'process/merged_data_with_metadata.csv'

# Function to fetch the latest CSV without caching
@st.cache_data(experimental_allow_widgets=True)
def fetch_latest_csv_data(extracted_csv_file):
    return pd.read_csv(extracted_csv_file)

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

# Function to delete all files in the input directory
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
def display_token_details():
    extracted_csv_file = csv_file_path

    # Debug: Print the working directory and the path to the CSV file
    print(f"Working directory: {os.getcwd()}")
    print(f"Full path to the CSV file: {os.path.abspath(extracted_csv_file)}")

    # Check if the CSV file exists
    if not os.path.exists(extracted_csv_file):
        st.error(f"CSV file not found at: {extracted_csv_file}")
        print(f"Error: CSV file not found at {os.path.abspath(extracted_csv_file)}")
        return
    else:
        print(f"CSV file found at {os.path.abspath(extracted_csv_file)}")

    # Fetch CSV data with cache control
    df = fetch_latest_csv_data(extracted_csv_file)

    if df.empty:
        st.error("CSV file is empty.")
        print("Error: CSV file is empty.")
        return
    else:
        print(f"CSV file is not empty. Number of rows: {len(df)}")

    # Get the last row of the DataFrame
    last_row = df.iloc[-1]
    print(f"Displaying the last row of the CSV file:\n{last_row}")

    # Extract the required parameters
    required_parameters = [
        "Latitude", "Longitude", "Type of Token", "description", "external_url",
        "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
        "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
    ]

    # Create a dictionary of parameters present in the last row
    parameters = {param: last_row[param] for param in required_parameters if param in last_row}
    
    # Display content in Streamlit
    st.write("### Token Information:")
    st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))

# Streamlit Page Layout
st.title("Scan Your Releafs' Token")

# Add manual cache clearing option
if st.button('Clear Cache'):
    st.cache_data.clear()
    st.success("Cache cleared successfully.")

# Create two columns: left for the image, right for the file upload and info
col1, col2 = st.columns([1, 2])

# File uploader widget in the right column
with col2:
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
        st.write("Clearing input directory...")
        clear_input_directory()
        file_name = uploaded_file.name
        file_content = uploaded_file.getvalue()  # Get the content of the file

        response = upload_file_to_github(file_name, file_content)

        if response.status_code in [201, 200]:
            st.success(f"File {file_name} uploaded/updated successfully!")
        else:
            st.error(f"Failed to upload {file_name}. Response: {response.status_code}, {response.text}")

# Display the uploaded image on the left column
if uploaded_file is not None:
    with col1:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# Section to display the token details
st.write("## Token Details")
if st.button("Fetch Token Details"):
    st.write("Fetching token details after processing...")
    time.sleep(80)  # Adjust delay if necessary
    display_token_details()
