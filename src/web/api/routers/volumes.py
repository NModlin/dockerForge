"""
Volumes router for the DockerForge Web UI.

This module provides the API endpoints for volume management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.web.api.auth.dependencies import get_current_active_user
from src.web.api.auth.permissions import check_permission
from src.web.api.db.session import get_db
from src.web.api.models.user import User
from src.web.api.schemas.volumes import Volume, VolumeCreate, VolumeUpdate
from src.web.api.services.volumes import (
    create_volume,
    delete_volume,
    get_volume,
    get_volume_containers,
    get_volumes,
    prune_volumes,
)

router = APIRouter()


@router.get("", response_model=List[Volume])
async def list_volumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by volume name"),
    driver: Optional[str] = Query(None, description="Filter by volume driver"),
):
    """
    Get all volumes.
    """
    # Check permission
    if not check_permission(current_user, "volumes:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        volumes = await get_volumes(name=name, driver=driver, db=db)
        return volumes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get volumes: {str(e)}",
        )


@router.get("/{volume_id}", response_model=Volume)
async def get_volume_by_id(
    volume_id: str = Path(..., description="Volume ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a volume by ID.
    """
    # Check permission
    if not check_permission(current_user, "volumes:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        volume = await get_volume(volume_id=volume_id, db=db)
        if not volume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Volume with ID {volume_id} not found",
            )
        return volume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get volume: {str(e)}",
        )


@router.post("", response_model=Volume, status_code=status.HTTP_201_CREATED)
async def create_new_volume(
    volume_data: VolumeCreate = Body(..., description="Volume data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new volume.
    """
    # Check permission
    if not check_permission(current_user, "volumes:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        volume = await create_volume(
            name=volume_data.name,
            driver=volume_data.driver,
            driver_opts=volume_data.driver_opts,
            labels=volume_data.labels,
            db=db,
        )
        return volume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create volume: {str(e)}",
        )


@router.delete("/{volume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_volume_by_id(
    volume_id: str = Path(..., description="Volume ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a volume.
    """
    # Check permission
    if not check_permission(current_user, "volumes:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        success = await delete_volume(volume_id=volume_id, db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Volume with ID {volume_id} not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete volume: {str(e)}",
        )


@router.get("/{volume_id}/containers", response_model=List[Dict[str, Any]])
async def get_containers_using_volume(
    volume_id: str = Path(..., description="Volume ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get containers using a volume.
    """
    # Check permission
    if not check_permission(current_user, "volumes:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        containers = await get_volume_containers(volume_id=volume_id, db=db)
        return containers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get containers using volume: {str(e)}",
        )


@router.post("/prune", response_model=Dict[str, Any])
async def prune_unused_volumes(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Prune unused volumes.
    """
    # Check permission
    if not check_permission(current_user, "volumes:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        result = await prune_volumes(db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to prune volumes: {str(e)}",
        )
