import os
import streamlit as st
import pandas as pd
import json
import hmac
import hashlib
from flask import Flask, request, abort
import threading
import time
import requests
import base64

# Create a Flask app to receive webhook events
app = Flask(__name__)

# GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
SECRET = 'releafstoken'  # Your webhook secret

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Webhook handler route with secret verification
@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    # Validate the secret
    signature = request.headers.get('X-Hub-Signature-256')
    if not is_valid_signature(request.data, signature):
        abort(403)  # Invalid signature

    if request.method == 'POST':
        payload = request.json
        workflow_status = payload.get('workflow_run', {}).get('conclusion')
        if workflow_status == 'success':
            st.write("Workflow completed successfully. Fetching result...")
            result = fetch_processed_result()
            if result:
                display_selected_parameters(result)
            else:
                st.error("Failed to fetch processed result.")
        else:
            st.error(f"Workflow failed with status: {workflow_status}")
    return '', 200

# Function to validate the webhook secret
def is_valid_signature(payload, signature):
    mac = hmac.new(SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = f'sha256={mac.hexdigest()}'
    return hmac.compare_digest(expected_signature, signature)

# Function to fetch the processed result from GitHub
def fetch_processed_result():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # API URL to fetch the processed file
    result_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/path-to-your-processed-result.csv"

    response = requests.get(result_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info['content']).decode('utf-8')
        return content
    else:
        st.error(f"Error fetching processed result: {response.status_code}")
        return None

# Function to display parameters
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

# Function to run Flask in a background thread
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Streamlit interface for file upload
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

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/decryption/input/{file_name}"

        response = requests.put(url, json=data, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        })

        return response

    sha = None  # This can be adjusted if you need to handle file existence
    response = upload_file_to_github(file_name, file_content, sha)

    if response.status_code in [201, 200]:
        st.write("File uploaded successfully. Waiting for webhook trigger...")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")

# Keep Streamlit running alongside Flask
while True:
    time.sleep(1)
