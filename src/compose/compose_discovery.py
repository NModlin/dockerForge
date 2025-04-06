"""
DockerForge Compose Discovery Module.

This module provides functionality for discovering Docker Compose files in the file system.
It includes recursive scanning, Docker context detection, and metadata indexing.
"""

import glob
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

# Common Docker Compose file names
COMPOSE_FILE_PATTERNS = [
    "docker-compose*.yml",
    "docker-compose*.yaml",
    "compose*.yml",
    "compose*.yaml",
]

# Common locations to check for Docker Compose files
COMMON_LOCATIONS = [
    ".",
    "~/docker",
    "~/projects",
    "/etc/docker/compose",
]


class ComposeFileInfo:
    """Information about a discovered Docker Compose file."""

    def __init__(self, path: str, version: str = None, services: List[str] = None):
        """Initialize ComposeFileInfo.

        Args:
            path: Path to the Docker Compose file
            version: Docker Compose file version
            services: List of services defined in the file
        """
        self.path = os.path.abspath(os.path.expanduser(path))
        self.filename = os.path.basename(path)
        self.directory = os.path.dirname(self.path)
        self.version = version
        self.services = services or []
        self.last_modified = os.path.getmtime(self.path)
        self.size = os.path.getsize(self.path)
        self._metadata = {}

    @property
    def metadata(self) -> Dict:
        """Get metadata about the Docker Compose file.

        Returns:
            Dict containing metadata
        """
        return self._metadata

    def update_metadata(self, metadata: Dict) -> None:
        """Update metadata about the Docker Compose file.

        Args:
            metadata: Dict containing metadata to update
        """
        self._metadata.update(metadata)

    def __str__(self) -> str:
        """Return string representation of ComposeFileInfo.

        Returns:
            String representation
        """
        return f"ComposeFileInfo(path={self.path}, version={self.version}, services={len(self.services)})"

    def __repr__(self) -> str:
        """Return string representation of ComposeFileInfo.

        Returns:
            String representation
        """
        return self.__str__()


class ComposeDiscovery:
    """Discover Docker Compose files in the file system."""

    def __init__(self, config: Dict = None):
        """Initialize ComposeDiscovery.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.discovered_files: Dict[str, ComposeFileInfo] = {}
        self.docker_contexts: Dict[str, str] = {}
        self._discover_docker_contexts()

    def _discover_docker_contexts(self) -> None:
        """Discover Docker contexts and their associated directories."""
        try:
            # This is a placeholder for actual Docker context discovery
            # In a real implementation, we would use the Docker CLI or API
            # to get the list of contexts and their metadata
            self.docker_contexts = {
                "default": os.path.expanduser("~/.docker"),
            }
            logger.debug(f"Discovered Docker contexts: {self.docker_contexts}")
        except Exception as e:
            logger.warning(f"Failed to discover Docker contexts: {e}")

    def discover_files(
        self,
        paths: List[str] = None,
        recursive: bool = True,
        include_common_locations: bool = True,
    ) -> Dict[str, ComposeFileInfo]:
        """Discover Docker Compose files in the specified paths.

        Args:
            paths: List of paths to search
            recursive: Whether to search recursively
            include_common_locations: Whether to include common locations

        Returns:
            Dict mapping file paths to ComposeFileInfo objects
        """
        search_paths = set()

        # Add user-specified paths
        if paths:
            for path in paths:
                expanded_path = os.path.abspath(os.path.expanduser(path))
                search_paths.add(expanded_path)

        # Add common locations if requested
        if include_common_locations:
            for location in COMMON_LOCATIONS:
                expanded_location = os.path.abspath(os.path.expanduser(location))
                search_paths.add(expanded_location)

        # Add Docker context locations
        for context, path in self.docker_contexts.items():
            search_paths.add(path)

        # Discover files in all search paths
        for search_path in search_paths:
            self._discover_in_path(search_path, recursive)

        return self.discovered_files

    def _discover_in_path(self, path: str, recursive: bool) -> None:
        """Discover Docker Compose files in the specified path.

        Args:
            path: Path to search
            recursive: Whether to search recursively
        """
        if not os.path.exists(path):
            logger.debug(f"Path does not exist: {path}")
            return

        logger.debug(f"Searching for Docker Compose files in {path}")

        # Search for Docker Compose files in the current directory
        for pattern in COMPOSE_FILE_PATTERNS:
            if recursive:
                # Use ** for recursive glob
                search_pattern = os.path.join(path, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                # Search only in the current directory
                search_pattern = os.path.join(path, pattern)
                files = glob.glob(search_pattern)

            for file_path in files:
                self._process_compose_file(file_path)

    def _process_compose_file(self, file_path: str) -> None:
        """Process a discovered Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
        """
        try:
            # Skip if already processed
            if file_path in self.discovered_files:
                return

            logger.debug(f"Processing Docker Compose file: {file_path}")

            # Extract basic information from the file
            with open(file_path, "r") as f:
                try:
                    compose_data = yaml.safe_load(f)
                    version = compose_data.get("version")
                    services = list(compose_data.get("services", {}).keys())

                    # Create ComposeFileInfo object
                    file_info = ComposeFileInfo(
                        path=file_path, version=version, services=services
                    )

                    # Add to discovered files
                    self.discovered_files[file_path] = file_info
                    logger.info(
                        f"Discovered Docker Compose file: {file_path} (version: {version}, services: {len(services)})"
                    )
                except yaml.YAMLError as e:
                    logger.warning(
                        f"Failed to parse Docker Compose file {file_path}: {e}"
                    )
        except Exception as e:
            logger.warning(f"Error processing Docker Compose file {file_path}: {e}")

    def get_file_info(self, path: str) -> Optional[ComposeFileInfo]:
        """Get information about a specific Docker Compose file.

        Args:
            path: Path to the Docker Compose file

        Returns:
            ComposeFileInfo object or None if not found
        """
        abs_path = os.path.abspath(os.path.expanduser(path))
        return self.discovered_files.get(abs_path)

    def refresh(self) -> None:
        """Refresh the list of discovered files."""
        # Clear the current list
        self.discovered_files = {}

        # Rediscover Docker contexts
        self._discover_docker_contexts()

        # Rediscover files using the same paths as before
        self.discover_files()

    def get_files_by_service(self, service_name: str) -> List[ComposeFileInfo]:
        """Get Docker Compose files that contain a specific service.

        Args:
            service_name: Name of the service to search for

        Returns:
            List of ComposeFileInfo objects
        """
        return [
            file_info
            for file_info in self.discovered_files.values()
            if service_name in file_info.services
        ]

    def get_files_by_directory(self, directory: str) -> List[ComposeFileInfo]:
        """Get Docker Compose files in a specific directory.

        Args:
            directory: Directory to search in

        Returns:
            List of ComposeFileInfo objects
        """
        abs_directory = os.path.abspath(os.path.expanduser(directory))
        return [
            file_info
            for file_info in self.discovered_files.values()
            if os.path.dirname(file_info.path) == abs_directory
        ]
