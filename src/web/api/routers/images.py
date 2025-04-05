"""
Images router for the DockerForge Web UI.

This module provides the API endpoints for image management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from schemas.images import Image, ImageCreate, ImageUpdate, ImageScan, ImageScanResult, ImageScanCreate
from services.images import (
    get_images, get_image, create_image, delete_image,
    scan_image, get_image_scans, get_image_scan,
)
from services.auth import get_current_active_user, check_permission
from database import get_db
from models import User

# Create router
router = APIRouter()


@router.get("/", response_model=List[Image])
async def list_images(
    name: Optional[str] = Query(None, description="Filter by image name"),
    tag: Optional[str] = Query(None, description="Filter by image tag"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of results"),
    skip: int = Query(0, ge=0, description="Skip the first N results"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all images with optional filtering.
    """
    # Check permission
    if not check_permission(current_user, "images:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return await get_images(name=name, tag=tag, limit=limit, skip=skip, db=db)


@router.get("/{image_id}", response_model=Image)
async def get_image_by_id(
    image_id: str = Path(..., description="The ID of the image to get"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get an image by ID.
    """
    # Check permission
    if not check_permission(current_user, "images:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    image = await get_image(image_id, db=db)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    return image


@router.post("/", response_model=Image, status_code=status.HTTP_201_CREATED)
async def create_new_image(
    image: ImageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create (pull) a new image.
    """
    # Check permission
    if not check_permission(current_user, "images:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return await create_image(image, db=db)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_by_id(
    image_id: str = Path(..., description="The ID of the image to delete"),
    force: bool = Query(False, description="Force deletion of the image"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete an image by ID.
    """
    # Check permission
    if not check_permission(current_user, "images:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    success = await delete_image(image_id, force=force, db=db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    return None


@router.post("/{image_id}/scan", response_model=ImageScanResult)
async def scan_image_by_id(
    image_id: str = Path(..., description="The ID of the image to scan"),
    scan_data: ImageScanCreate = Body(ImageScanCreate(), description="Scan configuration"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Scan an image for vulnerabilities.
    """
    # Check permission
    if not check_permission(current_user, "security:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if image exists
    image = await get_image(image_id, db=db)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    
    # Scan image
    return await scan_image(image_id, scan_type=scan_data.scan_type, db=db)


@router.get("/{image_id}/scans", response_model=List[ImageScan])
async def get_image_scans_by_id(
    image_id: str = Path(..., description="The ID of the image to get scans for"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all scans for an image.
    """
    # Check permission
    if not check_permission(current_user, "security:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if image exists
    image = await get_image(image_id, db=db)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    
    # Get scans
    return await get_image_scans(image_id, db=db)


@router.get("/{image_id}/scans/{scan_id}", response_model=ImageScanResult)
async def get_image_scan_by_id(
    image_id: str = Path(..., description="The ID of the image to get scan for"),
    scan_id: int = Path(..., description="The ID of the scan to get"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a scan for an image by ID.
    """
    # Check permission
    if not check_permission(current_user, "security:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Check if image exists
    image = await get_image(image_id, db=db)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    
    # Get scan
    scan_result = await get_image_scan(image_id, scan_id, db=db)
    if not scan_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID {scan_id} not found for image {image_id}",
        )
    
    return scan_result
