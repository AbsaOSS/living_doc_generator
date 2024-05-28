"""
GitHub Query Issues

This script is used to fetch, load and process issues from a GitHub repository based on a query.
It queries GitHub's REST API to get issue data and to does process issue data to generate a JSON file
for each unique repository.
"""

import requests
import json
import re
import os
from typing import Set, List
from utils import ensure_folder_exists, save_state_to_json_file, initialize_request_session
from containers import Repository, Issue

OUTPUT_DIRECTORY = "../data/fetched_data/feature_data"
ISSUE_PER_PAGE = 100


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes the provided filename by removing invalid characters and replacing spaces with underscores.

    @param filename: The filename to be sanitized.

    @return: The sanitized filename.
    """
    # Remove invalid characters for Windows filenames
    sanitized_name = re.sub(r'[<>:"/|?*`]', '', filename)
    # Reduce consecutive periods
    sanitized_name = re.sub(r'\.{2,}', '.', sanitized_name)
    # Reduce consecutive spaces to a single space
    sanitized_name = re.sub(r' {2,}', ' ', sanitized_name)
    # Replace space with '_'
    sanitized_name = sanitized_name.replace(' ', '_')

    return sanitized_name


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


def get_base_endpoint(label_name: str, org_name: str, repo_name: str) -> str:
    """
    Prepares the base endpoint for fetching issues from a GitHub repository.
    If the label name is not specified, the base endpoint is for fetching all issues.

    @param label_name: The name of the label.
    @param org_name: The organization / owner name.
    @param repo_name: The repository name.

    @return: The base endpoint for fetching issues.
    """
    if label_name is None:
        search_query = f"repo:{org_name}/{repo_name} is:issue"
    else:
        search_query = f"repo:{org_name}/{repo_name} is:issue label:{label_name}"

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


def get_issues_from_repository(org_name: str, repo_name: str, github_token: str, query_labels: List = None) -> List[dict]:
    """
    Fetches all issues from a GitHub repository using the GitHub REST API.
    If query_labels are not specified, all issues are fetched.

    @param org_name: The organization / owner name.
    @param repo_name: The repository name.
    @param github_token: The GitHub token.
    @param query_labels: The issue labels to query.

    @return: The list of all fetched issues.
    """
    loaded_issues = []
    added_issue_numbers = set()

    # Initialize the request session
    session = initialize_request_session(github_token)

    if query_labels is None:
        query_labels = []

    # One session request per one label
    for label_name in query_labels:
        base_endpoint = get_base_endpoint(label_name, org_name, repo_name)
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


def process_issues(loaded_issues: List[dict], org_name: str, repo_name: str) -> List[dict]:
    """
    Processes the fetched issues and prepares them for saving.
    Mandatory issue structure is generated here with all necessary fields.

    @param loaded_issues: The list of loaded issues.
    @param org_name: The organization / owner name.
    @param repo_name: The issue repository name.

    @return: The list of processed issues.
    """
    processed_issues = []

    for issue in loaded_issues:
        milestone = issue.get('milestone', {})
        milestone_number = milestone['number'] if milestone else "No milestone"
        milestone_title = milestone['title'] if milestone else "No milestone"
        milestone_html_url = milestone['html_url'] if milestone else "No milestone"

        labels = issue.get('labels', [])
        label_names = [label['name'] for label in labels]

        md_filename_base = f"{issue['number']}_{issue['title'].lower()}.md"
        sanitized_md_filename = sanitize_filename(md_filename_base)

        # Define Issue object as it follows the Issue dataclass
        issue_object = Issue(
            number=issue['number'],
            owner=org_name,
            repository_name=repo_name,
            title=issue['title'],
            state=issue['state'],
            url=issue['html_url'],
            body=issue['body'],
            created_at=issue['created_at'],
            updated_at=issue['updated_at'],
            closed_at=issue['closed_at'],
            milestone_number=milestone_number,
            milestone_title=milestone_title,
            milestone_html_url=milestone_html_url,
            labels=label_names,
            page_filename=sanitized_md_filename
        )

        # Convert Issue object to dictionary, because JSON does not support dataclasses
        issue_dict = issue_object.to_dict()
        processed_issues.append(issue_dict)

    return processed_issues


def main() -> None:
    print("Script for downloading issues from GitHub API started.")

    # Get environment variables from the controller script
    github_token = os.getenv('GITHUB_TOKEN')
    repositories = os.getenv('REPOSITORIES')

    # Parse repositories JSON string
    try:
        repositories = json.loads(repositories)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    # Get the current directory and check that output dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Run the function for every given repository
    for repository in repositories:
        repo = Repository(orgName=repository["orgName"],
                          repoName=repository["repoName"],
                          queryLabels=repository["queryLabels"])

        print(f"Downloading issues from repository `{repo.orgName}/{repo.repoName}`.")

        # Load Issues from repository
        loaded_issues = get_issues_from_repository(repo.orgName, repo.repoName, github_token, repo.queryLabels)

        # Process issues
        processed_issues = process_issues(loaded_issues, repo.orgName, repo.repoName)

        # Save issues from one repository to the unique JSON file
        output_file_name = save_state_to_json_file(processed_issues, "feature", OUTPUT_DIRECTORY, repo.repoName)
        print(f"Saved {len(processed_issues)} issues to {output_file_name}.")

    print("Script for downloading issues from GitHub API ended.")


if __name__ == "__main__":
    main()
