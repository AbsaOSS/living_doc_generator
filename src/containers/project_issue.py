from typing import Optional

NO_VALUE_SELECTED = "N/A"


class ProjectIssue:
    def __init__(self):
        self.number: int = 0
        self.organization_name: str = ""
        self.repository_name: str = ""
        # TODO: title and state can be deleted, since they are already mined in repository Issue
        # self.title: str = ""
        # self.state: str = ""
        self.status: Optional[str] = NO_VALUE_SELECTED
        self.priority: Optional[str] = NO_VALUE_SELECTED
        self.size: Optional[str] = NO_VALUE_SELECTED
        self.moscow: Optional[str] = NO_VALUE_SELECTED

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

    def load_from_api_json(self, issue_json, field_options):
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
    def load_from_data(self, issue_from_data):
        self.number = issue_from_data['number']
        self.organization_name = issue_from_data['organization_name']
        self.repository_name = issue_from_data['repository_name']
        self.status = issue_from_data['status']
        self.priority = issue_from_data['priority']
        self.size = issue_from_data['size']
        self.moscow = issue_from_data['moscow']

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
