"""
Logging management module for DockerForge.

This module provides functionality to set up and manage logging
for the application.
"""

import logging
import logging.handlers
import os
import sys
from typing import Any, Dict, List, Optional, Union

from src.config.config_manager import get_config


class LoggingManager:
    """
    Manager for application logging.

    This class handles setting up and managing logging for the application.
    """

    # Log format strings
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_LOG_FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
    )

    # Log level mapping
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logging manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.root_logger = logging.getLogger()
        self.app_logger = logging.getLogger("dockerforge")
        self.initialized = False

    def setup_logging(self) -> None:
        """
        Set up logging for the application.

        This method configures logging based on the application configuration.
        """
        if self.initialized:
            return

        # Get configuration values
        log_level_name = get_config("general.log_level", "INFO")
        log_file = get_config("general.log_file", "dockerforge.log")
        log_format = (
            self.DETAILED_LOG_FORMAT
            if log_level_name == "DEBUG"
            else self.DEFAULT_LOG_FORMAT
        )

        # Convert log level name to logging level
        log_level = self.LOG_LEVELS.get(log_level_name, logging.INFO)

        # Reset root logger
        self.root_logger.handlers = []
        self.root_logger.setLevel(log_level)

        # Create formatters
        formatter = logging.Formatter(log_format)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Add console handler to root logger
        self.root_logger.addHandler(console_handler)

        # Create file handler if log file is specified
        if log_file:
            # Expand user directory in log file path
            log_file = os.path.expanduser(log_file)

            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir)
                except (IOError, OSError) as e:
                    self.app_logger.warning(
                        f"Could not create log directory {log_dir}: {str(e)}"
                    )
                    return

            # Create rotating file handler
            try:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,  # 10 MB
                    backupCount=5,
                    encoding="utf-8",
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)

                # Add file handler to root logger
                self.root_logger.addHandler(file_handler)

                self.app_logger.info(f"Logging to file: {log_file}")
            except (IOError, OSError) as e:
                self.app_logger.warning(
                    f"Could not set up log file {log_file}: {str(e)}"
                )

        # Set initialized flag
        self.initialized = True

        self.app_logger.debug("Logging initialized")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.

        Args:
            name: Logger name

        Returns:
            logging.Logger: Logger instance
        """
        if not self.initialized:
            self.setup_logging()

        return logging.getLogger(f"dockerforge.{name}")


# Singleton instance
_logging_manager = None


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Set up logging for the application.

    Args:
        config: Optional configuration dictionary
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager(config)

    _logging_manager.setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Logger instance
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()

    return _logging_manager.get_logger(name)
