"""
Alert router for the DockerForge Web UI.

This module provides API endpoints for alert management.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.models.user import User
from src.web.api.auth import get_current_active_user, check_permission
from src.web.api.schemas.alerts import (
    AlertRule, AlertRuleCreate, AlertRuleUpdate,
    Alert, AlertCreate, AlertUpdate,
    NotificationChannel, NotificationChannelCreate,
    AlertHistoryFilter, AlertStatistics
)
from src.web.api.services import alerts as alerts_service

# Set up logging
import logging
logger = logging.getLogger("api.routers.alerts")

# Create router
router = APIRouter()


# Alert Rules Endpoints

@router.get("/rules", response_model=List[AlertRule])
async def get_alert_rules(
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all alert rules.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return await alerts_service.get_alert_rules(db, skip, limit, enabled_only)


@router.get("/rules/{rule_id}", response_model=AlertRule)
async def get_alert_rule(
    rule_id: str = Path(..., description="Alert rule ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get an alert rule by ID.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    rule = await alerts_service.get_alert_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )
    
    return rule


@router.post("/rules", response_model=AlertRule, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    rule_create: AlertRuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new alert rule.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await alerts_service.create_alert_rule(db, rule_create)
    except Exception as e:
        logger.exception(f"Error creating alert rule: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating alert rule: {str(e)}"
        )


@router.put("/rules/{rule_id}", response_model=AlertRule)
async def update_alert_rule(
    rule_id: str = Path(..., description="Alert rule ID"),
    rule_update: AlertRuleUpdate = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an alert rule.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    rule = await alerts_service.update_alert_rule(db, rule_id, rule_update)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )
    
    return rule


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: str = Path(..., description="Alert rule ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert rule.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await alerts_service.delete_alert_rule(db, rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )
    
    return None


# Notification Channels Endpoints

@router.get("/channels", response_model=List[NotificationChannel])
async def get_notification_channels(
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all notification channels.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return await alerts_service.get_notification_channels(db, skip, limit, enabled_only)


@router.get("/channels/{channel_id}", response_model=NotificationChannel)
async def get_notification_channel(
    channel_id: str = Path(..., description="Notification channel ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a notification channel by ID.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    channel = await alerts_service.get_notification_channel(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification channel with ID {channel_id} not found"
        )
    
    return channel


@router.post("/channels", response_model=NotificationChannel, status_code=status.HTTP_201_CREATED)
async def create_notification_channel(
    channel_create: NotificationChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new notification channel.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await alerts_service.create_notification_channel(db, channel_create)
    except Exception as e:
        logger.exception(f"Error creating notification channel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating notification channel: {str(e)}"
        )


@router.put("/channels/{channel_id}", response_model=NotificationChannel)
async def update_notification_channel(
    channel_id: str = Path(..., description="Notification channel ID"),
    channel_update: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a notification channel.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    channel = await alerts_service.update_notification_channel(db, channel_id, channel_update)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification channel with ID {channel_id} not found"
        )
    
    return channel


@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_channel(
    channel_id: str = Path(..., description="Notification channel ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a notification channel.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await alerts_service.delete_notification_channel(db, channel_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification channel with ID {channel_id} not found"
        )
    
    return None


# Alerts Endpoints

@router.get("/", response_model=List[Alert])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    source: Optional[List[str]] = Query(None, description="Filter by source"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    metric_type: Optional[List[str]] = Query(None, description="Filter by metric type"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all alerts with optional filtering.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create filter
    filter_params = AlertHistoryFilter(
        severity=severity,
        status=status,
        source=source,
        source_id=source_id,
        metric_type=metric_type,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
        rule_id=rule_id
    )
    
    return await alerts_service.get_alerts(db, filter_params, skip, limit)


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str = Path(..., description="Alert ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get an alert by ID.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    alert = await alerts_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return alert


@router.post("/", response_model=Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_create: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new alert.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        return await alerts_service.create_alert(db, alert_create)
    except Exception as e:
        logger.exception(f"Error creating alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating alert: {str(e)}"
        )


@router.put("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: str = Path(..., description="Alert ID"),
    alert_update: AlertUpdate = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an alert.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    alert = await alerts_service.update_alert(db, alert_id, alert_update, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return alert


@router.post("/{alert_id}/acknowledge", response_model=Alert)
async def acknowledge_alert(
    alert_id: str = Path(..., description="Alert ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create update with acknowledged status
    alert_update = AlertUpdate(
        status="acknowledged",
        acknowledged_by=current_user.id
    )
    
    alert = await alerts_service.update_alert(db, alert_id, alert_update, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return alert


@router.post("/{alert_id}/resolve", response_model=Alert)
async def resolve_alert(
    alert_id: str = Path(..., description="Alert ID"),
    resolution_notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Resolve an alert.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Create update with resolved status
    alert_update = AlertUpdate(
        status="resolved",
        resolution_notes=resolution_notes
    )
    
    alert = await alerts_service.update_alert(db, alert_id, alert_update, current_user.id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str = Path(..., description="Alert ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an alert.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = await alerts_service.delete_alert(db, alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return None


@router.get("/statistics", response_model=AlertStatistics)
async def get_alert_statistics(
    days: int = Query(7, description="Number of days to include in statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get alert statistics.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return await alerts_service.get_alert_statistics(db, days)
