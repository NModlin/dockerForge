"""
DockerForge Docker Daemon Configuration Service

This module provides functionality for managing Docker daemon configuration,
including registry configuration, logging drivers, storage drivers, and network settings.
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from src.config.config_manager import ConfigManager
from src.platforms.platform_factory import PlatformFactory

logger = logging.getLogger(__name__)

# Default daemon.json path
DEFAULT_DAEMON_JSON_PATH = "/etc/docker/daemon.json"


class DaemonConfigManager:
    """
    Manages Docker daemon configuration.

    This class handles:
    - Reading and writing to daemon.json
    - Registry configuration
    - Logging driver settings
    - Storage driver configuration
    - Network settings
    """

    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the daemon configuration manager.

        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.platform_adapter = PlatformFactory.create_adapter()

        # Get daemon.json path from config or use default
        self.daemon_json_path = self.config.get("docker", {}).get(
            "daemon_json_path", DEFAULT_DAEMON_JSON_PATH
        )

    def get_daemon_config(self) -> Dict[str, Any]:
        """
        Get the current Docker daemon configuration.

        Returns:
            The daemon configuration as a dictionary
        """
        try:
            if os.path.exists(self.daemon_json_path):
                with open(self.daemon_json_path, "r") as f:
                    return json.load(f)
            else:
                logger.warning(
                    f"Daemon configuration file {self.daemon_json_path} does not exist"
                )
                return {}
        except Exception as e:
            logger.error(f"Error reading daemon configuration: {str(e)}")
            return {}

    def update_daemon_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update the Docker daemon configuration.

        Args:
            config: The new configuration to apply

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create a backup of the current configuration
            self._backup_daemon_config()

            # Create a temporary file for the new configuration
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                json.dump(config, temp_file, indent=2)
                temp_path = temp_file.name

            # Copy the temporary file to the daemon.json path
            # This requires elevated privileges
            cmd = ["cp", temp_path, self.daemon_json_path]
            success, stdout, stderr = self._execute_command(cmd, use_sudo=True)

            # Clean up the temporary file
            os.unlink(temp_path)

            if not success:
                return False, f"Failed to update daemon configuration: {stderr}"

            # Restart Docker daemon to apply changes
            restart_success, restart_message = self.platform_adapter.restart_docker()

            if not restart_success:
                return (
                    False,
                    f"Configuration updated but failed to restart Docker: {restart_message}",
                )

            return True, "Docker daemon configuration updated successfully"
        except Exception as e:
            logger.error(f"Error updating daemon configuration: {str(e)}")
            return False, f"Error updating daemon configuration: {str(e)}"

    def get_registry_config(self) -> Dict[str, Any]:
        """
        Get the current registry configuration.

        Returns:
            The registry configuration
        """
        daemon_config = self.get_daemon_config()
        return {
            "registry-mirrors": daemon_config.get("registry-mirrors", []),
            "insecure-registries": daemon_config.get("insecure-registries", []),
            "allow-nondistributable-artifacts": daemon_config.get(
                "allow-nondistributable-artifacts", []
            ),
        }

    def update_registry_config(
        self, registry_config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Update the registry configuration.

        Args:
            registry_config: The new registry configuration

        Returns:
            Tuple of (success, message)
        """
        try:
            daemon_config = self.get_daemon_config()

            # Update registry configuration
            daemon_config["registry-mirrors"] = registry_config.get(
                "registry-mirrors", []
            )
            daemon_config["insecure-registries"] = registry_config.get(
                "insecure-registries", []
            )
            daemon_config["allow-nondistributable-artifacts"] = registry_config.get(
                "allow-nondistributable-artifacts", []
            )

            return self.update_daemon_config(daemon_config)
        except Exception as e:
            logger.error(f"Error updating registry configuration: {str(e)}")
            return False, f"Error updating registry configuration: {str(e)}"

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get the current logging driver configuration.

        Returns:
            The logging configuration
        """
        daemon_config = self.get_daemon_config()
        return {
            "log-driver": daemon_config.get("log-driver", "json-file"),
            "log-opts": daemon_config.get("log-opts", {}),
        }

    def update_logging_config(self, logging_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update the logging driver configuration.

        Args:
            logging_config: The new logging configuration

        Returns:
            Tuple of (success, message)
        """
        try:
            daemon_config = self.get_daemon_config()

            # Update logging configuration
            daemon_config["log-driver"] = logging_config.get("log-driver", "json-file")
            daemon_config["log-opts"] = logging_config.get("log-opts", {})

            return self.update_daemon_config(daemon_config)
        except Exception as e:
            logger.error(f"Error updating logging configuration: {str(e)}")
            return False, f"Error updating logging configuration: {str(e)}"

    def get_storage_config(self) -> Dict[str, Any]:
        """
        Get the current storage driver configuration.

        Returns:
            The storage configuration
        """
        daemon_config = self.get_daemon_config()
        return {
            "storage-driver": daemon_config.get("storage-driver", ""),
            "storage-opts": daemon_config.get("storage-opts", []),
            "data-root": daemon_config.get("data-root", "/var/lib/docker"),
        }

    def update_storage_config(self, storage_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update the storage driver configuration.

        Args:
            storage_config: The new storage configuration

        Returns:
            Tuple of (success, message)
        """
        try:
            daemon_config = self.get_daemon_config()

            # Update storage configuration
            if storage_config.get("storage-driver"):
                daemon_config["storage-driver"] = storage_config["storage-driver"]

            daemon_config["storage-opts"] = storage_config.get("storage-opts", [])

            if storage_config.get("data-root"):
                daemon_config["data-root"] = storage_config["data-root"]

            return self.update_daemon_config(daemon_config)
        except Exception as e:
            logger.error(f"Error updating storage configuration: {str(e)}")
            return False, f"Error updating storage configuration: {str(e)}"

    def get_network_config(self) -> Dict[str, Any]:
        """
        Get the current network configuration.

        Returns:
            The network configuration
        """
        daemon_config = self.get_daemon_config()
        return {
            "default-address-pools": daemon_config.get("default-address-pools", []),
            "dns": daemon_config.get("dns", []),
            "dns-opts": daemon_config.get("dns-opts", []),
            "dns-search": daemon_config.get("dns-search", []),
            "bip": daemon_config.get("bip", ""),
            "fixed-cidr": daemon_config.get("fixed-cidr", ""),
            "fixed-cidr-v6": daemon_config.get("fixed-cidr-v6", ""),
            "default-gateway": daemon_config.get("default-gateway", ""),
            "default-gateway-v6": daemon_config.get("default-gateway-v6", ""),
            "ip-forward": daemon_config.get("ip-forward", True),
            "ip-masq": daemon_config.get("ip-masq", True),
            "iptables": daemon_config.get("iptables", True),
            "ipv6": daemon_config.get("ipv6", False),
        }

    def update_network_config(self, network_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update the network configuration.

        Args:
            network_config: The new network configuration

        Returns:
            Tuple of (success, message)
        """
        try:
            daemon_config = self.get_daemon_config()

            # Update network configuration
            network_fields = [
                "default-address-pools",
                "dns",
                "dns-opts",
                "dns-search",
                "bip",
                "fixed-cidr",
                "fixed-cidr-v6",
                "default-gateway",
                "default-gateway-v6",
                "ip-forward",
                "ip-masq",
                "iptables",
                "ipv6",
            ]

            for field in network_fields:
                if field in network_config:
                    daemon_config[field] = network_config[field]

            return self.update_daemon_config(daemon_config)
        except Exception as e:
            logger.error(f"Error updating network configuration: {str(e)}")
            return False, f"Error updating network configuration: {str(e)}"

    def get_available_logging_drivers(self) -> List[str]:
        """
        Get a list of available logging drivers.

        Returns:
            List of available logging drivers
        """
        return [
            "json-file",
            "syslog",
            "journald",
            "gelf",
            "fluentd",
            "awslogs",
            "splunk",
            "etwlogs",
            "gcplogs",
            "logentries",
            "local",
        ]

    def get_available_storage_drivers(self) -> List[str]:
        """
        Get a list of available storage drivers.

        Returns:
            List of available storage drivers
        """
        return ["overlay2", "aufs", "btrfs", "devicemapper", "vfs", "zfs"]

    def _backup_daemon_config(self) -> Optional[str]:
        """
        Create a backup of the current daemon configuration.

        Returns:
            Path to the backup file or None if backup failed
        """
        try:
            if not os.path.exists(self.daemon_json_path):
                return None

            backup_dir = os.path.expanduser("~/.dockerforge/backups/daemon")
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = self._get_timestamp()
            backup_path = os.path.join(backup_dir, f"daemon.json.{timestamp}")

            shutil.copy2(self.daemon_json_path, backup_path)
            logger.info(f"Created backup of daemon configuration at {backup_path}")

            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of daemon configuration: {str(e)}")
            return None

    def _get_timestamp(self) -> str:
        """
        Get a timestamp string for backup files.

        Returns:
            Timestamp string
        """
        from datetime import datetime

        return datetime.now().strftime("%Y%m%d%H%M%S")

    def _execute_command(
        self, cmd: List[str], use_sudo: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Execute a shell command.

        Args:
            cmd: Command to execute
            use_sudo: Whether to use sudo

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            if use_sudo:
                cmd = ["sudo"] + cmd

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            stdout, stderr = process.communicate()
            success = process.returncode == 0

            return success, stdout, stderr
        except Exception as e:
            logger.error(f"Error executing command {cmd}: {str(e)}")
            return False, "", str(e)
