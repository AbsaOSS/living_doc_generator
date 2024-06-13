from typing import List

CONSTANT = "N/A"


class ProjectIssue:
    def __init__(self):
        self.title: str = ""
        self.number: int = 0
        self.state: str = ""
        self.repository_name: str = ""
        self.owner: str = ""
        self.field_types: List[str] = []

    def to_dict(self):
        return {
            "title": self.title,
            "number": self.number,
            "state": self.state,
            "repository_name": self.repository_name,
            "owner": self.owner,
            "field_types": [str(field_type) for field_type in self.field_types]
        }

    def load_from_json(self, issue):
        issue_content = issue['content']

        for key in ["title", "number", "state", "repository", "fieldValues"]:
            if key not in issue['content']:
                raise ValueError(f"ProjectIssue key '{key}' is missing in the input dictionary.")

        if (not isinstance(issue_content["title"], str) or not isinstance(issue_content["number"], int)
                or not isinstance(issue_content["state"], str)):
            raise ValueError("ProjectIssue value of 'title', 'number' and 'state' should be of correct type.")

        if 'repository' in issue and (not isinstance(issue_content['repository']['name'], str)
                                      or not isinstance(issue_content['repository']['owner']['login'], str)):
            raise ValueError("ProjectIssue value of 'repository_name' and 'owner' should be of type string.")

        if 'fieldValues' in issue and not isinstance(issue['fieldValues']['nodes'], list):
            raise ValueError("ProjectIssue value of 'fieldValues' should be a list.")

        self.title = issue_content.get('title', CONSTANT)
        self.number = issue_content.get('number', CONSTANT)
        self.state = issue_content.get('state', CONSTANT)
        self.repository_name = issue_content['repository']['name'] if 'repository' in issue else CONSTANT
        self.owner = issue_content['repository']['owner']['login'] if 'repository' in issue else CONSTANT

        if 'fieldValues' in issue:
            for node in issue['fieldValues']['nodes']:
                if node['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                    self.field_types.append(node['name'])
