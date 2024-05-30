from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Issue:
    number: int
    owner: str
    repositoryName: str
    title: str
    state: str
    url: str
    body: str
    createdAt: str
    updatedAt: str
    closedAt: Optional[str]
    milestoneNumber: Union[str, int]
    milestoneTitle: str
    milestoneHtmlUrl: str
    labels: List[str]
    pageFilename: str

    def to_dict(self):
        return asdict(self)
