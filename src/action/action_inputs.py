import json
import logging
import os

from .model.config_repository import ConfigRepository


class ActionInputs:
    def __init__(self):
        self.__github_token: str = ""
        self.__is_project_state_mining_enabled: bool = True
        self.__projects_title_filter: list = []
        self.__are_milestones_as_chapters_enabled: bool = False
        self.__repositories: list[ConfigRepository] = []
        self.__output_directory: str = "../output"

    @property
    def github_token(self) -> str:
        return self.__github_token

    @property
    def is_project_state_mining_enabled(self) -> bool:
        return self.__is_project_state_mining_enabled

    @property
    def projects_title_filter(self) -> list:
        return self.__projects_title_filter

    @property
    def are_milestones_as_chapters_enabled(self) -> bool:
        return self.__are_milestones_as_chapters_enabled

    @property
    def repositories(self) -> list[ConfigRepository]:
        return self.__repositories

    @property
    def output_directory(self) -> str:
        return self.__output_directory

    def load_from_environment(self, validate: bool = True) -> 'ActionInputs':
        self.__github_token = os.getenv('GITHUB_TOKEN')
        self.__is_project_state_mining_enabled = os.getenv('PROJECT_STATE_MINING').lower == "true"
        self.__projects_title_filter = os.getenv('PROJECTS_TITLE_FILTER')
        self.__are_milestones_as_chapters_enabled = os.getenv('MILESTONES_AS_CHAPTERS').lower() == "true"
        self.__output_directory = os.getenv('OUTPUT_DIRECTORY')
        repositories_json = os.getenv('REPOSITORIES')

        logging.debug(f'Is project state mining allowed: {self.__is_project_state_mining_enabled}')
        logging.debug(f'Project title filter: {self.__projects_title_filter}')
        logging.debug(f'Are milestones used as chapters: {self.__are_milestones_as_chapters_enabled}')
        logging.debug(f'Json repositories to fetch from: {repositories_json}')
        logging.debug(f'Output directory: {self.__output_directory}')

        # Validate inputs
        if validate:
            self.validate_inputs(repositories_json)

        # Parse repositories json string into json dictionary format
        try:
            repositories_json = json.loads(repositories_json)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing json repositories: {e}")
            exit(1)

        for repository_json in repositories_json:
            config_repository = ConfigRepository()
            config_repository.load_from_json(repository_json)
            self.__repositories.append(config_repository)

        return self

    def validate_inputs(self, repositories_json: str) -> None:
        # TODO: repositories je json string, mam github token, output dir je dosazitelna, jinak vytvorim
        pass
