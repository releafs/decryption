import os
import pandas as pd
import time

# File paths
csv_file_path = 'process/merged_data_with_metadata.csv'
html_output_path = 'output/token_details.html'

# List of parameters to extract from the CSV
required_parameters = [
    "Latitude", "Longitude", "Type of Token", "description", "external_url",
    "Starting Project", "Unit", "Deleverable", "Years_Duration", "Impact Type",
    "SDGs", "Implementer Partner", "Internal Verification", "Local Verification", "Imv_Document"
]

# Function to generate HTML from the last row of the CSV
def generate_html_from_csv():
    # Check if the CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return
    
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Get the last row of the dataframe
    last_row = df.iloc[-1]

    # Extract the required parameters
    parameters = {param: last_row[param] for param in required_parameters if param in last_row}

    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <title>Token Details</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 50px;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f4f4f4;
            }}
        </style>
    </head>
    <body>
        <h1>Token Details</h1>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
    """
    
    # Add rows for each parameter
    for param, value in parameters.items():
        html_content += f"<tr><td>{param}</td><td>{value}</td></tr>"
    
    # Close the table and body
    html_content += """
        </table>
    </body>
    </html>
    """
    
    # Write the HTML content to a file
    with open(html_output_path, 'w') as file:
        file.write(html_content)
    
    print(f"HTML generated and saved to {html_output_path}")

# Call the function to generate HTML
generate_html_from_csv()
