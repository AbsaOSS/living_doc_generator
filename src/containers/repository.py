from typing import List
import requests
from .gh_project import GHProject
from .base_container import BaseContainer

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
