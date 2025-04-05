"""
Backup router for the DockerForge Web UI.

This module provides API endpoints for backup management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.models.backup import Backup, BackupItem, RestoreJob, RestoreItem
from src.web.api.schemas import backup as schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Backup])
async def get_backups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all backups.
    """
    backups = db.query(Backup).offset(skip).limit(limit).all()
    return backups


@router.post("/", response_model=schemas.Backup, status_code=status.HTTP_201_CREATED)
async def create_backup(
    backup: schemas.BackupCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new backup.
    """
    db_backup = Backup(**backup.dict())
    db.add(db_backup)
    db.commit()
    db.refresh(db_backup)
    return db_backup


@router.get("/{backup_id}", response_model=schemas.BackupDetail)
async def get_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific backup by ID.
    """
    db_backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")
    return db_backup


@router.put("/{backup_id}", response_model=schemas.Backup)
async def update_backup(
    backup_id: int,
    backup: schemas.BackupUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a backup.
    """
    db_backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")

    for key, value in backup.dict(exclude_unset=True).items():
        setattr(db_backup, key, value)

    db.commit()
    db.refresh(db_backup)
    return db_backup


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a backup.
    """
    db_backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")

    db.delete(db_backup)
    db.commit()
    return None


@router.get("/{backup_id}/items", response_model=List[schemas.BackupItem])
async def get_backup_items(
    backup_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all items for a specific backup.
    """
    db_backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")

    items = db.query(BackupItem).filter(BackupItem.backup_id == backup_id).offset(skip).limit(limit).all()
    return items


@router.post("/{backup_id}/items", response_model=schemas.BackupItem, status_code=status.HTTP_201_CREATED)
async def create_backup_item(
    backup_id: int,
    item: schemas.BackupItemCreate,
    db: Session = Depends(get_db)
):
    """
    Add an item to a backup.
    """
    db_backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")

    db_item = BackupItem(**item.dict(), backup_id=backup_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/restore", response_model=List[schemas.RestoreJob])
async def get_restore_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all restore jobs.
    """
    jobs = db.query(RestoreJob).offset(skip).limit(limit).all()
    return jobs


@router.post("/restore", response_model=schemas.RestoreJob, status_code=status.HTTP_201_CREATED)
async def create_restore_job(
    job: schemas.RestoreJobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new restore job.
    """
    db_backup = db.query(Backup).filter(Backup.id == job.backup_id).first()
    if db_backup is None:
        raise HTTPException(status_code=404, detail="Backup not found")

    db_job = RestoreJob(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/restore/{job_id}", response_model=schemas.RestoreJobDetail)
async def get_restore_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific restore job by ID.
    """
    db_job = db.query(RestoreJob).filter(RestoreJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Restore job not found")
    return db_job


@router.put("/restore/{job_id}", response_model=schemas.RestoreJob)
async def update_restore_job(
    job_id: int,
    job: schemas.RestoreJobUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a restore job.
    """
    db_job = db.query(RestoreJob).filter(RestoreJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Restore job not found")

    for key, value in job.dict(exclude_unset=True).items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return db_job


@router.delete("/restore/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restore_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a restore job.
    """
    db_job = db.query(RestoreJob).filter(RestoreJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Restore job not found")

    db.delete(db_job)
    db.commit()
    return None


@router.post("/restore/{job_id}/items", response_model=schemas.RestoreItem, status_code=status.HTTP_201_CREATED)
async def create_restore_item(
    job_id: int,
    item: schemas.RestoreItemCreate,
    db: Session = Depends(get_db)
):
    """
    Add an item to a restore job.
    """
    db_job = db.query(RestoreJob).filter(RestoreJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Restore job not found")

    db_backup_item = db.query(BackupItem).filter(BackupItem.id == item.backup_item_id).first()
    if db_backup_item is None:
        raise HTTPException(status_code=404, detail="Backup item not found")

    db_item = RestoreItem(**item.dict(), restore_job_id=job_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
