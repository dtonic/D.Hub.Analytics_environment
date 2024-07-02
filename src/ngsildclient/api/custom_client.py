from ngsildclient.api.client import Client as OriginalClient
from ngsildclient.api.constants import ENDPOINT_ENTITIES, ENDPOINT_ALT_QUERY_ENTITIES
from ngsildclient.api.custom_entity import CustomEntity

import requests

class CustomClient(OriginalClient):
    def __init__(self, hostname, port=8085, token=None):
        """
        Initialize the CustomClient with the base URL, port, and optional token.
        
        :param hostname: The host name of the NGSI-LD API.
        :param port: The port number for the NGSI-LD API.
        :param token: Optional authentication token for the API.
        """
        self.token = token
        self.hostname = hostname
        self.port = port
        
        # Call the parent class constructor with the base URL and port
        super().__init__(hostname, port)
        
        # Override the _entities attribute with an instance of CustomEntitiy
        self._entities = CustomEntity(self, f"{self.url}/{ENDPOINT_ENTITIES}", f"{self.url}/{ENDPOINT_ALT_QUERY_ENTITIES}")

    def is_connected(self, raise_for_disconnected=False):
        """
        Check if the client is connected to the NGSI-LD API by making a test request.
        
        :param raise_for_disconnected: If True, raise an exception if not connected.
        :return: True if connected, False otherwise.
        """
        try:
            url = f"{self.url}/ngsi-ld/v1/entities"
            headers = {
                "Accept": "application/ld+json",
                "Content-Type": "application/ld+json"
            }

            # Add authorization header if token is provided
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            response = requests.get(url, headers=headers)
            return response.status_code == 200
        except requests.RequestException:
            return False

    # Override the get method to use CustomEntitiy's get method
    def get(self, entity_id, asdict=True, **kwargs):
        return self._entities.get(entity_id, asdict=asdict, **kwargs)