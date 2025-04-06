"""
Alert management service for the DockerForge Web UI.

This module provides functionality for managing alerts, alert rules, and notification channels.
"""
import logging
import uuid
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from src.web.api.database import get_db
from src.web.api.models.monitoring import Alert, AlertRule, NotificationChannel
from src.web.api.schemas.alerts import (
    AlertCreate, AlertUpdate, AlertRuleCreate, AlertRuleUpdate,
    NotificationChannelCreate, AlertHistoryFilter, AlertStatistics,
    AlertSeverity, AlertStatus, AlertSource, MetricType
)
from src.resource_monitoring.metrics_collector import MetricsCollector
from src.config.config_manager import get_config

# Set up logging
logger = logging.getLogger("api.services.alerts")

# In-memory cache for active alert rules
active_alert_rules: Dict[str, Any] = {}

# In-memory cache for notification channels
notification_channels: Dict[str, Any] = {}


async def get_alert_rules(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = False
) -> List[AlertRule]:
    """
    Get all alert rules.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        enabled_only: Whether to return only enabled rules
        
    Returns:
        List of alert rules
    """
    query = db.query(AlertRule)
    
    if enabled_only:
        query = query.filter(AlertRule.enabled == True)
    
    return query.order_by(AlertRule.created_at.desc()).offset(skip).limit(limit).all()


async def get_alert_rule(db: Session, rule_id: str) -> Optional[AlertRule]:
    """
    Get an alert rule by ID.
    
    Args:
        db: Database session
        rule_id: Alert rule ID
        
    Returns:
        Alert rule or None if not found
    """
    return db.query(AlertRule).filter(AlertRule.id == rule_id).first()


async def create_alert_rule(db: Session, rule_create: AlertRuleCreate) -> AlertRule:
    """
    Create a new alert rule.
    
    Args:
        db: Database session
        rule_create: Alert rule creation data
        
    Returns:
        Created alert rule
    """
    # Generate ID
    rule_id = str(uuid.uuid4())
    
    # Create alert rule
    rule = AlertRule(
        id=rule_id,
        name=rule_create.name,
        description=rule_create.description,
        enabled=rule_create.enabled,
        severity=rule_create.severity,
        source_type=rule_create.source_type,
        source_filter=rule_create.source_filter,
        metric_type=rule_create.metric_type,
        condition=rule_create.condition,
        threshold=rule_create.threshold,
        duration=rule_create.duration,
        cooldown=rule_create.cooldown,
        actions={"notification_channels": rule_create.notification_channels},
        created_at=datetime.now(),
        updated_at=None
    )
    
    # Add to database
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    # Update in-memory cache if enabled
    if rule.enabled:
        active_alert_rules[rule_id] = {
            "id": rule_id,
            "name": rule.name,
            "severity": rule.severity,
            "source_type": rule.source_type,
            "source_filter": rule.source_filter,
            "metric_type": rule.metric_type,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "duration": rule.duration,
            "cooldown": rule.cooldown,
            "actions": rule.actions,
            "last_triggered": {},  # Dict to track last trigger time per source
        }
    
    return rule


async def update_alert_rule(
    db: Session,
    rule_id: str,
    rule_update: AlertRuleUpdate
) -> Optional[AlertRule]:
    """
    Update an alert rule.
    
    Args:
        db: Database session
        rule_id: Alert rule ID
        rule_update: Alert rule update data
        
    Returns:
        Updated alert rule or None if not found
    """
    # Get rule
    rule = await get_alert_rule(db, rule_id)
    if not rule:
        return None
    
    # Update fields
    update_data = rule_update.dict(exclude_unset=True)
    
    # Handle notification channels separately
    if "notification_channels" in update_data:
        if not rule.actions:
            rule.actions = {}
        rule.actions["notification_channels"] = update_data.pop("notification_channels")
    
    # Update other fields
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    # Update timestamp
    rule.updated_at = datetime.now()
    
    # Commit changes
    db.commit()
    db.refresh(rule)
    
    # Update in-memory cache
    if rule_id in active_alert_rules:
        if not rule.enabled:
            # Remove from cache if disabled
            del active_alert_rules[rule_id]
        else:
            # Update cache
            active_alert_rules[rule_id] = {
                "id": rule_id,
                "name": rule.name,
                "severity": rule.severity,
                "source_type": rule.source_type,
                "source_filter": rule.source_filter,
                "metric_type": rule.metric_type,
                "condition": rule.condition,
                "threshold": rule.threshold,
                "duration": rule.duration,
                "cooldown": rule.cooldown,
                "actions": rule.actions,
                "last_triggered": active_alert_rules[rule_id].get("last_triggered", {}),
            }
    elif rule.enabled:
        # Add to cache if enabled
        active_alert_rules[rule_id] = {
            "id": rule_id,
            "name": rule.name,
            "severity": rule.severity,
            "source_type": rule.source_type,
            "source_filter": rule.source_filter,
            "metric_type": rule.metric_type,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "duration": rule.duration,
            "cooldown": rule.cooldown,
            "actions": rule.actions,
            "last_triggered": {},
        }
    
    return rule


async def delete_alert_rule(db: Session, rule_id: str) -> bool:
    """
    Delete an alert rule.
    
    Args:
        db: Database session
        rule_id: Alert rule ID
        
    Returns:
        True if deleted, False if not found
    """
    # Get rule
    rule = await get_alert_rule(db, rule_id)
    if not rule:
        return False
    
    # Delete rule
    db.delete(rule)
    db.commit()
    
    # Remove from in-memory cache
    if rule_id in active_alert_rules:
        del active_alert_rules[rule_id]
    
    return True


async def get_notification_channels(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = False
) -> List[NotificationChannel]:
    """
    Get all notification channels.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        enabled_only: Whether to return only enabled channels
        
    Returns:
        List of notification channels
    """
    query = db.query(NotificationChannel)
    
    if enabled_only:
        query = query.filter(NotificationChannel.enabled == True)
    
    return query.order_by(NotificationChannel.created_at.desc()).offset(skip).limit(limit).all()


async def get_notification_channel(db: Session, channel_id: str) -> Optional[NotificationChannel]:
    """
    Get a notification channel by ID.
    
    Args:
        db: Database session
        channel_id: Notification channel ID
        
    Returns:
        Notification channel or None if not found
    """
    return db.query(NotificationChannel).filter(NotificationChannel.id == channel_id).first()


async def create_notification_channel(
    db: Session,
    channel_create: NotificationChannelCreate
) -> NotificationChannel:
    """
    Create a new notification channel.
    
    Args:
        db: Database session
        channel_create: Notification channel creation data
        
    Returns:
        Created notification channel
    """
    # Generate ID
    channel_id = str(uuid.uuid4())
    
    # Create notification channel
    channel = NotificationChannel(
        id=channel_id,
        name=channel_create.name,
        type=channel_create.type,
        enabled=channel_create.enabled,
        config=channel_create.config,
        created_at=datetime.now(),
        updated_at=None
    )
    
    # Add to database
    db.add(channel)
    db.commit()
    db.refresh(channel)
    
    # Update in-memory cache if enabled
    if channel.enabled:
        notification_channels[channel_id] = {
            "id": channel_id,
            "name": channel.name,
            "type": channel.type,
            "config": channel.config,
        }
    
    return channel


async def update_notification_channel(
    db: Session,
    channel_id: str,
    channel_update: dict
) -> Optional[NotificationChannel]:
    """
    Update a notification channel.
    
    Args:
        db: Database session
        channel_id: Notification channel ID
        channel_update: Notification channel update data
        
    Returns:
        Updated notification channel or None if not found
    """
    # Get channel
    channel = await get_notification_channel(db, channel_id)
    if not channel:
        return None
    
    # Update fields
    for key, value in channel_update.items():
        setattr(channel, key, value)
    
    # Update timestamp
    channel.updated_at = datetime.now()
    
    # Commit changes
    db.commit()
    db.refresh(channel)
    
    # Update in-memory cache
    if channel_id in notification_channels:
        if not channel.enabled:
            # Remove from cache if disabled
            del notification_channels[channel_id]
        else:
            # Update cache
            notification_channels[channel_id] = {
                "id": channel_id,
                "name": channel.name,
                "type": channel.type,
                "config": channel.config,
            }
    elif channel.enabled:
        # Add to cache if enabled
        notification_channels[channel_id] = {
            "id": channel_id,
            "name": channel.name,
            "type": channel.type,
            "config": channel.config,
        }
    
    return channel


async def delete_notification_channel(db: Session, channel_id: str) -> bool:
    """
    Delete a notification channel.
    
    Args:
        db: Database session
        channel_id: Notification channel ID
        
    Returns:
        True if deleted, False if not found
    """
    # Get channel
    channel = await get_notification_channel(db, channel_id)
    if not channel:
        return False
    
    # Delete channel
    db.delete(channel)
    db.commit()
    
    # Remove from in-memory cache
    if channel_id in notification_channels:
        del notification_channels[channel_id]
    
    return True


async def get_alerts(
    db: Session,
    filter_params: AlertHistoryFilter = None,
    skip: int = 0,
    limit: int = 100
) -> List[Alert]:
    """
    Get alerts with optional filtering.
    
    Args:
        db: Database session
        filter_params: Alert filter parameters
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of alerts
    """
    query = db.query(Alert)
    
    # Apply filters if provided
    if filter_params:
        if filter_params.severity:
            query = query.filter(Alert.severity.in_(filter_params.severity))
        
        if filter_params.status:
            query = query.filter(Alert.status.in_(filter_params.status))
        
        if filter_params.source:
            query = query.filter(Alert.source.in_(filter_params.source))
        
        if filter_params.source_id:
            query = query.filter(Alert.source_id == filter_params.source_id)
        
        if filter_params.metric_type:
            query = query.filter(Alert.metric_type.in_(filter_params.metric_type))
        
        if filter_params.start_date:
            query = query.filter(Alert.created_at >= filter_params.start_date)
        
        if filter_params.end_date:
            query = query.filter(Alert.created_at <= filter_params.end_date)
        
        if filter_params.rule_id:
            query = query.filter(Alert.rule_id == filter_params.rule_id)
    
    # Order by creation date (newest first)
    query = query.order_by(Alert.created_at.desc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


async def get_alert(db: Session, alert_id: str) -> Optional[Alert]:
    """
    Get an alert by ID.
    
    Args:
        db: Database session
        alert_id: Alert ID
        
    Returns:
        Alert or None if not found
    """
    return db.query(Alert).filter(Alert.id == alert_id).first()


async def create_alert(db: Session, alert_create: AlertCreate) -> Alert:
    """
    Create a new alert.
    
    Args:
        db: Database session
        alert_create: Alert creation data
        
    Returns:
        Created alert
    """
    # Generate ID
    alert_id = str(uuid.uuid4())
    
    # Create alert
    alert = Alert(
        id=alert_id,
        name=alert_create.name,
        description=alert_create.description,
        severity=alert_create.severity,
        status=AlertStatus.ACTIVE,
        source=alert_create.source,
        source_id=alert_create.source_id,
        source_name=alert_create.source_name,
        metric_type=alert_create.metric_type,
        threshold=alert_create.threshold,
        value=alert_create.value,
        rule_id=alert_create.rule_id,
        created_at=datetime.now(),
        acknowledged_at=None,
        resolved_at=None,
        acknowledged_by=None
    )
    
    # Add to database
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # Send notifications
    if alert_create.rule_id:
        await _send_alert_notifications(db, alert)
    
    return alert


async def update_alert(
    db: Session,
    alert_id: str,
    alert_update: AlertUpdate,
    user_id: Optional[str] = None
) -> Optional[Alert]:
    """
    Update an alert.
    
    Args:
        db: Database session
        alert_id: Alert ID
        alert_update: Alert update data
        user_id: ID of the user making the update
        
    Returns:
        Updated alert or None if not found
    """
    # Get alert
    alert = await get_alert(db, alert_id)
    if not alert:
        return None
    
    # Update fields
    update_data = alert_update.dict(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        new_status = update_data["status"]
        
        if new_status == AlertStatus.ACKNOWLEDGED and alert.status != AlertStatus.ACKNOWLEDGED:
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user_id or alert_update.acknowledged_by
        
        if new_status == AlertStatus.RESOLVED and alert.status != AlertStatus.RESOLVED:
            alert.resolved_at = datetime.now()
    
    # Update other fields
    for key, value in update_data.items():
        setattr(alert, key, value)
    
    # Commit changes
    db.commit()
    db.refresh(alert)
    
    return alert


async def delete_alert(db: Session, alert_id: str) -> bool:
    """
    Delete an alert.
    
    Args:
        db: Database session
        alert_id: Alert ID
        
    Returns:
        True if deleted, False if not found
    """
    # Get alert
    alert = await get_alert(db, alert_id)
    if not alert:
        return False
    
    # Delete alert
    db.delete(alert)
    db.commit()
    
    return True


async def get_alert_statistics(db: Session, days: int = 7) -> AlertStatistics:
    """
    Get alert statistics.
    
    Args:
        db: Database session
        days: Number of days to include in statistics
        
    Returns:
        Alert statistics
    """
    # Calculate start date
    start_date = datetime.now() - timedelta(days=days)
    
    # Get total count
    total = db.query(func.count(Alert.id)).filter(Alert.created_at >= start_date).scalar()
    
    # Get counts by severity
    severity_counts = db.query(
        Alert.severity,
        func.count(Alert.id)
    ).filter(
        Alert.created_at >= start_date
    ).group_by(
        Alert.severity
    ).all()
    
    by_severity = {severity: 0 for severity in AlertSeverity}
    for severity, count in severity_counts:
        by_severity[severity] = count
    
    # Get counts by status
    status_counts = db.query(
        Alert.status,
        func.count(Alert.id)
    ).filter(
        Alert.created_at >= start_date
    ).group_by(
        Alert.status
    ).all()
    
    by_status = {status: 0 for status in AlertStatus}
    for status, count in status_counts:
        by_status[status] = count
    
    # Get counts by source
    source_counts = db.query(
        Alert.source,
        func.count(Alert.id)
    ).filter(
        Alert.created_at >= start_date
    ).group_by(
        Alert.source
    ).all()
    
    by_source = {source: 0 for source in AlertSource}
    for source, count in source_counts:
        by_source[source] = count
    
    # Get counts by metric type
    metric_counts = db.query(
        Alert.metric_type,
        func.count(Alert.id)
    ).filter(
        Alert.created_at >= start_date,
        Alert.metric_type != None
    ).group_by(
        Alert.metric_type
    ).all()
    
    by_metric_type = {metric_type: 0 for metric_type in MetricType}
    for metric_type, count in metric_counts:
        if metric_type:
            by_metric_type[metric_type] = count
    
    # Get active alerts by severity
    active_severity_counts = db.query(
        Alert.severity,
        func.count(Alert.id)
    ).filter(
        Alert.created_at >= start_date,
        Alert.status == AlertStatus.ACTIVE
    ).group_by(
        Alert.severity
    ).all()
    
    active_by_severity = {severity: 0 for severity in AlertSeverity}
    for severity, count in active_severity_counts:
        active_by_severity[severity] = count
    
    # Create statistics
    return AlertStatistics(
        total=total,
        by_severity=by_severity,
        by_status=by_status,
        by_source=by_source,
        by_metric_type=by_metric_type,
        active_by_severity=active_by_severity
    )


async def _send_alert_notifications(db: Session, alert: Alert) -> None:
    """
    Send notifications for an alert.
    
    Args:
        db: Database session
        alert: Alert to send notifications for
    """
    if not alert.rule_id:
        return
    
    # Get rule
    rule = await get_alert_rule(db, alert.rule_id)
    if not rule or not rule.actions:
        return
    
    # Get notification channels
    channel_ids = rule.actions.get("notification_channels", [])
    if not channel_ids:
        return
    
    # Send notifications to each channel
    for channel_id in channel_ids:
        channel = await get_notification_channel(db, channel_id)
        if not channel or not channel.enabled:
            continue
        
        try:
            await _send_notification(channel, alert)
        except Exception as e:
            logger.error(f"Error sending notification to channel {channel.name}: {str(e)}")


async def _send_notification(channel: NotificationChannel, alert: Alert) -> None:
    """
    Send a notification to a channel.
    
    Args:
        channel: Notification channel
        alert: Alert to send notification for
    """
    # Create notification message
    message = f"Alert: {alert.name}\n"
    message += f"Severity: {alert.severity}\n"
    message += f"Source: {alert.source}"
    
    if alert.source_name:
        message += f" ({alert.source_name})"
    
    message += f"\nTimestamp: {alert.created_at.isoformat()}\n"
    
    if alert.description:
        message += f"Description: {alert.description}\n"
    
    if alert.metric_type:
        message += f"Metric: {alert.metric_type}\n"
    
    if alert.threshold is not None and alert.value is not None:
        message += f"Threshold: {alert.threshold}\n"
        message += f"Value: {alert.value}\n"
    
    # Send notification based on channel type
    if channel.type == "email":
        await _send_email_notification(channel, alert, message)
    elif channel.type == "webhook":
        await _send_webhook_notification(channel, alert, message)
    elif channel.type == "slack":
        await _send_slack_notification(channel, alert, message)
    elif channel.type == "discord":
        await _send_discord_notification(channel, alert, message)
    else:
        logger.warning(f"Unsupported notification channel type: {channel.type}")


async def _send_email_notification(
    channel: NotificationChannel,
    alert: Alert,
    message: str
) -> None:
    """
    Send an email notification.
    
    Args:
        channel: Notification channel
        alert: Alert to send notification for
        message: Notification message
    """
    # TODO: Implement email notification
    logger.info(f"Sending email notification for alert {alert.id} to {channel.config.get('recipients')}")


async def _send_webhook_notification(
    channel: NotificationChannel,
    alert: Alert,
    message: str
) -> None:
    """
    Send a webhook notification.
    
    Args:
        channel: Notification channel
        alert: Alert to send notification for
        message: Notification message
    """
    # TODO: Implement webhook notification
    logger.info(f"Sending webhook notification for alert {alert.id} to {channel.config.get('url')}")


async def _send_slack_notification(
    channel: NotificationChannel,
    alert: Alert,
    message: str
) -> None:
    """
    Send a Slack notification.
    
    Args:
        channel: Notification channel
        alert: Alert to send notification for
        message: Notification message
    """
    # TODO: Implement Slack notification
    logger.info(f"Sending Slack notification for alert {alert.id} to {channel.config.get('webhook_url')}")


async def _send_discord_notification(
    channel: NotificationChannel,
    alert: Alert,
    message: str
) -> None:
    """
    Send a Discord notification.
    
    Args:
        channel: Notification channel
        alert: Alert to send notification for
        message: Notification message
    """
    # TODO: Implement Discord notification
    logger.info(f"Sending Discord notification for alert {alert.id} to {channel.config.get('webhook_url')}")


# Initialize alert rules cache
async def initialize_alert_rules_cache(db: Session) -> None:
    """
    Initialize the alert rules cache.
    
    Args:
        db: Database session
    """
    global active_alert_rules
    
    # Clear cache
    active_alert_rules = {}
    
    # Get all enabled rules
    rules = await get_alert_rules(db, enabled_only=True, limit=1000)
    
    # Add to cache
    for rule in rules:
        active_alert_rules[rule.id] = {
            "id": rule.id,
            "name": rule.name,
            "severity": rule.severity,
            "source_type": rule.source_type,
            "source_filter": rule.source_filter,
            "metric_type": rule.metric_type,
            "condition": rule.condition,
            "threshold": rule.threshold,
            "duration": rule.duration,
            "cooldown": rule.cooldown,
            "actions": rule.actions,
            "last_triggered": {},
        }
    
    logger.info(f"Initialized alert rules cache with {len(active_alert_rules)} rules")


# Initialize notification channels cache
async def initialize_notification_channels_cache(db: Session) -> None:
    """
    Initialize the notification channels cache.
    
    Args:
        db: Database session
    """
    global notification_channels
    
    # Clear cache
    notification_channels = {}
    
    # Get all enabled channels
    channels = await get_notification_channels(db, enabled_only=True, limit=1000)
    
    # Add to cache
    for channel in channels:
        notification_channels[channel.id] = {
            "id": channel.id,
            "name": channel.name,
            "type": channel.type,
            "config": channel.config,
        }
    
    logger.info(f"Initialized notification channels cache with {len(notification_channels)} channels")
