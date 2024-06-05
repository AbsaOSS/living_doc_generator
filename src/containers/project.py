from dataclasses import dataclass, field, asdict
from typing import List, Dict
from .project_issue import ProjectIssue


@dataclass
class Project:
    ID: str
    Number: int
    Title: str
    Owner: str
    RepositoriesFromConfig: List[str]
    ProjectRepositories: List[str] = field(default_factory=list)
    Issues: List[ProjectIssue] = field(default_factory=list)
    FieldOptions: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
