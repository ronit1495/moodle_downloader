"""Logging utilities for the Moodle Downloader."""

import logging
from config.config import LOG_FORMAT, LOG_LEVEL

def setup_logging():
    """Set up logging configuration."""
    # Configure logging to only use console output
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__) 