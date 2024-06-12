"""Clean environment before mining

This script is used to clean up the environment before mining data. It removes
files, links, and content from specified directories.

The script can be run from the command line:
    * python3 clean_env_before_mining.py
"""

import os
import shutil

DATA_DIRECTORY = "../data"


def clean_directory_content(script_dir: str, directory: str) -> None:
    """
        Deletes all content from the specified directory.

        @param script_dir: The directory of the current script.
        @param directory: The directory to be cleaned.

        @return: None
    """

    # Get the absolute path of the directory
    directory_path = os.path.join(script_dir, directory)
    print(f"Cleaning path: {directory_path}")

    # Check if the directory exists
    if os.path.exists(directory_path):
        # Delete all content from the directory
        shutil.rmtree(directory_path)


def clean_environment() -> None:
    print("Cleaning environment for the Living Doc Generator")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get output directory from the env variables
    output_directory = os.environ['OUTPUT_DIRECTORY']

    # Clean the directory content for generated data and output
    clean_directory_content(script_dir, DATA_DIRECTORY)
    clean_directory_content(script_dir, output_directory)

    print("Cleaning environment for Living Documentation ended")


if __name__ == "__main__":
    clean_environment()
