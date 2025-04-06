"""
Docker service for the DockerForge Web UI.

This module provides the Docker services for the DockerForge Web UI.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import docker
from docker.errors import APIError, DockerException, NotFound

# Configure logging
logger = logging.getLogger(__name__)

# Docker client
try:
    client = docker.from_env()
except DockerException as e:
    logger.error(f"Failed to connect to Docker: {e}")
    client = None


def get_docker_client():
    """
    Get Docker client.
    """
    global client
    if client is None:
        try:
            client = docker.from_env()
        except DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    return client


def get_system_info() -> Dict[str, Any]:
    """
    Get Docker system information.
    """
    try:
        client = get_docker_client()
        info = client.info()
        version = client.version()

        return {
            "version": version.get("Version", "Unknown"),
            "api_version": version.get("ApiVersion", "Unknown"),
            "os": info.get("OperatingSystem", "Unknown"),
            "architecture": info.get("Architecture", "Unknown"),
            "kernel_version": info.get("KernelVersion", "Unknown"),
            "cpu_count": info.get("NCPU", 0),
            "memory_total": info.get("MemTotal", 0),
            "containers_running": info.get("ContainersRunning", 0),
            "containers_paused": info.get("ContainersPaused", 0),
            "containers_stopped": info.get("ContainersStopped", 0),
            "images_count": info.get("Images", 0),
            "docker_root_dir": info.get("DockerRootDir", "Unknown"),
            "storage_driver": info.get("Driver", "Unknown"),
            "server_version": info.get("ServerVersion", "Unknown"),
        }
    except DockerException as e:
        logger.error(f"Failed to get Docker system information: {e}")
        raise


def get_containers(
    all: bool = True, filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Get all containers.
    """
    try:
        client = get_docker_client()
        containers = client.containers.list(all=all, filters=filters)

        result = []
        for container in containers:
            # Get container details
            container_dict = {
                "id": container.id,
                "name": container.name,
                "image": (
                    container.image.tags[0]
                    if container.image.tags
                    else container.image.id
                ),
                "status": container.status,
                "created_at": datetime.fromtimestamp(
                    container.attrs["Created"]
                ).isoformat(),
                "started_at": None,
                "finished_at": None,
                "health_status": None,
                "ip_address": None,
                "command": container.attrs.get("Config", {}).get("Cmd", []),
                "entrypoint": container.attrs.get("Config", {}).get("Entrypoint", []),
                "environment": parse_env(
                    container.attrs.get("Config", {}).get("Env", [])
                ),
                "ports": parse_ports(
                    container.attrs.get("NetworkSettings", {}).get("Ports", {})
                ),
                "volumes": parse_volumes(container.attrs.get("Mounts", [])),
                "network": list(
                    container.attrs.get("NetworkSettings", {})
                    .get("Networks", {})
                    .keys()
                ),
                "restart_policy": container.attrs.get("HostConfig", {})
                .get("RestartPolicy", {})
                .get("Name", ""),
                "labels": container.attrs.get("Config", {}).get("Labels", {}),
            }

            # Get state information
            state = container.attrs.get("State", {})
            if state.get("StartedAt"):
                container_dict["started_at"] = state.get("StartedAt")
            if (
                state.get("FinishedAt")
                and state.get("FinishedAt") != "0001-01-01T00:00:00Z"
            ):
                container_dict["finished_at"] = state.get("FinishedAt")

            # Get health status
            health = state.get("Health", {})
            if health:
                container_dict["health_status"] = health.get("Status")

            # Get IP address
            networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
            if networks:
                for network_name, network_config in networks.items():
                    if network_config.get("IPAddress"):
                        container_dict["ip_address"] = network_config.get("IPAddress")
                        break

            # Get resource usage if container is running
            if container.status == "running":
                try:
                    stats = container.stats(stream=False)
                    container_dict["resource_usage"] = parse_stats(stats)
                except:
                    container_dict["resource_usage"] = None

            result.append(container_dict)

        return result
    except DockerException as e:
        logger.error(f"Failed to get containers: {e}")
        raise


def get_container(container_id: str) -> Dict[str, Any]:
    """
    Get a container by ID.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)

        # Get container details
        container_dict = {
            "id": container.id,
            "name": container.name,
            "image": (
                container.image.tags[0] if container.image.tags else container.image.id
            ),
            "status": container.status,
            "created_at": datetime.fromtimestamp(
                container.attrs["Created"]
            ).isoformat(),
            "started_at": None,
            "finished_at": None,
            "health_status": None,
            "ip_address": None,
            "command": container.attrs.get("Config", {}).get("Cmd", []),
            "entrypoint": container.attrs.get("Config", {}).get("Entrypoint", []),
            "environment": parse_env(container.attrs.get("Config", {}).get("Env", [])),
            "ports": parse_ports(
                container.attrs.get("NetworkSettings", {}).get("Ports", {})
            ),
            "volumes": parse_volumes(container.attrs.get("Mounts", [])),
            "network": list(
                container.attrs.get("NetworkSettings", {}).get("Networks", {}).keys()
            ),
            "restart_policy": container.attrs.get("HostConfig", {})
            .get("RestartPolicy", {})
            .get("Name", ""),
            "labels": container.attrs.get("Config", {}).get("Labels", {}),
        }

        # Get state information
        state = container.attrs.get("State", {})
        if state.get("StartedAt"):
            container_dict["started_at"] = state.get("StartedAt")
        if (
            state.get("FinishedAt")
            and state.get("FinishedAt") != "0001-01-01T00:00:00Z"
        ):
            container_dict["finished_at"] = state.get("FinishedAt")

        # Get health status
        health = state.get("Health", {})
        if health:
            container_dict["health_status"] = health.get("Status")

        # Get IP address
        networks = container.attrs.get("NetworkSettings", {}).get("Networks", {})
        if networks:
            for network_name, network_config in networks.items():
                if network_config.get("IPAddress"):
                    container_dict["ip_address"] = network_config.get("IPAddress")
                    break

        # Get resource usage if container is running
        if container.status == "running":
            try:
                stats = container.stats(stream=False)
                container_dict["resource_usage"] = parse_stats(stats)
            except:
                container_dict["resource_usage"] = None

        return container_dict
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to get container: {e}")
        raise


def create_container(container_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new container.
    """
    try:
        client = get_docker_client()

        # Prepare container parameters
        params = {
            "image": container_data["image"],
            "name": container_data["name"],
            "detach": True,
        }

        # Add optional parameters
        if container_data.get("command"):
            params["command"] = container_data["command"]

        if container_data.get("entrypoint"):
            params["entrypoint"] = container_data["entrypoint"]

        if container_data.get("environment"):
            params["environment"] = container_data["environment"]

        if container_data.get("ports"):
            ports = {}
            for port in container_data["ports"]:
                container_port = f"{port['container_port']}/{port['protocol']}"
                host_port = (port.get("host_ip", ""), port["host_port"])
                ports[container_port] = host_port
            params["ports"] = ports

        if container_data.get("volumes"):
            volumes = {}
            for volume in container_data["volumes"]:
                host_path = volume["host_path"]
                container_path = volume["container_path"]
                mode = volume.get("mode", "rw")
                volumes[host_path] = {"bind": container_path, "mode": mode}
            params["volumes"] = volumes

        if container_data.get("network"):
            params["network"] = container_data["network"]

        if container_data.get("restart_policy"):
            params["restart_policy"] = {"Name": container_data["restart_policy"]}

        if container_data.get("labels"):
            params["labels"] = container_data["labels"]

        # Add hostname if provided
        if container_data.get("hostname"):
            params["hostname"] = container_data["hostname"]

        # Add DNS servers if provided
        if container_data.get("dns"):
            params["dns"] = container_data["dns"]

        # Add DNS search domains if provided
        if container_data.get("dns_search"):
            params["dns_search"] = container_data["dns_search"]

        # Add CPU limit if provided
        if container_data.get("cpu_limit"):
            if not params.get("host_config"):
                params["host_config"] = {}
            params["host_config"]["cpu_quota"] = int(
                container_data["cpu_limit"] * 100000
            )
            params["host_config"]["cpu_period"] = 100000

        # Add memory limit if provided
        if container_data.get("memory_limit"):
            if not params.get("host_config"):
                params["host_config"] = {}
            params["host_config"]["mem_limit"] = container_data["memory_limit"]

        # Create container
        container = client.containers.create(**params)

        # Start container if requested
        if container_data.get("start", False):
            container.start()

        # Get container details
        return get_container(container.id)
    except DockerException as e:
        logger.error(f"Failed to create container: {e}")
        raise


def start_container(container_id: str) -> Dict[str, Any]:
    """
    Start a container.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.start()
        return get_container(container_id)
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to start container: {e}")
        raise


def stop_container(container_id: str) -> Dict[str, Any]:
    """
    Stop a container.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.stop()
        return get_container(container_id)
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to stop container: {e}")
        raise


def restart_container(container_id: str) -> Dict[str, Any]:
    """
    Restart a container.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.restart()
        return get_container(container_id)
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to restart container: {e}")
        raise


def delete_container(container_id: str, force: bool = False) -> bool:
    """
    Delete a container.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        container.remove(force=force)
        return True
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return False
    except DockerException as e:
        logger.error(f"Failed to delete container: {e}")
        raise


def get_container_logs(container_id: str, tail: int = 100) -> List[str]:
    """
    Get container logs.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        logs = container.logs(tail=tail, timestamps=True).decode("utf-8").splitlines()
        return logs
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return []
    except DockerException as e:
        logger.error(f"Failed to get container logs: {e}")
        raise


def inspect_container(container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed inspection data for a container by ID.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)

        # Return the raw container attributes which contain all inspect data
        return container.attrs
    except NotFound:
        logger.error(f"Container not found: {container_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to inspect container: {e}")
        raise


def get_images() -> List[Dict[str, Any]]:
    """
    Get all images.
    """
    try:
        client = get_docker_client()
        images = client.images.list()

        result = []
        for image in images:
            # Get image details
            image_dict = {
                "id": image.id,
                "tags": image.tags,
                "short_id": image.short_id,
                "created_at": datetime.fromtimestamp(
                    image.attrs["Created"]
                ).isoformat(),
                "size": image.attrs["Size"],
                "labels": image.attrs.get("Config", {}).get("Labels", {}),
            }

            result.append(image_dict)

        return result
    except DockerException as e:
        logger.error(f"Failed to get images: {e}")
        raise


def get_image(image_id: str) -> Dict[str, Any]:
    """
    Get an image by ID.
    """
    try:
        client = get_docker_client()
        image = client.images.get(image_id)

        # Get image details
        image_dict = {
            "id": image.id,
            "tags": image.tags,
            "short_id": image.short_id,
            "created_at": datetime.fromtimestamp(image.attrs["Created"]).isoformat(),
            "size": image.attrs["Size"],
            "labels": image.attrs.get("Config", {}).get("Labels", {}),
            "architecture": image.attrs.get("Architecture"),
            "os": image.attrs.get("Os"),
            "author": image.attrs.get("Author"),
            "comment": image.attrs.get("Comment"),
            "config": image.attrs.get("Config", {}),
            "history": image.history(),
        }

        return image_dict
    except NotFound:
        logger.error(f"Image not found: {image_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to get image: {e}")
        raise


def pull_image(image_name: str) -> Dict[str, Any]:
    """
    Pull an image.
    """
    try:
        client = get_docker_client()
        image = client.images.pull(image_name)

        # Get image details
        image_dict = {
            "id": image.id,
            "tags": image.tags,
            "short_id": image.short_id,
            "created_at": datetime.fromtimestamp(image.attrs["Created"]).isoformat(),
            "size": image.attrs["Size"],
            "labels": image.attrs.get("Config", {}).get("Labels", {}),
        }

        return image_dict
    except DockerException as e:
        logger.error(f"Failed to pull image: {e}")
        raise


def delete_image(image_id: str, force: bool = False) -> bool:
    """
    Delete an image.
    """
    try:
        client = get_docker_client()
        client.images.remove(image_id, force=force)
        return True
    except NotFound:
        logger.error(f"Image not found: {image_id}")
        return False
    except DockerException as e:
        logger.error(f"Failed to delete image: {e}")
        raise


def get_volumes() -> List[Dict[str, Any]]:
    """
    Get all volumes.
    """
    try:
        client = get_docker_client()
        volumes = client.volumes.list()

        result = []
        for volume in volumes:
            # Get volume details
            volume_dict = {
                "id": volume.id,
                "name": volume.name,
                "driver": volume.attrs["Driver"],
                "mountpoint": volume.attrs["Mountpoint"],
                "created_at": volume.attrs["CreatedAt"],
                "status": "available",  # Docker API doesn't provide volume status
                "labels": volume.attrs.get("Labels", {}),
                "options": volume.attrs.get("Options", {}),
                "scope": volume.attrs.get("Scope", "local"),
            }

            result.append(volume_dict)

        return result
    except DockerException as e:
        logger.error(f"Failed to get volumes: {e}")
        raise


def get_volume(volume_id: str) -> Dict[str, Any]:
    """
    Get a volume by ID.
    """
    try:
        client = get_docker_client()
        volume = client.volumes.get(volume_id)

        # Get volume details
        volume_dict = {
            "id": volume.id,
            "name": volume.name,
            "driver": volume.attrs["Driver"],
            "mountpoint": volume.attrs["Mountpoint"],
            "created_at": volume.attrs["CreatedAt"],
            "status": "available",  # Docker API doesn't provide volume status
            "labels": volume.attrs.get("Labels", {}),
            "options": volume.attrs.get("Options", {}),
            "scope": volume.attrs.get("Scope", "local"),
        }

        return volume_dict
    except NotFound:
        logger.error(f"Volume not found: {volume_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to get volume: {e}")
        raise


def create_volume(volume_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new volume.
    """
    try:
        client = get_docker_client()

        # Prepare volume parameters
        params = {
            "name": volume_data["name"],
        }

        # Add optional parameters
        if volume_data.get("driver"):
            params["driver"] = volume_data["driver"]

        if volume_data.get("driver_opts"):
            params["driver_opts"] = volume_data["driver_opts"]

        if volume_data.get("labels"):
            params["labels"] = volume_data["labels"]

        # Create volume
        volume = client.volumes.create(**params)

        # Get volume details
        volume_dict = {
            "id": volume.id,
            "name": volume.name,
            "driver": volume.attrs["Driver"],
            "mountpoint": volume.attrs["Mountpoint"],
            "created_at": volume.attrs["CreatedAt"],
            "status": "available",  # Docker API doesn't provide volume status
            "labels": volume.attrs.get("Labels", {}),
            "options": volume.attrs.get("Options", {}),
            "scope": volume.attrs.get("Scope", "local"),
        }

        return volume_dict
    except DockerException as e:
        logger.error(f"Failed to create volume: {e}")
        raise


def delete_volume(volume_id: str, force: bool = False) -> bool:
    """
    Delete a volume.
    """
    try:
        client = get_docker_client()
        volume = client.volumes.get(volume_id)
        volume.remove(force=force)
        return True
    except NotFound:
        logger.error(f"Volume not found: {volume_id}")
        return False
    except DockerException as e:
        logger.error(f"Failed to delete volume: {e}")
        raise


def get_networks() -> List[Dict[str, Any]]:
    """
    Get all networks.
    """
    try:
        client = get_docker_client()
        networks = client.networks.list()

        result = []
        for network in networks:
            # Get network details
            network_dict = {
                "id": network.id,
                "name": network.name,
                "driver": network.attrs["Driver"],
                "scope": network.attrs["Scope"],
                "internal": network.attrs["Internal"],
                "ipam": network.attrs.get("IPAM", {}),
                "options": network.attrs.get("Options", {}),
                "labels": network.attrs.get("Labels", {}),
                "containers": list(network.attrs.get("Containers", {}).keys()),
            }

            result.append(network_dict)

        return result
    except DockerException as e:
        logger.error(f"Failed to get networks: {e}")
        raise


def get_network(network_id: str) -> Dict[str, Any]:
    """
    Get a network by ID.
    """
    try:
        client = get_docker_client()
        network = client.networks.get(network_id)

        # Get network details
        network_dict = {
            "id": network.id,
            "name": network.name,
            "driver": network.attrs["Driver"],
            "scope": network.attrs["Scope"],
            "internal": network.attrs["Internal"],
            "ipam": network.attrs.get("IPAM", {}),
            "options": network.attrs.get("Options", {}),
            "labels": network.attrs.get("Labels", {}),
            "containers": list(network.attrs.get("Containers", {}).keys()),
        }

        return network_dict
    except NotFound:
        logger.error(f"Network not found: {network_id}")
        return None
    except DockerException as e:
        logger.error(f"Failed to get network: {e}")
        raise


def create_network(network_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new network.
    """
    try:
        client = get_docker_client()

        # Prepare network parameters
        params = {
            "name": network_data["name"],
        }

        # Add optional parameters
        if network_data.get("driver"):
            params["driver"] = network_data["driver"]

        if network_data.get("options"):
            params["options"] = network_data["options"]

        if network_data.get("ipam"):
            params["ipam"] = network_data["ipam"]

        if network_data.get("internal") is not None:
            params["internal"] = network_data["internal"]

        if network_data.get("labels"):
            params["labels"] = network_data["labels"]

        # Create network
        network = client.networks.create(**params)

        # Get network details
        network_dict = {
            "id": network.id,
            "name": network.name,
            "driver": network.attrs["Driver"],
            "scope": network.attrs["Scope"],
            "internal": network.attrs["Internal"],
            "ipam": network.attrs.get("IPAM", {}),
            "options": network.attrs.get("Options", {}),
            "labels": network.attrs.get("Labels", {}),
            "containers": list(network.attrs.get("Containers", {}).keys()),
        }

        return network_dict
    except DockerException as e:
        logger.error(f"Failed to create network: {e}")
        raise


def delete_network(network_id: str) -> bool:
    """
    Delete a network.
    """
    try:
        client = get_docker_client()
        network = client.networks.get(network_id)
        network.remove()
        return True
    except NotFound:
        logger.error(f"Network not found: {network_id}")
        return False
    except DockerException as e:
        logger.error(f"Failed to delete network: {e}")
        raise


def connect_container_to_network(
    container_id: str, network_id: str, aliases: Optional[List[str]] = None
) -> bool:
    """
    Connect a container to a network.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        network = client.networks.get(network_id)

        # Prepare parameters
        params = {}
        if aliases:
            params["aliases"] = aliases

        # Connect container to network
        network.connect(container, **params)
        return True
    except NotFound as e:
        logger.error(f"Container or network not found: {e}")
        return False
    except DockerException as e:
        logger.error(f"Failed to connect container to network: {e}")
        raise


def disconnect_container_from_network(container_id: str, network_id: str) -> bool:
    """
    Disconnect a container from a network.
    """
    try:
        client = get_docker_client()
        container = client.containers.get(container_id)
        network = client.networks.get(network_id)

        # Disconnect container from network
        network.disconnect(container)
        return True
    except NotFound as e:
        logger.error(f"Container or network not found: {e}")
        return False
    except DockerException as e:
        logger.error(f"Failed to disconnect container from network: {e}")
        raise


# Helper functions


def parse_env(env_list: List[str]) -> Dict[str, str]:
    """
    Parse environment variables from a list of strings.
    """
    env_dict = {}
    for env in env_list:
        if "=" in env:
            key, value = env.split("=", 1)
            env_dict[key] = value
    return env_dict


def parse_ports(ports_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse port mappings from a dictionary.
    """
    ports_list = []
    for container_port, host_ports in ports_dict.items():
        if not host_ports:
            continue

        port, protocol = container_port.split("/")
        for host_port in host_ports:
            ports_list.append(
                {
                    # Use actual IP or localhost if not specified
                    "host_ip": host_port.get("HostIp") if host_port.get("HostIp") else "127.0.0.1",
                    "host_port": int(host_port.get("HostPort")),
                    "container_port": int(port),
                    "protocol": protocol,
                }
            )

    return ports_list


def parse_volumes(mounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse volume mounts from a list of dictionaries.
    """
    volumes_list = []
    for mount in mounts:
        volumes_list.append(
            {
                "host_path": mount.get("Source", ""),
                "container_path": mount.get("Destination", ""),
                "mode": mount.get("Mode", "rw"),
            }
        )

    return volumes_list


def parse_stats(stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse container stats.
    """
    # CPU usage
    cpu_stats = stats.get("cpu_stats", {})
    precpu_stats = stats.get("precpu_stats", {})

    cpu_total_usage = cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
    precpu_total_usage = precpu_stats.get("cpu_usage", {}).get("total_usage", 0)

    cpu_system_usage = cpu_stats.get("system_cpu_usage", 0)
    precpu_system_usage = precpu_stats.get("system_cpu_usage", 0)

    cpu_delta = cpu_total_usage - precpu_total_usage
    system_delta = cpu_system_usage - precpu_system_usage

    cpu_percent = 0.0
    if system_delta > 0 and cpu_delta > 0:
        cpu_percent = (cpu_delta / system_delta) * len(
            cpu_stats.get("cpu_usage", {}).get("percpu_usage", [])
        )

    # Memory usage
    memory_stats = stats.get("memory_stats", {})
    memory_usage = memory_stats.get("usage", 0)
    memory_limit = memory_stats.get("limit", 0)

    memory_percent = 0.0
    if memory_limit > 0:
        memory_percent = (memory_usage / memory_limit) * 100.0

    # Network usage
    networks = stats.get("networks", {})
    network_rx_bytes = 0
    network_tx_bytes = 0

    for network in networks.values():
        network_rx_bytes += network.get("rx_bytes", 0)
        network_tx_bytes += network.get("tx_bytes", 0)

    # Block I/O usage
    blkio_stats = stats.get("blkio_stats", {})
    io_service_bytes_recursive = blkio_stats.get("io_service_bytes_recursive", [])

    block_read_bytes = 0
    block_write_bytes = 0

    for io in io_service_bytes_recursive:
        if io.get("op") == "Read":
            block_read_bytes += io.get("value", 0)
        elif io.get("op") == "Write":
            block_write_bytes += io.get("value", 0)

    return {
        "cpu_percent": round(cpu_percent, 2),
        "memory_usage": memory_usage,
        "memory_limit": memory_limit,
        "memory_percent": round(memory_percent, 2),
        "network_rx_bytes": network_rx_bytes,
        "network_tx_bytes": network_tx_bytes,
        "block_read_bytes": block_read_bytes,
        "block_write_bytes": block_write_bytes,
    }
