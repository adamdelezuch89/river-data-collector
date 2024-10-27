from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from utils.exceptions import GeocodingError
from utils.logger import logger


class Geocoder:
    def __init__(self, user_agent: str):
        self.geolocator = Nominatim(user_agent=user_agent)

    def get_region_bbox(self, region_name: str) -> str:
        """
        Get the bounding box for a given region.

        Args:
            region_name (str): Name of the region to geocode.

        Returns:
            str: Bounding box as a comma-separated string.

        Raises:
            GeocodingError: If geocoding fails or no results are found.
        """
        try:
            location = self.geolocator.geocode(region_name, exactly_one=True)
            if not location:
                raise GeocodingError(f"Could not find bounding box for {region_name}")

            logger.info(
                f"Found bounding box for {region_name}: {location.raw['boundingbox']}"
            )
            return ",".join(
                [
                    location.raw["boundingbox"][0],
                    location.raw["boundingbox"][2],
                    location.raw["boundingbox"][1],
                    location.raw["boundingbox"][3],
                ]
            )

        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            raise GeocodingError(f"Geocoding service error: {e}") from e
