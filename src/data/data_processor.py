from typing import List, Dict, Any


class DataProcessor:
    """
    A class for processing and comparing geographical data.
    """

    def process_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process raw geographical data and extract relevant information.

        Args:
            raw_data (Dict[str, Any]): The raw data containing elements to process.

        Returns:
            List[Dict[str, Any]]: A list of processed elements with id,
            geometry, and name.
        """
        processed_data = []

        for element in raw_data.get("elements", []):
            if element["type"] == "way":
                processed_element = self._process(element)
                processed_data.append(processed_element)

        return processed_data

    def _process(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single 'way' element.

        Args:
            element (Dict[str, Any]): The element to process.

        Returns:
            Dict[str, Any]: A processed element with id, geometry, and name.
        """
        return {
            "id": element["id"],
            "geometry": self._extract_geometry(element),
            "name": element.get("tags", {}).get("name"),
        }

    def _extract_geometry(self, element: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Extract geometry information from an element.

        Args:
            element (Dict[str, Any]): The element containing geometry information.

        Returns:
            List[Dict[str, float]]: A list of nodes representing the geometry.
        """
        return element.get("geometry", []) if element["type"] == "way" else []

    @staticmethod
    def is_data_changed(new_data: Any, old_data: Any) -> bool:
        """
        Compare two data sets to determine if they are different.

        Args:
            new_data (Any): The new data set.
            old_data (Any): The old data set.

        Returns:
            bool: True if the data sets are different, False otherwise.
        """
        return new_data != old_data
