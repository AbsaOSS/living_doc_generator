"""Utility Functions

This script contains helper functions that are used across multiple src in this project.

These functions can be imported and used in other src as needed.
"""

import os
import json
import argparse
from typing import Union


def parse_arguments(description: str) -> argparse.Namespace:
    """
        Parses the command line arguments provided by the user when running the script.
        As default, the script will use the `config.json` file for configuration.

        @param description: The description of the script.

        @return: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description=description)

    parser.add_argument('-c', '--config',
                        type=str,
                        required=False,
                        default='config.json',
                        help='Configuration JSON file with parameters for data mining from GitHub. Default: config.json')

    args = parser.parse_args()

    return args


def ensure_folder_exists(folder_name: str, current_dir: str) -> None:
    """
        Ensures if folder exists. Creates it if it doesn't.

        @param folder_name: The name of the folder to check.
        @param current_dir: The directory of the current script.

        @return: None
    """

    # Path to the folder in the same directory as this script
    folder_path = os.path.join(current_dir, folder_name)

    # Create the folder if it does not exist
    os.makedirs(folder_path, exist_ok=True)
    print(f"The {folder_name} folder has been created.")


def save_state_to_json_file(state_to_save: Union[list, dict], object_type: str, output_directory: str, state_name: str) -> str:
    """Saves a list state to a JSON file.

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
