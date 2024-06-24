from typing import Optional

NO_PROJECT_ATTACHED = "---"
NO_PROJECT_MINING = "-?-"


class ConsolidatedIssue:
    def __init__(self, repository_issue):
        # Data from repository issue
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

        # Data from project issue
        # TODO: link to the True at the right place in the consolidated script
        # self.linked_to_project = False
        # self.archived = False
        self.project_title = None
        self.status = NO_PROJECT_ATTACHED
        self.priority = NO_PROJECT_ATTACHED
        self.size = NO_PROJECT_ATTACHED
        self.moscow = NO_PROJECT_ATTACHED

        self.error: Optional[str] = None

    def update_with_project_data(self, project_issue, project_title):
        self.project_title = project_title
        self.status = project_issue.status
        self.priority = project_issue.priority
        self.size = project_issue.size
        self.moscow = project_issue.moscow

    def no_project_mining(self):
        self.project_title = NO_PROJECT_MINING
        self.status = NO_PROJECT_MINING
        self.priority = NO_PROJECT_MINING
        self.size = NO_PROJECT_MINING
        self.moscow = NO_PROJECT_MINING

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
            "project_title": self.project_title,
            "status": self.status,
            "priority": self.priority,
            "size": self.size,
            "moscow": self.moscow,
            "error": self.error
        }
