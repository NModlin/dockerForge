"""
Containers router for the DockerForge Web UI.

This module provides the API endpoints for container management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.models.user import User
from src.web.api.schemas.containers import Container, ContainerCreate, ContainerUpdate
from src.web.api.services.auth import check_permission, get_current_active_user
from src.web.api.services.containers import (
    create_container,
    delete_container,
    get_container,
)
from src.web.api.services.containers import (
    get_container_logs as get_container_logs_service,
)
from src.web.api.services.containers import (
    get_containers,
)
from src.web.api.services.containers import get_system_info as get_system_info_service
from src.web.api.services.containers import (
    inspect_container as inspect_container_service,
)
from src.web.api.services.containers import (
    restart_container as restart_container_service,
)
from src.web.api.services.containers import start_container as start_container_service
from src.web.api.services.containers import stop_container as stop_container_service
from src.web.api.services.containers import (
    update_container,
)

# Create router
router = APIRouter()


@router.get("/", response_model=List[Container])
async def list_containers(
    status: Optional[str] = Query(
        None, description="Filter by container status (running, stopped, etc.)"
    ),
    name: Optional[str] = Query(None, description="Filter by container name"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of results"),
    skip: int = Query(0, ge=0, description="Skip the first N results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all containers with optional filtering.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return await get_containers(status=status, name=name, limit=limit, skip=skip, db=db)


@router.get("/{container_id}", response_model=Container)
async def get_container_by_id(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    container = await get_container(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )
    return container


@router.post("/", response_model=Container, status_code=status.HTTP_201_CREATED)
async def create_new_container(
    container: ContainerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new container.
    """
    # Check permission
    if not check_permission(current_user, "containers:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return await create_container(container, db=db)


@router.put("/{container_id}", response_model=Container)
async def update_container_by_id(
    container_id: str,
    container: ContainerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    updated_container = await update_container(container_id, container, db=db)
    if not updated_container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )
    return updated_container


@router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_container_by_id(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = await delete_container(container_id, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )
    return None


@router.post("/{container_id}/start", response_model=Container)
async def start_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Start a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    container = await start_container_service(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )

    return container


@router.post("/{container_id}/stop", response_model=Container)
async def stop_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Stop a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    container = await stop_container_service(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )

    return container


@router.post("/{container_id}/restart", response_model=Container)
async def restart_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Restart a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    container = await restart_container_service(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )

    return container


@router.get("/{container_id}/logs")
async def get_container_logs(
    container_id: str,
    tail: int = Query(
        100,
        ge=1,
        le=10000,
        description="Number of lines to show from the end of the logs",
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get logs for a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if container exists
    container = await get_container(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )

    # Get container logs
    logs = await get_container_logs_service(container_id, tail=tail, db=db)

    return {
        "container_id": container_id,
        "logs": logs,
    }


@router.get("/system/info")
async def get_system_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get Docker system information.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return await get_system_info_service(db=db)


@router.get("/{container_id}/inspect")
async def inspect_container(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed inspection data for a container by ID.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if container exists
    container = await get_container(container_id, db=db)
    if not container:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Container with ID {container_id} not found",
        )

    # Get container inspect data
    inspect_data = await inspect_container_service(container_id, db=db)
    if not inspect_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to inspect container with ID {container_id}",
        )

    return inspect_data
