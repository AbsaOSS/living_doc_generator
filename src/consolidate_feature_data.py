"""Consolidate Feature Data

This script is used to consolidate feature data with additional project data.
After merging datasets the output is one JSON file containing features with
additional project information.

The script can be run from the command line also with optional arguments:
    * python3 consolidate_feature_data.py
    * python3 consolidate_feature_data.py -c config.json
"""

import os
import json
from copy import deepcopy
from typing import List, Dict, Set, Tuple
from utils import ensure_folder_exists, save_state_to_json_file
from containers import Repository

OUTPUT_DIRECTORY = "../data/feature_consolidation"
FEATURE_DIRECTORY = "../data/fetched_data/feature_data"
PROJECT_DIRECTORY = "../data/fetched_data/project_data"


def load_feature_json_data(directory: str, repo_name: str) -> List[dict]:
    """
        Loads feature data from a JSON file located in a specified directory.

        @param directory: The directory where the JSON file to be loaded is located.
        @param repo_name: The name of the repository for which the feature data is being loaded.

        @return: The feature data as a list of dictionaries.
    """
    # Load feature data
    feature_filename = f"{repo_name}.feature.json"
    feature_filename_path = os.path.join(directory, feature_filename).replace("-", "_")
    feature_data = json.load(open(feature_filename_path))

    return feature_data


def make_unique_string_key(owner: str, repo_name: str, issue_number: str) -> str:
    """
       Creates a unique 3way string key for identifying every unique feature.

       @param owner: The owner of the repository.
       @param repo_name: The name of the repository.
       @param issue_number: The number of the issue.

       @return: The unique string key for the feature.
    """

    string_key = f"{owner}/{repo_name}/{issue_number}"

    return string_key


def merge_feature_and_project_data(feature_data: List[dict],
                                   project_data_dict: Dict[str, dict],
                                   project_title: str) -> List[dict]:
    """
        Merges feature data with additional project information.
        Every feature identified by unique string key is compared with keys of project data features.
        If the keys match, additional information from the project data is added to the feature.

        @param feature_data: The feature data to be merged.
        @param project_data_dict: The project data to be merged.
        @param project_title: The title of the project.

        @return: Updated feature data with project data as a list of dictionaries.
    """
    # Create list to store features
    modified_features = []

    # For each feature, add feature data from project
    for feature in feature_data:
        owner = feature['owner']
        repo_name = feature['repositoryName']
        feature_number = feature['number']

        # Create a key for feature with repo name and issue number
        string_key = make_unique_string_key(owner, repo_name, feature_number)

        # Create a deep copy of a feature
        modified_feature = deepcopy(feature)

        # Check if key for feature exists also in the project_data_dict
        if string_key in project_data_dict:
            for key, value in project_data_dict[string_key].items():
                if key not in modified_feature:
                    modified_feature[key] = value

        # Add project title into the feature
        modified_feature["ProjectTitle"] = project_title

        # Add the modified feature to the list
        modified_features.append(modified_feature)

    return modified_features


def consolidate_features_with_project() -> Tuple[List[dict], Set[str]]:
    """
        Consolidates features that have a project attached.
        Loading project data and creating project issue dictionary with unique string key.
        Merging feature and project data with additional info.

        @return: A tuple containing a list of consolidated features with a project and a set of used repository names.
    """
    # List to store the feature data with project
    consolidated_features_with_project = []
    # Set to store the names of repositories that have been used
    set_of_used_repos = set()

    if os.path.isdir(PROJECT_DIRECTORY):
        # Iterate over all project files
        for filename in os.listdir(PROJECT_DIRECTORY):
            # Load project data
            project_filename_path = os.path.join(PROJECT_DIRECTORY, filename)
            project_data = json.load(open(project_filename_path))
            project_title = project_data["Title"]

            # Iterate over all repositories that are part of the project
            for repo_name in project_data["RepositoriesFromConfig"]:
                print(f"Processing project with repository: {repo_name}...")

                # Initialize dictionary for project issues
                project_data_dict = {}

                # Add unique string key to every project issue
                for feature in project_data["Issues"]:
                    feature_owner = feature["Owner"]
                    feature_repo_name = feature["RepositoryName"]
                    feature_number = feature["Number"]

                    string_key = make_unique_string_key(feature_owner, feature_repo_name, feature_number)
                    project_data_dict[string_key] = feature

                # Load feature data
                feature_data = load_feature_json_data(FEATURE_DIRECTORY, repo_name)

                # Merge feature and project data with additional info
                merged_features = merge_feature_and_project_data(feature_data, project_data_dict, project_title)

                # Append the data to the list of all features with project
                consolidated_features_with_project.extend(merged_features)

                # Add the repository name to the set of used repositories
                set_of_used_repos.add(repo_name)

    return consolidated_features_with_project, set_of_used_repos


def consolidate_features_without_project(repositories: List[Repository],
                                         set_of_used_repos: Set[str],
                                         project_state_mining_switch: bool) -> List[dict]:
    """
        Consolidates features that do not have a project attached.
        Updating feature structure with info of not having project attached.

        @param repositories: The list of repositories to fetch features from.
        @param set_of_used_repos: The set of repository names that have been already used and are attached to a project.

        @return: A list of consolidated features without a project.
    """
    # List to store the feature data without project
    consolidated_features_without_project = []

    # Iterate over all repositories from config file
    for repository in repositories:
        repo = Repository(orgName=repository["orgName"],
                          repoName=repository["repoName"],
                          queryLabels=repository["queryLabels"])

        # Check if there are repositories without project
        if repo.repositoryName not in set_of_used_repos:
            print(f"Processing repository without project: {repo.repositoryName}...")
            feature_data = load_feature_json_data(FEATURE_DIRECTORY, repo.repositoryName)

            # Create a new list to store features
            modified_features = []

            # Add additional info also to features without project
            for feature in feature_data:
                # Create a deep copy of a feature
                modified_feature = deepcopy(feature)

                if not project_state_mining_switch:
                    modified_feature["ProjectTitle"] = "Not mined"
                else:
                    modified_feature["ProjectTitle"] = "No Project"

                # Add the modified feature to the list
                modified_features.append(modified_feature)

            # Append the data to the list of all features without project
            consolidated_features_without_project.extend(modified_features)

    return consolidated_features_without_project


if __name__ == '__main__':
    # Get environment variables set by the controller script
    user_token = os.getenv('GITHUB_TOKEN')
    project_state_mining = os.getenv('PROJECT_STATE_MINING')
    repositories = os.getenv('REPOSITORIES')

    # Parse the boolean values
    project_state_mining = project_state_mining.lower() == 'true'

    # Parse repositories JSON string
    try:
        repositories = json.loads(repositories)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    print("Environment variables:")
    print(f"PROJECT_STATE_MINING: {project_state_mining}")
    print(f"REPOSITORIES: {repositories}")

    print("Starting the consolidation process.")

    # Consolidate features that have project attached
    consolidated_features_with_project, set_of_used_repos = consolidate_features_with_project()

    # Consolidate features without a project
    consolidated_features_without_project = consolidate_features_without_project(repositories,
                                                                                 set_of_used_repos,
                                                                                 project_state_mining)

    # Combine all consolidated features
    consolidated_features = consolidated_features_with_project + consolidated_features_without_project

    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Make sure output folders do exist
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Save consolidated features into JSON file
    output_file_name = save_state_to_json_file(consolidated_features, "consolidation", OUTPUT_DIRECTORY, "feature")
    print(f"Consolidated {len(consolidated_features)} features in total in {output_file_name}.")
