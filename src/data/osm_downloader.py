import requests
from typing import Dict
from utils.exceptions import OsmApiError
from utils.logger import logger


class OSMDownloader:
    def __init__(self, api_url: str):
        """
        Initialize the OSMDownloader.

        Args:
            api_url (str): The URL of the OpenStreetMap API.
        """
        self.api_url = api_url

    def download_data(self, bbox: str) -> Dict:
        """
        Download river data for the given bounding box.

        Args:
            bbox (str): Bounding box coordinates.

        Returns:
            Dict: JSON response containing river data.

        Raises:
            OsmApiError: If there's an error downloading the data.
        """
        query = self._build_query(bbox)

        try:
            response = self._make_request(query)
            logger.info(f"Downloaded data for bbox: {bbox}")
            return response.json()
        except requests.RequestException as e:
            raise OsmApiError(f"Error downloading river data: {e}") from e

    @staticmethod
    def _build_query(bbox: str) -> str:
        """
        Build the Overpass QL query for downloading river data.

        Args:
            bbox (str): Bounding box coordinates.

        Returns:
            str: The Overpass QL query string.
        """
        return f"""
        [out:json];
        (
          way["waterway"="river"]({bbox});
          relation["waterway"="river"]({bbox});
        );
        out geom;
        """

    def _make_request(self, query: str) -> requests.Response:
        """
        Make an HTTP request to the OpenStreetMap API.

        Args:
            query (str): The Overpass QL query string.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            requests.RequestException: If there's an error making the request.
        """
        response = requests.get(self.api_url, params={"data": query})
        response.raise_for_status()
        return response
