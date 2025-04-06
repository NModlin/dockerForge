"""
Networks router for the DockerForge Web UI.

This module provides the API endpoints for network management.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from src.web.api.auth.dependencies import get_current_active_user
from src.web.api.auth.permissions import check_permission
from src.web.api.db.session import get_db
from src.web.api.models.user import User
from src.web.api.schemas.networks import Network, NetworkCreate, NetworkUpdate
from src.web.api.services.networks import (
    connect_container_to_network,
    create_network,
    delete_network,
    disconnect_container_from_network,
    get_connected_containers,
    get_network,
    get_networks,
)

router = APIRouter()


@router.get("", response_model=List[Network])
async def list_networks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by network name"),
    driver: Optional[str] = Query(None, description="Filter by network driver"),
    scope: Optional[str] = Query(None, description="Filter by network scope"),
):
    """
    Get all networks.
    """
    # Check permission
    if not check_permission(current_user, "networks:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        networks = await get_networks(name=name, driver=driver, scope=scope, db=db)
        return networks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get networks: {str(e)}",
        )


@router.get("/{network_id}", response_model=Network)
async def get_network_by_id(
    network_id: str = Path(..., description="Network ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a network by ID.
    """
    # Check permission
    if not check_permission(current_user, "networks:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        network = await get_network(network_id=network_id, db=db)
        if not network:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Network with ID {network_id} not found",
            )
        return network
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get network: {str(e)}",
        )


@router.post("", response_model=Network, status_code=status.HTTP_201_CREATED)
async def create_new_network(
    network_data: NetworkCreate = Body(..., description="Network data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new network.
    """
    # Check permission
    if not check_permission(current_user, "networks:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        network = await create_network(
            name=network_data.name,
            driver=network_data.driver,
            subnet=network_data.subnet,
            gateway=network_data.gateway,
            internal=network_data.internal,
            labels=network_data.labels,
            options=network_data.options,
            db=db,
        )
        return network
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create network: {str(e)}",
        )


@router.delete("/{network_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_network_by_id(
    network_id: str = Path(..., description="Network ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a network.
    """
    # Check permission
    if not check_permission(current_user, "networks:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        success = await delete_network(network_id=network_id, db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Network with ID {network_id} not found",
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete network: {str(e)}",
        )


@router.get("/{network_id}/containers", response_model=List[Dict[str, Any]])
async def get_containers_in_network(
    network_id: str = Path(..., description="Network ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get containers connected to a network.
    """
    # Check permission
    if not check_permission(current_user, "networks:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        containers = await get_connected_containers(network_id=network_id, db=db)
        return containers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get connected containers: {str(e)}",
        )


@router.post("/{network_id}/connect", response_model=Dict[str, Any])
async def connect_container(
    network_id: str = Path(..., description="Network ID"),
    connection_data: Dict[str, Any] = Body(..., description="Connection data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Connect a container to a network.
    """
    # Check permission
    if not check_permission(current_user, "networks:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        container_id = connection_data.get("container_id")
        aliases = connection_data.get("aliases", [])

        if not container_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Container ID is required",
            )

        success = await connect_container_to_network(
            network_id=network_id, container_id=container_id, aliases=aliases, db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect container to network",
            )

        return {
            "success": True,
            "message": f"Container {container_id} connected to network {network_id}",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect container to network: {str(e)}",
        )


@router.post("/{network_id}/disconnect", response_model=Dict[str, Any])
async def disconnect_container(
    network_id: str = Path(..., description="Network ID"),
    connection_data: Dict[str, Any] = Body(..., description="Connection data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Disconnect a container from a network.
    """
    # Check permission
    if not check_permission(current_user, "networks:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        container_id = connection_data.get("container_id")

        if not container_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Container ID is required",
            )

        success = await disconnect_container_from_network(
            network_id=network_id, container_id=container_id, db=db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to disconnect container from network",
            )

        return {
            "success": True,
            "message": f"Container {container_id} disconnected from network {network_id}",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to disconnect container from network: {str(e)}",
        )
