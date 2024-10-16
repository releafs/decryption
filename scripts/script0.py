import os
import streamlit as st
import pandas as pd
import base64
import requests
import time

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Define the process result path in your GitHub repository
process_result_path = "decryption/process/merged_data_with_metadata.csv"

# GitHub API URL to fetch results
GITHUB_PROCESS_RESULT_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{process_result_path}"

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to fetch processed result from GitHub
def fetch_processed_result():
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
        return None

# Function to display the selected parameters in a table
def display_selected_parameters(csv_data):
    from io import StringIO
    data = StringIO(csv_data)
    df = pd.read_csv(data)

    # Displaying filtered data
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

    # Introduce a delay to wait for the GitHub action to finish (adjust based on average time)
    time.sleep(60)  # Wait for 30 seconds (adjust this as needed)

    # Fetch the processed CSV result from GitHub
    result = fetch_processed_result()

    if result:
        st.success("Processing complete! Displaying the result below:")
        display_selected_parameters(result)
    else:
        st.error("Could not retrieve the processed result.")
