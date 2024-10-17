import os
import pandas as pd
import streamlit as st

def display_token_details():
    # Path to the CSV file
    csv_file_path = 'process/merged_data_with_metadata.csv'
    
    # Debug: Print the working directory and the path to the CSV file
    print(f"Working directory: {os.getcwd()}")
    print(f"Full path to the CSV file: {os.path.abspath(csv_file_path)}")
    
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        st.error(f"CSV file not found at: {csv_file_path}")
        print(f"Error: CSV file not found at {os.path.abspath(csv_file_path)}")
        return
    else:
        print(f"CSV file found at {os.path.abspath(csv_file_path)}")

    # Fetch CSV data
    df = pd.read_csv(csv_file_path)
    
    if df.empty:
        st.error("CSV file is empty.")
        print("Error: CSV file is empty.")
        return
    else:
        print(f"CSV file is not empty. Number of rows: {len(df)}")

    # Get the last row of the DataFrame
    last_row = df.iloc[-1]
    print(f"Displaying the last row of the CSV file:\n{last_row}")

    # Extract the required parameters
    required_parameters = [
        "Latitude", "Longitude", "Type of Token", "description", "external_url",
        "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
        "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
    ]

    # Create a dictionary of parameters present in the last row
    parameters = {param: last_row[param] for param in required_parameters if param in last_row}
    
    # Debug: Print the extracted parameters
    print("Extracted parameters from the last row:")
    for param, value in parameters.items():
        print(f"{param}: {value}")

    # Display content in Streamlit (optional)
    st.write("### Token Information:")
    st.table(pd.DataFrame.from_dict(parameters, orient='index', columns=['Value']).reset_index().rename(columns={"index": "Parameter"}))

if __name__ == '__main__':
    display_token_details()
