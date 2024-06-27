from typing import List, Set, Optional
import requests
import json
import os

from .gh_project import GHProject
from .base_container import BaseContainer
from .repository_issue import RepositoryIssue
from .project import Project
from .consolidated_issue import ConsolidatedIssue

ISSUE_PER_PAGE = 100
REPOSITORY_ISSUE_DIRECTORY = "../data/fetched_data/issue_data"
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


class Repository(BaseContainer):
    def __init__(self):
        self.organization_name: str = ""
        self.repository_name: str = ""
        self.query_labels: List[Optional[str]] = [None]

    def load_from_json(self, repository):
        for key in ["orgName", "repoName", "queryLabels"]:
            if key not in repository:
                raise ValueError(f"Repository key '{key}' is missing in the input dictionary.")

        if not isinstance(repository["orgName"], str) or not isinstance(repository["repoName"], str):
            raise ValueError("Repository value of 'orgName' and 'repoName' should be of type string.")

        if not isinstance(repository["queryLabels"], list) or not all(isinstance(i, str) for i in repository["queryLabels"]):
            raise ValueError("Repository value of 'queryLabels' should be a list of strings.")

        self.organization_name = repository["orgName"]
        self.repository_name = repository["repoName"]
        self.query_labels = repository["queryLabels"]

    def get_gh_projects(self, session: requests.sessions.Session) -> List[GHProject]:
        """
        Fetches all projects from a repository using GraphQL query.
        If the response is empty, it returns an empty list.

        @param session: A configured request session.

        @return: The list of fetched project objects attached to the repository.
        """

        # Fetch the GraphQL response with projects attached to the repository
        projects_from_repo_query = PROJECTS_FROM_REPO_QUERY.format(org_name=self.organization_name,
                                                                   repo_name=self.repository_name)
        project_response_raw = self.send_graphql_query(projects_from_repo_query, session)

        # Return empty list, if repository has no project attached
        if len(project_response_raw) == 0:
            return []

        if project_response_raw['repository'] is not None:
            project_response = project_response_raw['repository']['projectsV2']['nodes']
            gh_projects = [GHProject(id=project['id'], number=project['number'], title=project['title'])
                           for project in project_response]
        else:
            print(f"Warning: 'repository' key is None in response: {project_response_raw}")
            gh_projects = []

        return gh_projects

    def get_issues(self, session: requests.sessions.Session) -> List[RepositoryIssue]:
        loaded_issues = []
        issue_numbers = set()

        # Check if repository query_labels is empty, if so, set it to None to fetch all issues
        labels_to_query = self.query_labels if self.query_labels else [None]

        # Fetch issues for all repository query_labels
        for label_name in labels_to_query:
            # Base endpoint for fetching label_name or all issues if [] is passed
            base_endpoint = self.get_base_endpoint(label_name)
            page = 1

            try:
                while True:
                    # Update the endpoint with active pagination
                    endpoint = f"{base_endpoint}&page={page}"

                    # Retrieve the GitHub response
                    gh_response = session.get(endpoint)
                    # Check if the request was successful
                    gh_response.raise_for_status()

                    # TODO create small method like filter_issues_by_numbers ==> return instead of []
                    repository_issues = []

                    # Convert json issue to RepositoryIssue object
                    issues_json = gh_response.json()['items']
                    for issue_json in issues_json:
                        repository_issue = RepositoryIssue()
                        repository_issue.load_from_json(issue_json, self)

                        if label_name is not None:
                            # Filter out the RepositoryIssues which have label_name only in issue description
                            repository_issue.filter_out_labels_in_description(label_name, repository_issues)
                        else:
                            repository_issues.append(repository_issue)

                        if repository_issue.number not in issue_numbers:
                            loaded_issues.append(repository_issue)
                            issue_numbers.add(repository_issue.number)

                    # Logging the number of loaded issues
                    # TODO: Logic for printing will be removed, due to logging refactoring later
                    if label_name is None:
                        print(f"Loaded {len(repository_issues)} issues.")
                    else:
                        print(f"Loaded {len(repository_issues)} issues for label `{label_name}`.")

                    # If we retrieved less than issue_per_page constant, it means we're on the last page
                    if len(issues_json) < ISSUE_PER_PAGE:
                        break
                    page += 1

            # Specific error handling for HTTP errors
            except requests.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")

            except Exception as e:
                print(f"An error occurred: {e}")
                break

        return loaded_issues

    def get_base_endpoint(self, label_name: str) -> str:
        """
        Prepares the base endpoint for fetching issues from a GitHub repository.
        If the label name is not specified, the base endpoint is for fetching all issues.

        @param label_name: The name of the label.

        @return: The base endpoint for fetching issues.
        """
        if label_name is None:
            search_query = f"repo:{self.organization_name}/{self.repository_name} is:issue"
        else:
            search_query = f"repo:{self.organization_name}/{self.repository_name} is:issue label:{label_name}"

        base_endpoint = f"https://api.github.com/search/issues?q={search_query}&per_page={ISSUE_PER_PAGE}"

        return base_endpoint

    def get_unique_projects(self, session: requests.sessions.Session, projects_title_filter: str, projects: dict):
        """
        Generate a main structure for every unique project.
        Connects project with the repositories.

        @param projects: The dictionary to store project objects.
        @param projects_title_filter: The list of project titles to filter.
        @param session: A configured request session.

        @return: The unique project structure as a dictionary.
        """

        # Fetch all projects, that are attached to the repo
        gh_projects = self.get_gh_projects(session)

        # Update unique_projects with main project structure for every project
        for gh_project in gh_projects:
            subscriptable_project = gh_project.to_dict()
            project_id = subscriptable_project["id"]
            project_title = subscriptable_project["title"]

            is_project_required = (projects_title_filter == '[]') or (project_title in projects_title_filter)

            if is_project_required:
                if project_id not in projects:
                    project = Project()
                    project.load_from_api_json(self, subscriptable_project)
                    project.update_field_options(self, session)

                    # Primary project structure
                    projects[project_id] = project

                else:
                    projects[project_id].config_repositories.append(self.repository_name)

    def consolidate_issues_without_project(self, set_of_used_repos: Set[str],
                                           project_state_mining_switch: bool) -> List[ConsolidatedIssue]:
        """
            Consolidates features that do not have a project attached.
            Updating feature structure with info of not having project attached.

            @param set_of_used_repos: The set of repository names that have been already used and are attached to a project.
            @param project_state_mining_switch: The switch to enable or disable project state mining.

            @return: A list of consolidated features without a project.
        """
        # List to store the issues data without project
        consolidated_issues_without_project = []

        if self.repository_name not in set_of_used_repos:
            print(f"Processing repository without project: {self.repository_name}...")
            repository_issues_from_data = load_repository_issue_from_data(REPOSITORY_ISSUE_DIRECTORY, self.repository_name)

            # Add additional info also to features without project
            for repository_issue_from_data in repository_issues_from_data:
                repository_issue = RepositoryIssue()
                repository_issue.load_from_data(repository_issue_from_data)

                consolidated_issue = ConsolidatedIssue()
                consolidated_issue.fill_with_repository_issue(repository_issue)

                if not project_state_mining_switch:
                    consolidated_issue.no_project_mining()

                consolidated_issues_without_project.append(consolidated_issue)

        return consolidated_issues_without_project


# TODO: wrong import, should be in utils. ImportError: attempted relative import beyond top-level package
def load_repository_issue_from_data(directory: str, repository_name: str) -> List[dict]:
    """
        Loads feature data from a JSON file located in a specified directory.

        @param directory: The directory where the JSON file to be loaded is located.
        @param repository_name: The name of the repository for which the feature data is being loaded.

        @return: The feature data as a list of dictionaries.
    """
    # Load issue data
    # TODO: Make a context attribute for feature, so the method is more generic
    issue_filename = f"{repository_name}.feature.json"
    issue_filename_path = os.path.join(directory, issue_filename).replace("-", "_").lower()
    issue_json_from_data = json.load(open(issue_filename_path))

    return issue_json_from_data
