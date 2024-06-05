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

from utils import ensure_folder_exists, save_issues_to_json_file, initialize_request_session


OUTPUT_DIRECTORY = "../data/fetched_data/issue_data"
ISSUE_PER_PAGE = 100


def save_issue_without_duplicates(issue: dict, loaded_issues: List[dict], added_issue_numbers: Set[int]) -> None:
    """
    Saves the provided issue to a list, ensuring that no duplicates are added.
    Done by checking the issue's id in a set of added issue ids.

    @param issue: The issue to be saved.
    @param loaded_issues: The list to load and save all issues.
    @param added_issue_numbers: The set of added issue ids.

    @return: None
    """
    # Save only issues with unique issue number
    if issue["number"] not in added_issue_numbers:
        loaded_issues.append(issue)
        added_issue_numbers.add(issue["number"])


def get_base_endpoint(label_name: str, repo: Repository) -> str:
    """
    Prepares the base endpoint for fetching issues from a GitHub repository.
    If the label name is not specified, the base endpoint is for fetching all issues.

    @param label_name: The name of the label.
    @param repo: The repository object.

    @return: The base endpoint for fetching issues.
    """
    if label_name is None:
        search_query = f"repo:{repo.organizationName}/{repo.repositoryName} is:issue"
    else:
        search_query = f"repo:{repo.organizationName}/{repo.repositoryName} is:issue label:{label_name}"

    base_endpoint = f"https://api.github.com/search/issues?q={search_query}&per_page={ISSUE_PER_PAGE}"

    return base_endpoint


def process_issues_by_label(fetched_issues: List[dict], loaded_issues: List[dict], added_issue_numbers: Set[int], label_name: str) -> None:
    """
    Processes the fetched issues and loads them to the list.
    It ensures that no duplicates are added by checking the issue's number.

    @param fetched_issues: The list of fetched issues from the GitHub API.
    @param loaded_issues: The list to load and save all issues.
    @param added_issue_numbers: The set of added issue numbers.
    @param label_name: The name of the label used to filter issues.

    @return: None
    """
    # If there is no label specified, save all issues
    if label_name is None:
        print(f"Loaded {len(fetched_issues)} issues without specifying the label.")

        for issue in fetched_issues:
            save_issue_without_duplicates(issue, loaded_issues, added_issue_numbers)

    else:
        print(f"Loaded {len(fetched_issues)} issues for label `{label_name}`.")

        # Safe check, because of GH API not stable return
        for issue in fetched_issues:
            for label in issue["labels"]:
                # Filter out issues, that have label name just in description
                if label["name"] == label_name:
                    save_issue_without_duplicates(issue, loaded_issues, added_issue_numbers)


def get_issues_from_repository(repo: Repository, github_token: str) -> List[dict]:
    """
    Fetches all issues from a GitHub repository using the GitHub REST API.
    If query_labels are not specified, all issues are fetched.

    @param repo: The repository object.
    @param github_token: The GitHub token.

    @return: The list of all fetched issues.
    """
    loaded_issues = []
    added_issue_numbers = set()

    # Initialize the request session
    session = initialize_request_session(github_token)

    if repo.queryLabels is None:
        repo.queryLabels = []

    # One session request per one label
    for label_name in repo.queryLabels:
        base_endpoint = get_base_endpoint(label_name, repo)
        page = 1

        try:
            while True:
                # Update the endpoint for the current page
                endpoint = f"{base_endpoint}&page={page}"

                # Fetch the issues
                response = session.get(endpoint)
                # Check if the request was successful
                response.raise_for_status()

                fetched_issues = response.json()['items']

                # Process issues by label
                process_issues_by_label(fetched_issues, loaded_issues, added_issue_numbers, label_name)

                # If we retrieved less than issue_per_page constant, it means we're on the last page
                if len(fetched_issues) < ISSUE_PER_PAGE:
                    break
                page += 1

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return loaded_issues


def process_issues(loaded_issues: List[dict], repo: Repository) -> List[Issue]:
    """
    Processes the fetched issues and prepares them for saving.
    Mandatory issue structure is generated here with all necessary fields.

    @param loaded_issues: The list of loaded issues.
    @param repo: The repository object.

    @return: The list of processed issues.
    """
    processed_issues = []

    for loaded_issue in loaded_issues:
        issue = Issue(repo.organizationName, repo.repositoryName)
        issue.load_from_json(loaded_issue)
        processed_issues.append(issue)

    return processed_issues


def main() -> None:
    print("Script for downloading issues from GitHub API started.")

    # Get environment variables from the controller script
    github_token = os.getenv('GITHUB_TOKEN')
    repositories_raw = os.getenv('REPOSITORIES')

    # Parse repositories JSON string
    try:
        repositories_raw = json.loads(repositories_raw)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    # Get the current directory and check that output dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Run the function for every given repository
    for repository in repositories_raw:
        repo = Repository()
        repo.load_from_json(repository)

        print(f"Downloading issues from repository `{repo.organizationName}/{repo.repositoryName}`.")

        # Load Issues from repository
        loaded_issues = get_issues_from_repository(repo, github_token)

        # Process issues
        processed_issues = process_issues(loaded_issues, repo)

        # Save issues from one repository to the unique JSON file
        # output_file_name = save_issues_to_json_file(processed_issues, "feature", OUTPUT_DIRECTORY, repo.repositoryName)
        output_file_name = save_issues_to_json_file(processed_issues, "feature", OUTPUT_DIRECTORY, repo.repositoryName)
        print(f"Saved {len(processed_issues)} issues to {output_file_name}.")

    print("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
