"""
Test module for DockerForge notifications and fixes.

This module provides tests for the notification and fix functionality.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.fixes.fix_proposal import (
    FixProposal,
    FixProposalManager,
    FixRiskLevel,
    FixStatus,
    FixStep,
)
from src.notifications.notification_manager import (
    Notification,
    NotificationManager,
    NotificationSeverity,
    NotificationType,
)
from src.notifications.preference_manager import PreferenceManager, UserPreferences
from src.notifications.template_manager import NotificationTemplate, TemplateManager


# Notification Manager Tests
class TestNotificationManager:
    """Tests for the NotificationManager class."""

    @pytest.fixture
    def notification_manager(self):
        """Create a notification manager for testing."""
        with patch(
            "src.notifications.notification_manager.get_config"
        ) as mock_get_config:
            # Mock configuration
            mock_get_config.return_value = tempfile.mkdtemp()

            # Create notification manager
            manager = NotificationManager()

            # Mock notifiers
            manager._notifiers = {
                "email": MagicMock(),
                "slack": MagicMock(),
                "discord": MagicMock(),
                "webhook": MagicMock(),
            }

            # Return manager
            yield manager

    def test_create_notification(self):
        """Test creating a notification."""
        # Create notification
        notification = Notification(
            title="Test Notification",
            message="This is a test notification",
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.CUSTOM,
        )

        # Check notification
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test notification"
        assert notification.severity == NotificationSeverity.INFO
        assert notification.notification_type == NotificationType.CUSTOM
        assert notification.id is not None
        assert notification.created_at is not None
        assert notification.acknowledged is False
        assert notification.acknowledged_at is None
        assert notification.acknowledged_by is None

    def test_send_notification(self, notification_manager):
        """Test sending a notification."""
        # Mock notifiers
        for notifier in notification_manager._notifiers.values():
            notifier.send.return_value = True

        # Create notification
        notification = Notification(
            title="Test Notification",
            message="This is a test notification",
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.CUSTOM,
        )

        # Send notification
        result = notification_manager.send_notification(notification)

        # Check result
        assert result is True

        # Check that notifiers were called
        for notifier in notification_manager._notifiers.values():
            notifier.send.assert_called_once_with(notification)

    def test_get_notifications(self, notification_manager):
        """Test getting notifications."""
        # Create notifications
        notification1 = Notification(
            title="Test Notification 1",
            message="This is test notification 1",
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.CUSTOM,
        )

        notification2 = Notification(
            title="Test Notification 2",
            message="This is test notification 2",
            severity=NotificationSeverity.WARNING,
            notification_type=NotificationType.CONTAINER_EXIT,
            container_id="test-container",
            container_name="test-container",
        )

        # Add notifications to manager
        notification_manager._notifications = {
            notification1.id: notification1,
            notification2.id: notification2,
        }

        # Get all notifications
        notifications = notification_manager.get_notifications()
        assert len(notifications) == 2

        # Get notifications by severity
        notifications = notification_manager.get_notifications(
            severity=NotificationSeverity.INFO
        )
        assert len(notifications) == 1
        assert notifications[0].severity == NotificationSeverity.INFO

        # Get notifications by type
        notifications = notification_manager.get_notifications(
            notification_type=NotificationType.CONTAINER_EXIT
        )
        assert len(notifications) == 1
        assert notifications[0].notification_type == NotificationType.CONTAINER_EXIT

        # Get notifications by container
        notifications = notification_manager.get_notifications(
            container_id="test-container"
        )
        assert len(notifications) == 1
        assert notifications[0].container_id == "test-container"

    def test_acknowledge_notification(self, notification_manager):
        """Test acknowledging a notification."""
        # Create notification
        notification = Notification(
            title="Test Notification",
            message="This is a test notification",
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.CUSTOM,
        )

        # Add notification to manager
        notification_manager._notifications = {
            notification.id: notification,
        }

        # Acknowledge notification
        result = notification_manager.acknowledge_notification(
            notification.id, "test-user"
        )

        # Check result
        assert result is True

        # Check notification
        assert notification.acknowledged is True
        assert notification.acknowledged_at is not None
        assert notification.acknowledged_by == "test-user"


# Preference Manager Tests
class TestPreferenceManager:
    """Tests for the PreferenceManager class."""

    @pytest.fixture
    def preference_manager(self):
        """Create a preference manager for testing."""
        with patch(
            "src.notifications.preference_manager.get_config"
        ) as mock_get_config:
            # Mock configuration
            mock_get_config.return_value = tempfile.mkdtemp()

            # Create preference manager
            manager = PreferenceManager()

            # Return manager
            yield manager

    def test_create_user_preferences(self):
        """Test creating user preferences."""
        # Create preferences
        preferences = UserPreferences(
            user_id="test-user",
            name="Test User",
            email="test@example.com",
        )

        # Check preferences
        assert preferences.user_id == "test-user"
        assert preferences.name == "Test User"
        assert preferences.email == "test@example.com"
        assert preferences.enabled_channels == []
        assert preferences.severity_thresholds == {
            "info": False,
            "warning": True,
            "error": True,
            "critical": True,
        }
        assert preferences.notification_types == {
            "container_exit": True,
            "container_oom": True,
            "high_resource_usage": True,
            "security_issue": True,
            "update_available": True,
            "fix_proposal": True,
            "fix_applied": True,
            "custom": True,
        }
        assert preferences.quiet_hours == {
            "enabled": False,
            "start": "22:00",
            "end": "08:00",
        }
        assert preferences.container_filters == []

    def test_should_notify(self):
        """Test should_notify method."""
        # Create preferences
        preferences = UserPreferences(
            user_id="test-user",
            name="Test User",
            email="test@example.com",
        )

        # Test severity thresholds
        assert (
            preferences.should_notify(
                NotificationSeverity.INFO, NotificationType.CUSTOM
            )
            is False
        )
        assert (
            preferences.should_notify(
                NotificationSeverity.WARNING, NotificationType.CUSTOM
            )
            is True
        )
        assert (
            preferences.should_notify(
                NotificationSeverity.ERROR, NotificationType.CUSTOM
            )
            is True
        )
        assert (
            preferences.should_notify(
                NotificationSeverity.CRITICAL, NotificationType.CUSTOM
            )
            is True
        )

        # Test notification types
        preferences.notification_types["custom"] = False
        assert (
            preferences.should_notify(
                NotificationSeverity.WARNING, NotificationType.CUSTOM
            )
            is False
        )

        # Test container filters
        preferences.notification_types["custom"] = True
        preferences.container_filters = ["test-container"]
        assert (
            preferences.should_notify(
                NotificationSeverity.WARNING, NotificationType.CUSTOM, "test-container"
            )
            is True
        )
        assert (
            preferences.should_notify(
                NotificationSeverity.WARNING, NotificationType.CUSTOM, "other-container"
            )
            is False
        )

    def test_get_set_preferences(self, preference_manager):
        """Test getting and setting preferences."""
        # Create preferences
        preferences = UserPreferences(
            user_id="test-user",
            name="Test User",
            email="test@example.com",
        )

        # Set preferences
        preference_manager.set_preferences(preferences)

        # Get preferences
        result = preference_manager.get_preferences("test-user")

        # Check result
        assert result is not None
        assert result.user_id == "test-user"
        assert result.name == "Test User"
        assert result.email == "test@example.com"

    def test_get_users_for_notification(self, preference_manager):
        """Test getting users for a notification."""
        # Create preferences
        preferences1 = UserPreferences(
            user_id="user1",
            name="User 1",
            email="user1@example.com",
        )

        preferences2 = UserPreferences(
            user_id="user2",
            name="User 2",
            email="user2@example.com",
        )

        # Modify preferences
        preferences2.severity_thresholds["info"] = True

        # Set preferences
        preference_manager._preferences = {
            "user1": preferences1,
            "user2": preferences2,
        }

        # Get users for notification
        users = preference_manager.get_users_for_notification(
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.CUSTOM,
        )

        # Check result
        assert len(users) == 1
        assert users[0] == "user2"


# Template Manager Tests
class TestTemplateManager:
    """Tests for the TemplateManager class."""

    @pytest.fixture
    def template_manager(self):
        """Create a template manager for testing."""
        with patch("src.notifications.template_manager.get_config") as mock_get_config:
            # Mock configuration
            mock_get_config.return_value = tempfile.mkdtemp()

            # Create template manager
            manager = TemplateManager()

            # Return manager
            yield manager

    def test_create_notification_template(self):
        """Test creating a notification template."""
        # Create template
        template = NotificationTemplate(
            template_id="test-template",
            name="Test Template",
            description="This is a test template",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}",
        )

        # Check template
        assert template.template_id == "test-template"
        assert template.name == "Test Template"
        assert template.description == "This is a test template"
        assert (
            template.html_template
            == "<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>"
        )
        assert template.text_template == "{{ title }}\n\n{{ message }}"

    def test_render_template(self):
        """Test rendering a template."""
        # Create template
        template = NotificationTemplate(
            template_id="test-template",
            name="Test Template",
            description="This is a test template",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}",
        )

        # Render HTML template
        html = template.render(
            "html",
            {
                "title": "Test Title",
                "message": "Test Message",
            },
        )

        # Check HTML
        assert (
            html == "<html><body><h1>Test Title</h1><p>Test Message</p></body></html>"
        )

        # Render text template
        text = template.render(
            "text",
            {
                "title": "Test Title",
                "message": "Test Message",
            },
        )

        # Check text
        assert text == "Test Title\n\nTest Message"

    def test_get_template(self, template_manager):
        """Test getting a template."""
        # Create template
        template = NotificationTemplate(
            template_id="test-template",
            name="Test Template",
            description="This is a test template",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}",
        )

        # Add template to manager
        template_manager._templates = {
            "test-template": template,
        }

        # Get template
        result = template_manager.get_template("test-template")

        # Check result
        assert result is not None
        assert result.template_id == "test-template"
        assert result.name == "Test Template"

    def test_render_template_manager(self, template_manager):
        """Test rendering a template using the manager."""
        # Create template
        template = NotificationTemplate(
            template_id="test-template",
            name="Test Template",
            description="This is a test template",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}",
        )

        # Add template to manager
        template_manager._templates = {
            "test-template": template,
        }

        # Render template
        result = template_manager.render_template(
            "test-template",
            "html",
            {
                "title": "Test Title",
                "message": "Test Message",
            },
        )

        # Check result
        assert (
            result == "<html><body><h1>Test Title</h1><p>Test Message</p></body></html>"
        )


# Fix Proposal Tests
class TestFixProposal:
    """Tests for the FixProposal class."""

    def test_create_fix_step(self):
        """Test creating a fix step."""
        # Create step
        step = FixStep(
            title="Test Step",
            description="This is a test step",
            command="echo 'Hello, World!'",
        )

        # Check step
        assert step.title == "Test Step"
        assert step.description == "This is a test step"
        assert step.command == "echo 'Hello, World!'"
        assert step.code is None
        assert step.file_path is None
        assert step.manual_action is None
        assert step.verification is None

    def test_create_fix_proposal(self):
        """Test creating a fix proposal."""
        # Create steps
        steps = [
            FixStep(
                title="Test Step 1",
                description="This is test step 1",
                command="echo 'Step 1'",
            ),
            FixStep(
                title="Test Step 2",
                description="This is test step 2",
                command="echo 'Step 2'",
            ),
        ]

        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=steps,
            risk_level=FixRiskLevel.LOW,
        )

        # Check fix
        assert fix.issue_id == "test-issue"
        assert fix.title == "Test Fix"
        assert fix.description == "This is a test fix"
        assert len(fix.steps) == 2
        assert fix.risk_level == FixRiskLevel.LOW
        assert fix.status == FixStatus.PROPOSED
        assert fix.created_at is not None
        assert fix.updated_at is not None
        assert fix.approved_at is None
        assert fix.approved_by is None
        assert fix.rejected_at is None
        assert fix.rejected_by is None
        assert fix.applied_at is None
        assert fix.result is None

    def test_approve_fix(self):
        """Test approving a fix."""
        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        # Approve fix
        fix.approve("test-user")

        # Check fix
        assert fix.status == FixStatus.APPROVED
        assert fix.approved_at is not None
        assert fix.approved_by == "test-user"

    def test_reject_fix(self):
        """Test rejecting a fix."""
        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        # Reject fix
        fix.reject("test-user")

        # Check fix
        assert fix.status == FixStatus.REJECTED
        assert fix.rejected_at is not None
        assert fix.rejected_by == "test-user"

    def test_mark_as_applied(self):
        """Test marking a fix as applied."""
        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        # Mark as applied
        result = {"success": True}
        fix.mark_as_applied(result)

        # Check fix
        assert fix.status == FixStatus.APPLIED
        assert fix.applied_at is not None
        assert fix.result == result


# Fix Proposal Manager Tests
class TestFixProposalManager:
    """Tests for the FixProposalManager class."""

    @pytest.fixture
    def fix_proposal_manager(self):
        """Create a fix proposal manager for testing."""
        with patch("src.fixes.fix_proposal.get_config") as mock_get_config:
            # Mock configuration
            mock_get_config.return_value = tempfile.mkdtemp()

            # Create fix proposal manager
            manager = FixProposalManager()

            # Mock notification manager
            with patch(
                "src.fixes.fix_proposal.get_notification_manager"
            ) as mock_get_notification_manager:
                mock_get_notification_manager.return_value = MagicMock()

                # Return manager
                yield manager

    def test_create_fix(self, fix_proposal_manager):
        """Test creating a fix."""
        # Create steps
        steps = [
            FixStep(
                title="Test Step 1",
                description="This is test step 1",
                command="echo 'Step 1'",
            ),
            FixStep(
                title="Test Step 2",
                description="This is test step 2",
                command="echo 'Step 2'",
            ),
        ]

        # Create fix
        fix = fix_proposal_manager.create_fix(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=steps,
            risk_level=FixRiskLevel.LOW,
            send_notification=False,
        )

        # Check fix
        assert fix.issue_id == "test-issue"
        assert fix.title == "Test Fix"
        assert fix.description == "This is a test fix"
        assert len(fix.steps) == 2
        assert fix.risk_level == FixRiskLevel.LOW
        assert fix.status == FixStatus.PROPOSED

        # Check that fix was added to manager
        assert fix.id in fix_proposal_manager._fixes

    def test_get_fix(self, fix_proposal_manager):
        """Test getting a fix."""
        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        # Add fix to manager
        fix_proposal_manager._fixes = {
            fix.id: fix,
        }

        # Get fix
        result = fix_proposal_manager.get_fix(fix.id)

        # Check result
        assert result is not None
        assert result.id == fix.id
        assert result.title == "Test Fix"

    def test_get_fixes_for_issue(self, fix_proposal_manager):
        """Test getting fixes for an issue."""
        # Create fixes
        fix1 = FixProposal(
            issue_id="issue1",
            title="Fix 1",
            description="This is fix 1",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        fix2 = FixProposal(
            issue_id="issue2",
            title="Fix 2",
            description="This is fix 2",
            steps=[],
            risk_level=FixRiskLevel.MEDIUM,
        )

        fix3 = FixProposal(
            issue_id="issue1",
            title="Fix 3",
            description="This is fix 3",
            steps=[],
            risk_level=FixRiskLevel.HIGH,
        )

        # Add fixes to manager
        fix_proposal_manager._fixes = {
            fix1.id: fix1,
            fix2.id: fix2,
            fix3.id: fix3,
        }

        # Get fixes for issue
        fixes = fix_proposal_manager.get_fixes_for_issue("issue1")

        # Check result
        assert len(fixes) == 2
        assert fixes[0].issue_id == "issue1"
        assert fixes[1].issue_id == "issue1"

    def test_approve_fix(self, fix_proposal_manager):
        """Test approving a fix."""
        # Create fix
        fix = FixProposal(
            issue_id="test-issue",
            title="Test Fix",
            description="This is a test fix",
            steps=[],
            risk_level=FixRiskLevel.LOW,
        )

        # Add fix to manager
        fix_proposal_manager._fixes = {
            fix.id: fix,
        }

        # Approve fix
        result = fix_proposal_manager.approve_fix(fix.id, "test-user")

        # Check result
        assert result is True

        # Check fix
        assert fix.status == FixStatus.APPROVED
        assert fix.approved_at is not None
        assert fix.approved_by == "test-user"
