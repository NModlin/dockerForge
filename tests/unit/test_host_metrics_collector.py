"""
DockerForge Unit Tests - Host Metrics Collector
"""

import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
from resource_monitoring.host_metrics_collector import HostMetricsCollector


class TestHostMetricsCollector:
    """Test the HostMetricsCollector class"""

    def setup_method(self):
        """Set up test environment"""
        # Create mock config manager and connection manager
        self.config_manager = MagicMock()
        self.connection_manager = MagicMock()

        # Set up the mock config manager
        self.config_manager.get_config.return_value = {
            "collection_interval": 60,
            "retention_period": 7,
            "metrics_db_path": ":memory:",
        }

        # Set up the mock connection manager
        self.docker_client = MagicMock()
        self.connection_manager.get_client.return_value = self.docker_client

        # Create the host metrics collector
        self.collector = HostMetricsCollector(
            self.config_manager, self.connection_manager
        )

    def test_initialization(self):
        """Test that the host metrics collector can be initialized"""
        assert self.collector is not None
        assert hasattr(self.collector, "config_manager")
        assert hasattr(self.collector, "connection_manager")
        assert hasattr(self.collector, "collection_interval")
        assert hasattr(self.collector, "retention_period")
        assert hasattr(self.collector, "metrics_db_path")
        assert hasattr(self.collector, "is_collecting")
        assert hasattr(self.collector, "collection_thread")

        # Check that the configuration was loaded correctly
        assert self.collector.collection_interval == 60
        assert self.collector.retention_period == 7
        assert self.collector.metrics_db_path == ":memory:"
        assert self.collector.is_collecting is False
        assert self.collector.collection_thread is None

    @patch("resource_monitoring.host_metrics_collector.psutil")
    def test_get_latest_metrics(self, mock_psutil):
        """Test getting the latest metrics"""
        # Set up the mock psutil
        mock_psutil.cpu_percent.return_value = 10.5
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
        mock_psutil.cpu_freq.return_value = MagicMock(current=2500, min=800, max=3500)
        mock_psutil.cpu_times_percent.return_value = MagicMock(
            user=5.0,
            system=3.0,
            idle=92.0,
            nice=0.0,
            iowait=0.0,
            irq=0.0,
            softirq=0.0,
            steal=0.0,
            guest=0.0,
            guest_nice=0.0,
        )
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=16 * 1024 * 1024 * 1024,  # 16 GB
            available=8 * 1024 * 1024 * 1024,  # 8 GB
            used=8 * 1024 * 1024 * 1024,  # 8 GB
            free=8 * 1024 * 1024 * 1024,  # 8 GB
            percent=50.0,
            active=4 * 1024 * 1024 * 1024,  # 4 GB
            inactive=4 * 1024 * 1024 * 1024,  # 4 GB
            buffers=1 * 1024 * 1024 * 1024,  # 1 GB
            cached=2 * 1024 * 1024 * 1024,  # 2 GB
            shared=512 * 1024 * 1024,  # 512 MB
        )
        mock_psutil.swap_memory.return_value = MagicMock(
            total=8 * 1024 * 1024 * 1024,  # 8 GB
            used=1 * 1024 * 1024 * 1024,  # 1 GB
            free=7 * 1024 * 1024 * 1024,  # 7 GB
            percent=12.5,
            sin=0,
            sout=0,
        )
        mock_psutil.disk_partitions.return_value = [
            MagicMock(
                device="/dev/sda1", mountpoint="/", fstype="ext4", opts="rw,relatime"
            )
        ]
        mock_psutil.disk_usage.return_value = MagicMock(
            total=500 * 1024 * 1024 * 1024,  # 500 GB
            used=250 * 1024 * 1024 * 1024,  # 250 GB
            free=250 * 1024 * 1024 * 1024,  # 250 GB
            percent=50.0,
        )
        mock_psutil.disk_io_counters.return_value = MagicMock(
            read_count=1000,
            write_count=500,
            read_bytes=1024 * 1024 * 1024,  # 1 GB
            write_bytes=512 * 1024 * 1024,  # 512 MB
            read_time=1000,
            write_time=500,
            busy_time=1500,
        )
        mock_psutil.net_io_counters.return_value = MagicMock(
            bytes_sent=1024 * 1024 * 1024,  # 1 GB
            bytes_recv=2 * 1024 * 1024 * 1024,  # 2 GB
            packets_sent=10000,
            packets_recv=20000,
            errin=10,
            errout=5,
            dropin=2,
            dropout=1,
        )
        mock_psutil.net_if_stats.return_value = {
            "eth0": MagicMock(isup=True, duplex=2, speed=1000, mtu=1500)
        }
        mock_psutil.net_if_addrs.return_value = {
            "eth0": [
                MagicMock(
                    family=2,
                    address="192.168.1.100",
                    netmask="255.255.255.0",
                    broadcast="192.168.1.255",
                    ptp=None,
                )
            ]
        }
        mock_psutil.net_connections.return_value = [
            MagicMock(status="ESTABLISHED"),
            MagicMock(status="ESTABLISHED"),
            MagicMock(status="LISTEN"),
            MagicMock(status="TIME_WAIT"),
        ]

        # Get the latest metrics
        metrics = self.collector.get_latest_metrics()

        # Check that the metrics were collected correctly
        assert metrics is not None
        assert "timestamp" in metrics
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        assert "network" in metrics

        # Check CPU metrics
        assert metrics["cpu"]["percent"] == 10.5
        assert metrics["cpu"]["count"] == 8
        assert metrics["cpu"]["physical_count"] == 4
        assert metrics["cpu"]["frequency"]["current"] == 2500
        assert metrics["cpu"]["frequency"]["min"] == 800
        assert metrics["cpu"]["frequency"]["max"] == 3500
        assert metrics["cpu"]["times"]["user"] == 5.0
        assert metrics["cpu"]["times"]["system"] == 3.0
        assert metrics["cpu"]["times"]["idle"] == 92.0

        # Check memory metrics
        assert metrics["memory"]["virtual"]["total"] == 16 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["available"] == 8 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["used"] == 8 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["free"] == 8 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["percent"] == 50.0
        assert metrics["memory"]["virtual"]["active"] == 4 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["inactive"] == 4 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["buffers"] == 1 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["cached"] == 2 * 1024 * 1024 * 1024
        assert metrics["memory"]["virtual"]["shared"] == 512 * 1024 * 1024
        assert metrics["memory"]["swap"]["total"] == 8 * 1024 * 1024 * 1024
        assert metrics["memory"]["swap"]["used"] == 1 * 1024 * 1024 * 1024
        assert metrics["memory"]["swap"]["free"] == 7 * 1024 * 1024 * 1024
        assert metrics["memory"]["swap"]["percent"] == 12.5

        # Check disk metrics
        assert "/" in metrics["disk"]["usage"]
        assert metrics["disk"]["usage"]["/"]["total"] == 500 * 1024 * 1024 * 1024
        assert metrics["disk"]["usage"]["/"]["used"] == 250 * 1024 * 1024 * 1024
        assert metrics["disk"]["usage"]["/"]["free"] == 250 * 1024 * 1024 * 1024
        assert metrics["disk"]["usage"]["/"]["percent"] == 50.0
        assert metrics["disk"]["usage"]["/"]["device"] == "/dev/sda1"
        assert metrics["disk"]["usage"]["/"]["fstype"] == "ext4"
        assert metrics["disk"]["io"]["read_count"] == 1000
        assert metrics["disk"]["io"]["write_count"] == 500
        assert metrics["disk"]["io"]["read_bytes"] == 1024 * 1024 * 1024
        assert metrics["disk"]["io"]["write_bytes"] == 512 * 1024 * 1024
        assert metrics["disk"]["io"]["read_time"] == 1000
        assert metrics["disk"]["io"]["write_time"] == 500
        assert metrics["disk"]["io"]["busy_time"] == 1500

        # Check network metrics
        assert metrics["network"]["io"]["bytes_sent"] == 1024 * 1024 * 1024
        assert metrics["network"]["io"]["bytes_recv"] == 2 * 1024 * 1024 * 1024
        assert metrics["network"]["io"]["packets_sent"] == 10000
        assert metrics["network"]["io"]["packets_recv"] == 20000
        assert metrics["network"]["io"]["errin"] == 10
        assert metrics["network"]["io"]["errout"] == 5
        assert metrics["network"]["io"]["dropin"] == 2
        assert metrics["network"]["io"]["dropout"] == 1
        assert "eth0" in metrics["network"]["interfaces"]
        assert metrics["network"]["interfaces"]["eth0"]["isup"] is True
        assert metrics["network"]["interfaces"]["eth0"]["duplex"] == 2
        assert metrics["network"]["interfaces"]["eth0"]["speed"] == 1000
        assert metrics["network"]["interfaces"]["eth0"]["mtu"] == 1500
        assert len(metrics["network"]["interfaces"]["eth0"]["addresses"]) == 1
        assert metrics["network"]["interfaces"]["eth0"]["addresses"][0]["family"] == 2
        assert (
            metrics["network"]["interfaces"]["eth0"]["addresses"][0]["address"]
            == "192.168.1.100"
        )
        assert (
            metrics["network"]["interfaces"]["eth0"]["addresses"][0]["netmask"]
            == "255.255.255.0"
        )
        assert (
            metrics["network"]["interfaces"]["eth0"]["addresses"][0]["broadcast"]
            == "192.168.1.255"
        )
        assert metrics["network"]["connections"]["ESTABLISHED"] == 2
        assert metrics["network"]["connections"]["LISTEN"] == 1
        assert metrics["network"]["connections"]["TIME_WAIT"] == 1

    @patch("resource_monitoring.host_metrics_collector.threading.Thread")
    def test_start_stop_collection(self, mock_thread):
        """Test starting and stopping metrics collection"""
        # Set up the mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Start collection
        self.collector.start_collection()

        # Check that collection was started
        assert self.collector.is_collecting is True
        assert self.collector.collection_thread is not None
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

        # Stop collection
        self.collector.stop_collection()

        # Check that collection was stopped
        assert self.collector.is_collecting is False

    @patch("resource_monitoring.host_metrics_collector.sqlite3")
    def test_get_metrics_history(self, mock_sqlite3):
        """Test getting metrics history"""
        # Set up the mock sqlite3
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_sqlite3.connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1617235200, '{"cpu_percent": 10.5, "memory_percent": 50.0}'),
            (1617235260, '{"cpu_percent": 15.2, "memory_percent": 55.3}'),
            (1617235320, '{"cpu_percent": 20.1, "memory_percent": 60.7}'),
        ]

        # Get metrics history
        history = self.collector.get_metrics_history(
            "cpu", "2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"
        )

        # Check that the history was retrieved correctly
        assert history is not None
        assert len(history) == 3
        assert history[0]["timestamp"] == 1617235200
        assert history[0]["data"]["cpu_percent"] == 10.5
        assert history[1]["timestamp"] == 1617235260
        assert history[1]["data"]["cpu_percent"] == 15.2
        assert history[2]["timestamp"] == 1617235320
        assert history[2]["data"]["cpu_percent"] == 20.1

    @patch("resource_monitoring.host_metrics_collector.platform")
    @patch("resource_monitoring.host_metrics_collector.psutil")
    def test_get_system_info(self, mock_psutil, mock_platform):
        """Test getting system information"""
        # Set up the mock platform
        mock_platform.platform.return_value = (
            "Linux-5.4.0-42-generic-x86_64-with-glibc2.29"
        )
        mock_platform.system.return_value = "Linux"
        mock_platform.release.return_value = "5.4.0-42-generic"
        mock_platform.version.return_value = (
            "#46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020"
        )
        mock_platform.architecture.return_value = ("64bit", "ELF")
        mock_platform.processor.return_value = "x86_64"
        mock_platform.node.return_value = "test-host"
        mock_platform.python_version.return_value = "3.8.5"

        # Set up the mock psutil
        mock_psutil.cpu_count.return_value = 8
        mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
        mock_psutil.virtual_memory.return_value = MagicMock(
            total=16 * 1024 * 1024 * 1024
        )
        mock_psutil.boot_time.return_value = 1617235200

        # Set up the mock docker client
        self.docker_client.info.return_value = {
            "ServerVersion": "20.10.7",
            "Containers": 10,
            "ContainersRunning": 5,
            "ContainersPaused": 0,
            "ContainersStopped": 5,
            "Images": 20,
            "Driver": "overlay2",
            "DriverStatus": [["Backing Filesystem", "extfs"]],
            "LoggingDriver": "json-file",
            "CgroupDriver": "systemd",
            "KernelVersion": "5.4.0-42-generic",
            "OperatingSystem": "Ubuntu 20.04.2 LTS",
            "OSType": "linux",
            "Architecture": "x86_64",
            "NCPU": 8,
            "MemTotal": 16 * 1024 * 1024 * 1024,
            "DockerRootDir": "/var/lib/docker",
            "IndexServerAddress": "https://index.docker.io/v1/",
            "RegistryConfig": {
                "AllowNondistributableArtifactsCIDRs": [],
                "AllowNondistributableArtifactsHostnames": [],
                "InsecureRegistryCIDRs": ["127.0.0.0/8"],
                "IndexConfigs": {
                    "docker.io": {
                        "Name": "docker.io",
                        "Mirrors": [],
                        "Secure": True,
                        "Official": True,
                    }
                },
                "Mirrors": [],
            },
        }

        # Get system information
        system_info = self.collector.get_system_info()

        # Check that the system information was retrieved correctly
        assert system_info is not None
        assert system_info["platform"] == "Linux-5.4.0-42-generic-x86_64-with-glibc2.29"
        assert system_info["system"] == "Linux"
        assert system_info["release"] == "5.4.0-42-generic"
        assert system_info["version"] == "#46-Ubuntu SMP Fri Jul 10 00:24:02 UTC 2020"
        assert system_info["architecture"] == "64bit"
        assert system_info["processor"] == "x86_64"
        assert system_info["hostname"] == "test-host"
        assert system_info["python_version"] == "3.8.5"
        assert system_info["cpu_count"] == 8
        assert system_info["physical_cpu_count"] == 4
        assert system_info["memory_total"] == 16 * 1024 * 1024 * 1024
        assert system_info["boot_time"] == "1970-01-19T17:00:35.200000"
        assert system_info["docker"]["version"] == "20.10.7"
        assert system_info["docker"]["containers"] == 10
        assert system_info["docker"]["running"] == 5
        assert system_info["docker"]["paused"] == 0
        assert system_info["docker"]["stopped"] == 5
        assert system_info["docker"]["images"] == 20
        assert system_info["docker"]["driver"] == "overlay2"
        assert system_info["docker"]["storage_driver"] == "overlay2"
        assert system_info["docker"]["logging_driver"] == "json-file"
        assert system_info["docker"]["cgroup_driver"] == "systemd"
        assert system_info["docker"]["kernel_version"] == "5.4.0-42-generic"
        assert system_info["docker"]["operating_system"] == "Ubuntu 20.04.2 LTS"
        assert system_info["docker"]["os_type"] == "linux"
        assert system_info["docker"]["architecture"] == "x86_64"
        assert system_info["docker"]["cpus"] == 8
        assert system_info["docker"]["memory"] == 16 * 1024 * 1024 * 1024
        assert system_info["docker"]["docker_root_dir"] == "/var/lib/docker"
        assert (
            system_info["docker"]["index_server_address"]
            == "https://index.docker.io/v1/"
        )
        assert system_info["docker"]["registry_config"] is not None


if __name__ == "__main__":
    pytest.main(["-v", __file__])
