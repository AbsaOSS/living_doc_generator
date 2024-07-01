from typing import List, Dict
import requests

from .project_issue import ProjectIssue
from .base_container import BaseContainer
from .gh_project import GHProject

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
PROJECT_FIELD_OPTIONS_QUERY = """
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


class Project(BaseContainer):
    def __init__(self):
        self.id: str = ""
        self.number: int = 0
        self.title: str = ""
        self.organization_name: str = ""
        self.config_repositories: List[str] = []
        self.project_repositories: List[str] = []
        self.issues: List[ProjectIssue] = []
        self.field_options: Dict[str, List[str]] = {}

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'title': self.title,
            'organization_name': self.organization_name,
            'config_repositories': self.config_repositories,
            'project_repositories': self.project_repositories,
            'issues': self.issues,
            'field_options': self.field_options
        }

    def load_from_gh_project(self, repository, gh_project: GHProject):
        for key in ["id", "title", "number"]:
            if key not in gh_project:
                raise ValueError(f"Project key '{key}' is missing in the input dictionary.")

        if not isinstance(gh_project["id"], str) or not isinstance(gh_project["title"], str):
            raise ValueError("Project value of 'id' and 'title' should be of type string.")

        if not isinstance(gh_project["number"], int):
            raise ValueError("Project value of 'number' should be of type integer.")

        self.id = gh_project.id
        self.title = gh_project.title
        self.number = gh_project.number
        self.organization_name = repository.owner
        self.config_repositories.append(repository.name)

    def update_field_options(self, repository, session: requests.sessions.Session):
        project_field_options_query = PROJECT_FIELD_OPTIONS_QUERY.format(org_name=repository.owner,
                                                                         repo_name=repository.name,
                                                                         project_number=self.number)
        field_option_response = self.send_graphql_query(project_field_options_query, session)

        # Return empty list, if project has no issues attached
        if len(field_option_response) == 0:
            exit()

        field_options_nodes = field_option_response['repository']['projectV2']['fields']['nodes']
        for field_option in field_options_nodes:
            if "name" in field_option and "options" in field_option:
                field_name = field_option["name"]
                options = [option["name"] for option in field_option["options"]]

                # Update the dict with every unique field
                self.field_options.update({field_name: options})

    def get_gh_issues(self, session: requests.sessions.Session) -> List[dict]:
        """
        Fetches all issues from a given project using a GraphQL query.
        The issues are fetched supported by pagination.

        @param session: A configured request session.

        @return: The list of all issues in the project.
        """
        gh_project_issues = []
        cursor = None

        while True:
            # Add the after argument to the query if a cursor is provided
            after_argument = f'after: "{cursor}"' if cursor else ''

            # Fetch the GraphQL response with all issues attached to specific project
            issues_from_project_query = ISSUES_FROM_PROJECT_QUERY.format(project_id=self.id,
                                                                         issues_per_page=ISSUE_PER_PAGE,
                                                                         after_argument=after_argument)
            project_issues_response = self.send_graphql_query(issues_from_project_query, session)

            # Return empty list, if project has no issues attached
            if len(project_issues_response) == 0:
                return []

            general_response_structure = project_issues_response['node']['items']
            issue_data = general_response_structure['nodes']
            page_info = general_response_structure['pageInfo']

            # Extend project issues list per every page during pagination
            gh_project_issues.extend(issue_data)
            print(f"Loaded `{len(issue_data)}` issues.")

            # Check for closing the pagination process
            if not page_info['hasNextPage']:
                break
            cursor = page_info['endCursor']

        return gh_project_issues

    def update_attached_repositories(self, repository_name, attached_repositories):
        if repository_name:
            if repository_name not in attached_repositories:
                self.project_repositories.append(repository_name)
                attached_repositories.append(repository_name)

    # TODO: I have to mine also archived issues. Find out how.
    def update_with_issue_data(self, session: requests.sessions.Session):
        """
        Processes the projects and updates their state with the fetched issues.
        The state of each project includes the issues and the attached repositories.

        @param session: A configured request session.

        @return: The state of all projects as a `project_title: project_state` dictionary.
        """

        attached_repositories = []

        print(f"Loaded project: `{self.title}`")
        print(f"Processing issues...")

        # Get issues for project
        gh_project_issues = self.get_gh_issues(session)

        # Process the issue data and update project state
        for gh_issue in gh_project_issues:
            if ('content' in gh_issue and gh_issue['content'] is not None
                    and gh_issue['content'] != {}):
                project_issue = ProjectIssue()
                project_issue.load_from_api_json(gh_issue, self.field_options)

                # Update project with attached repositories
                repository_name = project_issue.repository_name
                self.update_attached_repositories(repository_name, attached_repositories)

                # Append the issue to the project
                # TODO: Check if this is the right way to append the issue to the project, to_dict and back to json
                subscriptable_project_issue = project_issue.to_dict()
                self.issues.append(subscriptable_project_issue)

            else:
                print(f"Warning: 'content' key missing or None in {self.title}'s issue: {gh_issue}")

        print(f"Processed {len(self.issues)} project issues in total for `{self.title}`.")
