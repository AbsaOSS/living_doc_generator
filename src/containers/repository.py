from typing import List
import requests

from .gh_project import GHProject
from .base_container import BaseContainer
from .repository_issue import RepositoryIssue

ISSUE_PER_PAGE = 100
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
        self.query_labels: List[str] = [None]

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

    def get_projects(self, session: requests.sessions.Session) -> List[GHProject]:
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
