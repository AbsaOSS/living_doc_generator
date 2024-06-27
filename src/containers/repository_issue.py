import re
from typing import List, Optional

from .milestone import Milestone


class RepositoryIssue:
    def __init__(self):
        self.number: int = 0
        self.organization_name: str = ""
        self.repository_name: str = ""
        self.title: str = ""
        self.state: str = ""
        self.url: str = ""
        self.body: str = ""
        self.created_at: str = ""
        self.updated_at: str = ""
        self.closed_at: Optional[str] = None
        self.milestone: Optional[Milestone] = None
        self.labels: List[str] = []
        self.page_filename: str = ""

    def load_from_json(self, issue_json, repository):
        # TODO: is possible to remove load and save from and to json, so it is json native
        self.number = issue_json["number"]
        self.organization_name = repository.organization_name
        self.repository_name = repository.repository_name
        self.title = issue_json["title"]
        self.state = issue_json["state"]
        self.url = issue_json["html_url"]
        self.body = issue_json["body"]
        self.created_at = issue_json["created_at"]
        self.updated_at = issue_json["updated_at"]
        self.closed_at = issue_json["closed_at"]

        # Have to initialize milestone before loading from JSON, so it has default values
        milestone_json = issue_json['milestone']
        self.milestone = Milestone()

        if milestone_json is not None:
            self.milestone.load_from_api_json(milestone_json)

        labels = issue_json.get('labels', [])
        self.labels = [label['name'] for label in labels]

        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        self.page_filename = self.sanitize_filename(md_filename_base)

    def to_dict(self):
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
            "milestone_number": self.milestone.number,
            "milestone_title": self.milestone.title,
            "milestone_html_url": self.milestone.html_url,
            "labels": [str(label) for label in self.labels],
            "page_filename": self.page_filename
        }

    def filter_out_labels_in_description(self, label_name: str, repository_issues: List['RepositoryIssue']):
        """
        Filter out the RepositoryIssues which have label_name only in issue description and append
        them into issues

        @param label_name: The name of the label.
        @param repository_issues: The list of fetched issues.
        """
        for label in self.labels:
            if label == label_name:
                repository_issues.append(self)

    def load_from_data(self, issue_from_data):
        self.number = issue_from_data["number"]
        self.title = issue_from_data["title"]
        self.state = issue_from_data["state"]
        self.url = issue_from_data["url"]
        self.body = issue_from_data["body"]
        self.created_at = issue_from_data["created_at"]
        self.updated_at = issue_from_data["updated_at"]
        self.closed_at = issue_from_data["closed_at"]
        self.organization_name = issue_from_data["organization_name"]
        self.repository_name = issue_from_data["repository_name"]

        self.milestone = Milestone()
        self.milestone.number = issue_from_data["milestone_number"]
        self.milestone.title = issue_from_data["milestone_title"]
        self.milestone.html_url = issue_from_data["milestone_html_url"]

        self.labels = issue_from_data["labels"]
        self.page_filename = issue_from_data["page_filename"]

    # TODO: Candidate for issue parent class
    def make_string_key(self) -> str:
        """
           Creates a unique 3way string key for identifying every unique feature.

           @return: The unique string key for the feature.
        """

        string_key = f"{self.organization_name}/{self.repository_name}/{self.number}"

        return string_key

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes the provided filename by removing invalid characters and replacing spaces with underscores.

        @param filename: The filename to be sanitized.

        @return: The sanitized filename.
        """
        # Remove invalid characters for Windows filenames
        sanitized_name = re.sub(r'[<>:"/|?*`]', '', filename)
        # Reduce consecutive periods
        sanitized_name = re.sub(r'\.{2,}', '.', sanitized_name)
        # Reduce consecutive spaces to a single space
        sanitized_name = re.sub(r' {2,}', ' ', sanitized_name)
        # Replace space with '_'
        sanitized_name = sanitized_name.replace(' ', '_')

        return sanitized_name
