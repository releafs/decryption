import os
import streamlit as st
import pandas as pd
import json
import hmac
import hashlib
import requests
from flask import Flask, request, abort

# Create a Flask app to receive webhook events
app = Flask(__name__)

# GitHub Secret for signature validation
SECRET = 'releafstoken'

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to validate GitHub signature
def validate_github_signature(payload_body, signature):
    mac = hmac.new(SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

# Function to fetch processed result from GitHub
def fetch_processed_result():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Replace with the actual URL where the processed CSV is saved
    result_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/decryption/process/merged_data_with_metadata.csv"
    
    response = requests.get(result_url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        content = base64.b64decode(file_info["content"]).decode("utf-8")
        return content
    else:
        return None

# Function to display parameters from the CSV
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

# Webhook handler route
@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    if request.method == 'POST':
        # Validate GitHub signature
        signature = request.headers.get('X-Hub-Signature-256')
        payload_body = request.get_data()
        
        if not validate_github_signature(payload_body, signature):
            abort(403)  # Invalid signature

        payload = json.loads(request.data)
        if payload.get('action') == 'completed':
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

# Start the webhook handler (since Flask and Streamlit can't run side by side, you'll need to adapt)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
