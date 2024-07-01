class ConfigRepository:
    def __init__(self):
        self.__owner: str = ""
        self.__name: str = ""
        self.__query_labels: list[str | None] = [None]

    @property
    def owner(self) -> str:
        return self.__owner

    @property
    def name(self) -> str:
        return self.__name

    @property
    def query_labels(self) -> list[str]:
        return self.__query_labels if self.__query_labels is not None else []

    def load_from_json(self, repository_json: dict):
        self.__owner = repository_json["owner"]
        self.__name = repository_json["repo-name"]
        self.__query_labels = repository_json["query-labels"]
