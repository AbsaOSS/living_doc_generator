from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Repository:
    orgName: str
    repoName: str
    queryLabels: Optional[List[str]]
