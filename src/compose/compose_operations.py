"""
DockerForge Compose Operations Module.

This module provides functionality for integrating with Docker Compose operations,
including up/down operations, service updates, configuration validation, health checking,
and controlled restarts.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from ..docker.connection_manager import DockerConnectionManager
from ..utils.logging_manager import get_logger

logger = get_logger(__name__)


class ComposeOperations:
    """Integrate with Docker Compose operations."""

    def __init__(
        self, config: Dict = None, docker_connection: DockerConnectionManager = None
    ):
        """Initialize ComposeOperations.

        Args:
            config: Configuration dictionary
            docker_connection: Docker connection manager
        """
        self.config = config or {}
        self.docker_connection = docker_connection or DockerConnectionManager(config)
        self.compose_command = self._get_compose_command()

    def _get_compose_command(self) -> str:
        """Get the Docker Compose command.

        Returns:
            Docker Compose command
        """
        # Check for docker-compose or docker compose
        try:
            # Try docker compose (new style)
            result = subprocess.run(
                ["docker", "compose", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.debug("Using 'docker compose' command")
                return "docker compose"
        except Exception as e:
            logger.debug(f"Error checking for 'docker compose' command: {e}")

        try:
            # Try docker-compose (old style)
            result = subprocess.run(
                ["docker-compose", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                logger.debug("Using 'docker-compose' command")
                return "docker-compose"
        except Exception as e:
            logger.debug(f"Error checking for 'docker-compose' command: {e}")

        # Default to new style
        logger.warning(
            "Could not determine Docker Compose command, defaulting to 'docker compose'"
        )
        return "docker compose"

    def validate_compose_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            # Run docker-compose config to validate
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "config", "--quiet"]
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose file {file_path} is valid")
                return True, []
            else:
                logger.warning(
                    f"Docker Compose file {file_path} is invalid: {result.stderr}"
                )
                return False, result.stderr.strip().split("\n")
        except Exception as e:
            logger.error(f"Failed to validate Docker Compose file {file_path}: {e}")
            return False, [str(e)]

    def up(
        self,
        file_path: str,
        services: List[str] = None,
        detach: bool = True,
        build: bool = False,
    ) -> Tuple[bool, str]:
        """Start services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to start (optional, starts all if not provided)
            detach: Whether to run in detached mode
            build: Whether to build images before starting

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path]

            # Add options
            if detach:
                cmd.append("-d")

            if build:
                cmd.append("--build")

            cmd.append("up")

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Starting Docker Compose services: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose services started successfully")
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to start Docker Compose services: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error starting Docker Compose services: {e}")
            return False, str(e)

    def down(
        self, file_path: str, volumes: bool = False, remove_orphans: bool = True
    ) -> Tuple[bool, str]:
        """Stop services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            volumes: Whether to remove volumes
            remove_orphans: Whether to remove containers for services not defined in the Compose file

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path]

            # Add options
            if volumes:
                cmd.append("-v")

            if remove_orphans:
                cmd.append("--remove-orphans")

            cmd.append("down")

            # Run command
            logger.info(f"Stopping Docker Compose services: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose services stopped successfully")
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to stop Docker Compose services: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error stopping Docker Compose services: {e}")
            return False, str(e)

    def restart(self, file_path: str, services: List[str] = None) -> Tuple[bool, str]:
        """Restart services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to restart (optional, restarts all if not provided)

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "restart"]

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Restarting Docker Compose services: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose services restarted successfully")
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to restart Docker Compose services: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error restarting Docker Compose services: {e}")
            return False, str(e)

    def pull(self, file_path: str, services: List[str] = None) -> Tuple[bool, str]:
        """Pull images for services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to pull (optional, pulls all if not provided)

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "pull"]

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Pulling Docker Compose images: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose images pulled successfully")
                return True, result.stdout
            else:
                logger.warning(f"Failed to pull Docker Compose images: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error pulling Docker Compose images: {e}")
            return False, str(e)

    def build(
        self, file_path: str, services: List[str] = None, no_cache: bool = False
    ) -> Tuple[bool, str]:
        """Build images for services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to build (optional, builds all if not provided)
            no_cache: Whether to use cache when building the image

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path]

            # Add options
            if no_cache:
                cmd.append("--no-cache")

            cmd.append("build")

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Building Docker Compose images: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                logger.info(f"Docker Compose images built successfully")
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to build Docker Compose images: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error building Docker Compose images: {e}")
            return False, str(e)

    def logs(
        self,
        file_path: str,
        services: List[str] = None,
        follow: bool = False,
        tail: str = "all",
    ) -> Tuple[bool, str]:
        """Get logs for services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to get logs for (optional, gets all if not provided)
            follow: Whether to follow log output
            tail: Number of lines to show from the end of the logs

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path]

            # Add options
            if follow:
                cmd.append("-f")

            cmd.append(f"--tail={tail}")
            cmd.append("logs")

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Getting Docker Compose logs: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.warning(f"Failed to get Docker Compose logs: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error getting Docker Compose logs: {e}")
            return False, str(e)

    def ps(self, file_path: str, services: List[str] = None) -> Tuple[bool, str]:
        """List containers for services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to list (optional, lists all if not provided)

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "ps"]

            # Add services if specified
            if services:
                cmd.extend(services)

            # Run command
            logger.info(f"Listing Docker Compose containers: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to list Docker Compose containers: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error listing Docker Compose containers: {e}")
            return False, str(e)

    def exec(self, file_path: str, service: str, command: str) -> Tuple[bool, str]:
        """Execute a command in a running container.

        Args:
            file_path: Path to the Docker Compose file
            service: Name of the service
            command: Command to execute

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "exec", service]

            # Add the command parts
            cmd.extend(command.split())

            # Run command
            logger.info(f"Executing command in Docker Compose container: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.warning(
                    f"Failed to execute command in Docker Compose container: {result.stderr}"
                )
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error executing command in Docker Compose container: {e}")
            return False, str(e)

    def check_health(
        self, file_path: str, services: List[str] = None
    ) -> Dict[str, str]:
        """Check the health status of services defined in a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to check (optional, checks all if not provided)

        Returns:
            Dictionary mapping service names to health status
        """
        try:
            # Get container IDs for services
            success, output = self.ps(file_path, services)
            if not success:
                logger.warning(f"Failed to get container IDs: {output}")
                return {}

            # Parse output to get container IDs
            lines = output.strip().split("\n")
            if len(lines) < 2:
                logger.warning("No containers found")
                return {}

            # Skip header line
            container_ids = {}
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    container_id = parts[0]
                    service_name = parts[1].split("_")[-1]
                    container_ids[service_name] = container_id

            # Check health status for each container
            health_status = {}
            for service_name, container_id in container_ids.items():
                try:
                    # Use Docker API to get container info
                    container = self.docker_connection.client.containers.get(
                        container_id
                    )
                    inspect_data = container.attrs

                    # Check if container has health check
                    if "Health" in inspect_data.get("State", {}):
                        health = inspect_data["State"]["Health"]
                        health_status[service_name] = health["Status"]
                    else:
                        # No health check defined
                        if inspect_data.get("State", {}).get("Running", False):
                            health_status[service_name] = "running (no health check)"
                        else:
                            health_status[service_name] = "not running"
                except Exception as e:
                    logger.warning(f"Failed to check health for {service_name}: {e}")
                    health_status[service_name] = "unknown"

            return health_status
        except Exception as e:
            logger.error(f"Error checking health status: {e}")
            return {}

    def controlled_restart(
        self, file_path: str, services: List[str] = None, wait_time: int = 5
    ) -> Tuple[bool, Dict[str, str]]:
        """Perform a controlled restart of services with health checks.

        Args:
            file_path: Path to the Docker Compose file
            services: List of services to restart (optional, restarts all if not provided)
            wait_time: Time to wait for services to become healthy (in seconds)

        Returns:
            Tuple of (success, health_status)
        """
        try:
            # Restart services
            success, output = self.restart(file_path, services)
            if not success:
                logger.warning(f"Failed to restart services: {output}")
                return False, {}

            # Wait for services to start
            logger.info(f"Waiting {wait_time} seconds for services to start...")
            time.sleep(wait_time)

            # Check health status
            health_status = self.check_health(file_path, services)

            # Check if all services are healthy
            all_healthy = all(status == "healthy" for status in health_status.values())

            if all_healthy:
                logger.info("All services are healthy")
            else:
                logger.warning("Not all services are healthy")

            return all_healthy, health_status
        except Exception as e:
            logger.error(f"Error performing controlled restart: {e}")
            return False, {}

    def config(self, file_path: str) -> Tuple[bool, Dict]:
        """Get the resolved Docker Compose configuration.

        Args:
            file_path: Path to the Docker Compose file

        Returns:
            Tuple of (success, config_dict)
        """
        try:
            # Run docker-compose config
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path, "config"]
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                # Parse YAML output
                config_dict = yaml.safe_load(result.stdout)
                return True, config_dict
            else:
                logger.warning(f"Failed to get Docker Compose config: {result.stderr}")
                return False, {}
        except Exception as e:
            logger.error(f"Error getting Docker Compose config: {e}")
            return False, {}

    def run_command(self, file_path: str, command: str) -> Tuple[bool, str]:
        """Run a custom Docker Compose command.

        Args:
            file_path: Path to the Docker Compose file
            command: Docker Compose command to run

        Returns:
            Tuple of (success, output)
        """
        try:
            # Build command
            cmd_parts = self.compose_command.split()
            cmd = cmd_parts + ["-f", file_path]

            # Add the command parts
            cmd.extend(command.split())

            # Run command
            logger.info(f"Running Docker Compose command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                logger.warning(f"Failed to run Docker Compose command: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Error running Docker Compose command: {e}")
            return False, str(e)
