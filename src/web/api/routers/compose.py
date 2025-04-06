"""
Compose router for the DockerForge Web UI.

This module provides the API endpoints for Docker Compose management.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, status, File, UploadFile
from sqlalchemy.orm import Session

from src.web.api.db.session import get_db
from src.web.api.auth.dependencies import get_current_active_user
from src.web.api.auth.permissions import check_permission
from src.web.api.models.user import User
from src.web.api.schemas.compose import ComposeFile, ComposeFileCreate, ComposeFileUpdate, ComposeService
from src.web.api.services.compose import (
    get_compose_files, get_compose_file, create_compose_file, update_compose_file,
    delete_compose_file, get_compose_services, compose_up, compose_down,
    compose_restart, compose_pull, get_compose_logs
)

router = APIRouter()


@router.get("", response_model=List[ComposeFile])
async def list_compose_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by compose file name")
):
    """
    Get all compose files.
    """
    # Check permission
    if not check_permission(current_user, "compose:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        compose_files = await get_compose_files(
            name=name,
            db=db
        )
        return compose_files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compose files: {str(e)}"
        )


@router.get("/{file_id}", response_model=ComposeFile)
async def get_compose_file_by_id(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a compose file by ID.
    """
    # Check permission
    if not check_permission(current_user, "compose:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        compose_file = await get_compose_file(file_id=file_id, db=db)
        if not compose_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compose file with ID {file_id} not found"
            )
        return compose_file
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compose file: {str(e)}"
        )


@router.post("", response_model=ComposeFile, status_code=status.HTTP_201_CREATED)
async def create_new_compose_file(
    file_data: ComposeFileCreate = Body(..., description="Compose file data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new compose file.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        compose_file = await create_compose_file(
            name=file_data.name,
            path=file_data.path,
            content=file_data.content,
            description=file_data.description,
            db=db
        )
        return compose_file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create compose file: {str(e)}"
        )


@router.put("/{file_id}", response_model=ComposeFile)
async def update_existing_compose_file(
    file_id: str = Path(..., description="Compose file ID"),
    file_data: ComposeFileUpdate = Body(..., description="Compose file data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a compose file.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        compose_file = await update_compose_file(
            file_id=file_id,
            name=file_data.name,
            path=file_data.path,
            content=file_data.content,
            description=file_data.description,
            db=db
        )
        if not compose_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compose file with ID {file_id} not found"
            )
        return compose_file
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update compose file: {str(e)}"
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_compose_file_by_id(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a compose file.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        success = await delete_compose_file(file_id=file_id, db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Compose file with ID {file_id} not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete compose file: {str(e)}"
        )


@router.get("/{file_id}/services", response_model=List[ComposeService])
async def get_services_for_compose_file(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get services for a compose file.
    """
    # Check permission
    if not check_permission(current_user, "compose:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        services = await get_compose_services(file_id=file_id, db=db)
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get compose services: {str(e)}"
        )


@router.post("/{file_id}/up", response_model=Dict[str, Any])
async def start_compose_project(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start a compose project.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        result = await compose_up(file_id=file_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start compose project: {str(e)}"
        )


@router.post("/{file_id}/down", response_model=Dict[str, Any])
async def stop_compose_project(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Stop a compose project.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        result = await compose_down(file_id=file_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to stop compose project: {str(e)}"
        )


@router.post("/{file_id}/restart", response_model=Dict[str, Any])
async def restart_compose_project(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Restart a compose project.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        result = await compose_restart(file_id=file_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to restart compose project: {str(e)}"
        )


@router.post("/{file_id}/pull", response_model=Dict[str, Any])
async def pull_compose_images(
    file_id: str = Path(..., description="Compose file ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Pull images for a compose project.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        result = await compose_pull(file_id=file_id, db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to pull compose images: {str(e)}"
        )


@router.get("/{file_id}/logs", response_model=Dict[str, Any])
async def get_logs_for_compose_project(
    file_id: str = Path(..., description="Compose file ID"),
    service: Optional[str] = Query(None, description="Service name"),
    tail: Optional[int] = Query(100, description="Number of lines to tail"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get logs for a compose project.
    """
    # Check permission
    if not check_permission(current_user, "compose:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        logs = await get_compose_logs(
            file_id=file_id,
            service=service,
            tail=tail,
            db=db
        )
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get compose logs: {str(e)}"
        )


@router.post("/upload", response_model=ComposeFile)
async def upload_compose_file(
    file: UploadFile = File(...),
    name: str = Query(..., description="Compose file name"),
    description: Optional[str] = Query(None, description="Compose file description"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a compose file.
    """
    # Check permission
    if not check_permission(current_user, "compose:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        compose_file = await create_compose_file(
            name=name,
            path=file.filename,
            content=content_str,
            description=description,
            db=db
        )
        return compose_file
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload compose file: {str(e)}"
        )
