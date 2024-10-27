"""Custom exceptions for the application."""


class ConfigError(Exception):
    """Raised when there's an error in configuration."""


class DatabaseError(Exception):
    """Raised when there's a database-related error."""


class GeocodingError(Exception):
    """Raised when there's an error in geocoding operations."""


class GraphBuilderError(Exception):
    """Raised when there's an error in graph building operations."""


class OsmApiError(Exception):
    """Raised when there's an error in OpenStreetMap API operations."""
