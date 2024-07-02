from ngsildclient.api.entities import Entities as OriginalEntities

class CustomEntity(OriginalEntities):
    def __init__(self, client, url, url_alt_post_query):
        # Call the parent class constructor with the client, url, and url_alt_post_query
        super().__init__(client, url, url_alt_post_query)

    def get(self, entity_id, asdict=True, **kwargs):
        """
        Override the get method to customize the GET request for retrieving entities.
        
        :param entity_id: The ID of the entity to retrieve.
        :param asdict: If True, return the response as a dictionary. If False, return as an Entity object(지원X).
        """
        headers = {
            "Accept": "application/ld+json",
            "Content-Type": None,
        }  # overrides session headers

        # Add authorization header if token is provided
        if self._client.token:
            headers["Authorization"] = f"Bearer {self._client.token}"

				# Make a GET request to the entity endpoint with the provided entity_id parameter
        r = self._session.get(f"{self.url}?id={entity_id}", headers=headers, **kwargs)
        self._client.raise_for_status(r)
        return r.json()