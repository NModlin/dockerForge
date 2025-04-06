"""
Connection manager adapter module for DockerForge.

This module provides a compatibility layer for the ConnectionManager class.
"""

from src.docker.connection_manager import DockerConnectionManager


class ConnectionManager(DockerConnectionManager):
    """
    Compatibility adapter for DockerConnectionManager.

    This class is a thin wrapper around DockerConnectionManager to provide
    backward compatibility with code that expects a ConnectionManager class.
    """

    def __init__(self, config_manager=None):
        """
        Initialize the connection manager.

        Args:
            config_manager: Configuration manager instance or dictionary
        """
        # Extract config from config_manager if provided
        config = None
        if config_manager is not None:
            if hasattr(config_manager, "get"):
                # If it's a ConfigManager instance, get the full config
                config = config_manager.config
            else:
                # Otherwise, assume it's a dictionary
                config = config_manager

        super().__init__(config)
