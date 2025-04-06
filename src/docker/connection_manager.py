"""
Docker connection manager module for DockerForge.

This module provides functionality to connect to the Docker daemon
using different methods based on the platform.
"""

import logging
import os
import socket
import time
from typing import Any, Dict, List, Optional, Tuple

import docker
from docker.errors import DockerException
from src.platforms.platform_adapter import get_platform_adapter
from src.platforms.platform_detector import PlatformType, get_platform_info

logger = logging.getLogger(__name__)


class DockerConnectionError(Exception):
    """Exception raised for Docker connection errors."""

    pass


class DockerConnectionManager:
    """
    Manager for Docker connections.

    This class handles connecting to the Docker daemon using different
    methods based on the platform.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Docker connection manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.platform_info = get_platform_info()
        self.platform_adapter = get_platform_adapter()
        self.client = None
        self.connection_method = None
        self.connection_params = {}

    def connect(
        self, retry_count: int = 3, retry_delay: float = 1.0
    ) -> docker.DockerClient:
        """
        Connect to the Docker daemon.

        Args:
            retry_count: Number of connection attempts
            retry_delay: Delay between retries in seconds

        Returns:
            docker.DockerClient: Docker client

        Raises:
            DockerConnectionError: If connection fails
        """
        if self.client is not None:
            # Check if the connection is still valid
            try:
                self.client.ping()
                return self.client
            except (DockerException, AttributeError):
                # Connection is invalid, create a new one
                self.client = None
                self.connection_method = None

        # Try different connection methods
        connection_methods = [
            self._connect_with_environment,
            self._connect_with_socket,
            self._connect_with_named_pipe,
            self._connect_with_tcp,
            self._connect_with_ssh,
        ]

        last_error = None
        for method in connection_methods:
            for attempt in range(retry_count):
                try:
                    client = method()
                    if client is not None:
                        # Test the connection
                        client.ping()
                        self.client = client
                        self.connection_method = method.__name__
                        logger.info(f"Connected to Docker using {method.__name__}")
                        return client
                except Exception as e:
                    last_error = e
                    logger.debug(
                        f"Connection attempt {attempt+1} with {method.__name__} failed: {str(e)}"
                    )
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)

        # All connection methods failed
        error_msg = f"Failed to connect to Docker daemon: {str(last_error)}"
        logger.error(error_msg)
        raise DockerConnectionError(error_msg)

    def _connect_with_environment(self) -> Optional[docker.DockerClient]:
        """
        Connect to Docker using environment variables.

        Returns:
            Optional[docker.DockerClient]: Docker client or None
        """
        try:
            client = docker.from_env()
            self.connection_params = {"method": "environment"}
            return client
        except DockerException:
            return None

    def _connect_with_socket(self) -> Optional[docker.DockerClient]:
        """
        Connect to Docker using Unix socket.

        Returns:
            Optional[docker.DockerClient]: Docker client or None
        """
        if self.platform_info.platform_type in (PlatformType.LINUX, PlatformType.MACOS):
            socket_path = self.platform_info.docker_socket_path

            if not socket_path or not os.path.exists(socket_path):
                # Try common socket paths
                socket_paths = [
                    "/var/run/docker.sock",
                    "/run/docker.sock",
                    os.path.expanduser("~/.docker/run/docker.sock"),
                ]

                for path in socket_paths:
                    if os.path.exists(path):
                        socket_path = path
                        break

            if socket_path and os.path.exists(socket_path):
                try:
                    # Check if socket is accessible
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect(socket_path)
                    sock.close()

                    # Connect to Docker
                    client = docker.DockerClient(base_url=f"unix://{socket_path}")
                    self.connection_params = {"method": "socket", "path": socket_path}
                    return client
                except (socket.error, DockerException) as e:
                    logger.debug(f"Socket connection failed: {str(e)}")

                    # Try to fix permissions
                    try:
                        success, message = self.platform_adapter.fix_permissions(
                            socket_path
                        )
                        if success:
                            logger.info(
                                f"Fixed permissions for {socket_path}: {message}"
                            )
                            # Try connecting again
                            client = docker.DockerClient(
                                base_url=f"unix://{socket_path}"
                            )
                            self.connection_params = {
                                "method": "socket",
                                "path": socket_path,
                            }
                            return client
                    except Exception as fix_error:
                        logger.debug(f"Failed to fix permissions: {str(fix_error)}")

        return None

    def _connect_with_named_pipe(self) -> Optional[docker.DockerClient]:
        """
        Connect to Docker using Windows named pipe.

        Returns:
            Optional[docker.DockerClient]: Docker client or None
        """
        if self.platform_info.platform_type == PlatformType.WINDOWS:
            try:
                client = docker.DockerClient(base_url="npipe:////./pipe/docker_engine")
                self.connection_params = {"method": "named_pipe"}
                return client
            except DockerException as e:
                logger.debug(f"Named pipe connection failed: {str(e)}")

        return None

    def _connect_with_tcp(self) -> Optional[docker.DockerClient]:
        """
        Connect to Docker using TCP.

        Returns:
            Optional[docker.DockerClient]: Docker client or None
        """
        # Try to get host from config or environment
        host = self.config.get("docker_host")
        if not host:
            host = os.environ.get("DOCKER_HOST")

        if host and host.startswith(("tcp://", "http://", "https://")):
            try:
                client = docker.DockerClient(base_url=host)
                self.connection_params = {"method": "tcp", "host": host}
                return client
            except DockerException as e:
                logger.debug(f"TCP connection failed: {str(e)}")

        return None

    def _connect_with_ssh(self) -> Optional[docker.DockerClient]:
        """
        Connect to Docker using SSH.

        Returns:
            Optional[docker.DockerClient]: Docker client or None
        """
        # Try to get SSH connection details from config or environment
        ssh_host = self.config.get("docker_ssh_host")
        if not ssh_host:
            ssh_host = os.environ.get("DOCKER_SSH_HOST")

        if ssh_host:
            try:
                client = docker.DockerClient(base_url=f"ssh://{ssh_host}")
                self.connection_params = {"method": "ssh", "host": ssh_host}
                return client
            except DockerException as e:
                logger.debug(f"SSH connection failed: {str(e)}")

        return None

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current Docker connection.

        Returns:
            Dict[str, Any]: Connection information
        """
        if not self.client:
            return {"connected": False}

        try:
            version = self.client.version()
            info = self.client.info()

            return {
                "connected": True,
                "method": self.connection_method,
                "params": self.connection_params,
                "version": version,
                "info": {
                    "containers": info.get("Containers"),
                    "images": info.get("Images"),
                    "server_version": info.get("ServerVersion"),
                    "operating_system": info.get("OperatingSystem"),
                    "architecture": info.get("Architecture"),
                    "kernel_version": info.get("KernelVersion"),
                    "driver": info.get("Driver"),
                    "cpu_count": info.get("NCPU"),
                    "memory_total": info.get("MemTotal"),
                },
            }
        except Exception as e:
            logger.error(f"Error getting Docker connection info: {str(e)}")
            return {"connected": False, "error": str(e)}

    def disconnect(self) -> None:
        """Disconnect from Docker."""
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                logger.debug(f"Error closing Docker connection: {str(e)}")
            finally:
                self.client = None
                self.connection_method = None
                self.connection_params = {}

    def __enter__(self) -> docker.DockerClient:
        """Context manager entry."""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()


# Singleton instance
_docker_connection_manager = None


def get_docker_connection_manager(
    config: Optional[Dict[str, Any]] = None,
) -> DockerConnectionManager:
    """
    Get the Docker connection manager (singleton).

    Args:
        config: Optional configuration dictionary

    Returns:
        DockerConnectionManager: Docker connection manager
    """
    global _docker_connection_manager
    if _docker_connection_manager is None:
        _docker_connection_manager = DockerConnectionManager(config)
    elif config is not None:
        # Update config if provided
        _docker_connection_manager.config.update(config)

    return _docker_connection_manager


def get_docker_client(config: Optional[Dict[str, Any]] = None) -> docker.DockerClient:
    """
    Get a Docker client.

    Args:
        config: Optional configuration dictionary

    Returns:
        docker.DockerClient: Docker client

    Raises:
        DockerConnectionError: If connection fails
    """
    manager = get_docker_connection_manager(config)
    return manager.connect()
