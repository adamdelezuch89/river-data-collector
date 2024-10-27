import json
import os
import psycopg2
from abc import ABC, abstractmethod
from psycopg2 import sql
from typing import Dict, List, Any
from utils.exceptions import DatabaseError
from utils.config import SQLConfig
from utils.logger import logger


class IDataStorage(ABC):
    """
    Interface for data storage classes.
    """

    @abstractmethod
    def save_data(self, data: Any) -> None:
        """
        Save data to the storage.

        Args:
            data (Any): The data to be saved.
        """
        pass

    @abstractmethod
    def get_data(self) -> Any:
        """
        Retrieve data from the storage.

        Returns:
            Any: The retrieved data.
        """
        pass


class JsonDataStorage(IDataStorage):
    """
    Class for saving and retrieving processed data to/from a JSON file.
    """

    def __init__(self, target: str):
        """
        Initialize JsonDataStorage.

        Args:
            target (str): The path to the JSON file.
        """
        self.target = target

    def save_data(self, data: Dict[str, Any]) -> None:
        """
        Save data to a JSON file.

        Args:
            data (Dict[str, Any]): The data to be saved.
        """
        with open(self.target, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"New processed data saved to {self.target}")

    def get_data(self) -> Dict[str, Any] | None:
        """
        Retrieve data from the JSON file.

        Returns:
            Dict[str, Any] | None: The retrieved data or None if the file doesn't exist.
        """
        if not os.path.exists(self.target):
            return None
        with open(self.target, "r") as f:
            return json.load(f)


class SqlDataStorage(IDataStorage):
    """
    Class for saving and retrieving processed data to/from a SQL database.
    """

    def __init__(self, config: SQLConfig):
        """
        Initialize SqlDataStorage.

        Args:
            config (SQLConfig): Configuration for the SQL database connection.
        """
        self.config = config

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Save data to the SQL database.

        Args:
            data (List[Dict[str, Any]]): The data to be saved.

        Raises:
            DatabaseError: If there's an error inserting data into the database.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    for item in data:
                        query = sql.SQL(
                            """
                            INSERT INTO {} (id, name, geometry)
                            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                            ON CONFLICT (id) DO UPDATE
                            SET name = EXCLUDED.name,
                                geometry = EXCLUDED.geometry
                        """
                        ).format(sql.Identifier(self.config.table))

                        linestring = self._create_linestring(item["geometry"])
                        cur.execute(query, (item["id"], item["name"], linestring))

                        conn.commit()
                    logger.info(
                        f"Successfully inserted {len(data)} records \
                        into {self.config.table}"
                    )
        except Exception as e:
            raise DatabaseError(
                f"Error inserting data into \
                                {self.config.table}: {e}"
            ) from e

    def cleanup(self) -> None:
        """
        Remove all data from the SQL database table.

        Raises:
            DatabaseError: If there's an error removing data from the database.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    query = sql.SQL("TRUNCATE TABLE {}").format(
                        sql.Identifier(self.config.table)
                    )
                    cur.execute(query)
                    conn.commit()
                    logger.info(
                        f"Successfully removed all records from \
                        {self.config.table}"
                    )
        except Exception as e:
            raise DatabaseError(
                f"Error removing data from \
                                {self.config.table}: {e}"
            ) from e

    def get_data(self) -> Any:
        """
        Retrieve data from the SQL database.

        Returns:
            Any: The retrieved data.

        TODO: Implement this method
        """
        pass

    def _get_connection(self):
        """
        Create and return a database connection.

        Returns:
            psycopg2.extensions.connection: A database connection object.

        Raises:
            DatabaseError: If there's an error connecting to the database.
        """
        try:
            return psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.name,
                user=self.config.user,
                password=self.config.password,
            )
        except psycopg2.Error as e:
            raise DatabaseError(f"Error connecting to database: {e}") from e

    @staticmethod
    def _create_linestring(
        coordinates: List[Dict[str, float]] | List[List[float]]
    ) -> str:
        """
        Create a LINESTRING representation from coordinates.

        Args:
            coordinates (List[Dict[str, float]] | List[List[float]]): The coordinates
            to convert.

        Returns:
            str: The LINESTRING representation.

        Raises:
            ValueError: If the coordinate format is unexpected.
        """
        points = []
        for coord in coordinates:
            if isinstance(coord, dict):
                points.append(f"{coord['lon']} {coord['lat']}")
            elif isinstance(coord, (list, tuple)):
                points.append(f"{coord[0]} {coord[1]}")
            else:
                raise ValueError(f"Unexpected coordinate format: {coord}")
        return f"LINESTRING({', '.join(points)})"
