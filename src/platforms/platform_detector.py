"""
Platform detection and adaptation module for DockerForge.

This module provides functionality to detect the operating system and
adapt to platform-specific requirements.
"""

import os
import platform
import subprocess
import sys
import ctypes
from enum import Enum
from typing import Dict, Optional, Tuple, List

# Try to import distro for Linux distribution detection
try:
    import distro
except ImportError:
    distro = None


class PlatformType(Enum):
    """Enum representing supported platform types."""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "darwin"
    UNKNOWN = "unknown"


class InitSystem(Enum):
    """Enum representing supported init systems."""
    SYSTEMD = "systemd"
    UPSTART = "upstart"
    SYSVINIT = "sysvinit"
    LAUNCHD = "launchd"
    WINDOWS_SERVICE = "windows_service"
    UNKNOWN = "unknown"


class PlatformInfo:
    """Class representing platform information."""

    def __init__(self):
        """Initialize platform information."""
        self.platform_type = self._detect_platform_type()
        self.distribution = self._detect_distribution()
        self.distribution_version = self._detect_distribution_version()
        self.init_system = self._detect_init_system()
        self.docker_socket_path = self._get_docker_socket_path()
        self.docker_config_path = self._get_docker_config_path()
        self.home_dir = self._get_home_dir()
        self.is_root = self._is_root()
        self.has_sudo = self._has_sudo()

    def _detect_platform_type(self) -> PlatformType:
        """Detect the platform type."""
        system = platform.system().lower()
        if system == "linux":
            return PlatformType.LINUX
        elif system == "windows":
            return PlatformType.WINDOWS
        elif system == "darwin":
            return PlatformType.MACOS
        else:
            return PlatformType.UNKNOWN

    def _detect_distribution(self) -> str:
        """Detect the Linux distribution."""
        if self.platform_type == PlatformType.LINUX:
            if distro:
                return distro.id()
            else:
                # Fallback method if distro is not available
                try:
                    with open("/etc/os-release") as f:
                        for line in f:
                            if line.startswith("ID="):
                                return line.split("=")[1].strip().strip('"')
                except (FileNotFoundError, IOError):
                    pass
                
                # Try lsb_release command
                try:
                    return subprocess.check_output(
                        ["lsb_release", "-is"], 
                        universal_newlines=True
                    ).strip().lower()
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return "unknown"
        elif self.platform_type == PlatformType.MACOS:
            return "macos"
        elif self.platform_type == PlatformType.WINDOWS:
            return "windows"
        else:
            return "unknown"

    def _detect_distribution_version(self) -> str:
        """Detect the Linux distribution version."""
        if self.platform_type == PlatformType.LINUX:
            if distro:
                return distro.version()
            else:
                # Fallback method if distro is not available
                try:
                    with open("/etc/os-release") as f:
                        for line in f:
                            if line.startswith("VERSION_ID="):
                                return line.split("=")[1].strip().strip('"')
                except (FileNotFoundError, IOError):
                    pass
                
                # Try lsb_release command
                try:
                    return subprocess.check_output(
                        ["lsb_release", "-rs"], 
                        universal_newlines=True
                    ).strip()
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
                
                return "unknown"
        elif self.platform_type == PlatformType.MACOS:
            return platform.mac_ver()[0]
        elif self.platform_type == PlatformType.WINDOWS:
            return platform.version()
        else:
            return "unknown"

    def _detect_init_system(self) -> InitSystem:
        """Detect the init system."""
        if self.platform_type == PlatformType.LINUX:
            # Check for systemd
            if os.path.exists("/run/systemd/system") or os.path.exists("/sys/fs/cgroup/systemd"):
                return InitSystem.SYSTEMD
            
            # Check for Upstart
            if os.path.exists("/sbin/initctl") and os.path.exists("/etc/init"):
                return InitSystem.UPSTART
            
            # Assume SysVinit if neither systemd nor Upstart
            if os.path.exists("/etc/init.d"):
                return InitSystem.SYSVINIT
            
            return InitSystem.UNKNOWN
        
        elif self.platform_type == PlatformType.MACOS:
            return InitSystem.LAUNCHD
        
        elif self.platform_type == PlatformType.WINDOWS:
            return InitSystem.WINDOWS_SERVICE
        
        return InitSystem.UNKNOWN

    def _get_docker_socket_path(self) -> str:
        """Get the Docker socket path."""
        if self.platform_type == PlatformType.LINUX or self.platform_type == PlatformType.MACOS:
            # Common Docker socket paths
            socket_paths = [
                "/var/run/docker.sock",
                "/run/docker.sock",
                os.path.expanduser("~/.docker/run/docker.sock"),
            ]
            
            for path in socket_paths:
                if os.path.exists(path):
                    return path
            
            # Default path even if it doesn't exist
            return "/var/run/docker.sock"
        
        elif self.platform_type == PlatformType.WINDOWS:
            # Windows uses named pipes
            return "//./pipe/docker_engine"
        
        return ""

    def _get_docker_config_path(self) -> str:
        """Get the Docker configuration path."""
        if self.platform_type == PlatformType.LINUX:
            return "/etc/docker"
        elif self.platform_type == PlatformType.MACOS:
            return os.path.expanduser("~/Library/Containers/com.docker.docker/Data")
        elif self.platform_type == PlatformType.WINDOWS:
            return os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Docker")
        return ""

    def _get_home_dir(self) -> str:
        """Get the user's home directory."""
        return os.path.expanduser("~")

    def _is_root(self) -> bool:
        """Check if the current user is root."""
        if self.platform_type == PlatformType.WINDOWS:
            # On Windows, check for admin privileges
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except (AttributeError, ImportError):
                return False
        else:
            # On Unix-like systems, check if UID is 0
            return os.geteuid() == 0

    def _has_sudo(self) -> bool:
        """Check if sudo is available."""
        if self.platform_type == PlatformType.WINDOWS:
            return False
        
        try:
            subprocess.run(
                ["sudo", "-n", "true"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def to_dict(self) -> Dict:
        """Convert platform information to a dictionary."""
        return {
            "platform_type": self.platform_type.value,
            "distribution": self.distribution,
            "distribution_version": self.distribution_version,
            "init_system": self.init_system.value,
            "docker_socket_path": self.docker_socket_path,
            "docker_config_path": self.docker_config_path,
            "home_dir": self.home_dir,
            "is_root": self.is_root,
            "has_sudo": self.has_sudo,
        }

    def __str__(self) -> str:
        """Return a string representation of platform information."""
        return (
            f"Platform: {self.platform_type.value}\n"
            f"Distribution: {self.distribution} {self.distribution_version}\n"
            f"Init System: {self.init_system.value}\n"
            f"Docker Socket: {self.docker_socket_path}\n"
            f"Docker Config: {self.docker_config_path}\n"
            f"Home Directory: {self.home_dir}\n"
            f"Root User: {self.is_root}\n"
            f"Sudo Available: {self.has_sudo}"
        )


# Singleton instance of PlatformInfo
_platform_info = None


def get_platform_info() -> PlatformInfo:
    """Get platform information (singleton)."""
    global _platform_info
    if _platform_info is None:
        _platform_info = PlatformInfo()
    return _platform_info
