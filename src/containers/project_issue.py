from typing import Optional


class ProjectIssue:
    def __init__(self):
        self.number: int = 0
        self.organization_name: str = ""
        self.repository_name: str = ""
        # TODO: title and state can be deleted, since they are already mined in repository Issue
        # self.title: str = ""
        # self.state: str = ""
        self.status: Optional[str] = None
        self.priority: Optional[str] = None
        self.size: Optional[str] = None
        self.moscow: Optional[str] = None

    def to_dict(self):
        return {
            "number": self.number,
            "organization_name": self.organization_name,
            "repository_name": self.repository_name,
            # "title": self.title,
            # "state": self.state,
            "status": self.status,
            "priority": self.priority,
            "size": self.size,
            "moscow": self.moscow
        }

    def load_from_json(self, issue_json, field_options):
        issue_content = issue_json['content']

        # self.title = issue_content['title']
        self.number = issue_content['number']
        # self.state = issue_content['state']

        repository_info = issue_content.get('repository', {})
        self.repository_name = repository_info['name']
        self.organization_name = repository_info['owner']['login']

        field_types = []
        if 'fieldValues' in issue_json:
            for node in issue_json['fieldValues']['nodes']:
                if node['__typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                    field_types.append(node['name'])

        for field_type in field_types:
            if field_type in field_options.get('Status', []):
                self.status = field_type
            elif field_type in field_options.get('Priority', []):
                self.priority = field_type
            elif field_type in field_options.get('Size', []):
                self.size = field_type
            elif field_type in field_options.get('MoSCoW', []):
                self.moscow = field_type

    # TODO: wrong naming
    def load_from_output(self, issue_output):
        # self.title = issue_output['title']
        self.number = issue_output['number']
        # self.state = issue_output['state']
        self.organization_name = issue_output['organization_name']
        self.repository_name = issue_output['repository_name']
        self.status = issue_output['status']
        self.priority = issue_output['priority']
        self.size = issue_output['size']

    # TODO: Candidate for issue parent class
    def make_string_key(self) -> str:
        """
           Creates a unique 3way string key for identifying every unique feature.

           @return: The unique string key for the feature.
        """
        organization_name = self.organization_name
        repository_name = self.repository_name
        number = self.number

        string_key = f"{organization_name}/{repository_name}/{number}"

        return string_key
