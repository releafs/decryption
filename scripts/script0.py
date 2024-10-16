import os
import streamlit as st
import requests
import base64

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Function to fetch processed result
def fetch_processed_result():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    result_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/decryption/process/merged_data_with_metadata.csv"
    
    response = requests.get(result_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info["content"]).decode("utf-8")
        return content
    else:
        return None

# Poll GitHub API for results
st.title("Scan your Releafs Token")

result = fetch_processed_result()
if result:
    st.write("Processing complete! Displaying the result...")
    st.write(result)
else:
    st.write("No processed results available yet. Please wait or check back later.")
