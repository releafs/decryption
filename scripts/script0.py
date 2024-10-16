import os
import streamlit as st
import pandas as pd
import json
from flask import Flask, request, jsonify
import hmac
import hashlib

# Create a Flask app
app = Flask(__name__)

# Define GitHub secret (use the secret you have 'releafstoken')
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

# Function to verify the webhook signature from GitHub
def verify_signature(payload, signature):
    mac = hmac.new(SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest('sha256=' + mac.hexdigest(), signature)

# Webhook handler route
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify the signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature or not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 403

    payload = request.json
    if payload.get('action') == 'completed':
        workflow_status = payload.get('workflow_run', {}).get('conclusion')
        if workflow_status == 'success':
            st.write("Workflow completed successfully. Fetching result...")
            result = fetch_processed_result()  # Implement fetching logic
            if result:
                display_selected_parameters(result)
            else:
                st.error("Failed to fetch processed result.")
        else:
            st.error(f"Workflow failed with status: {workflow_status}")
    return jsonify({'status': 'received'}), 200

# Function to fetch the processed result (same as your wait_for_process_completion)
def fetch_processed_result():
    # Fetch the CSV result logic
    pass

# Function to display the parameters in the Streamlit app
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

# Set up Streamlit file uploader
st.title("Scan your Releafs Token")
uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    st.write("Uploading and processing your file. Please wait...")

    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()

    # Upload the file to GitHub (implement your upload logic here)
    # response = upload_file_to_github(file_name, file_content)

    if True:  # Assuming upload is successful
        st.write("File uploaded successfully! Waiting for webhook response...")
    else:
        st.error("Failed to upload the file.")

# Start the Flask app to handle webhooks
if __name__ == '__main__':
    app.run(port=8501)
