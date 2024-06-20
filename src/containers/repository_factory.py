from .repository import Repository


class RepositoryFactory:
    @staticmethod
    def load_repositories_from_json(repositories_json) -> list[Repository]:
        repositories = []

        for repository_json in repositories_json:
            repository = Repository()
            repository.load_from_json(repository_json)
            repositories.append(repository)

        return repositories
