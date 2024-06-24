"""Consolidate Feature Data

This script is used to consolidate feature data with additional project data.
After merging datasets the output is one JSON file containing features with
additional project information.

The script can be run from the command line also with optional arguments:
    * python3 consolidate_issue_data.py
    * python3 consolidate_issue_data.py -c config.json
"""

import os
import json
from typing import List, Dict, Set, Tuple
from utils import ensure_folder_exists, save_to_json_file

from containers.repository import Repository
from containers.repository_issue import RepositoryIssue
from containers.project_issue import ProjectIssue
from containers.consolidated_issue import ConsolidatedIssue

REPOSITORY_ISSUE_DIRECTORY = "../data/fetched_data/issue_data"
PROJECT_ISSUE_DIRECTORY = "../data/fetched_data/project_data"
CONSOLIDATED_ISSUE_DIRECTORY = "../data/issue_consolidation"


def load_repository_issue_from_data(directory: str, repository_name: str) -> List[dict]:
    """
        Loads feature data from a JSON file located in a specified directory.

        @param directory: The directory where the JSON file to be loaded is located.
        @param repository_name: The name of the repository for which the feature data is being loaded.

        @return: The feature data as a list of dictionaries.
    """
    # Load feature data
    # TODO: Make a context attribute for feature, so the method is more generic
    issue_filename = f"{repository_name}.feature.json"
    issue_filename_path = os.path.join(directory, issue_filename).replace("-", "_").lower()
    issue_json_from_data = json.load(open(issue_filename_path))

    return issue_json_from_data


# TODO: probably wrong typehint for repository_issues
def consolidate_project_issues(repository_issues: List[RepositoryIssue],
                               project_issues: Dict[str, ProjectIssue],
                               project_title: str) -> List[ConsolidatedIssue]:
    """
        Merges feature data with additional project information.
        Every feature identified by unique string key is compared with keys of project data features.
        If the keys match, additional information from the project data is added to the feature.

        @param repository_issues: The feature data to be merged.
        @param project_issues: The project data to be merged.
        @param project_title: The title of the project.

        @return: Updated feature data with project data as a list of dictionaries.
    """

    consolidated_issues_per_repository = []

    # For each feature, add feature data from project
    for repository_issue in repository_issues:
        repository_issue_key = repository_issue.make_string_key()

        consolidate_issue = ConsolidatedIssue(repository_issue)

        # Check if key for feature exists also in the project_data_dict
        if repository_issue_key in project_issues:
            project_issue = project_issues[repository_issue_key]
            consolidate_issue.update_with_project_data(project_issue, project_title)
        else:
            consolidate_issue.error = "Not found in project, but expected."

        consolidated_issues_per_repository.append(consolidate_issue)

    return consolidated_issues_per_repository


# TODO: list vs List from typing
def consolidate_issues_with_project() -> Tuple[List[ConsolidatedIssue], Set[str]]:
    """
        Consolidates features that have a project attached.
        Loading project data and creating project issue dictionary with unique string key.
        Merging feature and project data with additional info.

        @return: A tuple containing a list of consolidated features with a project and a set of used repository names.
    """

    consolidated_project_issues = []
    used_repositories = set()

    if os.path.isdir(PROJECT_ISSUE_DIRECTORY):
        # Iterate over all project files
        for project_filename in os.listdir(PROJECT_ISSUE_DIRECTORY):
            # Load project data
            project_filename_path = os.path.join(PROJECT_ISSUE_DIRECTORY, project_filename)
            project_json_from_data = json.load(open(project_filename_path))
            project_title = project_json_from_data["title"]

            project_issues = {}
            for project_json_issue in project_json_from_data["issues"]:
                project_issue = ProjectIssue()
                project_issue.load_from_output(project_json_issue)

                string_key = project_issue.make_string_key()
                project_issues[string_key] = project_issue

            for repository_name in project_json_from_data["config_repositories"]:
                print(f"Processing project with repository: {repository_name}...")

                repository_issues = []

                repository_issues_output = load_repository_issue_from_data(REPOSITORY_ISSUE_DIRECTORY, repository_name)

                for repository_issue_output in repository_issues_output:
                    repository_issue = RepositoryIssue()
                    repository_issue.load_from_data(repository_issue_output)
                    repository_issues.append(repository_issue)

                # Merge feature with additional project data
                consolidated_issues_per_repository = consolidate_project_issues(repository_issues,
                                                                                project_issues, project_title)
                consolidated_project_issues.extend(consolidated_issues_per_repository)

                # Add the repository name to the set of used repositories
                used_repositories.add(repository_name)

    return consolidated_project_issues, used_repositories


def consolidate_issues_without_project(repositories: List[Repository],
                                       set_of_used_repos: Set[str],
                                       project_state_mining_switch: bool) -> List[ConsolidatedIssue]:
    """
        Consolidates features that do not have a project attached.
        Updating feature structure with info of not having project attached.

        @param repositories: The list of repositories to fetch features from.
        @param set_of_used_repos: The set of repository names that have been already used and are attached to a project.
        @param project_state_mining_switch: The switch to enable or disable project state mining.

        @return: A list of consolidated features without a project.
    """
    # List to store the issues data without project
    consolidated_issues_without_project = []

    for repository in repositories:
        if repository.repository_name not in set_of_used_repos:
            print(f"Processing repository without project: {repository.repository_name}...")
            repository_issues_from_data = load_repository_issue_from_data(REPOSITORY_ISSUE_DIRECTORY, repository.repository_name)

            # Add additional info also to features without project
            for repository_issue_from_data in repository_issues_from_data:
                repository_issue = RepositoryIssue()
                repository_issue.load_from_data(repository_issue_from_data)

                consolidate_issue = ConsolidatedIssue(repository_issue)

                if not project_state_mining_switch:
                    consolidate_issue.no_project_mining()

                consolidated_issues_without_project.append(consolidate_issue)

    return consolidated_issues_without_project


def main() -> None:
    # TODO: There are issues, that should be connected to the project, but are archived. We don't know how to solve this
    # TODO: issue since, we cant get the issue archived information. Find a way, how to solve this.
    project_state_mining = os.getenv('PROJECT_STATE_MINING')
    project_state_mining = project_state_mining.lower() == 'true'

    # TODO: Make an util method for parsing JSON from env to remove duplicity code
    # TODO: Delete all code not been used
    # Parse repositories JSON string
    repositories_env = os.getenv('REPOSITORIES')

    try:
        repositories_json = json.loads(repositories_env)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    # Get the current directory and check that output dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(CONSOLIDATED_ISSUE_DIRECTORY, current_dir)

    print("Starting the consolidation process.")

    repositories = []

    # Process every repo from repos input
    # TODO: through the scripts I have to create a repository objects three times. I should refactor it.
    for repository_json in repositories_json:
        repository = Repository()
        repository.load_from_api_json(repository_json)
        repositories.append(repository)

    # Consolidate issues that have project attached
    consolidated_issues_with_project, used_repositories = consolidate_issues_with_project()

    # Consolidate issues without a project
    consolidated_issues_without_project = consolidate_issues_without_project(repositories,
                                                                             used_repositories,
                                                                             project_state_mining)

    # Combine all consolidated issues
    consolidated_issues = consolidated_issues_with_project + consolidated_issues_without_project

    issues_to_save = [issue.to_dict() for issue in consolidated_issues]

    # Save consolidated issues into JSON file
    output_file_name = save_to_json_file(issues_to_save, "consolidation", CONSOLIDATED_ISSUE_DIRECTORY, "issue")
    print(f"Consolidated {len(consolidated_issues)} issues in total in {output_file_name}.")


if __name__ == '__main__':
    main()
