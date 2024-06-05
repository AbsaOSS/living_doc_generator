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
from utils import ensure_folder_exists, save_state_to_json_file, initialize_request_session
from containers import Repository, ProjectIssue, Project

OUTPUT_DIRECTORY = "../data/fetched_data/project_data"
ISSUE_PER_PAGE = 100
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
PROJECTS_FROM_REPO_QUERY = """
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
PROJECT_OPTION_FIELDS_QUERY = """
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


def send_graphql_query(query: str, session: requests.sessions.Session) -> Dict[str, dict]:
    """
    Sends a GraphQL query to the GitHub API and returns the response.
    If an HTTP error occurs, it prints the error and returns an empty dictionary.

    @param query: The GraphQL query to be sent in f string format.
    @param session: A configured request session.

    @return: The response from the GitHub GraphQL API in a dictionary format.
    """
    try:
        # Fetch the response from the API
        response = session.post('https://api.github.com/graphql', json={'query': query})
        # Check if the request was successful
        response.raise_for_status()

        return response.json()["data"]

    # Specific error handling for HTTP errors
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return {}


def get_projects_from_repo(org_name: str, repo_name: str, session: requests.sessions.Session) -> List[dict]:
    """
    Fetches all projects from a given GitHub repository using GraphQL query.
    If the response is empty, it returns an empty list.

    @param org_name: The organization / owner name.
    @param repo_name: The repository name for getting attached projects.
    @param session: A configured request session.

    @return: The list of all projects attached to the repository.
    """

    # Fetch the GraphQL response with projects attached to the repository
    projects_from_repo_query = PROJECTS_FROM_REPO_QUERY.format(org_name=org_name, repo_name=repo_name)
    project_response = send_graphql_query(projects_from_repo_query, session)

    # Return empty list, if repo has no project attached
    if len(project_response) == 0:
        return []

    if project_response['repository'] is not None:
        projects = project_response['repository']['projectsV2']['nodes']
    else:
        print(f"Warning: 'repository' key is None in response: {project_response}")
        projects = []

    return projects


def get_project_option_fields(org_name: str, repo_name: str, project_number: str, session: requests.sessions.Session) -> List[dict]:
    """
    Fetches the option fields for a given project using a GraphQL query like size or priority.
    If the response is empty, it returns an empty list.

    @param org_name: The organization / owner name.
    @param repo_name: The repository name.
    @param project_number: The project number.
    @param session: A configured request session.

    @return: The raw list output of option fields for the project.
    """
    # Fetch the GraphQL response with option fields used in a project
    project_option_fields_query = PROJECT_OPTION_FIELDS_QUERY.format(org_name=org_name, repo_name=repo_name, project_number=project_number)
    option_field_response = send_graphql_query(project_option_fields_query, session)

    # Return empty list, if project does not use option fields
    if len(option_field_response) == 0:
        return []

    raw_field_options = option_field_response['repository']['projectV2']['fields']['nodes']

    return raw_field_options


def sanitize_field_options(raw_field_options: List[dict]) -> Dict[str, List[str]]:
    """
    Converts the raw field options output to a formated dictionary.
    The dictionary keys are the field names and the values are lists of options.

    @param raw_field_options: The raw field options output.

    @return: The field options for a project as a dictionary.
    """
    field_options = {}

    # Make a sanitized dict with field names and its options
    for field_option in raw_field_options:
        if "name" in field_option and "options" in field_option:
            field_name = field_option["name"]
            options = [option["name"] for option in field_option["options"]]

            # Update the dict with every unique field
            field_options.update({field_name: options})

    return field_options


def get_unique_projects(repositories: List[Repository], session: requests.sessions.Session) -> Dict[str, dict]:
    """
    Generate a main structure for every unique project.
    Connects project with the repositories.

    @param repositories: The list of repositories to fetch projects from.
    @param session: A configured request session.

    @return: The unique project structure as a dictionary.
    """
    unique_projects = {}

    # Process every repo from repos input
    for repository in repositories:
        repo = Repository(orgName=repository["orgName"],
                          repoName=repository["repoName"],
                          queryLabels=repository["queryLabels"])

        # Fetch projects, that are attached to the repo
        projects = get_projects_from_repo(repo.orgName, repo.repoName, session)

        # Update unique_projects with main project structure for every project
        for project in projects:
            project_id = project["id"]

            # Ensure project is unique and add its structure to unique projects
            if project_id not in unique_projects:
                project_title = project["title"]
                project_number = project["number"]

                # Get the raw output for field project options
                raw_field_options = get_project_option_fields(repo.orgName, repo.repoName, project_number, session)

                # Convert the raw field options output to a sanitized dict version
                sanitized_field_options = sanitize_field_options(raw_field_options)

                # Primary project structure
                unique_projects[project_id] = Project(
                    ID=project_id,
                    Number=project_number,
                    Title=project_title,
                    Owner=repo.orgName,
                    RepositoriesFromConfig=[repo.repoName],
                    FieldOptions=sanitized_field_options
                )
            else:
                # If the project already exists, update the `RepositoriesFromConfig` list
                unique_projects[project_id]["RepositoriesFromConfig"].append(repo.orgName)

    return unique_projects


def get_issues_from_project(project_id: str, session: requests.sessions.Session) -> List[Dict[str, dict]]:
    """
    Fetches all issues from a given project using a GraphQL query.
    The issues are fetched supported by pagination.

    @param project_id: The project ID to fetch issues from.
    @param session: A configured request session.

    @return: The list of all issues in the project.
    """
    project_issues = []
    cursor = None

    while True:
        # Add the after argument to the query if a cursor is provided
        after_argument = f'after: "{cursor}"' if cursor else ''

        # Fetch the GraphQL response with all issues attached to specific project
        issues_from_project_query = ISSUES_FROM_PROJECT_QUERY.format(project_id=project_id, issues_per_page=ISSUE_PER_PAGE, after_argument=after_argument)
        project_issues_response = send_graphql_query(issues_from_project_query, session)

        # Return empty list, if project has no issues attached
        if len(project_issues_response) == 0:
            return []

        general_response_structure = project_issues_response['node']['items']
        issue_data = general_response_structure['nodes']
        page_info = general_response_structure['pageInfo']

        # Extend project issues list per every page during pagination
        project_issues.extend(issue_data)
        print(f"Loaded `{len(issue_data)}` issues.")

        # Check for closing the pagination process
        if not page_info['hasNextPage']:
            break
        cursor = page_info['endCursor']

    return project_issues


def process_projects(unique_projects: Dict[str, dict], session: requests.sessions.Session) -> Dict[str, dict]:
    """
    Processes the projects and updates their state with the fetched issues.
    The state of each project includes the issues and the attached repositories.

    @param unique_projects: The unique project structures to process.
    @param session: A configured request session.

    @return: The state of all projects as a `project_title: project_state` dictionary.
    """
    project_states = {}

    # Update every project with adequate issue data
    for project_id, project_state in unique_projects.items():
        attached_repos = []
        project_title = project_state.Title

        print(f"Loaded project: `{project_title}`")
        print(f"Processing issues...")

        # Get issues for project
        project_issue_data = get_issues_from_project(project_id, session)

        # Process the issue data and update project state
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
                project_issue = ProjectIssue(
                    Number=number,
                    Owner=owner,
                    RepositoryName=repo_name,
                    Title=title,
                    State=state
                )

                issue_repo_name = project_issue.RepositoryName

                # Updating the ProjectRepositories
                if issue_repo_name != "N/A":
                    if issue_repo_name not in attached_repos:
                        project_state.ProjectRepositories.append(issue_repo_name)
                        attached_repos.append(issue_repo_name)

                # Prepare the field options structure for usage
                field_options = unique_projects[project_id].FieldOptions

                # Add the field types to the issue dictionary
                for field_type in issue_field_types:
                    # Look if issue field is in the field options
                    for name, options in field_options.items():
                        if field_type in options:
                            setattr(project_issue, name, field_type)

                project_issue = project_issue.to_dict()

                # Add the issue to the project state
                project_state.Issues.append(project_issue)

            else:
                print(f"Warning: 'content' key missing or None in issue: {issue}")

        print(f"Processed {len(project_state.Issues)} project issues in total.")

        # Add the project state to the dictionary
        project_states.update({project_title: project_state})

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
        repositories = json.loads(repositories)
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

    # Get unique projects with primary structure
    unique_projects = get_unique_projects(repositories, session)

    # Process unique projects with updating their state with attached issues' info
    project_states = process_projects(unique_projects, session)

    # Save project states to the unique JSON files
    for project_title, project_state in project_states.items():
        project_state = project_state.to_dict()
        output_file_name = save_state_to_json_file(project_state, "project", OUTPUT_DIRECTORY, project_title)
        print(f"Project's '{project_title}' Issue state saved into file: {output_file_name}.")

    print("Script for downloading project data from GitHub GraphQL ended.")


if __name__ == "__main__":
    main()

