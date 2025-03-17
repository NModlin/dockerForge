"""
Container service for the DockerForge Web UI.

This module provides the container management services for the DockerForge Web UI.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from ..schemas.containers import Container, ContainerCreate, ContainerUpdate
from ..services import docker
from ..models import Container as ContainerModel

# Configure logging
logger = logging.getLogger(__name__)


async def get_containers(
    status: Optional[str] = None,
    name: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: Session = None,
) -> List[Container]:
    """
    Get all containers with optional filtering.
    """
    try:
        # Prepare filters
        filters = {}
        if status:
            filters["status"] = status
        if name:
            filters["name"] = name
        
        # Get containers from Docker API
        docker_containers = docker.get_containers(all=True, filters=filters)
        
        # Apply pagination
        paginated_containers = docker_containers[skip:skip + limit]
        
        # Convert to Container objects
        return [Container(**container) for container in paginated_containers]
    except Exception as e:
        logger.error(f"Failed to get containers: {e}")
        raise


async def get_container(container_id: str, db: Session = None) -> Optional[Container]:
    """
    Get a container by ID.
    """
    try:
        # Get container from Docker API
        container_data = docker.get_container(container_id)
        if not container_data:
            return None
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to get container: {e}")
        raise


async def create_container(container: ContainerCreate, db: Session = None) -> Container:
    """
    Create a new container.
    """
    try:
        # Prepare container data
        container_data = container.dict()
        
        # Create container using Docker API
        container_data = docker.create_container(container_data)
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to create container: {e}")
        raise


async def update_container(container_id: str, container: ContainerUpdate, db: Session = None) -> Optional[Container]:
    """
    Update a container by ID.
    
    Note: Docker doesn't support updating a running container.
    This method will stop the container, remove it, and create a new one with the updated configuration.
    """
    try:
        # Get existing container
        existing_container = await get_container(container_id)
        if not existing_container:
            return None
        
        # Prepare update data
        update_data = container.dict(exclude_unset=True)
        
        # Check if container is running
        if existing_container.status == "running":
            # Stop container
            docker.stop_container(container_id)
        
        # Delete container
        docker.delete_container(container_id)
        
        # Prepare new container data
        new_container_data = existing_container.dict()
        new_container_data.update(update_data)
        
        # Create new container
        container_data = docker.create_container(new_container_data)
        
        # Start container if it was running before
        if existing_container.status == "running":
            docker.start_container(container_data["id"])
            container_data = docker.get_container(container_data["id"])
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to update container: {e}")
        raise


async def delete_container(container_id: str, db: Session = None) -> bool:
    """
    Delete a container by ID.
    """
    try:
        # Delete container using Docker API
        return docker.delete_container(container_id, force=True)
    except Exception as e:
        logger.error(f"Failed to delete container: {e}")
        raise


async def start_container(container_id: str, db: Session = None) -> Optional[Container]:
    """
    Start a container by ID.
    """
    try:
        # Start container using Docker API
        container_data = docker.start_container(container_id)
        if not container_data:
            return None
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to start container: {e}")
        raise


async def stop_container(container_id: str, db: Session = None) -> Optional[Container]:
    """
    Stop a container by ID.
    """
    try:
        # Stop container using Docker API
        container_data = docker.stop_container(container_id)
        if not container_data:
            return None
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to stop container: {e}")
        raise


async def restart_container(container_id: str, db: Session = None) -> Optional[Container]:
    """
    Restart a container by ID.
    """
    try:
        # Restart container using Docker API
        container_data = docker.restart_container(container_id)
        if not container_data:
            return None
        
        # Convert to Container object
        return Container(**container_data)
    except Exception as e:
        logger.error(f"Failed to restart container: {e}")
        raise


async def get_container_logs(container_id: str, tail: int = 100, db: Session = None) -> List[str]:
    """
    Get container logs.
    """
    try:
        # Get container logs using Docker API
        return docker.get_container_logs(container_id, tail=tail)
    except Exception as e:
        logger.error(f"Failed to get container logs: {e}")
        raise


async def get_system_info(db: Session = None) -> Dict[str, Any]:
    """
    Get Docker system information.
    """
    try:
        # Get system info using Docker API
        return docker.get_system_info()
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise
