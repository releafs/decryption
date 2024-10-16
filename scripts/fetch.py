import os
import pandas as pd
import streamlit as st

# File path for the CSV
csv_file_path = 'process/merged_data_with_metadata.csv'

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to display the last row of the CSV in Streamlit
def display_token_details():
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        st.error(f"CSV file not found: {csv_file_path}")
        return
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Get the last row of the dataframe
    last_row = df.iloc[-1]

    # Extract the required parameters
    parameters = {param: last_row[param] for param in required_parameters if param in last_row}

    # Display content in Streamlit
    st.title("Token Details")
    
    # Create a table to display parameters
    st.write("### Token Information:")
    st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))

# Streamlit page setup
st.set_page_config(page_title="Token Details", layout="wide")

# Call the function to display the details
display_token_details()
