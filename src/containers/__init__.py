from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Repository:
    orgName: str
    repoName: str
    queryLabels: List[str]


@dataclass
class Issue:
    number: int
    owner: str
    repository_name: str
    title: str
    state: str
    url: str
    body: str
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    milestone_number: Union[str, int]
    milestone_title: str
    milestone_html_url: str
    labels: List[str]
    page_filename: str

    def to_dict(self):
        return asdict(self)
