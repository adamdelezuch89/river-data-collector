"""
Main script for processing and storing OpenStreetMap data.

This script orchestrates the process of downloading, processing, and storing
OpenStreetMap data for a specified region. It uses various components to
handle different aspects of the data pipeline.
"""

from data.data_processor import DataProcessor
from data.data_storage import JsonDataStorage, SqlDataStorage
from data.geocoder import Geocoder
from data.graph_builder import GraphBuilder
from data.osm_downloader import OSMDownloader
from utils.config import Config
from utils.exceptions import (
    ConfigError,
    DatabaseError,
    GeocodingError,
    GraphBuilderError,
    OsmApiError,
)
from utils.logger import logger


def main():
    """
    Main function to execute the OSM data processing pipeline.

    This function coordinates the following steps:
    1. Validate configuration
    2. Initialize components
    3. Download and process OSM data
    4. Store processed data in JSON and SQL formats
    5. Build a graph representation of the data
    """
    try:
        # Validate configuration
        Config.validate()

        # Initialize components
        geocoder = Geocoder(user_agent=Config.GEOCODING_AGENT)
        downloader = OSMDownloader(api_url=Config.OSM_API_URL)
        processor = DataProcessor()
        json_storage = JsonDataStorage(target=Config.get_output_file_path())
        sql_storage = SqlDataStorage(config=Config.SQL_CONFIG)
        graph_builder = GraphBuilder(config=Config.NEO4J_CONFIG)

        # Process data
        logger.info(f"Geocoding region: {Config.REGION}")
        bbox = geocoder.get_region_bbox(Config.REGION)

        logger.info(f"Downloading data for region: {Config.REGION}")
        raw_data = downloader.download_data(bbox)

        logger.info(f"Processing data for region: {Config.REGION}")
        processed_data = processor.process_data(raw_data)

        if not processor.is_data_changed(processed_data, json_storage.get_data()):
            logger.info(
                f"Processed data is not changed for region: {Config.REGION}, skipping"
            )
            return

        # Store data
        logger.info(f"Saving processed data to {Config.get_output_file_path()}")
        json_storage.save_data(processed_data)

        logger.info("Inserting new data into database")
        sql_storage.cleanup()
        sql_storage.save_data(processed_data)

        # Build graph
        logger.info("Creating new graph")
        graph_builder.cleanup()
        graph_builder.build_graph(processed_data, Config.NEO4J_CONFIG.graph_name)

    except ConfigError as e:
        logger.error(f"Config is not valid: {e}", exc_info=Config.DEBUG)
        return
    except GeocodingError as e:
        logger.error(f"Geocoding error: {e}", exc_info=Config.DEBUG)
        return
    except OsmApiError as e:
        logger.error(f"OSM API error: {e}", exc_info=Config.DEBUG)
        return
    except DatabaseError as e:
        logger.error(f"Database error: {e}", exc_info=Config.DEBUG)
        return
    except GraphBuilderError as e:
        logger.error(f"Graph builder error: {e}", exc_info=Config.DEBUG)
        return
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=Config.DEBUG)
        return


if __name__ == "__main__":
    main()
