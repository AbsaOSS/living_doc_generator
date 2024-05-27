"""Clean environment before mining

This script is used to clean up the environment before mining data. It removes
files, links, and content from specified directories.

The script can be run from the command line:
    * python3 clean_env_before_mining.py
"""

import os
import shutil


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


def clean_environment():
    print("Cleaning environment for the Living Doc Generator")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the directory variables from the environment variables
    fetch_directory = os.environ['FETCH_DIRECTORY']
    consolidation_directory = os.environ['CONSOLIDATION_DIRECTORY']
    markdown_page_directory = os.environ['MARKDOWN_PAGE_DIRECTORY']

    # Clean the fetched data directories
    clean_directory_content(script_dir, fetch_directory)
    clean_directory_content(script_dir, consolidation_directory)

    # Clean the output directory
    clean_directory_content(script_dir, markdown_page_directory)

    print("Cleaning of env for Living Documentation ended")


if __name__ == "__main__":
    clean_environment()