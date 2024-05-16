"""GitHub Query Issues

This script is used to fetch and process issues from a GitHub repository based on a query.
It queries GitHub's REST API to get issue data, processes this data to generate a JSON file
for each unique repository.

The script can be run from the command line with optional arguments:
    * python3 github_query_issues.py
    * python3 github_query_issues.py -c config.json
"""

import requests
import json
import re
import os
from typing import Set, List
from utils import ensure_folder_exists, save_state_to_json_file

OUTPUT_DIRECTORY = "data/fetched_data/feature_data"


def sanitize_filename(filename: str) -> str:
    """
        Sanitizes the provided filename by removing invalid characters and replacing spaces with underscores.

        @param filename: The filename to be sanitized.

        @return: The sanitized filename.
    """
    # Remove invalid characters for Windows filenames
    sanitized_name = re.sub(r'[<>:"/\|?*`]', '', filename)
    # Reduce consecutive periods
    sanitized_name = re.sub(r'\.{2,}', '.', sanitized_name)
    # Reduce consecutive spaces to a single space
    sanitized_name = re.sub(r' {2,}', ' ', sanitized_name)
    # Replace space with '_'
    sanitized_name = sanitized_name.replace(' ', '_')

    return sanitized_name


def save_issue_without_duplicates(issue: dict, all_issues: List[dict], added_issue_ids: Set[int]) -> None:
    """
        Saves the provided issue to a list, ensuring that no duplicates are added.
        Done by checking the issue's id in a set of added issue ids.

        @param issue: The issue to be saved.
        @param all_issues: The list for saving all issues.
        @param added_issue_ids: The set of added issue ids.

        @return: None
    """
    # Check if the issue id is not in the set of added issue ids
    if issue["id"] not in added_issue_ids:
        all_issues.append(issue)
        added_issue_ids.add(issue["id"])


def get_issues_from_repository(org_name: str, repo_name: str, token: str, query_labels: str = "") -> List[dict]:
    """
        Fetches all issues from a GitHub repository using the GitHub REST API.
        If query_labels are not specified, all issues are fetched.

        @param org_name: The organization / owner name.
        @param repo_name: The repository name.
        @param token: The GitHub token.
        @param query_labels: The issue labels to query.

        @return: The list of all fetched issues.
    """
    # Prepare the search query
    issues_per_page = 100
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "IssueFetcher/1.0"
    }

    all_issues = []
    added_issue_ids = set()
    session = requests.Session()
    session.headers.update(headers)

    if len(query_labels) == 0:
        query_labels = [None]

    # One request per one label, GitHub query does not support OR logic in queries.
    for label_name in query_labels:
        if label_name is None:
            search_query = f"repo:{org_name}/{repo_name} is:issue"
        else:
            search_query = f"repo:{org_name}/{repo_name} is:issue label:{label_name}"
        base_endpoint = f"https://api.github.com/search/issues?q={search_query}&per_page={issues_per_page}"
        page = 1

        try:
            while True:
                # Update the endpoint for the current page
                endpoint = f"{base_endpoint}&page={page}"

                # Fetch the issues
                response = session.get(endpoint)
                # Check if the request was successful
                response.raise_for_status()

                issues = response.json()['items']

                # Print the sum of loaded issues per label
                if label_name is None:
                    print(f"Loaded {len(issues)} issues without specifying the label.")

                    for issue in issues:
                        # Save issue without duplicates
                        save_issue_without_duplicates(issue, all_issues, added_issue_ids)

                else:
                    print(f"Loaded {len(issues)} issues for label `{label_name}`.")

                    # Safe check, because of GH API not stable return
                    for issue in issues:
                        for label in issue["labels"]:
                            # Filter out issues, that have label name just in description
                            if label["name"] == label_name:
                                # Save issue without duplicates
                                save_issue_without_duplicates(issue, all_issues, added_issue_ids)

                # If we retrieved less than issue_per_page constant, it means we're on the last page
                if len(issues) < issues_per_page:
                    break
                page += 1

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return all_issues


def process_issues(issues: List[dict], org_name: str, repo_name: str) -> List[dict]:
    """
        Processes the fetched issues and prepares them for saving.
        Mandatory issue structure is generated here with all necessary fields.

        @param issues: The list of fetched issues.
        @param org_name: The organization / owner name.
        @param repo_name: The issue repository name.

        @return: The list of processed issues.
    """
    # Initialize the list for modified issues
    issue_list = []

    for issue in issues:
        milestone = issue.get('milestone', {})
        milestone_number = milestone['number'] if milestone else "No milestone"
        milestone_title = milestone['title'] if milestone else "No milestone"
        milestone_html_url = milestone['html_url'] if milestone else "No milestone"

        labels = issue.get('labels', [])
        label_names = [label['name'] for label in labels]

        md_filename_base = f"{issue['number']}_{issue['title'].lower()}.md"
        sanitized_md_filename = sanitize_filename(md_filename_base)

        issue_data = {
            "Number": issue['number'],
            "Owner": org_name,
            "RepositoryName": repo_name,
            "Title": issue['title'],
            "State": issue['state'],
            "URL": issue['html_url'],
            "Body": issue['body'],
            "CreatedAt": issue['created_at'],
            "UpdatedAt": issue['updated_at'],
            "ClosedAt": issue['closed_at'],
            "MilestoneNumber": milestone_number,
            "MilestoneTitle": milestone_title,
            "MilestoneHtmlUrl": milestone_html_url,
            "Labels": label_names,
            "PageFilename": sanitized_md_filename
        }
        issue_list.append(issue_data)

    return issue_list


if __name__ == "__main__":
    print("Downloading issues from GitHub started")

    # Get environment variables set by the controller script
    user_token = os.getenv('GITHUB_TOKEN')
    repositories = os.getenv('REPOSITORIES')

    # Parse repositories JSON string
    try:
        repositories = json.loads(repositories)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    print("Environment variables:")
    print(f"REPOSITORIES: {repositories}")

    # Get the current directory and ensure the output directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Run the function for every repository in the config file
    for repo in repositories:
        org_name = repo["org-name"]
        repo_name = repo["repo-name"]
        query_labels = repo["query-labels"]

        print(f"Downloading issues from repository `{org_name}/{repo_name}`.")

        # Get Issues from repository
        issues = get_issues_from_repository(org_name, repo_name, user_token, query_labels)

        # Process issues
        issue_list = process_issues(issues, org_name, repo_name)

        # Save issues from one repository to the unique JSON file
        output_file_name = save_state_to_json_file(issue_list, "feature", OUTPUT_DIRECTORY, repo_name)
        print(f"Saved {len(issue_list)} issues to {output_file_name}.")

    print("Downloading issues from GitHub ended")

