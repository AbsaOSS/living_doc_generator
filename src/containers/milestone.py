from typing import Optional


class Milestone:
    def __init__(self):
        self.number: Optional[int] = None
        self.title: Optional[str] = None
        self.html_url: Optional[str] = None

    def load_from_json(self, milestone):
        for key in ["number", "title", "html_url"]:
            if key not in milestone:
                raise ValueError(f"Milestone key '{key}' is missing in the input dictionary.")

        if not isinstance(milestone["number"], int):
            raise ValueError("Milestone value of 'number' should be of type int.")

        if not isinstance(milestone["title"], str) or not isinstance(milestone["html_url"], str):
            raise ValueError("Milestone value of 'title' and 'html_url' should be of type string.")

        self.number = milestone["number"]
        self.title = milestone["title"]
        self.html_url = milestone["html_url"]
