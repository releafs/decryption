import os
import streamlit as st
import pandas as pd
import json
from flask import Flask, request

# Create a Flask app to receive webhook events
app = Flask(__name__)

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

# Function to fetch processed result
def fetch_processed_result():
    # Implement logic to fetch the result (same as `wait_for_process_completion`)
    pass

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

# Webhook handler route
@app.route('/webhook', methods=['POST'])
def handle_github_webhook():
    if request.method == 'POST':
        payload = request.json
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

# Start the webhook handler (this requires you to run the Streamlit app on a compatible platform)
if __name__ == '__main__':
    app.run(debug=True, port=5000)

