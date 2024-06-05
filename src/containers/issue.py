import re
from typing import List, Optional, Union


class Issue:
    def __init__(self, organization_name: str, repository_name: str):
        self.number: int = 0
        self.organizationName: str = organization_name
        self.repositoryName: str = repository_name
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

    def load_from_json(self, issue):
        self.number = issue["number"]
        self.title = issue["title"]
        self.state = issue["state"]
        self.url = issue["url"]
        self.body = issue["body"]
        self.createdAt = issue["created_at"]
        self.updatedAt = issue["updated_at"]

        md_filename_base = f"{issue['number']}_{issue['title'].lower()}.md"
        self.pageFilename = self.__sanitize_filename(md_filename_base)

        labels = issue.get('labels', [])
        self.labels = [label['name'] for label in labels]

        if "closedAt" in issue:
            self.closedAt = issue["closed_at"]

        milestone = issue.get('milestone', {})
        self.milestoneTitle = milestone["title"] if milestone else "No milestone"
        self.milestoneHtmlUrl = milestone["html_url"] if milestone else "No milestone"
        self.milestoneNumber = milestone["number"] if milestone else "No milestone"

        # Generated
        for key in ["number", "title", "state", "url", "body", "created_at", "updated_at"]:
            if key not in issue:
                raise ValueError(f"Key '{key}' is missing in the input dictionary.")

        if not isinstance(issue["number"], int):
            raise ValueError("'number' should be of type int.")

        if not all(isinstance(issue[key], str) for key in ["title", "state", "url", "body", "created_at", "updated_at"]):
            raise ValueError("'owner', 'title', 'state', 'url', 'body', 'createdAt', 'updatedAt' should be of type string.")

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
