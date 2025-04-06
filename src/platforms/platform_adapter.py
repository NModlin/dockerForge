"""
Platform-specific adapter module for DockerForge.

This module provides abstract interfaces and concrete implementations
for platform-specific operations.
"""

import logging
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from .platform_detector import InitSystem, PlatformType, get_platform_info

logger = logging.getLogger(__name__)


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific adapters."""

    @abstractmethod
    def restart_docker(self) -> Tuple[bool, str]:
        """
        Restart the Docker daemon.

        Returns:
            Tuple[bool, str]: Success status and message
        """
        pass

    @abstractmethod
    def get_docker_info(self) -> Dict[str, Any]:
        """
        Get system-specific Docker information.

        Returns:
            Dict[str, Any]: Docker information
        """
        pass

    @abstractmethod
    def fix_permissions(self, path: str) -> Tuple[bool, str]:
        """
        Fix permissions for Docker access.

        Args:
            path: Path to fix permissions for

        Returns:
            Tuple[bool, str]: Success status and message
        """
        pass

    @abstractmethod
    def start_on_boot(self, enable: bool = True) -> Tuple[bool, str]:
        """
        Configure Docker to start on system boot.

        Args:
            enable: Whether to enable or disable

        Returns:
            Tuple[bool, str]: Success status and message
        """
        pass

    @abstractmethod
    def execute_command(
        self, command: List[str], use_sudo: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Execute a command on the system.

        Args:
            command: Command to execute as a list of arguments
            use_sudo: Whether to use sudo

        Returns:
            Tuple[bool, str, str]: Success status, stdout, and stderr
        """
        pass

    @abstractmethod
    def get_docker_compose_command(self) -> List[str]:
        """
        Get the Docker Compose command for this platform.

        Returns:
            List[str]: Docker Compose command as a list of arguments
        """
        pass


class LinuxAdapter(PlatformAdapter):
    """Linux-specific platform adapter."""

    def __init__(self):
        """Initialize the Linux adapter."""
        self.platform_info = get_platform_info()
        self.init_system = self.platform_info.init_system

    def restart_docker(self) -> Tuple[bool, str]:
        """Restart the Docker daemon on Linux."""
        if self.init_system == InitSystem.SYSTEMD:
            return self._systemd_restart_docker()
        elif self.init_system == InitSystem.UPSTART:
            return self._upstart_restart_docker()
        elif self.init_system == InitSystem.SYSVINIT:
            return self._sysvinit_restart_docker()
        else:
            # Try all methods as fallback
            methods = [
                self._systemd_restart_docker,
                self._upstart_restart_docker,
                self._sysvinit_restart_docker,
            ]

            for method in methods:
                success, message = method()
                if success:
                    return success, message

            return False, "Could not restart Docker with any known method"

    def _systemd_restart_docker(self) -> Tuple[bool, str]:
        """Restart Docker using systemd."""
        cmd = ["systemctl", "restart", "docker"]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            return True, "Docker restarted successfully with systemd"
        else:
            return False, f"Failed to restart Docker with systemd: {stderr}"

    def _upstart_restart_docker(self) -> Tuple[bool, str]:
        """Restart Docker using Upstart."""
        cmd = ["service", "docker", "restart"]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            return True, "Docker restarted successfully with Upstart"
        else:
            return False, f"Failed to restart Docker with Upstart: {stderr}"

    def _sysvinit_restart_docker(self) -> Tuple[bool, str]:
        """Restart Docker using SysVinit."""
        cmd = ["/etc/init.d/docker", "restart"]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            return True, "Docker restarted successfully with SysVinit"
        else:
            return False, f"Failed to restart Docker with SysVinit: {stderr}"

    def get_docker_info(self) -> Dict[str, Any]:
        """Get Docker information on Linux."""
        info = {}

        # Get Docker version
        cmd = ["docker", "version", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["version"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["version"] = stdout

        # Get Docker info
        cmd = ["docker", "info", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["info"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["info"] = stdout

        # Get systemd unit file location if applicable
        if self.init_system == InitSystem.SYSTEMD:
            cmd = ["systemctl", "show", "docker", "--property", "FragmentPath"]
            success, stdout, stderr = self.execute_command(cmd)
            if success and stdout:
                unit_file = stdout.strip().split("=", 1)[-1]
                info["unit_file"] = unit_file

        return info

    def fix_permissions(self, path: str) -> Tuple[bool, str]:
        """Fix permissions for Docker access on Linux."""
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"

        # If it's the Docker socket, add user to docker group
        if path == "/var/run/docker.sock" or path == "/run/docker.sock":
            # Check if docker group exists
            try:
                import grp

                grp.getgrnam("docker")

                # Add current user to docker group
                username = os.environ.get("USER", os.environ.get("USERNAME"))
                if username:
                    cmd = ["usermod", "-aG", "docker", username]
                    success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

                    if success:
                        return (
                            True,
                            f"Added user {username} to docker group. You may need to log out and back in for changes to take effect.",
                        )
                    else:
                        return False, f"Failed to add user to docker group: {stderr}"
            except (ImportError, KeyError):
                pass

        # Otherwise, just chmod the path
        cmd = ["chmod", "666", path]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            return True, f"Fixed permissions for {path}"
        else:
            return False, f"Failed to fix permissions for {path}: {stderr}"

    def start_on_boot(self, enable: bool = True) -> Tuple[bool, str]:
        """Configure Docker to start on system boot on Linux."""
        if self.init_system == InitSystem.SYSTEMD:
            action = "enable" if enable else "disable"
            cmd = ["systemctl", action, "docker"]
            success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

            if success:
                return True, f"Docker {action}d to start on boot"
            else:
                return False, f"Failed to {action} Docker on boot: {stderr}"

        elif self.init_system == InitSystem.UPSTART:
            # Upstart services are enabled by default if the conf file exists
            if enable:
                return True, "Upstart services are enabled by default"
            else:
                # Create an override file to disable the service
                override_dir = "/etc/init/docker.override"
                cmd = ["bash", "-c", f"echo 'manual' | sudo tee {override_dir}"]
                success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

                if success:
                    return True, "Docker disabled on boot"
                else:
                    return False, f"Failed to disable Docker on boot: {stderr}"

        elif self.init_system == InitSystem.SYSVINIT:
            if enable:
                cmd = ["update-rc.d", "docker", "defaults"]
            else:
                cmd = ["update-rc.d", "docker", "remove"]

            success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

            if success:
                action = "enabled" if enable else "disabled"
                return True, f"Docker {action} on boot"
            else:
                action = "enable" if enable else "disable"
                return False, f"Failed to {action} Docker on boot: {stderr}"

        else:
            return False, "Unsupported init system"

    def execute_command(
        self, command: List[str], use_sudo: bool = False
    ) -> Tuple[bool, str, str]:
        """Execute a command on Linux."""
        try:
            if (
                use_sudo
                and not self.platform_info.is_root
                and self.platform_info.has_sudo
            ):
                command = ["sudo"] + command

            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return process.returncode == 0, process.stdout, process.stderr
        except Exception as e:
            logger.exception(f"Error executing command {command}: {str(e)}")
            return False, "", str(e)

    def get_docker_compose_command(self) -> List[str]:
        """Get the Docker Compose command for Linux."""
        # Check for docker-compose standalone
        if shutil.which("docker-compose"):
            return ["docker-compose"]

        # Check for docker compose plugin
        cmd = ["docker", "compose", "version"]
        success, stdout, stderr = self.execute_command(cmd)

        if success:
            return ["docker", "compose"]

        # Default to docker-compose and let it fail if not found
        return ["docker-compose"]


class MacOSAdapter(PlatformAdapter):
    """macOS-specific platform adapter."""

    def __init__(self):
        """Initialize the macOS adapter."""
        self.platform_info = get_platform_info()

    def restart_docker(self) -> Tuple[bool, str]:
        """Restart Docker on macOS."""
        # On macOS, Docker is typically a desktop application
        # Try to restart the Docker app using osascript
        cmd = [
            "osascript",
            "-e",
            'quit app "Docker"',
            "-e",
            "delay 2",
            "-e",
            'tell application "Docker" to activate',
        ]

        success, stdout, stderr = self.execute_command(cmd)

        if success:
            return True, "Docker Desktop restarted successfully"
        else:
            # Fallback to killall
            cmd = ["killall", "Docker"]
            success, stdout, stderr = self.execute_command(cmd)

            if success:
                # Wait a moment and then start Docker again
                import time

                time.sleep(2)

                cmd = ["open", "-a", "Docker"]
                success, stdout, stderr = self.execute_command(cmd)

                if success:
                    return True, "Docker Desktop restarted successfully using killall"
                else:
                    return (
                        False,
                        f"Failed to start Docker Desktop after killing it: {stderr}",
                    )
            else:
                return False, f"Failed to restart Docker Desktop: {stderr}"

    def get_docker_info(self) -> Dict[str, Any]:
        """Get Docker information on macOS."""
        info = {}

        # Get Docker version
        cmd = ["docker", "version", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["version"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["version"] = stdout

        # Get Docker info
        cmd = ["docker", "info", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["info"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["info"] = stdout

        # Get Docker Desktop app info
        cmd = ["defaults", "read", "com.docker.docker"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            info["desktop_settings"] = stdout

        return info

    def fix_permissions(self, path: str) -> Tuple[bool, str]:
        """Fix permissions for Docker access on macOS."""
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"

        # On macOS, Docker socket is typically owned by the current user already
        # Just make sure it's readable/writable
        cmd = ["chmod", "666", path]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            return True, f"Fixed permissions for {path}"
        else:
            return False, f"Failed to fix permissions for {path}: {stderr}"

    def start_on_boot(self, enable: bool = True) -> Tuple[bool, str]:
        """Configure Docker to start on system boot on macOS."""
        # On macOS, this is typically done through the Docker Desktop preferences
        # We can try to use defaults to modify the settings

        if enable:
            cmd = [
                "defaults",
                "write",
                "com.docker.docker",
                "autoStart",
                "-bool",
                "true",
            ]
        else:
            cmd = [
                "defaults",
                "write",
                "com.docker.docker",
                "autoStart",
                "-bool",
                "false",
            ]

        success, stdout, stderr = self.execute_command(cmd)

        if success:
            action = "enabled" if enable else "disabled"
            return True, f"Docker Desktop {action} to start on boot"
        else:
            action = "enable" if enable else "disable"
            return False, f"Failed to {action} Docker Desktop on boot: {stderr}"

    def execute_command(
        self, command: List[str], use_sudo: bool = False
    ) -> Tuple[bool, str, str]:
        """Execute a command on macOS."""
        try:
            if (
                use_sudo
                and not self.platform_info.is_root
                and self.platform_info.has_sudo
            ):
                command = ["sudo"] + command

            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            return process.returncode == 0, process.stdout, process.stderr
        except Exception as e:
            logger.exception(f"Error executing command {command}: {str(e)}")
            return False, "", str(e)

    def get_docker_compose_command(self) -> List[str]:
        """Get the Docker Compose command for macOS."""
        # Check for docker-compose standalone
        if shutil.which("docker-compose"):
            return ["docker-compose"]

        # Check for docker compose plugin
        cmd = ["docker", "compose", "version"]
        success, stdout, stderr = self.execute_command(cmd)

        if success:
            return ["docker", "compose"]

        # Default to docker-compose and let it fail if not found
        return ["docker-compose"]


class WindowsAdapter(PlatformAdapter):
    """Windows-specific platform adapter."""

    def __init__(self):
        """Initialize the Windows adapter."""
        self.platform_info = get_platform_info()

    def restart_docker(self) -> Tuple[bool, str]:
        """Restart Docker on Windows."""
        # On Windows, Docker is typically a desktop application
        # Try to restart the Docker service
        cmd = ["net", "stop", "com.docker.service"]
        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success or "service is not started" in stderr:
            # Wait a moment and then start Docker again
            import time

            time.sleep(2)

            cmd = ["net", "start", "com.docker.service"]
            success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

            if success:
                return True, "Docker service restarted successfully"
            else:
                return False, f"Failed to start Docker service: {stderr}"
        else:
            # Try to restart Docker Desktop
            cmd = ["taskkill", "/f", "/im", "Docker Desktop.exe"]
            success, stdout, stderr = self.execute_command(cmd)

            if success or "not found" in stderr:
                # Wait a moment and then start Docker again
                import time

                time.sleep(2)

                # Use the Windows 'start' command without shell=True
                # For Windows, we need to use the full path to the Docker Desktop executable
                cmd = ["cmd", "/c", "start", "\"Docker Desktop\"", "\"C:\Program Files\Docker\Docker\Docker Desktop.exe\""]
                success, stdout, stderr = self.execute_command(cmd, shell=False)

                if success:
                    return True, "Docker Desktop restarted successfully"
                else:
                    return False, f"Failed to start Docker Desktop: {stderr}"
            else:
                return False, f"Failed to restart Docker: {stderr}"

    def get_docker_info(self) -> Dict[str, Any]:
        """Get Docker information on Windows."""
        info = {}

        # Get Docker version
        cmd = ["docker", "version", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["version"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["version"] = stdout

        # Get Docker info
        cmd = ["docker", "info", "--format", "{{json .}}"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            try:
                import json

                info["info"] = json.loads(stdout)
            except (json.JSONDecodeError, ImportError):
                info["info"] = stdout

        # Get Docker service info
        cmd = ["sc", "query", "com.docker.service"]
        success, stdout, stderr = self.execute_command(cmd)
        if success:
            info["service_info"] = stdout

        return info

    def fix_permissions(self, path: str) -> Tuple[bool, str]:
        """Fix permissions for Docker access on Windows."""
        # On Windows, Docker typically uses named pipes
        # Permissions are usually handled by the Docker service
        # This is a no-op on Windows
        return True, "Permissions are managed by Docker Desktop on Windows"

    def start_on_boot(self, enable: bool = True) -> Tuple[bool, str]:
        """Configure Docker to start on system boot on Windows."""
        # On Windows, this is typically done through the Docker Desktop settings
        # We can try to use the sc command to configure the service

        if enable:
            cmd = ["sc", "config", "com.docker.service", "start=", "auto"]
        else:
            cmd = ["sc", "config", "com.docker.service", "start=", "demand"]

        success, stdout, stderr = self.execute_command(cmd, use_sudo=True)

        if success:
            action = "enabled" if enable else "disabled"
            return True, f"Docker service {action} to start on boot"
        else:
            action = "enable" if enable else "disable"
            return False, f"Failed to {action} Docker service on boot: {stderr}"

    def execute_command(
        self, command: List[str], use_sudo: bool = False, shell: bool = False
    ) -> Tuple[bool, str, str]:
        """Execute a command on Windows."""
        try:
            if use_sudo and not self.platform_info.is_root:
                # On Windows, use runas to elevate privileges
                # This will prompt for UAC confirmation
                command = ["runas", "/user:Administrator"] + command

            if shell:
                # For Windows commands that need shell, use cmd /c instead of shell=True
                if isinstance(command, list):
                    cmd_parts = ["cmd", "/c"] + command
                else:
                    cmd_parts = ["cmd", "/c", command]

                process = subprocess.run(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                    shell=False,
                )
            else:
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )

            return process.returncode == 0, process.stdout, process.stderr
        except Exception as e:
            logger.exception(f"Error executing command {command}: {str(e)}")
            return False, "", str(e)

    def get_docker_compose_command(self) -> List[str]:
        """Get the Docker Compose command for Windows."""
        # Check for docker-compose standalone
        if shutil.which("docker-compose"):
            return ["docker-compose"]

        # Check for docker compose plugin
        cmd = ["docker", "compose", "version"]
        success, stdout, stderr = self.execute_command(cmd)

        if success:
            return ["docker", "compose"]

        # Default to docker-compose and let it fail if not found
        return ["docker-compose"]


def get_platform_adapter() -> PlatformAdapter:
    """
    Get the appropriate platform adapter for the current system.

    Returns:
        PlatformAdapter: Platform-specific adapter
    """
    platform_info = get_platform_info()

    if platform_info.platform_type == PlatformType.LINUX:
        return LinuxAdapter()
    elif platform_info.platform_type == PlatformType.MACOS:
        return MacOSAdapter()
    elif platform_info.platform_type == PlatformType.WINDOWS:
        return WindowsAdapter()
    else:
        raise NotImplementedError(
            f"Unsupported platform: {platform_info.platform_type}"
        )
