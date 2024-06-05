import json
from typing import Any

from .issue import Issue


class IssueEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Issue):
            return obj.__dict__
        return super().default(obj)
