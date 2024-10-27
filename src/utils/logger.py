"""Logging configuration for the application."""

import logging
import os
from logging.config import fileConfig
from utils.config import Config


def setup_logger():
    """Set up and configure the logger."""
    config_path = os.path.join(Config.LOGGER_CONFIG_PATH)
    fileConfig(config_path)
    return logging.getLogger(__name__)


logger = setup_logger()
