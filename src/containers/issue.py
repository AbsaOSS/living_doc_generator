import re
from typing import List, Optional

from .repository import Repository
from .milestone import Milestone


class Issue:
    def __init__(self, repository: Repository):
        self.number: int = 0
        self.organization_name: str = repository.organization_name
        self.repository_name: str = repository.repository_name
        self.title: str = ""
        self.state: str = ""
        self.url: str = ""
        self.body: str = ""
        self.created_at: str = ""
        self.updated_at: str = ""
        self.closed_at: Optional[str] = None
        self.milestone_number: Optional[int] = None
        self.milestone_title: Optional[str] = None
        self.milestone_html_url: Optional[str] = None
        self.labels: List[str] = []
        self.page_filename: str = ""

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
            "milestone_number": self.milestone_number,
            "milestone_title": self.milestone_title,
            "milestone_html_url": self.milestone_html_url,
            "labels": [str(label) for label in self.labels],
            "page_filename": self.page_filename
        }

    def load_from_json(self, issue):
        for key in ["number", "title", "state", "url", "body", "created_at", "updated_at"]:
            if key not in issue:
                raise ValueError(f"Issue key '{key}' is missing in the input dictionary.")

        if not isinstance(issue["number"], int):
            raise ValueError("Issue value of 'number' should be of type int.")

        string_keys_to_check = ["title", "state", "url", "body", "created_at", "updated_at"]
        for key in string_keys_to_check:
            if not isinstance(issue[key], str):
                raise ValueError(f"Issue value of '{key}' should be of type string.")

        self.number = issue["number"]
        self.title = issue["title"]
        self.state = issue["state"]
        self.url = issue["url"]
        self.body = issue["body"]
        self.created_at = issue["created_at"]
        self.updated_at = issue["updated_at"]
        self.closed_at = issue["closed_at"]

        milestone_json = issue['milestone']

        if milestone_json is not None:
            milestone = Milestone()
            milestone.load_from_json(milestone_json)

            self.milestone_number = milestone.number
            self.milestone_title = milestone.title
            self.milestone_html_url = milestone.html_url

        labels = issue.get('labels', [])
        self.labels = [label['name'] for label in labels]

        md_filename_base = f"{self.number}_{self.title.lower()}.md"
        self.page_filename = self.__sanitize_filename(md_filename_base)

    def __sanitize_filename(self, filename: str) -> str:
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
