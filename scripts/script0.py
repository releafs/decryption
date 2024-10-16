import streamlit as st
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import time
import io

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
AWS_S3_BUCKET = st.secrets["AWS_S3_BUCKET"]
AWS_S3_REGION = 'us-east-1'  # Replace with your region
S3_FILE_KEY = 'merged_data_with_metadata.csv'  # The key of the file in S3

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to fetch the processed result from S3
def fetch_processed_result():
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION
    )
    try:
        obj = s3.get_object(Bucket=AWS_S3_BUCKET, Key=S3_FILE_KEY)
        data = obj['Body'].read()
        return data
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        else:
            st.error(f"Error fetching processed result: {e}")
            return None

# Function to display the selected parameters in a table
def display_selected_parameters(csv_data):
    df = pd.read_csv(io.BytesIO(csv_data))

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
    Your Releafs Token empowers real-world climate action. Track your token to discover the tangible, positive impact you're contributing to. Together, we're making a sustainable future possible.
    Powered by [Releafs](https://www.releafs.co)
    """
)

uploaded_file = st.file_uploader("Choose a PNG image", type="png")

if uploaded_file is not None:
    st.write("Uploading and processing your file. Please wait...")

    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()

    # Upload the file to GitHub (this will trigger the workflow)
    def upload_file_to_github(file_name, file_content):
        import base64
        import requests

        GITHUB_REPO = "releafs/decryption"
        GITHUB_BRANCH = "main"
        GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

        encoded_content = base64.b64encode(file_content).decode("utf-8")
        commit_message = f"Upload {file_name}"

        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }

        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/decryption/input/{file_name}"

        response = requests.put(url, json=data, headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        })

        return response

    response = upload_file_to_github(file_name, file_content)

    if response.status_code in [201, 200]:
        st.write("File uploaded successfully! Processing...")

        # Wait for the workflow to complete and the file to be available in S3
        result = None
        max_retries = 20
        delay = 10  # seconds

        for attempt in range(max_retries):
            result = fetch_processed_result()
            if result:
                break
            else:
                st.write(f"Processed result not found. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(delay)

        if result:
            st.success("Processing complete! Displaying the result below:")
            display_selected_parameters(result)
        else:
            st.error("Could not retrieve the processed result.")
    else:
        st.error(f"Failed to upload {file_name}. Response: {response.text}")
