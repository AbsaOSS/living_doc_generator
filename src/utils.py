"""Utility Functions

This script contains helper functions that are used across multiple src in this project.

These functions can be imported and used in other src as needed.
"""

import os
import json
import requests
from typing import Union


def initialize_request_session(github_token: str) -> requests.sessions.Session:
    """
    Initializes the request Session and updates the headers.

    @param github_token: The GitHub user token for authentication.

    @return: A configured request session.
    """

    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {github_token}",
        "User-Agent": "IssueFetcher/1.0"
    }
    session.headers.update(headers)

    return session


def ensure_folder_exists(folder_name: str, current_dir: str) -> None:
    """
    Ensures that given folder exists. Creates it if it doesn't.

    @param folder_name: The name of the folder to check.
    @param current_dir: The directory of the current script.

    @return: None
    """

    # Path to the folder in the same directory as this script
    folder_path = os.path.join(current_dir, folder_name)

    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"The '{folder_path}' folder has been created.")


def save_state_to_json_file(state_to_save: Union[list, dict], object_type: str, output_directory: str, state_name: str) -> str:
    """
    Saves a list state to a JSON file.

    @param state_to_save: The list or dict to be saved.
    @param object_type: The object type of the state (e.g., 'feature', 'project').
    @param output_directory: The directory, where the file will be saved.
    @param state_name: The naming of the state.

    @return: The name of the output file.
    """
    # Prepare the unique saving naming
    sanitized_name = state_name.lower().replace(" ", "_").replace("-", "_")
    output_file_name = f"{sanitized_name}.{object_type}.json"
    output_file_path = f"{output_directory}/{output_file_name}"

    # Save a file with correct output
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(state_to_save, json_file, ensure_ascii=False, indent=4)

    return output_file_name
