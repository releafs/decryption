import os
import streamlit as st

# Define the absolute path for the input directory
base_directory = os.path.dirname(os.path.abspath(__file__))  # Get the current script's directory
input_directory = os.path.join(base_directory, "decryption", "input")

# Ensure the input directory exists
if not os.path.exists(input_directory):
    os.makedirs(input_directory)

# Title of the Streamlit App
st.title("Image Uploader to 'decryption/input' Directory")

# File uploader widget
uploaded_files = st.file_uploader("Choose PNG images to upload", type="png", accept_multiple_files=True)

# Save the uploaded files to the 'decryption/input' folder
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(input_directory, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Successfully uploaded {uploaded_file.name} to {input_directory}")
