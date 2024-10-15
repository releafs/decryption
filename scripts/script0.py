import os
import streamlit as st

# Define directories
input_directory = "input/"
process_directory = "process/"

# Ensure the directories exist
if not os.path.exists(input_directory):
    os.makedirs(input_directory)

if not os.path.exists(process_directory):
    os.makedirs(process_directory)

# Title of the Streamlit App
st.title("Image Uploader and Processing Pipeline")

# File uploader widget
uploaded_files = st.file_uploader("Choose PNG images to upload", type="png", accept_multiple_files=True)

# Save the uploaded files to the 'input' folder
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(input_directory, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Successfully uploaded {uploaded_file.name} to {input_directory}")

    # Once files are uploaded, trigger the processing scripts
    st.write("Starting the processing pipeline...")

    # Call script1.py, script2.py, and script3.py sequentially
    os.system("python script1.py")
    os.system("python script2.py")
    os.system("python script3.py")

    st.success("Processing complete!")
    st.write(f"Check the output in the '{process_directory}' directory.")
