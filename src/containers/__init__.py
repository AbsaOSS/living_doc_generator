from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Repository:
    orgName: str
    repoName: str
    queryLabels: List[str]

    def __getitem__(self, item):
        return self.__dict__[item]

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
