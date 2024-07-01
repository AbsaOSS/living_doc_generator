"""
GitHub Query Project State

This script is used to fetch and process project state data from GitHub.
It queries GitHub's GraphQL API to get the data, and then processes and generate
project output JSON file/s.
"""

import json
import os

from containers.repository_old import Repository

from utils import (ensure_folder_exists,
                   initialize_request_session,
                   save_to_json_file)

OUTPUT_DIRECTORY = "../data/fetched_data/project_data"


def main() -> None:
    print("Script for downloading project data from GitHub GraphQL started.")

    # TODO: This part of code almost identical as in query_issues.py script
    # TODO: Make an util method for parsing repositories
    # Get environment variables from the controller script
    github_token = os.getenv('GITHUB_TOKEN')
    repositories_env = os.getenv('REPOSITORIES')
    projects_title_filter = os.getenv('PROJECTS_TITLE_FILTER')

    project_state_mining = os.getenv('PROJECT_STATE_MINING')
    project_state_mining = project_state_mining.lower() == 'true'

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

    # Check if project mining is allowed and exit the script if necessary
    if not project_state_mining:
        print("Project data mining is not allowed. The process will not start.")
        exit()

    print("Project data mining allowed, starting the process.")

    projects = {}

    # Generate main project structure for every unique project, that is attached to any input repository
    for repository_json in repositories_json:
        repository = Repository()
        repository.load_from_json(repository_json)

        # Update `projects` dictionary with key / value of project_id / project object
        repository.get_unique_projects(session, projects_title_filter, projects)

    # Update every project with project issue related data
    for project_id, project in projects.items():
        project.update_with_issue_data(session)

        # Convert object back into dictionary, so it can be serialized to JSON directly
        project_state_to_save = project.to_dict()

        # Save project state into unique JSON file
        output_file_name = save_to_json_file(project_state_to_save, "project", OUTPUT_DIRECTORY, project.title)
        print(f"Project's '{project.title}' Issue state saved into file: {output_file_name}.")

    print("Script for downloading project data from GitHub GraphQL ended.")


if __name__ == "__main__":
    main()

