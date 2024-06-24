"""
GitHub Query Issues

This script is used to fetch, load and process issues from a GitHub repository based on a query.
It queries GitHub's REST API to get issue data and to does process issue data to generate a JSON file
for each unique repository.
"""

import json
import os

from containers.repository import Repository

from utils import (ensure_folder_exists,
                   initialize_request_session,
                   save_to_json_file)


OUTPUT_DIRECTORY = "../data/fetched_data/issue_data"
ISSUE_PER_PAGE = 100


def main() -> None:
    print("Script for downloading issues from GitHub API started.")

    # Get environment variables from the controller script
    github_token = os.getenv('GITHUB_TOKEN')
    repositories_env = os.getenv('REPOSITORIES')

    # Parse repositories JSON string
    try:
        repositories_json = json.loads(repositories_env)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Initialize the request session
    session = initialize_request_session(github_token)

    # Mine issues from every input Repository
    for repository_json in repositories_json:
        repository = Repository()
        repository.load_from_json(repository_json)

        print(f"Downloading issues from repository `{repository.organization_name}/{repository.repository_name}`.")

        # Load issues from one repository (unique for each repository)
        loaded_repository_issues = repository.get_issues(session)

        # Convert issue objects to dictionaries because they cannot be serialized to JSON directly
        # TODO: Check if this is the right way to append the issue to the project, json, object, to_dict and back to json
        issues_to_save = [issue.to_dict() for issue in loaded_repository_issues]

        # Save issues from one repository as a unique JSON file
        output_file_name = save_to_json_file(issues_to_save, "feature", OUTPUT_DIRECTORY, repository.repository_name)
        print(f"Saved {len(issues_to_save)} issues to {output_file_name}.")

    print("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
