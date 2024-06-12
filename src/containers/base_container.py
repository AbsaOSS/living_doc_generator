import json
from typing import List


class BaseContainer:
    # TODO: There should be issues: List[Issue], but there is (most likely due to a circular import) error
    def save_issues_to_json_file(self, issues: List["Issue"], object_type: str, output_directory: str, state_name: str) -> str:
        """
        Saves a list state to a JSON file.

        @param issues: The list of issues ot be saved.
        @param object_type: The object type of the state (e.g., 'feature', 'project').
        @param output_directory: The directory, where the file will be saved.
        @param state_name: The naming of the state.

        @return: The name of the output file.
        """
        # Prepare the unique saving naming
        sanitized_name = state_name.lower().replace(" ", "_").replace("-", "_")
        output_file_name = f"{sanitized_name}.{object_type}.json"
        output_file_path = f"{output_directory}/{output_file_name}"

        # Save a file with correct output
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(
                [issue.to_dict() for issue in issues],
                json_file,
                ensure_ascii=False,
                indent=4)

        return output_file_name
