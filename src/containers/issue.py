import re

from dataclasses import asdict
from typing import List, Optional, Union


class Issue:
    def __init__(self, repositoryName: str, organizationName: str):
        self.number: int = 0
        self.organizationName: str = organizationName
        self.repositoryName: str = repositoryName
        self.title: str = ""
        self.state: str = ""
        self.url: str = ""
        self.body: str = ""
        self.createdAt: str = ""
        self.updatedAt: str = ""
        self.closedAt: Optional[str] = None
        self.milestoneNumber: Union[str, int] = ""
        self.milestoneTitle: str = ""
        self.milestoneHtmlUrl: str = ""
        self.labels: List[str] = []
        self.pageFilename: str = ""

    def to_dict(self):
        return asdict(self)

    def load_from_json(self, issue):
        for key in ["number", "owner", "repositoryName", "title", "state", "url", "body", "createdAt", "updatedAt"]:
            if key not in issue:
                raise ValueError(f"Key '{key}' is missing in the input dictionary.")

        if not isinstance(issue["number"], int):
            raise ValueError("'number' should be of type int.")

        if not all(isinstance(issue[key], str) for key in ["owner", "repositoryName", "title", "state", "url", "body", "createdAt", "updatedAt"]):
            raise ValueError("'owner', 'repositoryName', 'title', 'state', 'url', 'body', 'createdAt', 'updatedAt' should be of type string.")

        self.number = issue["number"]
        self.organizationName = issue["owner"]
        self.repositoryName = issue["repositoryName"]
        self.title = issue["title"]
        self.state = issue["state"]
        self.url = issue["url"]
        self.body = issue["body"]
        self.createdAt = issue["createdAt"]
        self.updatedAt = issue["updatedAt"]

        md_filename_base = f"{issue['number']}_{issue['title'].lower()}.md"
        self.pageFilename = self.__sanitize_filename(md_filename_base)

        labels = issue.get('labels', [])
        self.labels = [label['name'] for label in labels]

        if "closedAt" in issue:
            self.closedAt = issue["closedAt"]

        milestone = issue.get('milestone', {})
        self.milestoneTitle = issue["milestoneTitle"] if milestone else "No milestone"
        self.milestoneHtmlUrl = issue["milestoneHtmlUrl"] if milestone else "No milestone"
        self.milestoneNumber = issue["milestoneNumber"] if milestone else "No milestone"

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
