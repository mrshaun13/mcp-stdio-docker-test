"""
Logging configuration for MCP STDIO Test Server.
"""

import logging
import os
import sys
from pythonjsonlogger import jsonlogger


def configure_logging() -> None:
    """Configure JSON logging to stderr."""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    handler = logging.StreamHandler(sys.stderr)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
