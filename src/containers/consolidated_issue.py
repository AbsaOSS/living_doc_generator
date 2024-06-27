from typing import List, Optional, Union

from .milestone import Milestone

NO_PROJECT_ATTACHED = "---"
NO_PROJECT_MINING = "-?-"


class ConsolidatedIssue:
    def __init__(self):
        # Data from repository issue
        self.number: int = 0
        self.organization_name: str = ""
        self.repository_name: str = ""
        self.title: str = ""
        self.state: str = ""
        self.url: str = ""
        self.body: str = "Feature has no content"
        self.created_at: str = ""
        self.updated_at: str = ""
        self.closed_at: Optional[str] = None
        self.milestone: Optional[Milestone] = None
        self.labels: List[str] = []
        self.page_filename: str = ""

        # Data from project issue
        self.linked_to_project: Union[bool, str] = False
        self.project_title: Optional[str] = None
        self.status: str = NO_PROJECT_ATTACHED
        self.priority: str = NO_PROJECT_ATTACHED
        self.size: str = NO_PROJECT_ATTACHED
        self.moscow: str = NO_PROJECT_ATTACHED

        self.error: Optional[str] = None

    def fill_with_repository_issue(self, repository_issue):
        self.number = repository_issue.number
        self.organization_name = repository_issue.organization_name
        self.repository_name = repository_issue.repository_name
        self.title = repository_issue.title
        self.state = repository_issue.state
        self.url = repository_issue.url
        self.body = repository_issue.body
        self.created_at = repository_issue.created_at
        self.updated_at = repository_issue.updated_at
        self.closed_at = repository_issue.closed_at

        if repository_issue.milestone:
            self.milestone = repository_issue.milestone
        else:
            self.milestone = None

        self.labels = list(repository_issue.labels)
        self.page_filename = repository_issue.page_filename

    def update_with_project_data(self, project_issue, project_title):
        self.linked_to_project = True
        self.project_title = project_title
        self.status = project_issue.status
        self.priority = project_issue.priority
        self.size = project_issue.size
        self.moscow = project_issue.moscow

    def no_project_mining(self):
        self.linked_to_project = NO_PROJECT_MINING
        self.project_title = NO_PROJECT_MINING
        self.status = NO_PROJECT_MINING
        self.priority = NO_PROJECT_MINING
        self.size = NO_PROJECT_MINING
        self.moscow = NO_PROJECT_MINING

    def load_from_data(self, consolidated_issue_data):
        self.number = consolidated_issue_data["number"]
        self.organization_name = consolidated_issue_data["organization_name"]
        self.repository_name = consolidated_issue_data["repository_name"]
        self.title = consolidated_issue_data["title"]
        self.state = consolidated_issue_data["state"]
        self.url = consolidated_issue_data["url"]
        self.body = consolidated_issue_data["body"]
        self.created_at = consolidated_issue_data["created_at"]
        self.updated_at = consolidated_issue_data["updated_at"]
        self.closed_at = consolidated_issue_data["closed_at"]

        # TODO: might be an issue somewhere here
        if "milestone_number" in consolidated_issue_data and consolidated_issue_data["milestone_number"]:
            milestone_data = {
                "number": consolidated_issue_data["milestone_number"],
                "title": consolidated_issue_data.get("milestone_title", ""),
                "html_url": consolidated_issue_data.get("milestone_html_url", "")
            }
            self.milestone = Milestone()
            self.milestone.load_from_api_json(milestone_data)
        else:
            self.milestone = None

        self.labels = list(consolidated_issue_data["labels"])
        self.page_filename = consolidated_issue_data["page_filename"]
        self.linked_to_project = consolidated_issue_data["linked_to_project"]
        self.project_title = consolidated_issue_data["project_title"]
        self.status = consolidated_issue_data["status"]
        self.priority = consolidated_issue_data["priority"]
        self.size = consolidated_issue_data["size"]
        self.moscow = consolidated_issue_data["moscow"]
        self.error = consolidated_issue_data["error"]

    def to_dict(self):
        milestone_number = self.milestone.number if self.milestone else None
        milestone_title = self.milestone.title if self.milestone else None
        milestone_html_url = self.milestone.html_url if self.milestone else None

        return {
            "number": self.number,
            "organization_name": self.organization_name,
            "repository_name": self.repository_name,
            "title": self.title,
            "state": self.state,
            "url": self.url,
            "body": self.body,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
            "milestone_number": milestone_number,
            "milestone_title": milestone_title,
            "milestone_html_url": milestone_html_url,
            "labels": self.labels,
            "page_filename": self.page_filename,
            "linked_to_project": self.linked_to_project,
            "project_title": self.project_title,
            "status": self.status,
            "priority": self.priority,
            "size": self.size,
            "moscow": self.moscow,
            "error": self.error
        }
