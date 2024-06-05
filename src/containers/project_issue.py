from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ProjectIssue:
    Number: int
    Owner: str
    RepositoryName: str
    Title: str
    State: str
    Status: Optional[str] = None
    Size: Optional[str] = None
    Priority: Optional[str] = None
    MSCW: Optional[str] = None

    def to_dict(self):
        return asdict(self)
