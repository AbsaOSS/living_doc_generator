import requests
from typing import Dict


class BaseContainer:
    @staticmethod
    def send_graphql_query(query: str, session: requests.sessions.Session) -> Dict[str, dict]:
        """
        Sends a GraphQL query to the GitHub API and returns the response.
        If an HTTP error occurs, it prints the error and returns an empty dictionary.

        @param query: The GraphQL query to be sent in f string format.
        @param session: A configured request session.

        @return: The response from the GitHub GraphQL API in a dictionary format.
        """
        try:
            # Fetch the response from the API
            response = session.post('https://api.github.com/graphql', json={'query': query})
            # Check if the request was successful
            response.raise_for_status()

            return response.json()["data"]

        # Specific error handling for HTTP errors
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")

        except Exception as e:
            print(f"An error occurred: {e}")

        return {}
