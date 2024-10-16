import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64
import zlib
import json

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to process the uploaded image
def process_image(file_content):
    # Step 1: Read the image and extract data (simulate script1.py)
    image = Image.open(io.BytesIO(file_content))
    # Assuming the data is stored in the image metadata (replace with actual logic)
    if 'Description' in image.info:
        binary_data = image.info['Description']
    else:
        st.error("No embedded data found in the image.")
        return None

    # Step 2: Decompress and decode the data (simulate script2.py)
    try:
        compressed_data = base64.b64decode(binary_data)
        decompressed_data = zlib.decompress(compressed_data).decode('utf-8')
        data_dict = json.loads(decompressed_data)
    except Exception as e:
        st.error(f"Error decompressing data: {e}")
        return None

    # Step 3: Merge data with metadata (simulate script3.py)
    # Assuming you have a metadata CSV file to merge with
    try:
        metadata_df = pd.read_csv('metadata.csv')  # Ensure this file is accessible
        data_df = pd.DataFrame([data_dict])
        merged_df = pd.merge(data_df, metadata_df, on='some_common_key')  # Replace with actual key
    except Exception as e:
        st.error(f"Error merging data: {e}")
        return None

    return merged_df

# Function to display the selected parameters in a table
def display_selected_parameters(df):
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
    st.write("Processing your file. Please wait...")

    file_content = uploaded_file.getvalue()

    # Process the image
    with st.spinner("Processing..."):
        result_df = process_image(file_content)

    if result_df is not None:
        st.success("Processing complete! Displaying the result below:")
        display_selected_parameters(result_df)
    else:
        st.error("Processing failed. Please check the image and try again.")
