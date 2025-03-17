"""
DockerForge Version Checker

This module provides functionality for checking for updates to the DockerForge application.
"""

import os
import json
import logging
import requests
import semver
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any

from src.config.config_manager import ConfigManager
from src.utils.logging_manager import get_logger

logger = get_logger(__name__)

class VersionChecker:
    """
    Checks for updates to the DockerForge application.
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the VersionChecker.

        Args:
            config_manager: The configuration manager instance.
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config().get("update", {})
        self.current_version = self._get_current_version()
        self.cache_file = os.path.join(
            config_manager.get_data_dir(), "update_cache.json"
        )
        self.cache_ttl = self.config.get("cache_ttl", 24)  # hours
        self.api_url = self.config.get(
            "api_url", "https://api.github.com/repos/dockerforge/dockerforge/releases/latest"
        )
        self.release_url = self.config.get(
            "release_url", "https://github.com/dockerforge/dockerforge/releases"
        )

    def _get_current_version(self) -> str:
        """
        Get the current version of the application.

        Returns:
            The current version string.
        """
        # This could be imported from a version.py file or from package metadata
        # For now, we'll use a hardcoded version
        return "0.1.0"

    def _read_cache(self) -> Optional[Dict[str, Any]]:
        """
        Read the update check cache.

        Returns:
            The cached data or None if the cache is invalid or expired.
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)

            # Check if cache is expired
            cache_time = datetime.fromisoformat(cache.get("timestamp", ""))
            if datetime.now() - cache_time > timedelta(hours=self.cache_ttl):
                logger.debug("Update cache expired")
                return None

            return cache
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Error reading update cache: {e}")
            return None

    def _write_cache(self, data: Dict[str, Any]) -> None:
        """
        Write data to the update check cache.

        Args:
            data: The data to cache.
        """
        try:
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

            # Add timestamp to cache
            data["timestamp"] = datetime.now().isoformat()

            with open(self.cache_file, "w") as f:
                json.dump(data, f)
        except (OSError, TypeError) as e:
            logger.warning(f"Error writing update cache: {e}")

    def check_for_updates(self, force: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if updates are available.

        Args:
            force: Force a check even if the cache is valid.

        Returns:
            A tuple containing:
            - Boolean indicating if an update is available
            - The latest version string (or None if check failed)
            - The release URL (or None if check failed)
        """
        if not force:
            # Check cache first
            cache = self._read_cache()
            if cache:
                logger.debug("Using cached update information")
                return (
                    cache.get("update_available", False),
                    cache.get("latest_version"),
                    cache.get("release_url"),
                )

        try:
            logger.info("Checking for updates...")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")
            release_url = release_data.get("html_url", self.release_url)

            # Compare versions
            update_available = False
            if latest_version:
                try:
                    update_available = semver.compare(latest_version, self.current_version) > 0
                except ValueError:
                    # If semver parsing fails, fall back to string comparison
                    update_available = latest_version > self.current_version

            # Cache the result
            self._write_cache({
                "update_available": update_available,
                "latest_version": latest_version,
                "release_url": release_url,
                "release_notes": release_data.get("body", ""),
            })

            return update_available, latest_version, release_url

        except Exception as e:
            logger.warning(f"Error checking for updates: {e}")
            return False, None, None

    def get_release_notes(self, version: Optional[str] = None) -> str:
        """
        Get the release notes for a specific version.

        Args:
            version: The version to get release notes for. If None, gets the latest version.

        Returns:
            The release notes as a string.
        """
        cache = self._read_cache()
        if cache and not version:
            return cache.get("release_notes", "No release notes available.")

        # If we need to fetch specific version notes or cache is invalid
        try:
            if version:
                url = f"https://api.github.com/repos/dockerforge/dockerforge/releases/tags/v{version}"
            else:
                url = self.api_url

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            return release_data.get("body", "No release notes available.")
        except Exception as e:
            logger.warning(f"Error fetching release notes: {e}")
            return "Unable to fetch release notes."
