from typing import List


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

    def load_from_json(self, issue_json):
        issue_content = issue_json['content']

        self.title = issue_content['title']
        self.number = issue_content['number']
        self.state = issue_content['state']

        repository_info = issue_content.get('repository', {})
        self.repository_name = repository_info['name']
        self.owner = repository_info['owner']['login']

        if 'fieldValues' in issue_json:
            for node in issue_json['fieldValues']['nodes']:
                if node['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                    self.field_types.append(node['name'])
