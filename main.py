import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import requests
from sms import send_sms

def read_google_sheet(json_key_path, sheet_id):
    """
    Reads data from a Google Sheet and returns it as a pandas DataFrame.

    Args:
        json_key_path (str): Path to the GCP service account JSON key file.
        sheet_id (str): Google Sheet ID.

    Returns:
        pd.DataFrame: Data from the Google Sheet.
    """
    # Define the required scopes
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # Authenticate using the service account key
    credentials = Credentials.from_service_account_file(json_key_path, scopes=scopes)
    gc = gspread.authorize(credentials)

    # Open the Google Sheet by ID
    sheet = gc.open_by_key(sheet_id)

    # Assuming data is in the first worksheet
    worksheet = sheet.get_worksheet(0)

    # Get all values as a list of lists
    data = worksheet.get_all_values()

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # Skip the header row

    return df

def interact_with_openai(task, api_endpoint, api_key):
    """
    Interacts with the Azure OpenAI API for a given task.

    Args:
        task (str): Task description to pass to the API.
        api_endpoint (str): API endpoint URL.
        api_key (str): API key for authentication.

    Returns:
        None
    """
    # Define the headers for the API call
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # Define the payload for the chat completion
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"You are a construction scheduler agent. Here is the task you "
                           f"need to focus on now >> {task}. Assume you are contacting the "
                           f"person assigned to this task in the field. You need to ask a "
                           f"sequence of max 4 to 5 questions one by one until you get "
                           f"the update "
                           f"related to this task. Try to figure out first if the task is "
                           f"ongoing, completed, or not started. Then get the updates and "
                           f"also get an updated end date. Once you are done getting the "
                           f"updates "
                           f"create a summary of the conversation plus the image (if "
                           f"uploaded) "
                           f"and publish the report. Make sure you say BYE at the end of "
                           f"the chat this is very important."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    user_input = ""
    counter = 1
    completion = ""

    while user_input != "exit" and "bye" not in completion.lower():
        if counter != 1:
            user_input = input("write here: ... ")
            payload["messages"].append({"role": "user", "content": user_input})

        try:
            # Make the POST request
            response = requests.post(api_endpoint, headers=headers, json=payload)

            # Check if the response is successful
            if response.status_code == 200:
                response_data = response.json()
                completion = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                # print("Response:", completion)
                send_sms(completion,"+16473911477")
            else:
                print(f"Error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)

        counter += 1

def main():
    """
    Main function to read tasks from Google Sheet and interact with OpenAI API.
    """
    # Configuration
    json_key_path = "creds/smartscheduler-444021-2581ce4ff8b6.json"
    sheet_id = "1ymM9a-_iMuxuKyn0XioaA3aEaTkbkBihDGi9eeOicSs"
    api_endpoint = "https://progress-tracking-dev-east-us.openai.azure.com/openai/deployments/gpt-4o-prig-dev/chat/completions?api-version=2024-08-01-preview"
    api_key = "3aac79231b2d402ea89f0d94d5cefec4"

    # Read tasks from Google Sheet
    df = read_google_sheet(json_key_path, sheet_id)

    # Process each task
    for _, item in df.iterrows():
        task = item["Task"]
        interact_with_openai(task, api_endpoint, api_key)

if __name__ == "__main__":
    main()
