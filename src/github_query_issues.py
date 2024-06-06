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


def filter_issues_by_numbers(issues: List[Issue], added_issue_numbers: Set[int]) -> (List[Issue], Set[int]):
    """
    TODO - update docstring
    Saves the provided issue to a list, ensuring that no duplicates are added.
    Done by checking the issue's id in a set of added issue ids.

    @param issue: The issue to be saved.
    @param loaded_issues: The list to load and save all issues.
    @param added_issue_numbers: The set of added issue ids.

    @return: None TODO
    """
    # Save only issues with unique issue number
    filtered_issues = []
    for issue in issues:
        if issue.number not in added_issue_numbers:
            filtered_issues.append(issue)
            added_issue_numbers.add(issue.number)

    return filtered_issues, added_issue_numbers


def get_base_endpoint(label_name: str, repo: Repository) -> str:
    """
    Prepares the base endpoint for fetching issues from a GitHub repository.
    If the label name is not specified, the base endpoint is for fetching all issues.

    @param label_name: The name of the label.
    @param repo: The repository object.

    @return: The base endpoint for fetching issues.
    """
    if label_name is None:
        search_query = f"repo:{repo.organization_name}/{repo.repository_name} is:issue"
    else:
        search_query = f"repo:{repo.organization_name}/{repo.repository_name} is:issue label:{label_name}"

    base_endpoint = f"https://api.github.com/search/issues?q={search_query}&per_page={ISSUE_PER_PAGE}"

    return base_endpoint


# TODO delete
# def process_issues_by_label(fetched_issues: List[dict], added_issue_numbers: Set[int], label_name: str) -> List[Issue]:
#     """
#     Processes the fetched issues and loads them to the list.
#     It ensures that no duplicates are added by checking the issue's number.
#
#     @param fetched_issues: The list of fetched issues from the GitHub API.
#     @param loaded_issues: The list to load and save all issues.
#     @param added_issue_numbers: The set of added issue numbers.
#     @param label_name: The name of the label used to filter issues.
#
#     @return: None
#     """
#     issues = []
#
#     # If there is no label specified, save all issues
#     if label_name is None:
#         print(f"Loaded {len(fetched_issues)} issues without specifying the label.")
#
#         for issue in fetched_issues:
#             loaded_issues = filter_issues_by_numbers(issue, added_issue_numbers)
#             issues.extend(loaded_issues)
#
#     else:
#         print(f"Loaded {len(fetched_issues)} issues for label `{label_name}`.")
#
#         # Safe check, because of GH API not stable return
#         for issue in fetched_issues:
#             for label in issue["labels"]:
#                 # Filter out issues, that have label name just in description
#                 if label["name"] == label_name:
#                     loaded_issues = filter_issues_by_numbers(issue, added_issue_numbers)
#                     issues.extend(loaded_issues)
#
#     return issues


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

    # Fetch issues for each label
    # One session request per one label - TODO why?
    for label_name in repository.query_labels:
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

                # Parse json issue to Issue object
                fetched_issues_json = response.json()['items']
                fetched_issues = []     # TODO create small method like filter_issues_by_numbers ==> return instead of []
                for issue_json in fetched_issues_json:
                    issue = Issue(repository)
                    issue.load_from_json(issue_json)

                    fetched_issues.append(issue)
                print(f"Loaded {len(fetched_issues)} issues for label `{label_name}`, page {page}.")

                # Filter issues with unique issue number
                unique_issues, issue_numbers = filter_issues_by_numbers(fetched_issues, issue_numbers)
                loaded_issues.extend(unique_issues)

                # If we retrieved less than issue_per_page constant, it means we're on the last page
                if len(fetched_issues_json) < ISSUE_PER_PAGE:
                    break
                page += 1

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return loaded_issues


# def process_issues(loaded_issues: List[dict], repo: Repository) -> List[Issue]:
#     """
#     Processes the fetched issues and prepares them for saving.
#     Mandatory issue structure is generated here with all necessary fields.
#
#     @param loaded_issues: The list of loaded issues.
#     @param repo: The repository object.
#
#     @return: The list of processed issues.
#     """
#     processed_issues = []
#
#     for loaded_issue in loaded_issues:
#         issue = Issue(repo.organization_name, repo.repository_name)
#         issue.load_from_json(loaded_issue)
#         processed_issues.append(issue)
#
#     return processed_issues


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

        # Process issues - TODO delete
        # processed_issues = process_issues(loaded_issues, repository)

        # Save issues from one repository to the unique JSON file
        output_file_name = save_issues_to_json_file(loaded_issues, "feature", OUTPUT_DIRECTORY, repository.repository_name)
        print(f"Saved {len(loaded_issues)} issues to {output_file_name}.")

    print("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
