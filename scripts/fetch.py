import os
import streamlit as st
import requests
import base64
import time
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Define the process result path in your GitHub repository
process_result_path = "decryption/process/merged_data_with_metadata.csv"

# GitHub API URL to fetch the result
GITHUB_PROCESS_RESULT_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{process_result_path}"

# Function to fetch processed result
def wait_for_process_completion(retries=100, initial_delay=100, subsequent_delay=100):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Initial wait for 1 minute before the first attempt
    st.write(f"Waiting for {initial_delay} seconds before the first attempt...")
    time.sleep(initial_delay)

    for attempt in range(retries):
        response = requests.get(GITHUB_PROCESS_RESULT_URL, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            content = base64.b64decode(file_info["content"]).decode("utf-8")
            return content
        else:
            st.write(f"Processed result not found. Retrying {attempt+1}/{retries} after {subsequent_delay} seconds...")

        # Wait for 30 seconds before the next attempt
        time.sleep(subsequent_delay)

    st.error("Processed result could not be fetched after multiple retries.")
    return None

# Function to display the selected parameters in a two-column table
def display_selected_parameters(csv_data):
    from io import StringIO
    data = StringIO(csv_data)
    df = pd.read_csv(data)

    required_parameters = [
        "Latitude", "Longitude", "Type of Token", "description", "external_url",
        "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
        "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
    ]

    filtered_data = df[required_parameters].iloc[0]

    parameters_df = pd.DataFrame({
        "Parameters": filtered_data.index,
        "Values": filtered_data.values
    })

    st.table(parameters_df)

# Streamlit Button to Fetch Result
st.title("Fetch Releafs Token Results")

if st.button("Fetch Processed Results"):
    st.write("Waiting for the processed result...")
    
    # Wait for the result and fetch it from GitHub
    result = wait_for_process_completion()

    if result:
        st.success("Processing complete! Displaying the result below:")
        display_selected_parameters(result)
    else:
        st.error("Could not retrieve the processed result.")
