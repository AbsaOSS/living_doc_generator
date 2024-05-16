"""Clean environment before mining

This script is used to clean up the environment before mining data. It removes
files, links, and content from specified directories.

The script can be run from the command line:
    * python3 clean_env_before_mining.py
"""

import os
import shutil


# Directories used in the project
FETCH_DIRECTORY = "data/fetched_data"
CONSOLIDATION_DIRECTORY = "data/consolidation_data"
MARKDOWN_PAGE_DIRECTORY = "output/markdown_pages"


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


if __name__ == "__main__":
    print("Data mining for Living Documentation started")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Clean the fetched data directories
    clean_directory_content(script_dir, FETCH_DIRECTORY)
    clean_directory_content(script_dir, CONSOLIDATION_DIRECTORY)

    # Clean the output directory
    clean_directory_content(script_dir, MARKDOWN_PAGE_DIRECTORY)

    print("Data mining for Living Documentation ended")
