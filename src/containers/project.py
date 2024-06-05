from typing import List, Dict

from .project_issue import ProjectIssue


class Project:
    def __init__(self):
        self.id: str = ""
        self.number: int = 0
        self.title: str = ""
        self.organizationName: str = ""
        self.repositoriesFromConfig: List[str] = []
        self.projectRepositories: List[str] = []
        self.issues: List[ProjectIssue] = []
        self.fieldOptions: Dict[str, List[str]] = {}

    def load_from_json(self, project, repo):
        self.id = project["id"]
        self.title = project["title"]
        self.number = project["number"]
        self.organizationName = repo.organization_name
        self.repositoriesFromConfig = repo.repositories



        # Get the raw output for field project options
        raw_field_options = get_project_option_fields(repo.organization_name, repo.repository_name, project_number,
                                                      session)

        # Convert the raw field options output to a sanitized dict version
        sanitized_field_options = sanitize_field_options(raw_field_options)




