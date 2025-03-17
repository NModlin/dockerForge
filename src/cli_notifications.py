"""
Command-line interface module for DockerForge notifications and fixes.

This module provides the command-line interface for notifications and fixes.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.config.config_manager import get_config, set_config, save_config
from src.utils.logging_manager import get_logger
from src.notifications.notification_manager import get_notification_manager, Notification, NotificationSeverity, NotificationType
from src.notifications.preference_manager import get_preference_manager
from src.fixes.fix_proposal import get_fix_proposal_manager, FixProposal, FixStep, FixRiskLevel, FixStatus
from src.fixes.fix_applier import get_fix_applier

# Set up logging
logger = get_logger("cli_notifications")


# Notification command group
@click.group()
def notify():
    """Manage notifications and fixes."""
    pass


# Send notification command
@notify.command("send")
@click.option("--title", "-t", required=True, help="Notification title")
@click.option("--message", "-m", required=True, help="Notification message")
@click.option("--severity", "-s", type=click.Choice(["info", "warning", "error", "critical"]), default="info", help="Notification severity")
@click.option("--type", "-y", "notification_type", type=click.Choice(["container_exit", "container_oom", "high_resource_usage", "security_issue", "update_available", "fix_proposal", "fix_applied", "custom"]), default="custom", help="Notification type")
@click.option("--container", "-c", help="Container ID or name")
@click.option("--issue", "-i", help="Issue ID")
@click.option("--fix", "-f", help="Fix ID")
@click.option("--channel", "-ch", type=click.Choice(["email", "slack", "discord", "webhook", "all"]), default="all", help="Notification channel")
def send_notification(title, message, severity, notification_type, container, issue, fix, channel):
    """Send a notification."""
    logger.info(f"Sending notification: {title}")
    
    try:
        # Get notification manager
        notification_manager = get_notification_manager()
        
        # Create notification
        notification = Notification(
            title=title,
            message=message,
            severity=NotificationSeverity(severity),
            notification_type=NotificationType(notification_type),
            container_id=container,
            container_name=container,
            issue_id=issue,
            fix_id=fix,
        )
        
        # Send notification
        if channel == "all":
            result = notification_manager.send_notification(notification)
        else:
            # Get notifier
            notifier = notification_manager._notifiers.get(channel)
            
            if not notifier:
                click.secho(f"Unknown notification channel: {channel}", fg="red")
                sys.exit(1)
            
            # Send notification
            result = notifier.send(notification)
        
        if result:
            click.secho(f"Notification sent: {title}", fg="green")
        else:
            click.secho(f"Failed to send notification: {title}", fg="red")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# List notifications command
@notify.command("list")
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of notifications to show")
@click.option("--offset", "-o", type=int, default=0, help="Offset for pagination")
@click.option("--severity", "-s", type=click.Choice(["info", "warning", "error", "critical"]), help="Filter by severity")
@click.option("--type", "-y", "notification_type", type=click.Choice(["container_exit", "container_oom", "high_resource_usage", "security_issue", "update_available", "fix_proposal", "fix_applied", "custom"]), help="Filter by type")
@click.option("--container", "-c", help="Filter by container ID or name")
@click.option("--issue", "-i", help="Filter by issue ID")
@click.option("--fix", "-f", help="Filter by fix ID")
@click.option("--acknowledged", "-a", is_flag=True, help="Show only acknowledged notifications")
@click.option("--unacknowledged", "-u", is_flag=True, help="Show only unacknowledged notifications")
@click.option("--export", "-e", help="Export notifications to a file")
def list_notifications(limit, offset, severity, notification_type, container, issue, fix, acknowledged, unacknowledged, export):
    """List notifications."""
    logger.info("Listing notifications")
    
    try:
        # Get notification manager
        notification_manager = get_notification_manager()
        
        # Convert string severity to enum if provided
        severity_enum = None
        if severity:
            severity_enum = NotificationSeverity(severity)
        
        # Convert string notification type to enum if provided
        notification_type_enum = None
        if notification_type:
            notification_type_enum = NotificationType(notification_type)
        
        # Determine acknowledged filter
        acknowledged_filter = None
        if acknowledged:
            acknowledged_filter = True
        elif unacknowledged:
            acknowledged_filter = False
        
        # Get notifications
        notifications = notification_manager.get_notifications(
            limit=limit,
            offset=offset,
            severity=severity_enum,
            notification_type=notification_type_enum,
            container_id=container,
            issue_id=issue,
            fix_id=fix,
            acknowledged=acknowledged_filter,
        )
        
        # Export if requested
        if export:
            import json
            
            with open(export, "w") as f:
                json.dump([n.to_dict() for n in notifications], f, indent=2)
            
            click.secho(f"Exported {len(notifications)} notifications to {export}", fg="green")
            return
        
        # Print notifications
        if not notifications:
            click.echo("No notifications found")
            return
        
        click.secho(f"Found {len(notifications)} notifications", fg="blue", bold=True)
        
        for notification in notifications:
            # Determine color based on severity
            if notification.severity == NotificationSeverity.CRITICAL:
                color = "red"
            elif notification.severity == NotificationSeverity.ERROR:
                color = "bright_red"
            elif notification.severity == NotificationSeverity.WARNING:
                color = "yellow"
            else:
                color = "blue"
            
            click.secho(f"\nNotification: {notification.title}", fg=color, bold=True)
            click.echo(f"ID: {notification.id}")
            click.echo(f"Severity: {notification.severity.value}")
            click.echo(f"Type: {notification.notification_type.value}")
            click.echo(f"Created: {notification.created_at.isoformat()}")
            
            if notification.container_name:
                click.echo(f"Container: {notification.container_name}")
            
            if notification.issue_id:
                click.echo(f"Issue: {notification.issue_id}")
            
            if notification.fix_id:
                click.echo(f"Fix: {notification.fix_id}")
            
            click.echo(f"Message: {notification.message}")
            
            if notification.acknowledged:
                click.echo(f"Acknowledged: Yes, by {notification.acknowledged_by or 'unknown'} at {notification.acknowledged_at.isoformat()}")
            else:
                click.echo("Acknowledged: No")
    except Exception as e:
        logger.error(f"Error listing notifications: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Acknowledge notification command
@notify.command("acknowledge")
@click.argument("notification_id")
@click.option("--user", "-u", help="User acknowledging the notification")
def acknowledge_notification(notification_id, user):
    """Acknowledge a notification."""
    logger.info(f"Acknowledging notification: {notification_id}")
    
    try:
        # Get notification manager
        notification_manager = get_notification_manager()
        
        # Acknowledge notification
        result = notification_manager.acknowledge_notification(notification_id, user)
        
        if result:
            click.secho(f"Notification acknowledged: {notification_id}", fg="green")
        else:
            click.secho(f"Failed to acknowledge notification: {notification_id}", fg="red")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error acknowledging notification: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Clear notifications command
@notify.command("clear")
@click.option("--confirm", is_flag=True, help="Confirm clearing all notifications")
def clear_notifications(confirm):
    """Clear all notifications."""
    logger.info("Clearing notifications")
    
    if not confirm:
        click.confirm("Are you sure you want to clear all notifications?", abort=True)
    
    try:
        # Get notification manager
        notification_manager = get_notification_manager()
        
        # Clear notifications
        notification_manager.clear_history()
        
        click.secho("Notifications cleared", fg="green")
    except Exception as e:
        logger.error(f"Error clearing notifications: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Fix command group
@notify.group()
def fix():
    """Manage fix proposals."""
    pass


# Create fix command
@fix.command("create")
@click.option("--issue", "-i", required=True, help="Issue ID")
@click.option("--title", "-t", required=True, help="Fix title")
@click.option("--description", "-d", required=True, help="Fix description")
@click.option("--risk", "-r", type=click.Choice(["low", "medium", "high"]), default="medium", help="Risk level")
@click.option("--container", "-c", help="Container ID or name")
@click.option("--step", "-s", multiple=True, help="Add a step (format: title|description|command|code|file_path|manual_action|verification)")
@click.option("--notify/--no-notify", default=True, help="Send notification")
def create_fix(issue, title, description, risk, container, step, notify):
    """Create a fix proposal."""
    logger.info(f"Creating fix proposal: {title}")
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Parse steps
        steps = []
        
        for s in step:
            parts = s.split("|")
            
            if len(parts) < 2:
                click.secho(f"Invalid step format: {s}", fg="red")
                click.echo("Format: title|description|command|code|file_path|manual_action|verification")
                sys.exit(1)
            
            step_title = parts[0]
            step_description = parts[1]
            step_command = parts[2] if len(parts) > 2 and parts[2] else None
            step_code = parts[3] if len(parts) > 3 and parts[3] else None
            step_file_path = parts[4] if len(parts) > 4 and parts[4] else None
            step_manual_action = parts[5] if len(parts) > 5 and parts[5] else None
            step_verification = parts[6] if len(parts) > 6 and parts[6] else None
            
            steps.append(FixStep(
                title=step_title,
                description=step_description,
                command=step_command,
                code=step_code,
                file_path=step_file_path,
                manual_action=step_manual_action,
                verification=step_verification,
            ))
        
        # Create fix
        fix = fix_proposal_manager.create_fix(
            issue_id=issue,
            title=title,
            description=description,
            steps=steps,
            risk_level=FixRiskLevel(risk),
            container_id=container,
            container_name=container,
            send_notification=notify,
        )
        
        click.secho(f"Fix proposal created: {fix.id} - {fix.title}", fg="green")
    except Exception as e:
        logger.error(f"Error creating fix proposal: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# List fixes command
@fix.command("list")
@click.option("--status", "-s", type=click.Choice(["proposed", "approved", "rejected", "applied", "failed", "rolled_back"]), help="Filter by status")
@click.option("--issue", "-i", help="Filter by issue ID")
@click.option("--container", "-c", help="Filter by container ID or name")
@click.option("--export", "-e", help="Export fixes to a file")
def list_fixes(status, issue, container, export):
    """List fix proposals."""
    logger.info("Listing fix proposals")
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Convert string status to enum if provided
        status_enum = None
        if status:
            status_enum = FixStatus(status)
        
        # Get fixes
        if issue:
            fixes = fix_proposal_manager.get_fixes_for_issue(issue)
        elif container:
            fixes = fix_proposal_manager.get_fixes_for_container(container)
        else:
            fixes = fix_proposal_manager.get_all_fixes(status_enum)
        
        # Filter by status if needed
        if status_enum and (issue or container):
            fixes = [fix for fix in fixes if fix.status == status_enum]
        
        # Export if requested
        if export:
            import json
            
            with open(export, "w") as f:
                json.dump([fix.to_dict() for fix in fixes], f, indent=2)
            
            click.secho(f"Exported {len(fixes)} fixes to {export}", fg="green")
            return
        
        # Print fixes
        if not fixes:
            click.echo("No fixes found")
            return
        
        click.secho(f"Found {len(fixes)} fixes", fg="blue", bold=True)
        
        for fix in fixes:
            # Determine color based on status
            if fix.status == FixStatus.APPLIED:
                color = "green"
            elif fix.status == FixStatus.FAILED:
                color = "red"
            elif fix.status == FixStatus.REJECTED:
                color = "bright_red"
            elif fix.status == FixStatus.APPROVED:
                color = "blue"
            elif fix.status == FixStatus.ROLLED_BACK:
                color = "yellow"
            else:
                color = "white"
            
            click.secho(f"\nFix: {fix.title}", fg=color, bold=True)
            click.echo(f"ID: {fix.id}")
            click.echo(f"Issue: {fix.issue_id}")
            click.echo(f"Status: {fix.status.value}")
            click.echo(f"Risk Level: {fix.risk_level.value}")
            click.echo(f"Created: {fix.created_at.isoformat()}")
            
            if fix.container_name:
                click.echo(f"Container: {fix.container_name}")
            
            click.echo(f"Description: {fix.description}")
            
            click.secho("Steps:", fg="blue")
            for i, step in enumerate(fix.steps):
                click.echo(f"  {i+1}. {step.title}")
                click.echo(f"     {step.description}")
                
                if step.command:
                    click.echo(f"     Command: {step.command}")
                
                if step.file_path:
                    click.echo(f"     File: {step.file_path}")
                
                if step.manual_action:
                    click.echo(f"     Manual Action: {step.manual_action}")
            
            if fix.status == FixStatus.APPROVED:
                click.echo(f"Approved: {fix.approved_at.isoformat()} by {fix.approved_by or 'unknown'}")
            
            if fix.status == FixStatus.REJECTED:
                click.echo(f"Rejected: {fix.rejected_at.isoformat()} by {fix.rejected_by or 'unknown'}")
                
                if fix.metadata.get("rejection_reason"):
                    click.echo(f"Reason: {fix.metadata['rejection_reason']}")
            
            if fix.status == FixStatus.APPLIED:
                click.echo(f"Applied: {fix.applied_at.isoformat()}")
    except Exception as e:
        logger.error(f"Error listing fixes: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Show fix command
@fix.command("show")
@click.argument("fix_id")
def show_fix(fix_id):
    """Show details of a fix proposal."""
    logger.info(f"Showing fix proposal: {fix_id}")
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Get fix
        fix = fix_proposal_manager.get_fix(fix_id)
        
        if not fix:
            click.secho(f"Fix not found: {fix_id}", fg="red")
            sys.exit(1)
        
        # Determine color based on status
        if fix.status == FixStatus.APPLIED:
            color = "green"
        elif fix.status == FixStatus.FAILED:
            color = "red"
        elif fix.status == FixStatus.REJECTED:
            color = "bright_red"
        elif fix.status == FixStatus.APPROVED:
            color = "blue"
        elif fix.status == FixStatus.ROLLED_BACK:
            color = "yellow"
        else:
            color = "white"
        
        click.secho(f"Fix: {fix.title}", fg=color, bold=True)
        click.echo(f"ID: {fix.id}")
        click.echo(f"Issue: {fix.issue_id}")
        click.echo(f"Status: {fix.status.value}")
        click.echo(f"Risk Level: {fix.risk_level.value}")
        click.echo(f"Created: {fix.created_at.isoformat()}")
        click.echo(f"Updated: {fix.updated_at.isoformat()}")
        
        if fix.container_id:
            click.echo(f"Container ID: {fix.container_id}")
        
        if fix.container_name:
            click.echo(f"Container Name: {fix.container_name}")
        
        click.echo(f"\nDescription: {fix.description}")
        
        click.secho("\nSteps:", fg="blue", bold=True)
        for i, step in enumerate(fix.steps):
            click.secho(f"  {i+1}. {step.title}", fg="blue")
            click.echo(f"     Description: {step.description}")
            
            if step.command:
                click.echo(f"     Command: {step.command}")
            
            if step.code:
                click.echo(f"     Code: {step.code}")
            
            if step.file_path:
                click.echo(f"     File: {step.file_path}")
            
            if step.manual_action:
                click.echo(f"     Manual Action: {step.manual_action}")
            
            if step.verification:
                click.echo(f"     Verification: {step.verification}")
        
        if fix.status == FixStatus.APPROVED:
            click.secho("\nApproval:", fg="blue", bold=True)
            click.echo(f"  Approved At: {fix.approved_at.isoformat()}")
            click.echo(f"  Approved By: {fix.approved_by or 'unknown'}")
        
        if fix.status == FixStatus.REJECTED:
            click.secho("\nRejection:", fg="blue", bold=True)
            click.echo(f"  Rejected At: {fix.rejected_at.isoformat()}")
            click.echo(f"  Rejected By: {fix.rejected_by or 'unknown'}")
            
            if fix.metadata.get("rejection_reason"):
                click.echo(f"  Reason: {fix.metadata['rejection_reason']}")
        
        if fix.status in [FixStatus.APPLIED, FixStatus.FAILED, FixStatus.ROLLED_BACK] and fix.result:
            click.secho("\nResult:", fg="blue", bold=True)
            
            if fix.status == FixStatus.APPLIED:
                click.echo(f"  Applied At: {fix.applied_at.isoformat()}")
            
            if fix.result.get("success") is not None:
                success = fix.result["success"]
                click.echo(f"  Success: {success}")
            
            if fix.result.get("dry_run") is not None:
                click.echo(f"  Dry Run: {fix.result['dry_run']}")
            
            if fix.result.get("error"):
                click.echo(f"  Error: {fix.result['error']}")
            
            if fix.result.get("steps"):
                click.secho("\n  Step Results:", fg="blue")
                
                for i, step_result in enumerate(fix.result["steps"]):
                    step_title = step_result.get("title", f"Step {i+1}")
                    step_success = step_result.get("success", False)
                    
                    if step_success:
                        step_color = "green"
                    else:
                        step_color = "red"
                    
                    click.secho(f"    {i+1}. {step_title}: {'Success' if step_success else 'Failed'}", fg=step_color)
                    
                    if step_result.get("error"):
                        click.echo(f"       Error: {step_result['error']}")
                    
                    if step_result.get("command"):
                        click.echo(f"       Command: {step_result['command']}")
                    
                    if step_result.get("file_path"):
                        click.echo(f"       File: {step_result['file_path']}")
                    
                    if step_result.get("backup_path"):
                        click.echo(f"       Backup: {step_result['backup_path']}")
                    
                    if step_result.get("verification"):
                        verification = step_result["verification"]
                        verification_success = verification.get("success", False)
                        
                        if verification_success:
                            verification_color = "green"
                        else:
                            verification_color = "red"
                        
                        click.secho(f"       Verification: {'Success' if verification_success else 'Failed'}", fg=verification_color)
                        
                        if verification.get("error"):
                            click.echo(f"         Error: {verification['error']}")
                        
                        if verification.get("note"):
                            click.echo(f"         Note: {verification['note']}")
    except Exception as e:
        logger.error(f"Error showing fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Approve fix command
@fix.command("approve")
@click.argument("fix_id")
@click.option("--user", "-u", help="User approving the fix")
def approve_fix(fix_id, user):
    """Approve a fix proposal."""
    logger.info(f"Approving fix proposal: {fix_id}")
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Approve fix
        result = fix_proposal_manager.approve_fix(fix_id, user)
        
        if result:
            click.secho(f"Fix approved: {fix_id}", fg="green")
        else:
            click.secho(f"Failed to approve fix: {fix_id}", fg="red")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error approving fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Reject fix command
@fix.command("reject")
@click.argument("fix_id")
@click.option("--user", "-u", help="User rejecting the fix")
@click.option("--reason", "-r", help="Reason for rejection")
def reject_fix(fix_id, user, reason):
    """Reject a fix proposal."""
    logger.info(f"Rejecting fix proposal: {fix_id}")
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Reject fix
        result = fix_proposal_manager.reject_fix(fix_id, user, reason)
        
        if result:
            click.secho(f"Fix rejected: {fix_id}", fg="green")
        else:
            click.secho(f"Failed to reject fix: {fix_id}", fg="red")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error rejecting fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Apply fix command
@fix.command("apply")
@click.argument("fix_id")
@click.option("--dry-run", "-d", is_flag=True, help="Perform a dry run")
def apply_fix(fix_id, dry_run):
    """Apply a fix proposal."""
    logger.info(f"Applying fix proposal: {fix_id}")
    
    try:
        # Get fix applier
        fix_applier = get_fix_applier()
        
        # Apply fix
        result = fix_applier.apply_fix(fix_id, dry_run)
        
        if result["success"]:
            if dry_run:
                click.secho(f"Dry run of fix successful: {fix_id}", fg="green")
            else:
                click.secho(f"Fix applied successfully: {fix_id}", fg="green")
        else:
            if dry_run:
                click.secho(f"Dry run of fix failed: {fix_id}", fg="red")
            else:
                click.secho(f"Fix application failed: {fix_id}", fg="red")
            
            if result.get("error"):
                click.echo(f"Error: {result['error']}")
            
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error applying fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Rollback fix command
@fix.command("rollback")
@click.argument("fix_id")
def rollback_fix(fix_id):
    """Roll back an applied fix."""
    logger.info(f"Rolling back fix: {fix_id}")
    
    try:
        # Get fix applier
        fix_applier = get_fix_applier()
        
        # Rollback fix
        result = fix_applier.rollback_fix(fix_id)
        
        if result["success"]:
            click.secho(f"Fix rolled back successfully: {fix_id}", fg="green")
        else:
            if result.get("partial"):
                click.secho(f"Fix partially rolled back with errors: {fix_id}", fg="yellow")
            else:
                click.secho(f"Fix rollback failed: {fix_id}", fg="red")
            
            if result.get("error"):
                click.echo(f"Error: {result['error']}")
            
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error rolling back fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Delete fix command
@fix.command("delete")
@click.argument("fix_id")
@click.option("--confirm", is_flag=True, help="Confirm deletion")
def delete_fix(fix_id, confirm):
    """Delete a fix proposal."""
    logger.info(f"Deleting fix proposal: {fix_id}")
    
    if not confirm:
        click.confirm(f"Are you sure you want to delete fix {fix_id}?", abort=True)
    
    try:
        # Get fix proposal manager
        fix_proposal_manager = get_fix_proposal_manager()
        
        # Delete fix
        result = fix_proposal_manager.delete_fix(fix_id)
        
        if result:
            click.secho(f"Fix deleted: {fix_id}", fg="green")
        else:
            click.secho(f"Failed to delete fix: {fix_id}", fg="red")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error deleting fix: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)
