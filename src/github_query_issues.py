"""
GitHub Query Issues

This script is used to fetch, load and process issues from a GitHub repository based on a query.
It queries GitHub's REST API to get issue data and to does process issue data to generate a JSON file
for each unique repository.
"""

import os
import logging

from github import Github, Auth

from action.action_inputs import ActionInputs
from github_integration.github_manager import GithubManager

from utils import (ensure_folder_exists,
                   save_to_json_file,
                   issue_to_dict)


ISSUES_PER_PAGE_LIMIT = 100
OUTPUT_DIRECTORY = "../data/fetched_data/issue_data"


def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Script for downloading issues from GitHub API started.")

    # Load action inputs from the environment
    action_inputs = ActionInputs().load_from_environment()

    # Check if the output directory exists and create it if not
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Initialize GitHub instance
    auth = Auth.Token(token=action_inputs.github_token)
    GithubManager().github = Github(auth=auth, per_page=ISSUES_PER_PAGE_LIMIT)
    GithubManager().show_rate_limit()

    # Mine issues from every config repository
    config_repositories = action_inputs.repositories
    for config_repository in config_repositories:
        repository_id = f"{config_repository.owner}/{config_repository.name}"

        if GithubManager().fetch_repository(repository_id) is None:
            return None

        logging.info(f"Downloading issues from repository `{config_repository.owner}/{config_repository.name}`.")

        # Load all issues from one repository (unique for each repository)
        issues = GithubManager().fetch_issues(labels=config_repository.query_labels)

        # Convert issue objects to dictionaries because they cannot be serialized to JSON directly
        issues_to_save = [issue_to_dict(issue) for issue in issues]

        # Save issues from one repository as a unique JSON file
        output_file_name = save_to_json_file(issues_to_save, "feature", OUTPUT_DIRECTORY, config_repository.name)
        logging.info(f"Saved {len(issues_to_save)} issues to {output_file_name}.")

    logging.info("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
