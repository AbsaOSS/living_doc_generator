"""
GitHub Query Issues

This script is used to fetch, load and process issues from a GitHub repository based on a query.
It queries GitHub's REST API to get issue data and to does process issue data to generate a JSON file
for each unique repository.
"""

import requests
import json
import os

from containers.issue import Issue
from containers.repository import Repository
from typing import Set, List

from utils import (ensure_folder_exists,
                   save_to_json_file,
                   initialize_request_session)


OUTPUT_DIRECTORY = "../data/fetched_data/issue_data"
ISSUE_PER_PAGE = 100


def filter_issues_by_numbers(issues: List[Issue], added_issue_numbers: Set[int]) -> (List[Issue], Set[int]):
    """
    Saves the provided issue to a list, ensuring that no duplicates are added.
    Done by checking the issue's id in a set of added issue ids.

    @param issues: The list of issues to filter.
    @param added_issue_numbers: The set of added issue ids.

    @return: The filtered list of issues and the updated set of added issue ids.
    """
    # Save only issues with unique issue number
    filtered_issues = []
    for issue in issues:
        if issue.number not in added_issue_numbers:
            filtered_issues.append(issue)
            added_issue_numbers.add(issue.number)

    return filtered_issues, added_issue_numbers


def get_base_endpoint(label_name: str, repository: Repository) -> str:
    """
    Prepares the base endpoint for fetching issues from a GitHub repository.
    If the label name is not specified, the base endpoint is for fetching all issues.

    @param label_name: The name of the label.
    @param repository: The repository object.

    @return: The base endpoint for fetching issues.
    """
    if label_name is None:
        search_query = f"repo:{repository.organization_name}/{repository.repository_name} is:issue"
    else:
        search_query = f"repo:{repository.organization_name}/{repository.repository_name} is:issue label:{label_name}"

    base_endpoint = f"https://api.github.com/search/issues?q={search_query}&per_page={ISSUE_PER_PAGE}"

    return base_endpoint


def get_issues_from_repository(repository: Repository, github_token: str) -> List[Issue]:
    """
    Fetches all issues from a GitHub repository using the GitHub REST API.
    If query_labels are not specified, all issues are fetched.

    @param repository: The instance of Repository class.
    @param github_token: The GitHub token.

    @return: The list of all fetched issues.
    """
    loaded_issues = []
    issue_numbers = set()

    # Initialize the request session
    session = initialize_request_session(github_token)

    # Check if query_labels is empty, if so, set it to None to fetch all issues
    labels_to_query = repository.query_labels if repository.query_labels else [None]

    # Fetch issues for each label
    # One session request per one label - TODO why?
    for label_name in labels_to_query:
        base_endpoint = get_base_endpoint(label_name, repository)
        page = 1

        try:
            while True:
                # Update the endpoint for the current page
                endpoint = f"{base_endpoint}&page={page}"

                # Fetch the issues
                response = session.get(endpoint)
                # Check if the request was successful
                response.raise_for_status()

                issues = []     # TODO create small method like filter_issues_by_numbers ==> return instead of []

                # Parse json issue to Issue object
                issues_json = response.json()['items']
                for issue_json in issues_json:
                    issue = Issue(repository)
                    issue.load_from_json(issue_json)

                    if label_name is not None:
                        issue.filter_out_labels_in_description(label_name, issues)
                    else:
                        issues.append(issue)

                if label_name is None:
                    print(f"Loaded {len(issues)} issues.")
                else:
                    print(f"Loaded {len(issues)} issues for label `{label_name}`.")

                # Filter issues with unique issue number
                unique_issues, issue_numbers = filter_issues_by_numbers(issues, issue_numbers)
                loaded_issues.extend(unique_issues)

                # If we retrieved less than issue_per_page constant, it means we're on the last page
                if len(issues_json) < ISSUE_PER_PAGE:
                    break
                page += 1

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return loaded_issues


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

    # Get the current directory and check that output dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Run the function for every given repository
    for repository_json in repositories_json:
        repository = Repository()
        repository.load_from_json(repository_json)

        print(f"Downloading issues from repository `{repository.organization_name}/{repository.repository_name}`.")

        # Load Issues from repository (unique for each repository)
        loaded_issues = get_issues_from_repository(repository, github_token)

        # Save issues from one repository to the unique JSON file
        issues_to_save = [issue.to_dict() for issue in loaded_issues]

        output_file_name = save_to_json_file(issues_to_save, "feature", OUTPUT_DIRECTORY, repository.repository_name)
        print(f"Saved {len(loaded_issues)} issues to {output_file_name}.")

    print("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
