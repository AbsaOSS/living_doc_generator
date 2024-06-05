from typing import List


class Repository:
    def __init__(self):
        self.organizationName: str = ""
        self.repositoryName: str = ""
        self.queryLabels: List[str] = []

    def load_from_json(self, repository):
        for key in ["orgName", "repoName", "queryLabels"]:
            if key not in repository:
                raise ValueError(f"Key '{key}' is missing in the input dictionary.")

        if not isinstance(repository["orgName"], str) or not isinstance(repository["repoName"], str):
            raise ValueError("'orgName' and 'repoName' should be of type string.")

        if not isinstance(repository["queryLabels"], list) or not all(isinstance(i, str) for i in repository["queryLabels"]):
            raise ValueError("'queryLabels' should be a list of strings.")

        self.organizationName = repository["orgName"]
        self.repositoryName = repository["repoName"]
        self.queryLabels = repository["queryLabels"]
