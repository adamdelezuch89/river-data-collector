"""Configuration management for the application."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from utils.exceptions import ConfigError


@dataclass
class SQLConfig:
    """Configuration for SQL database connection."""

    host: str
    port: str
    name: str
    user: str
    password: str
    table: str


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j database connection."""

    uri: str
    user: str
    password: str
    graph_name: str


class Config:
    """Main configuration class for the application."""

    load_dotenv()

    REGION = os.getenv("REGION")

    SQL_CONFIG = SQLConfig(
        host=os.getenv("SQL_HOST"),
        port=os.getenv("SQL_PORT"),
        name=os.getenv("SQL_NAME"),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PASS"),
        table=os.getenv("SQL_TABLE"),
    )

    NEO4J_CONFIG = Neo4jConfig(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASS"),
        graph_name=os.getenv("NEO4J_GRAPH_NAME"),
    )

    LOGGER_CONFIG_PATH = os.getenv("LOGGER_CONFIG_PATH")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    OUTPUT_DIR_PATH = os.getenv("OUTPUT_DIR_PATH")
    OUTPUT_FILE_NAME = os.getenv("OUTPUT_FILE_NAME")
    GEOCODING_AGENT = os.getenv("GEOCODING_AGENT")

    OSM_API_URL = os.getenv("OSM_API_URL")

    @classmethod
    def get_output_file_path(cls) -> str:
        """Get the full path of the output file."""
        return os.path.join(cls.OUTPUT_DIR_PATH, cls.OUTPUT_FILE_NAME)

    @classmethod
    def validate(cls) -> None:
        """Validate the configuration settings."""
        if not cls.REGION:
            raise ValueError("REGION environment variable is not set")

        cls._validate_sql_config()
        cls._validate_neo4j_config()

        if not cls.LOGGER_CONFIG_PATH:
            raise ConfigError("LOGGER_CONFIG_PATH environment variable is not set")
        if not cls.OUTPUT_DIR_PATH:
            raise ConfigError("OUTPUT_DIR_PATH environment variable is not set")
        if not cls.OUTPUT_FILE_NAME:
            raise ConfigError("OUTPUT_FILE_NAME environment variable is not set")
        if not cls.GEOCODING_AGENT:
            raise ConfigError("GEOCODING_AGENT environment variable is not set")
        if not cls.OSM_API_URL:
            raise ConfigError("OSM_API_URL environment variable is not set")

    @classmethod
    def _validate_sql_config(cls) -> None:
        """Validate SQL configuration."""
        if not all(
            [
                cls.SQL_CONFIG.host,
                cls.SQL_CONFIG.port,
                cls.SQL_CONFIG.name,
                cls.SQL_CONFIG.user,
                cls.SQL_CONFIG.password,
                cls.SQL_CONFIG.table,
            ]
        ):
            raise ConfigError("SQL database configuration is incomplete")

    @classmethod
    def _validate_neo4j_config(cls) -> None:
        """Validate Neo4j configuration."""
        if not all(
            [
                cls.NEO4J_CONFIG.uri,
                cls.NEO4J_CONFIG.user,
                cls.NEO4J_CONFIG.password,
                cls.NEO4J_CONFIG.graph_name,
            ]
        ):
            raise ConfigError("Neo4j configuration is incomplete")
