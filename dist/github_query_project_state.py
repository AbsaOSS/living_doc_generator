"""GitHub Query Project State

This script is used to fetch and process project state data from GitHub.
It queries GitHub's GraphQL API to get the data, and then processes and generate
project output JSON file/s.

The script can be run from the command line with optional arguments:
    * python3 github_query_project_state.py
    * python3 github_query_project_state.py -c config.json
"""

import requests
import json
import os
from typing import Dict, List
from utils import parse_arguments, ensure_folder_exists, save_state_to_json_file

OUTPUT_DIRECTORY = "../data/fetched_data/project_data"
ISSUES_FROM_PROJECT_QUERY = """
    query {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          items(first: {issues_per_page}, {after_argument}) {{
            pageInfo {{
              endCursor
              hasNextPage
            }}
            nodes {{
              content {{
                  ... on Issue {{
                    title
                    state
                    number
                    repository {{
                      name
                      owner {{
                        login
                      }}
                    }}
                  }}
                }}
              fieldValues(first: 100) {{
                nodes {{
                  __typename
                  ... on ProjectV2ItemFieldSingleSelectValue {{
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    """


def send_graphql_query(query: str, headers: Dict[str, str]) -> Dict[str, dict]:
    """
        Sends a GraphQL query to the GitHub API and returns the response.
        If an HTTP error occurs, it prints the error and returns an empty dictionary.

        @param query: The GraphQL query to be sent in f string format.
        @param headers: The headers to be included in the request.

        @return: The response from the GitHub GraphQL API as a dictionary.
    """
    try:
        # Fetch the response
        response = session.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # Check if the request was successful
        response.raise_for_status()

        return response.json()["data"]

    # Specific error handling for HTTP errors
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return {}


def get_projects_from_repo(org_name: str, repo_name: str, headers: Dict[str, str]) -> List[dict]:
    """
        Fetches all projects from a given GitHub repository using GraphQL query.
        If the response is empty, it returns an empty list.

        @param org_name: The organization / owner name.
        @param repo_name: The repository name for getting attached projects.
        @param headers: The headers to be included in the request.

        @return: The list of all projects attached to the repository.
    """
    query = f"""
        query {{
          repository(owner: "{org_name}", name: "{repo_name}") {{
            projectsV2(first: 100) {{
              nodes {{
                id
                number
                title
              }}
            }}
          }}
        }}
        """

    # Fetch the response from the server
    response = send_graphql_query(query, headers)

    # Check if the response is empty
    if len(response) == 0:
        return []

    if response['repository'] is not None:
        project_data = response['repository']['projectsV2']['nodes']
    else:
        print(f"Warning: 'repository' key is None in response: {response}")
        project_data = []

    return project_data


def get_project_option_fields(org_name: str, repo_name: str, project_number: str, headers: Dict[str, str]) -> List[dict]:
    """
        Fetches the option fields for a given project using a GraphQL query like size or priority.
        If the response is empty, it returns an empty list.

        @param org_name: The organization / owner name.
        @param repo_name: The repository name.
        @param project_number: The project number.
        @param headers: The headers to be included in the request.

        @return: The list of option fields for the project.
    """
    query = f"""
        query {{
          repository(owner: "{org_name}", name: "{repo_name}") {{
            projectV2(number: {project_number}) {{
              title
              fields(first: 100) {{
                nodes {{
                  ... on ProjectV2SingleSelectField {{
                    name
                    options {{
                      name
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

    # Fetch the response from the server
    response = send_graphql_query(query, headers)
    # Check if the response is empty
    if len(response) == 0:
        return []

    field_options = response['repository']['projectV2']['fields']['nodes']

    return field_options


def convert_field_options_to_dict(field_options: List[dict]) -> Dict[str, List[str]]:
    """
        Converts the raw field options output to a dictionary.
        The dictionary keys are the field names and the values are lists of options.

        @param field_options: The raw field options output.

        @return: The field options as a dictionary.
    """
    field_options_dict = {}

    # Make a dictionary with field title and its options
    for field_option in field_options:
        if "name" in field_option and "options" in field_option:
            field_name = field_option["name"]
            options = [option["name"] for option in field_option["options"]]
            # Update the dict with every field
            field_options_dict.update({field_name: options})

    return field_options_dict


def get_unique_projects(repositories: List[dict], headers: Dict[str, str]) -> Dict[str, dict]:
    """
        Generate a main structure for every unique project.
        Connects project with the repositories.

        @param repositories: The list of repositories to fetch projects from.
        @param headers: The headers to be included in the request.

        @return: The unique project structure as a dictionary.
    """
    unique_projects = {}

    # Look for projects in every config repo
    for repo in repositories:
        org_name = repo["orgName"]
        repo_name = repo["repoName"]

        # Get the projects from the repo
        projects = get_projects_from_repo(org_name, repo_name, headers)

        # Check if the project is unique
        for project in projects:
            project_id = project["id"]

            # Add info about the unique project to the dictionary
            if project_id not in unique_projects:
                project_title = project["title"]
                project_number = project["number"]

                # Get the raw version of field options for project
                field_options_raw = get_project_option_fields(org_name, repo_name, project_number, headers)

                # Convert the raw field options output to a dictionary
                sanitized_field_options_dict = convert_field_options_to_dict(field_options_raw)

                # Structure of one project
                unique_projects[project_id] = {
                    "ID": project_id,
                    "Number": project_number,
                    "Title": project_title,
                    "Owner": org_name,
                    "RepositoriesFromConfig": [repo_name],
                    "ProjectRepositories": [],
                    "Issues": [],
                    "FieldOptions": sanitized_field_options_dict
                }
            else:
                # If the project does exist, update the attached repositories list
                unique_projects[project_id]["RepositoriesFromConfig"].append(repo_name)

    return unique_projects


def get_issues_from_project(project_id: str, headers: Dict[str, str], issues_per_page: int = 100) -> List[Dict[str, dict]]:
    """
        Fetches all issues from a given project using a GraphQL query.
        The issues are fetched page by page, with set 100 issues per page.

        @param project_id: The project ID to fetch issues from.
        @param headers: The headers to be included in the request.
        @param issues_per_page: The maximum number of issues to fetch per page.

        @return: The list of all issues in the project.
    """
    all_project_issues = []
    cursor = None

    while True:
        # Add the after argument to the query if a cursor is provided
        after_argument = f'after: "{cursor}"' if cursor else ''

        query = ISSUES_FROM_PROJECT_QUERY.format(project_id=project_id, issues_per_page=issues_per_page, after_argument=after_argument)

        # Fetch the response from the server
        response = send_graphql_query(query, headers)

        # Check if the response is empty
        if len(response) == 0:
            return []

        response_structure = response['node']['items']
        issue_data = response_structure['nodes']
        page_info = response_structure['pageInfo']

        all_project_issues.extend(issue_data)
        print(f"Loaded `{len(issue_data)}` issues.")

        if not page_info['hasNextPage']:
            break
        cursor = page_info['endCursor']

    return all_project_issues


def process_projects(unique_projects: Dict[str, dict], headers: Dict[str, str]) -> Dict[str, dict]:
    """
        Processes the projects and updates their state with the fetched issues.
        The state of each project includes the issues and the attached repositories.

        @param unique_projects: The unique projects to process.
        @param headers: The headers to be included in the request.

        @return: The state of all projects as a `project_title: project_state` dictionary.
    """
    project_states = {}

    # For unique project update it's state with adequate issues
    for project_id, project_state in unique_projects.items():
        project_title = project_state["Title"]
        # Setting attached repositories to a project
        attached_repos = []

        print(f"Loaded project: `{project_title}`")
        print(f"Processing issues...")

        # Get issues from project
        project_issue_data = get_issues_from_project(project_id, headers)

        # Process the issues and add them to the project state
        for issue in project_issue_data:
            if 'content' in issue and issue['content'] is not None:
                content = issue['content']
                title = content.get('title', 'N/A')
                number = content.get('number', 'N/A')
                state = content.get('state', 'N/A')
                repo_name = content['repository'].get('name', 'N/A') if 'repository' in content else 'N/A'
                owner = content['repository']['owner'].get('login', 'N/A') if 'repository' in content else 'N/A'
                issue_field_types = []

                # Get the field types for the issue
                for node in issue['fieldValues']['nodes']:
                    if node['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                        issue_field_types.append(node['name'])

                # Initialize a dictionary for the issue
                project_issue_dict = {
                    "Number": number,
                    "Owner": owner,
                    "RepositoryName": repo_name,
                    "Title": title,
                    "State": state
                }

                issue_repo_name = project_issue_dict["RepositoryName"]

                # Updating the ProjectRepositories
                if issue_repo_name != "N/A":
                    if issue_repo_name not in attached_repos:
                        project_state['ProjectRepositories'].append(issue_repo_name)
                        attached_repos.append(issue_repo_name)

                # Prepare the field options structure for usage
                field_options = unique_projects[project_id]["FieldOptions"]

                # Add the field types to the issue dictionary
                for field_type in issue_field_types:
                    # Look if issue field is in the field options
                    for name, options in field_options.items():
                        if field_type in options:
                            project_issue_dict.update({name: field_type})

                # Add the issue to the project state
                project_state['Issues'].append(project_issue_dict)
            else:
                print(f"Warning: 'content' key missing or None in issue: {issue}")

        print(f"Processed {len(project_state['Issues'])} project issues in total.")

        # Add the project state to the dictionary
        project_states.update({project_title: project_state})

    return project_states


if __name__ == "__main__":
    # Get environment variables set by the controller script
    user_token = os.getenv('GITHUB_TOKEN')
    project_state_mining = os.getenv('PROJECT_STATE_MINING')
    # projects_title_filter = os.getenv('PROJECTS_TITLE_FILTER')
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
    # print(f"PROJECTS_TITLE_FILTER: {projects_title_filter}")
    print(f"REPOSITORIES: {repositories}")

    # Get the current directory and ensure the output directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ensure_folder_exists(OUTPUT_DIRECTORY, current_dir)

    # Check the condition and exit the script if necessary
    if not project_state_mining:
        print("Project data mining is not allowed. The process will not start.")
        exit()

    print("Project data mining allowed, starting the process.")

    # Set the variable for running the script
    headers = {
        "Authorization": f"Bearer {user_token}",
        "User-Agent": "IssueFetcher/1.0"
    }

    # Start a session for the queries
    session = requests.Session()

    # Get unique projects
    unique_projects = get_unique_projects(repositories, headers)

    # Final process for each unique project
    project_states = process_projects(unique_projects, headers)

    # Save project state to the unique JSON file
    for project_title, project_state in project_states.items():
        # Save the project state to a file
        output_file_name = save_state_to_json_file(project_state, "project", OUTPUT_DIRECTORY, project_title)
        print(f"Project's '{project_title}' Issue state saved into file: {output_file_name}.")
