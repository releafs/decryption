import os
import time
import pandas as pd
import streamlit as st

# Function to upload file and display upload logic
def upload_image():
    st.title("Upload Your Token Image")
    uploaded_file = st.file_uploader("Choose a PNG image to upload", type="png")

    if uploaded_file is not None:
        st.write(f"File selected: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
        # Your logic to upload and handle the file goes here...

        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

# Function to display token details using the fetched CSV
def display_token_details():
    # Path to the CSV file
    csv_file_path = 'process/merged_data_with_metadata.csv'
    
    # Fetch CSV data without caching
    df = pd.read_csv(csv_file_path)
    
    if df.empty:
        st.error("CSV file is empty.")
        return

    last_row = df.iloc[-1]

    parameters = {col: last_row[col] for col in df.columns}
    
    st.write("### Token Information:")
    st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))

# Layout: Two columns for Upload and Display
col1, col2 = st.columns(2)

# Column 1: Image Upload
with col1:
    upload_image()

# Column 2: Display Token Details with "Fetch Latest" Button
with col2:
    st.title("Display Token Details")
    
    if st.button("Fetch Latest"):
        st.write("Fetching latest token details...")
        with st.spinner('Waiting for 60 seconds...'):
            time.sleep(60)
        
        display_token_details()
