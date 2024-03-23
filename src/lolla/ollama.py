"""
Ollama connector module for lolla.
"""

import json

from requests import Session


class OllamaConnector:
    """
    Ollama connector class.
    """

    def __init__(self, app_version, logger, endpoint, keep_alive):
        self.app_version = app_version
        self.logger = logger
        self.endpoint = endpoint
        self.keep_alive = keep_alive

        self.client = self._get_client()

    def _get_client(self):
        """
        Get the client for the Ollama connector.
        """
        client = Session()
        client.headers.user_agent = f"lolla/{self.app_version}"

        return client

    def health(self):
        """
        Check the health of the Ollama service.
        """
        response = self.client.get(f"{self.endpoint}/")
        response.raise_for_status()

        return True

    def version(self):
        """
        Get the version of the Ollama service.
        """
        response = self.client.get(f"{self.endpoint}/api/version")
        response.raise_for_status()

        return response.json().get("version")

    def list_models(self):
        """
        List all the available models.
        """
        response = self.client.get(f"{self.endpoint}/api/tags")
        response.raise_for_status()

        return response.json().get("models")

    def pull_model(self, name, version="latest"):
        """
        Pull a model from the server.
        """
        response = self.client.post(
            f"{self.endpoint}/api/pull",
            json={"name": f"{name}:{version}", "stream": True},
            stream=True,
        )
        response.raise_for_status()

        for chunk in response.iter_lines():
            yield json.loads(chunk)

    def delete_model(self, name, version):
        """
        Delete a model from the server.
        """
        response = self.client.delete(
            f"{self.endpoint}/api/delete", json={"name": f"{name}:{version}"}
        )
        response.raise_for_status()

        return response.json()

    def chat(self, model, messages):
        """
        Chat with a Ollama model.
        """
        response = self.client.post(
            f"{self.endpoint}/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            stream=True,
        )
        response.raise_for_status()

        for chunk in response.iter_lines():
            yield json.loads(chunk)
