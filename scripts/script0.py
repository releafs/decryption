import os
import streamlit as st
import pandas as pd
import base64
import requests

# Define GitHub repository details
GITHUB_USERNAME = "releafs"  # Replace with your GitHub username or organization
GITHUB_REPO = "decryption"
GITHUB_BRANCH = "main"

# Define the process result path in your GitHub repository
process_result_path = "decryption/process/merged_data_with_metadata.csv"

# Construct the URL to the processed CSV file on GitHub
def get_github_file_url():
    return f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{process_result_path}"

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

    # (Optional) Upload the file to GitHub or trigger the workflow as needed
    # Assuming this step is already handled in your existing code

    # Provide the direct link to the processed result
    result_url = get_github_file_url()
    st.success("Your file has been uploaded and is being processed.")
    st.markdown(f"[Click here to view your processed result]({result_url})")

    st.write("Please note: The processing may take a few moments. If the result is not immediately visible, please refresh the page after a short while.")

