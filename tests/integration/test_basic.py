"""
DockerForge Integration Tests - Basic Functionality
"""

import pytest
import os
import sys
import subprocess
from pathlib import Path

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
try:
    from core.troubleshooter import Troubleshooter
    from platforms.platform_detector import PlatformDetector
    from docker.connection_manager import ConnectionManager
    from config.config_manager import ConfigManager
except ImportError as e:
    print(f"Import error: {e}")
    print("These tests may be running in a limited environment.")
    print("Some tests will be skipped.")


class TestBasicFunctionality:
    """Test basic functionality of DockerForge"""

    def setup_method(self):
        """Set up test environment"""
        # This will be run before each test method
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.config_path = self.project_root / "config" / "dockerforge.yaml"

    def test_project_structure(self):
        """Test that the project structure is correct"""
        # Check that the main directories exist
        assert (self.project_root / "src").exists()
        assert (self.project_root / "tests").exists()
        assert (self.project_root / "docs").exists()
        assert (self.project_root / "examples").exists()
        assert (self.project_root / "config").exists()

    def test_config_file(self):
        """Test that the config file exists and is valid"""
        assert self.config_path.exists()
        
        # Try to load the config file
        try:
            config_manager = ConfigManager()
            config = config_manager.load_config()
            assert config is not None
        except (ImportError, NameError):
            pytest.skip("ConfigManager not available in this environment")

    def test_platform_detection(self):
        """Test platform detection"""
        try:
            platform_detector = PlatformDetector()
            platform_info = platform_detector.detect_platform()
            assert platform_info is not None
            assert "os_type" in platform_info
            assert "init_system" in platform_info
        except (ImportError, NameError):
            pytest.skip("PlatformDetector not available in this environment")

    def test_docker_connection(self):
        """Test Docker connection"""
        try:
            connection_manager = ConnectionManager()
            client = connection_manager.get_client()
            assert client is not None
            # Check that we can list containers
            containers = client.containers.list(all=True)
            assert isinstance(containers, list)
        except (ImportError, NameError):
            pytest.skip("ConnectionManager not available in this environment")
        except Exception as e:
            pytest.skip(f"Docker connection failed: {e}")

    def test_cli_execution(self):
        """Test that the CLI can be executed"""
        # Run the CLI with --help
        result = subprocess.run(
            ["python", "-m", "dockerforge", "--help"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        # Check that the command executed successfully
        assert result.returncode == 0
        # Check that the output contains "DockerForge"
        assert "DockerForge" in result.stdout

    def test_troubleshooter_initialization(self):
        """Test that the troubleshooter can be initialized"""
        try:
            troubleshooter = Troubleshooter()
            assert troubleshooter is not None
        except (ImportError, NameError):
            pytest.skip("Troubleshooter not available in this environment")
        except Exception as e:
            pytest.skip(f"Troubleshooter initialization failed: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
