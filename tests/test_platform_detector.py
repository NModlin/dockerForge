"""
Tests for the platform detection module.
"""

import unittest
import os
import platform
from unittest.mock import patch, MagicMock

from src.platforms.platform_detector import (
    PlatformType,
    InitSystem,
    PlatformInfo,
    get_platform_info,
)


class TestPlatformDetector(unittest.TestCase):
    """Test cases for the platform detection module."""

    def test_platform_type_enum(self):
        """Test the PlatformType enum."""
        self.assertEqual(PlatformType.LINUX.value, "linux")
        self.assertEqual(PlatformType.WINDOWS.value, "windows")
        self.assertEqual(PlatformType.MACOS.value, "darwin")
        self.assertEqual(PlatformType.UNKNOWN.value, "unknown")

    def test_init_system_enum(self):
        """Test the InitSystem enum."""
        self.assertEqual(InitSystem.SYSTEMD.value, "systemd")
        self.assertEqual(InitSystem.UPSTART.value, "upstart")
        self.assertEqual(InitSystem.SYSVINIT.value, "sysvinit")
        self.assertEqual(InitSystem.LAUNCHD.value, "launchd")
        self.assertEqual(InitSystem.WINDOWS_SERVICE.value, "windows_service")
        self.assertEqual(InitSystem.UNKNOWN.value, "unknown")

    @patch("platform.system")
    def test_detect_platform_type_linux(self, mock_system):
        """Test platform type detection for Linux."""
        mock_system.return_value = "Linux"
        platform_info = PlatformInfo()
        self.assertEqual(platform_info.platform_type, PlatformType.LINUX)

    @patch("platform.system")
    def test_detect_platform_type_windows(self, mock_system):
        """Test platform type detection for Windows."""
        mock_system.return_value = "Windows"
        platform_info = PlatformInfo()
        self.assertEqual(platform_info.platform_type, PlatformType.WINDOWS)

    @patch("platform.system")
    def test_detect_platform_type_macos(self, mock_system):
        """Test platform type detection for macOS."""
        mock_system.return_value = "Darwin"
        platform_info = PlatformInfo()
        self.assertEqual(platform_info.platform_type, PlatformType.MACOS)

    @patch("platform.system")
    def test_detect_platform_type_unknown(self, mock_system):
        """Test platform type detection for unknown platform."""
        mock_system.return_value = "Unknown"
        platform_info = PlatformInfo()
        self.assertEqual(platform_info.platform_type, PlatformType.UNKNOWN)

    @patch("src.platforms.platform_detector.PlatformInfo")
    def test_get_platform_info_singleton(self, mock_platform_info):
        """Test that get_platform_info returns a singleton instance."""
        mock_instance = MagicMock()
        mock_platform_info.return_value = mock_instance

        # First call should create a new instance
        result1 = get_platform_info()
        mock_platform_info.assert_called_once()
        self.assertEqual(result1, mock_instance)

        # Reset the mock to verify it's not called again
        mock_platform_info.reset_mock()

        # Second call should return the existing instance
        result2 = get_platform_info()
        mock_platform_info.assert_not_called()
        self.assertEqual(result2, mock_instance)
        self.assertEqual(result1, result2)

    def test_platform_info_to_dict(self):
        """Test the to_dict method of PlatformInfo."""
        platform_info = PlatformInfo()
        info_dict = platform_info.to_dict()

        # Check that the dictionary contains the expected keys
        expected_keys = [
            "platform_type",
            "distribution",
            "distribution_version",
            "init_system",
            "docker_socket_path",
            "docker_config_path",
            "home_dir",
            "is_root",
            "has_sudo",
        ]
        for key in expected_keys:
            self.assertIn(key, info_dict)

        # Check that the values are of the expected types
        self.assertIsInstance(info_dict["platform_type"], str)
        self.assertIsInstance(info_dict["distribution"], str)
        self.assertIsInstance(info_dict["distribution_version"], str)
        self.assertIsInstance(info_dict["init_system"], str)
        self.assertIsInstance(info_dict["docker_socket_path"], str)
        self.assertIsInstance(info_dict["docker_config_path"], str)
        self.assertIsInstance(info_dict["home_dir"], str)
        self.assertIsInstance(info_dict["is_root"], bool)
        self.assertIsInstance(info_dict["has_sudo"], bool)

    def test_platform_info_str(self):
        """Test the __str__ method of PlatformInfo."""
        platform_info = PlatformInfo()
        info_str = str(platform_info)

        # Check that the string contains the expected information
        self.assertIn("Platform:", info_str)
        self.assertIn("Distribution:", info_str)
        self.assertIn("Init System:", info_str)
        self.assertIn("Docker Socket:", info_str)
        self.assertIn("Docker Config:", info_str)
        self.assertIn("Home Directory:", info_str)
        self.assertIn("Root User:", info_str)
        self.assertIn("Sudo Available:", info_str)


if __name__ == "__main__":
    unittest.main()
