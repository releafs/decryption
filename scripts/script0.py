import os
import requests
import base64
import time
import pandas as pd

# Define GitHub repository details
GITHUB_REPO = "releafs/decryption"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Use environment variable for GitHub token

# Define the input directory and process result paths in your GitHub repository
process_result_path = "decryption/process/merged_data_with_metadata.csv"

# GitHub API URL to fetch results
GITHUB_PROCESS_RESULT_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{process_result_path}"

# Function to fetch the processed result file
def fetch_processed_result(retries=30, initial_delay=0, subsequent_delay=30):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Initial wait for 1 minute before the first attempt
    print(f"Waiting for {initial_delay} seconds before the first attempt...")
    time.sleep(initial_delay)

    for attempt in range(retries):
        response = requests.get(GITHUB_PROCESS_RESULT_URL, headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            content = base64.b64decode(file_info["content"]).decode("utf-8")
            return content
        else:
            print(f"Processed result not found. Retrying {attempt+1}/{retries} after {subsequent_delay} seconds...")

        # Wait for 30 seconds before the next attempt
        time.sleep(subsequent_delay)

    print("Processed result could not be fetched after multiple retries.")
    return None

# Main function to trigger the fetching process
if __name__ == "__main__":
    result = fetch_processed_result()

    if result:
        # Save the result to a local CSV file for further analysis
        with open("fetched_results.csv", "w") as file:
            file.write(result)
        print("Processing complete! Result saved to fetched_results.csv.")
    else:
        print("Failed to fetch the processed result.")
