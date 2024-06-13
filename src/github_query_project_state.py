"""
GitHub Query Project State

This script is used to fetch and process project state data from GitHub.
It queries GitHub's GraphQL API to get the data, and then processes and generate
project output JSON file/s.
"""

import requests
import json
import os
from typing import Dict, List

from utils import (ensure_folder_exists,
                   save_to_json_file,
                   initialize_request_session)

from containers.project import Project
from containers.project_issue import ProjectIssue
from containers.repository import Repository

OUTPUT_DIRECTORY = "../data/fetched_data/project_data"


def get_unique_projects(repositories: List[Repository], session: requests.sessions.Session) -> Dict[str, Project]:
    """
    Generate a main structure for every unique project.
    Connects project with the repositories.

    @param repositories: The list of repositories to fetch projects from.
    @param session: A configured request session.

    @return: The unique project structure as a dictionary.
    """
    projects = {}

    for repository in repositories:
        # Fetch projects, that are attached to the repo
        gh_projects = repository.get_projects(session)

        # Update unique_projects with main project structure for every project
        for gh_project in gh_projects:
            subscriptable_project = gh_project.to_dict()
            project_id = subscriptable_project["id"]

            if project_id not in projects:
                project = Project()
                organization_name = repository.organization_name
                project.load_from_json(subscriptable_project, organization_name)
                project.update_field_options(session, repository)

                # Primary project structure
                projects[project_id] = project

    return projects


def process_projects(projects: Dict[str, Project], session: requests.sessions.Session) -> Dict[str, Project]:
    """
    Processes the projects and updates their state with the fetched issues.
    The state of each project includes the issues and the attached repositories.

    @param projects: The unique project structures to process.
    @param session: A configured request session.

    @return: The state of all projects as a `project_title: project_state` dictionary.
    """
    project_states = {}

    # Update every project with adequate issue data
    for project_id, project in projects.items():
        attached_repositories = []

        print(f"Loaded project: `{project.title}`")
        print(f"Processing issues...")

        # Get issues for project
        gh_project_issues = project.get_gh_issues(session)

        # Process the issue data and update project state
        for gh_issue in gh_project_issues:
            if 'content' in gh_issue and gh_issue['content'] is not None:
                project_issue = ProjectIssue()
                project_issue.load_from_json(gh_issue)

                # Update project with attached repositories
                repository_name = project_issue.repository_name
                project.update_attached_repositories(repository_name, attached_repositories)

                # Append the issue to the project
                subscriptable_project_issue = project_issue.to_dict()
                project.issues.append(subscriptable_project_issue)

            else:
                print(f"Warning: 'content' key missing or None in issue: {gh_issue}")

        print(f"Processed {len(project.issues)} project issues in total.")

        # Add the project state to the dictionary
        project_states.update({project.title: project})

    return project_states


def main() -> None:
    print("Script for downloading project data from GitHub GraphQL started.")

    # Get environment variables from the controller script
    github_token = os.getenv('GITHUB_TOKEN')
    repositories = os.getenv('REPOSITORIES')
    project_state_mining = os.getenv('PROJECT_STATE_MINING')
    # TODO: Implement this mentioned feature, that filter just some projects
    # projects_title_filter = os.getenv('PROJECTS_TITLE_FILTER')

    # Parse the boolean values
    project_state_mining = project_state_mining.lower() == 'true'
    # projects_title_filter = projects_title_filter.lower() == 'true'

    # Parse repositories JSON string
    try:
        repositories_json = json.loads(repositories)
    except json.JSONDecodeError as e:
        print(f"Error parsing REPOSITORIES: {e}")
        exit(1)

    # Get the current directory and check that output dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Check if project mining is allowed and exit the script if necessary
    if not project_state_mining:
        print("Project data mining is not allowed. The process will not start.")
        exit()

    print("Project data mining allowed, starting the process.")

    # Initialize the request session
    session = initialize_request_session(github_token)

    repositories = []

    # Process every repo from repos input
    for repository_json in repositories_json:
        repository = Repository()
        repository.load_from_json(repository_json)
        repositories.append(repository)

    # Get dict of project objects with primary structure
    projects = get_unique_projects(repositories, session)

    # Process unique projects with updating their state with attached issues' info
    project_states = process_projects(projects, session)

    # Save project states to the unique JSON files
    for project_title, project_state in project_states.items():
        project_state_to_save = project_state.to_dict()
        output_file_name = save_to_json_file(project_state_to_save, "project", OUTPUT_DIRECTORY, project_title)
        print(f"Project's '{project_title}' Issue state saved into file: {output_file_name}.")

    print("Script for downloading project data from GitHub GraphQL ended.")


if __name__ == "__main__":
    main()

