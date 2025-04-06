"""
Chat handler for DockerForge AI assistant.

This module handles the processing of chat messages and generating responses.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from src.backup.checkpoint_manager import get_checkpoint_manager
from src.monitoring.issue_detector import get_issue_detector
from src.monitoring.log_analyzer import get_log_analyzer
from src.security.security_reporter import get_security_reporter
from src.security.vulnerability_scanner import get_vulnerability_scanner

from .ai_provider import get_ai_provider
from .prompt_template import PromptTemplate

logger = logging.getLogger(__name__)


class ChatHandler:
    """
    Handler for chat messages and responses.

    This class processes user messages and generates AI responses.
    """

    def __init__(self):
        """
        Initialize the chat handler.
        """
        # Use the configured AI provider
        from src.core.ai_provider import get_ai_provider

        self.ai_provider = get_ai_provider()

        # Load prompt templates
        self.general_template = PromptTemplate.from_file("general_chat")
        self.container_template = PromptTemplate.from_file("container_chat")
        self.image_template = PromptTemplate.from_file("image_chat")
        self.troubleshooting_template = PromptTemplate.from_file("troubleshooting_chat")
        self.security_template = PromptTemplate.from_file("security_chat")

        # Initialize related systems
        self.checkpoint_manager = get_checkpoint_manager()
        self.vulnerability_scanner = get_vulnerability_scanner()
        self.security_reporter = get_security_reporter()
        self.log_analyzer = get_log_analyzer()
        self.issue_detector = get_issue_detector()

        # Track workflow states for security and troubleshooting resolutions
        self.active_workflows = {}

    def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[str]]:
        """
        Process a user message and generate a response.

        Args:
            message: The user message text
            context: Optional contextual information

        Returns:
            A tuple containing (response_text, suggested_responses)
        """
        # Check if this is part of an active workflow
        workflow_id = context.get("workflow_id") if context else None
        if workflow_id and workflow_id in self.active_workflows:
            workflow_type = self.active_workflows[workflow_id].get("type")
            if workflow_type == "vulnerability_fix":
                return self._process_security_workflow_step(
                    message, workflow_id, context
                )
            elif workflow_type == "container_troubleshooting":
                return self._process_container_workflow_step(
                    message, workflow_id, context
                )

        # Select the appropriate template based on context
        template = self._select_template(message, context)

        # Build prompt with context
        prompt = self._build_prompt(template, message, context)

        # Get response from AI provider
        response = self.ai_provider.generate_text(prompt)

        # Generate suggested responses based on the message and context
        suggestions = self._generate_suggestions(message, context)

        return response, suggestions

    def _select_template(
        self, message: str, context: Optional[Dict[str, Any]]
    ) -> PromptTemplate:
        """
        Select the appropriate template based on the message and context.

        Args:
            message: The user message text
            context: Optional contextual information

        Returns:
            The selected prompt template
        """
        # Check if this is a security-related message or context
        security_keywords = [
            "vulnerability",
            "security",
            "cve",
            "exploit",
            "patch",
            "fix",
            "secure",
            "risk",
        ]

        # Check context for security-related properties
        is_security_context = False
        if context:
            if context.get("current_page") == "security":
                is_security_context = True

            if context.get("vulnerability_id") or context.get("recommendation_id"):
                is_security_context = True

            # If we have vulnerability data, return security template
            if any(
                key in context
                for key in [
                    "vulnerability_id",
                    "vulnerability_severity",
                    "vulnerability_description",
                    "affected_package",
                    "fixed_version",
                    "cve_id",
                ]
            ):
                return self.security_template

        # Check if the message contains security keywords
        if any(keyword in message.lower() for keyword in security_keywords):
            return self.security_template

        # Check if we have context about the current page
        if context and context.get("current_page"):
            page = context.get("current_page")

            # Container-specific template
            if page == "containers" or message.lower().find("container") >= 0:
                return self.container_template

            # Image-specific template
            if page == "images" or message.lower().find("image") >= 0:
                return self.image_template

        # Check for troubleshooting keywords
        troubleshooting_keywords = [
            "error",
            "issue",
            "problem",
            "fail",
            "crash",
            "debug",
            "troubleshoot",
        ]
        if any(keyword in message.lower() for keyword in troubleshooting_keywords):
            return self.troubleshooting_template

        # Default to general template
        return self.general_template

    def _build_prompt(
        self, template: PromptTemplate, message: str, context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build a prompt with context for the AI provider.

        Args:
            template: The prompt template to use
            message: The user message text
            context: Optional contextual information

        Returns:
            The formatted prompt
        """
        # Default variables
        variables = {
            "user_message": message,
            "current_page": "unknown",
            "container_id": "none",
            "image_id": "none",
            "vulnerability_id": "none",
            "vulnerability_severity": "none",
            "vulnerability_description": "none",
            "affected_package": "none",
            "current_version": "none",
            "fixed_version": "none",
            "cve_id": "none",
            "recommendation_id": "none",
        }

        # Update with context if available
        if context:
            variables.update(
                {
                    "current_page": context.get("current_page", "unknown"),
                    "container_id": context.get("current_container_id", "none"),
                    "image_id": context.get("current_image_id", "none"),
                }
            )

            # Add security context if available
            if context.get("vulnerability_id"):
                variables.update(
                    {
                        "vulnerability_id": context.get("vulnerability_id", "none"),
                        "vulnerability_severity": context.get(
                            "vulnerability_severity", "none"
                        ),
                        "vulnerability_description": context.get(
                            "vulnerability_description", "none"
                        ),
                        "affected_package": context.get("affected_package", "none"),
                        "current_version": context.get("current_version", "none"),
                        "fixed_version": context.get("fixed_version", "none"),
                        "cve_id": context.get("cve_id", "none"),
                    }
                )

            if context.get("recommendation_id"):
                variables["recommendation_id"] = context.get(
                    "recommendation_id", "none"
                )

            # Add any additional context data
            if context.get("additional_data"):
                variables.update(context.get("additional_data"))

        # Render the template with the variables
        return template.render(**variables)

    def _generate_suggestions(
        self, message: str, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate suggested responses based on the message and context.

        Args:
            message: The user message text
            context: Optional contextual information

        Returns:
            A list of suggested responses
        """
        suggestions = []

        # Page-specific suggestions
        if context and context.get("current_page"):
            page = context.get("current_page")

            if page == "containers":
                suggestions.extend(
                    [
                        "Show me the logs for this container",
                        "What's using the most CPU in this container?",
                        "How can I optimize this container?",
                    ]
                )

            elif page == "images":
                suggestions.extend(
                    [
                        "Are there any security vulnerabilities in this image?",
                        "Show me how to optimize this Dockerfile",
                        "What are the tags for this image?",
                    ]
                )

            elif page == "volumes":
                suggestions.extend(
                    [
                        "Which containers are using this volume?",
                        "How can I back up this volume?",
                        "Show me the data in this volume",
                    ]
                )

            elif page == "security":
                suggestions.extend(
                    [
                        "How do I fix these vulnerabilities?",
                        "Explain the impact of this security issue",
                        "Create a security fix workflow",
                    ]
                )

        # Security vulnerability context
        if context and (
            context.get("vulnerability_id") or context.get("recommendation_id")
        ):
            suggestions = [
                "Show me how to fix this vulnerability",
                "What's the impact of this vulnerability?",
                "Create a checkpoint before applying fixes",
            ]
            return suggestions

        # General suggestions based on keywords in the message
        if "error" in message.lower() or "issue" in message.lower():
            suggestions.append("How can I troubleshoot this issue?")

        if "docker" in message.lower() and "compose" in message.lower():
            suggestions.append("Show me best practices for Docker Compose")

        if "security" in message.lower() or "vulnerability" in message.lower():
            suggestions.append("How can I improve Docker security?")

        # Add some default suggestions if we don't have enough
        if len(suggestions) < 3:
            default_suggestions = [
                "Show me Docker best practices",
                "How can I monitor my containers?",
                "Explain Docker networking",
                "Tell me about Docker volumes",
            ]

            # Add default suggestions until we have at least 3
            for suggestion in default_suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
                    if len(suggestions) >= 3:
                        break

        # Return no more than 3 suggestions
        return suggestions[:3]

    def _process_security_workflow_step(
        self, message: str, workflow_id: str, context: Optional[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """
        Process a step in an active security workflow.

        Args:
            message: The user message text
            workflow_id: The ID of the active workflow
            context: Optional contextual information

        Returns:
            A tuple containing (response_text, suggested_responses)
        """
        workflow = self.active_workflows[workflow_id]
        current_step = workflow.get("current_step", 0)

        # Process confirmation/response based on the current step
        if (
            "yes" in message.lower()
            or "confirm" in message.lower()
            or "proceed" in message.lower()
        ):
            # User confirmed the action, proceed to next step
            if current_step == 1:  # Create checkpoint confirmation
                # Create a checkpoint before applying fixes
                checkpoint_id = self._create_security_checkpoint(workflow)
                workflow["checkpoint_id"] = checkpoint_id

                response = f"Checkpoint created successfully with ID: {checkpoint_id}. I'll now proceed with applying the recommended fixes for the vulnerability."

                # Move to next step
                workflow["current_step"] = 2
                suggestions = [
                    "Proceed with fixes",
                    "Show me details first",
                    "Cancel fix workflow",
                ]

            elif current_step == 2:  # Apply fixes confirmation
                # Apply the security fixes
                result = self._apply_security_fixes(workflow)

                if result.get("success", False):
                    response = f"The security fixes were successfully applied! The vulnerability has been addressed by updating {workflow.get('affected_package')} from {workflow.get('current_version')} to {workflow.get('fixed_version')}."

                    # Clean up workflow
                    del self.active_workflows[workflow_id]
                    suggestions = [
                        "Verify the fix",
                        "Run security scan",
                        "Show me other vulnerabilities",
                    ]
                else:
                    response = f"There was an issue applying the security fixes: {result.get('error', 'Unknown error')}. Would you like to restore from the checkpoint?"
                    workflow["current_step"] = 3
                    suggestions = [
                        "Restore from checkpoint",
                        "Try again",
                        "Cancel and exit workflow",
                    ]

            elif current_step == 3:  # Restore confirmation
                # Restore from checkpoint
                checkpoint_id = workflow.get("checkpoint_id")
                if checkpoint_id:
                    result = self._restore_from_checkpoint(checkpoint_id)

                    if result.get("success", False):
                        response = "Successfully restored from checkpoint. The system has been returned to its state before the fix attempt."
                    else:
                        response = f"There was an issue restoring from checkpoint: {result.get('error', 'Unknown error')}."
                else:
                    response = "No checkpoint was created, unable to restore."

                # Clean up workflow
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Try a different approach",
                    "Explain the issue again",
                    "Run security scan",
                ]

            else:
                response = (
                    "I'm not sure what to do at this step. Let's restart the workflow."
                )
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Start new security workflow",
                    "Show security dashboard",
                    "Run security scan",
                ]

        elif (
            "no" in message.lower()
            or "cancel" in message.lower()
            or "stop" in message.lower()
        ):
            # User canceled or rejected the action
            response = (
                "Security fix workflow canceled. No changes were made to your system."
            )

            # Clean up workflow
            del self.active_workflows[workflow_id]
            suggestions = [
                "Show security dashboard",
                "Run security scan",
                "Show me other vulnerabilities",
            ]

        else:
            # User provided some other input, provide help based on current step
            if current_step == 1:
                response = "To proceed with creating a checkpoint before applying security fixes, please confirm with 'yes' or 'proceed'. If you want to cancel, please say 'no' or 'cancel'."
                suggestions = [
                    "Yes, create checkpoint",
                    "No, cancel workflow",
                    "Explain what a checkpoint is",
                ]

            elif current_step == 2:
                response = "To proceed with applying the security fixes, please confirm with 'yes' or 'proceed'. If you want to cancel, please say 'no' or 'cancel'."
                suggestions = [
                    "Yes, apply fixes",
                    "No, cancel workflow",
                    "Show me what changes will be made",
                ]

            elif current_step == 3:
                response = "Would you like to restore from the checkpoint? Please confirm with 'yes' or 'proceed'. If you want to exit without restoring, please say 'no' or 'cancel'."
                suggestions = [
                    "Yes, restore from checkpoint",
                    "No, exit workflow",
                    "Explain what happened",
                ]

            else:
                response = (
                    "I'm not sure what to do at this step. Let's restart the workflow."
                )
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Start new security workflow",
                    "Show security dashboard",
                    "Run security scan",
                ]

        return response, suggestions

    def start_security_workflow(
        self, vulnerability_id: str, context: Dict[str, Any]
    ) -> Tuple[str, List[str], str]:
        """
        Start a new security resolution workflow for a vulnerability.

        Args:
            vulnerability_id: The ID of the vulnerability to resolve
            context: Contextual information

        Returns:
            A tuple containing (response_text, suggested_responses, workflow_id)
        """
        # Create a unique workflow ID
        workflow_id = (
            f"security-workflow-{vulnerability_id}-{int(datetime.now().timestamp())}"
        )

        # Set up workflow details
        workflow = {
            "id": workflow_id,
            "type": "vulnerability_fix",
            "vulnerability_id": vulnerability_id,
            "current_step": 1,
            "affected_package": context.get("affected_package", "unknown"),
            "current_version": context.get("current_version", "unknown"),
            "fixed_version": context.get("fixed_version", "unknown"),
            "container_id": context.get("container_id"),
            "image_id": context.get("image_id"),
            "started_at": datetime.now().isoformat(),
        }

        # Store workflow
        self.active_workflows[workflow_id] = workflow

        # Generate initial workflow message
        response = (
            f"I'm starting a security fix workflow for vulnerability {vulnerability_id}. "
            f"This will update {workflow['affected_package']} from version {workflow['current_version']} to {workflow['fixed_version']}.\n\n"
            f"Before proceeding, I'll create a checkpoint of your current system state. This will allow you to rollback "
            f"if anything goes wrong during the fix process. Would you like to proceed with creating a checkpoint?"
        )

        suggestions = [
            "Yes, create checkpoint",
            "No, cancel workflow",
            "Explain what changes will be made",
        ]

        return response, suggestions, workflow_id

    def _create_security_checkpoint(self, workflow: Dict[str, Any]) -> str:
        """
        Create a checkpoint before applying security fixes.

        Args:
            workflow: The active workflow data

        Returns:
            The checkpoint ID
        """
        # In a real implementation, this would call the checkpoint manager
        # checkpoint_id = self.checkpoint_manager.create_checkpoint(
        #     reason=f"Security fix for vulnerability {workflow['vulnerability_id']}",
        #     metadata={
        #         "workflow_id": workflow["id"],
        #         "vulnerability_id": workflow["vulnerability_id"],
        #         "affected_package": workflow["affected_package"],
        #         "fixed_version": workflow["fixed_version"]
        #     }
        # )

        # Mock implementation for now
        checkpoint_id = f"checkpoint-{workflow['vulnerability_id']}-{int(datetime.now().timestamp())}"
        logger.info(
            f"Created checkpoint {checkpoint_id} for security workflow {workflow['id']}"
        )

        return checkpoint_id

    def _apply_security_fixes(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply security fixes for a vulnerability.

        Args:
            workflow: The active workflow data

        Returns:
            Result dictionary
        """
        # In a real implementation, this would use the vulnerability scanner to apply fixes
        # result = self.vulnerability_scanner.apply_fix(
        #     vulnerability_id=workflow["vulnerability_id"],
        #     container_id=workflow.get("container_id"),
        #     image_id=workflow.get("image_id")
        # )

        # Mock implementation
        logger.info(
            f"Applied security fix for vulnerability {workflow['vulnerability_id']}"
        )

        # Simulate successful fix
        return {
            "success": True,
            "message": f"Updated {workflow['affected_package']} to version {workflow['fixed_version']}",
            "timestamp": datetime.now().isoformat(),
        }

    def _restore_from_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Restore from a checkpoint after a failed fix attempt.

        Args:
            checkpoint_id: The checkpoint ID to restore from

        Returns:
            Result dictionary
        """
        # In a real implementation, this would call the checkpoint manager
        # result = self.checkpoint_manager.restore_checkpoint(checkpoint_id)

        # Mock implementation
        logger.info(f"Restored from checkpoint {checkpoint_id}")

        # Simulate successful restore
        return {
            "success": True,
            "message": f"Restored from checkpoint {checkpoint_id}",
            "timestamp": datetime.now().isoformat(),
        }

    def _process_container_workflow_step(
        self, message: str, workflow_id: str, context: Optional[Dict[str, Any]]
    ) -> Tuple[str, List[str]]:
        """
        Process a step in an active container troubleshooting workflow.

        Args:
            message: The user message text
            workflow_id: The ID of the active workflow
            context: Optional contextual information

        Returns:
            A tuple containing (response_text, suggested_responses)
        """
        workflow = self.active_workflows[workflow_id]
        current_step = workflow.get("current_step", 0)

        # Process confirmation/response based on the current step
        if (
            "yes" in message.lower()
            or "confirm" in message.lower()
            or "proceed" in message.lower()
        ):
            # User confirmed the action, proceed to next step
            if current_step == 1:  # Log analysis confirmation
                # Analyze container logs
                analysis_result = self._analyze_container_logs(workflow)
                workflow["analysis_result"] = (
                    analysis_result.to_dict()
                    if hasattr(analysis_result, "to_dict")
                    else analysis_result
                )

                # Format the analysis results for display
                if analysis_result.get("issues"):
                    issues_text = "\n\n**Issues Found:**\n"
                    for i, issue in enumerate(analysis_result.get("issues", []), 1):
                        issues_text += f"{i}. **{issue.get('title')}** ({issue.get('severity', 'unknown')})\n   {issue.get('description')}\n"
                else:
                    issues_text = "\n\nNo specific issues were found in the logs."

                response = (
                    f"I've analyzed the logs for container {workflow.get('container_name')}.\n\n"
                    f"**Summary**: {analysis_result.get('summary', 'No summary available.')}"
                    f"{issues_text}\n\n"
                    f"Would you like me to help you resolve these issues? I can provide step-by-step guidance for fixing the most critical problems."
                )

                # Move to next step
                workflow["current_step"] = 2
                suggestions = [
                    "Yes, help me fix the issues",
                    "Show me more details",
                    "No, I'll handle it myself",
                ]

            elif current_step == 2:  # Fix confirmation
                # Start applying fixes
                if len(workflow.get("analysis_result", {}).get("issues", [])) > 0:
                    # Create a checkpoint before applying fixes
                    checkpoint_id = self._create_container_checkpoint(workflow)
                    workflow["checkpoint_id"] = checkpoint_id
                    workflow["current_issue_index"] = 0
                    workflow["current_step"] = 3

                    # Get the first issue
                    current_issue = workflow["analysis_result"]["issues"][0]

                    response = (
                        f"I've created a checkpoint (ID: {checkpoint_id}) before we start making changes.\n\n"
                        f"Let's start by addressing this issue: **{current_issue.get('title')}**\n\n"
                        f"{current_issue.get('description')}\n\n"
                    )

                    # Get the recommendations for this issue
                    recommendations = []
                    for rec in workflow["analysis_result"].get("recommendations", []):
                        if rec.get("for_issue") == current_issue.get("id", ""):
                            recommendations.append(rec)

                    if recommendations:
                        rec = recommendations[0]
                        steps_text = "\n".join(
                            [f"- {step}" for step in rec.get("steps", [])]
                        )
                        response += f"**Recommended Fix:**\n{rec.get('description')}\n\n**Steps:**\n{steps_text}\n\nWould you like me to apply this fix?"
                        suggestions = [
                            "Yes, apply the fix",
                            "Show me more details",
                            "Skip to next issue",
                        ]
                    else:
                        response += "I don't have specific recommendations for this issue. Would you like suggestions for troubleshooting?"
                        suggestions = [
                            "Show me troubleshooting steps",
                            "Skip to next issue",
                            "Exit workflow",
                        ]
                else:
                    response = "There are no issues to fix based on the analysis. Would you like me to suggest general container optimization tips instead?"
                    workflow["current_step"] = 5  # Skip to final step
                    suggestions = [
                        "Show me optimization tips",
                        "Analyze logs again",
                        "Exit workflow",
                    ]

            elif current_step == 3:  # Apply specific fix
                # Get the current issue and recommendations
                current_index = workflow.get("current_issue_index", 0)
                issues = workflow["analysis_result"].get("issues", [])

                if current_index < len(issues):
                    current_issue = issues[current_index]
                    issue_id = current_issue.get("id", f"issue-{current_index}")

                    # Apply the fix
                    fix_result = self._apply_container_fix(workflow, issue_id)

                    if fix_result.get("success", False):
                        response = f"✅ Successfully applied fix for issue: **{current_issue.get('title')}**\n\n{fix_result.get('message', '')}"

                        # Move to next issue or completion
                        workflow["current_issue_index"] = current_index + 1

                        if current_index + 1 < len(issues):
                            next_issue = issues[current_index + 1]
                            response += f"\n\nNext issue to address: **{next_issue.get('title')}**\n\n{next_issue.get('description')}\n\nWould you like to fix this issue as well?"
                            suggestions = [
                                "Yes, fix this issue",
                                "Skip this issue",
                                "Stop and exit workflow",
                            ]
                        else:
                            response += "\n\nAll identified issues have been addressed! Would you like to verify that the fixes resolved the problems?"
                            workflow["current_step"] = 4  # Move to verification step
                            suggestions = [
                                "Verify fixes",
                                "Show me the updated container",
                                "Exit workflow",
                            ]
                    else:
                        response = f"❌ There was a problem applying the fix: {fix_result.get('error', 'Unknown error')}\n\nWould you like to try an alternative approach or restore from the checkpoint?"
                        suggestions = [
                            "Try alternative approach",
                            "Restore from checkpoint",
                            "Skip to next issue",
                        ]
                else:
                    # No more issues to fix
                    response = "All identified issues have been addressed! Would you like to verify that the fixes resolved the problems?"
                    workflow["current_step"] = 4  # Move to verification step
                    suggestions = [
                        "Verify fixes",
                        "Show me the updated container",
                        "Exit workflow",
                    ]

            elif current_step == 4:  # Verification step
                # Verify the fixes
                verification_result = self._verify_container_fixes(workflow)

                if verification_result.get("success", False):
                    response = (
                        "✅ Verification successful! The container is now running properly.\n\n"
                        f"**Status**: {verification_result.get('status', 'Unknown')}\n"
                        f"**Health**: {verification_result.get('health', 'Unknown')}\n\n"
                        "The troubleshooting workflow is now complete. Is there anything else you'd like to know about this container?"
                    )

                    # Clean up workflow
                    del self.active_workflows[workflow_id]
                    suggestions = [
                        "Show container metrics",
                        "Optimize this container",
                        "Back to container list",
                    ]
                else:
                    response = (
                        "⚠️ Verification shows there are still issues with the container.\n\n"
                        f"**Status**: {verification_result.get('status', 'Unknown')}\n"
                        f"**Health**: {verification_result.get('health', 'Unknown')}\n"
                        f"**Issues**: {verification_result.get('message', 'Unknown errors')}\n\n"
                        "Would you like to restore from the checkpoint and try a different approach?"
                    )
                    suggestions = [
                        "Restore from checkpoint",
                        "Try more fixes",
                        "Exit workflow",
                    ]

            elif current_step == 5:  # Final step / optimization
                # Provide optimization tips
                response = (
                    "Here are some general container optimization tips:\n\n"
                    "1. **Resource Limits**: Set appropriate CPU and memory limits\n"
                    "2. **Multi-Stage Builds**: Use multi-stage builds to reduce image size\n"
                    "3. **Cache Management**: Optimize Dockerfile to leverage build cache\n"
                    "4. **Logging**: Configure appropriate logging drivers and rotation\n"
                    "5. **Health Checks**: Implement proper health check mechanisms\n\n"
                    "The troubleshooting workflow is now complete. Would you like detailed information on any of these optimization techniques?"
                )

                # Clean up workflow
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Resource limit best practices",
                    "Multi-stage build examples",
                    "Health check setup",
                ]

            else:
                response = (
                    "I'm not sure what to do at this step. Let's restart the workflow."
                )
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Start new troubleshooting",
                    "Show container dashboard",
                    "Back to container list",
                ]

        elif (
            "no" in message.lower()
            or "cancel" in message.lower()
            or "stop" in message.lower()
            or "exit" in message.lower()
        ):
            # User canceled or rejected the action
            response = "Container troubleshooting workflow canceled. No changes were made to your container."

            # Clean up workflow
            del self.active_workflows[workflow_id]
            suggestions = [
                "Show container dashboard",
                "Show container logs",
                "Back to container list",
            ]

        else:
            # User provided some other input, provide help based on current step
            if current_step == 1:
                response = "Would you like me to analyze the logs for this container? Please confirm with 'yes' or 'proceed'. If you want to cancel, please say 'no' or 'cancel'."
                suggestions = [
                    "Yes, analyze logs",
                    "No, cancel",
                    "Show me the logs first",
                ]

            elif current_step == 2:
                response = "Would you like me to help resolve the issues found in the container? Please confirm with 'yes' or 'proceed'. If you want to cancel, please say 'no' or 'cancel'."
                suggestions = [
                    "Yes, help me fix issues",
                    "No, cancel",
                    "Show me more details",
                ]

            elif current_step == 3:
                current_index = workflow.get("current_issue_index", 0)
                issues = workflow["analysis_result"].get("issues", [])

                if current_index < len(issues):
                    current_issue = issues[current_index]
                    response = f"Would you like me to fix the issue '{current_issue.get('title')}'? Please confirm with 'yes' or 'proceed'. If you want to skip this issue, please say 'skip' or 'next'."
                    suggestions = [
                        "Yes, fix this issue",
                        "Skip this issue",
                        "Cancel workflow",
                    ]
                else:
                    response = "There are no more issues to fix. Would you like to verify the fixes?"
                    suggestions = [
                        "Verify fixes",
                        "Exit workflow",
                        "Show container dashboard",
                    ]

            elif current_step == 4:
                response = "Would you like to verify that the fixes resolved the container issues? Please confirm with 'yes' or 'proceed'."
                suggestions = [
                    "Yes, verify fixes",
                    "No, exit workflow",
                    "Show me the container",
                ]

            else:
                response = (
                    "I'm not sure what to do at this step. Let's restart the workflow."
                )
                del self.active_workflows[workflow_id]
                suggestions = [
                    "Start new troubleshooting",
                    "Show container dashboard",
                    "Back to container list",
                ]

        return response, suggestions

    def start_container_troubleshooting_workflow(
        self, container_id: str, context: Dict[str, Any]
    ) -> Tuple[str, List[str], str]:
        """
        Start a new container troubleshooting workflow for a container.

        Args:
            container_id: The ID of the container to troubleshoot
            context: Contextual information

        Returns:
            A tuple containing (response_text, suggested_responses, workflow_id)
        """
        # Create a unique workflow ID
        workflow_id = (
            f"container-workflow-{container_id[:8]}-{int(datetime.now().timestamp())}"
        )

        # Set up workflow details
        workflow = {
            "id": workflow_id,
            "type": "container_troubleshooting",
            "container_id": container_id,
            "container_name": context.get("container_name", "Unknown container"),
            "current_step": 1,
            "issue_id": context.get("issue_id"),
            "issue_severity": context.get("issue_severity"),
            "container_status": context.get("container_status", "unknown"),
            "container_health": context.get("container_health", "unknown"),
            "exit_code": context.get("exit_code"),
            "started_at": datetime.now().isoformat(),
        }

        # Store workflow
        self.active_workflows[workflow_id] = workflow

        # Generate initial workflow message
        container_status_info = ""
        if workflow["container_status"]:
            container_status_info += f"Status: {workflow['container_status']}\n"
        if workflow["container_health"]:
            container_status_info += f"Health: {workflow['container_health']}\n"
        if workflow["exit_code"] is not None:
            container_status_info += f"Exit Code: {workflow['exit_code']}\n"

        response = (
            f"I'm starting a troubleshooting workflow for container {workflow['container_name']} ({container_id[:12]}).\n\n"
            f"{container_status_info}\n"
            "To diagnose issues with this container, I'll need to analyze its logs. "
            "This will help me identify any errors or performance problems.\n\n"
            "Would you like me to analyze the container logs now?"
        )

        suggestions = [
            "Yes, analyze logs",
            "Show me more details first",
            "Cancel workflow",
        ]

        return response, suggestions, workflow_id

    def _create_container_checkpoint(self, workflow: Dict[str, Any]) -> str:
        """
        Create a checkpoint before applying container fixes.

        Args:
            workflow: The active workflow data

        Returns:
            The checkpoint ID
        """
        # In a real implementation, this would call the checkpoint manager
        # checkpoint_id = self.checkpoint_manager.create_checkpoint(
        #     reason=f"Container troubleshooting for {workflow['container_name']}",
        #     metadata={
        #         "workflow_id": workflow["id"],
        #         "container_id": workflow["container_id"],
        #         "container_name": workflow["container_name"]
        #     }
        # )

        # Mock implementation for now
        checkpoint_id = f"checkpoint-container-{workflow['container_id'][:8]}-{int(datetime.now().timestamp())}"
        logger.info(
            f"Created checkpoint {checkpoint_id} for container workflow {workflow['id']}"
        )

        return checkpoint_id

    def _analyze_container_logs(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze container logs to identify issues.

        Args:
            workflow: The active workflow data

        Returns:
            Analysis result dictionary
        """
        # In a real implementation, this would call the log analyzer
        # result = self.log_analyzer.analyze_container_logs(
        #     container_id=workflow["container_id"],
        #     template_id="default"
        # )

        # Mock implementation
        logger.info(f"Analyzed logs for container {workflow['container_id']}")

        # Simulate analysis result
        return {
            "summary": f"Analysis of container {workflow['container_name']} shows several issues that may be affecting stability and performance.",
            "issues": [
                {
                    "id": "issue-1",
                    "title": "Memory limit reached multiple times",
                    "description": "The container is hitting its memory limit, causing possible OOM (Out of Memory) events",
                    "severity": "error",
                    "evidence": "2023-03-15T10:22:31Z Container memory usage high: 98%",
                },
                {
                    "id": "issue-2",
                    "title": "High CPU usage spikes",
                    "description": "The container shows periodic CPU usage spikes that may indicate inefficient processing",
                    "severity": "warning",
                    "evidence": "2023-03-15T10:24:12Z Container CPU usage: 95%",
                },
                {
                    "id": "issue-3",
                    "title": "Slow database queries",
                    "description": "Several database queries are taking longer than 500ms to complete",
                    "severity": "warning",
                    "evidence": "2023-03-15T10:23:45Z Query took 1250ms to complete",
                },
            ],
            "recommendations": [
                {
                    "id": "rec-1",
                    "for_issue": "issue-1",
                    "title": "Increase memory limit",
                    "description": "Increase the container's memory limit to prevent OOM events",
                    "steps": [
                        "Update the container configuration to set memory limit to at least 1GB",
                        "Restart the container with the new configuration",
                        "Monitor memory usage after the change",
                    ],
                },
                {
                    "id": "rec-2",
                    "for_issue": "issue-2",
                    "title": "Optimize CPU usage",
                    "description": "Identify and optimize the processing causing CPU spikes",
                    "steps": [
                        "Enable application profiling to identify hotspots",
                        "Consider adding caching for frequently accessed data",
                        "Update resource limits to set CPU constraints",
                    ],
                },
                {
                    "id": "rec-3",
                    "for_issue": "issue-3",
                    "title": "Optimize database queries",
                    "description": "Optimize slow database queries to improve performance",
                    "steps": [
                        "Add indexes for frequently queried fields",
                        "Review and optimize query structure",
                        "Consider implementing query caching",
                    ],
                },
            ],
            "pattern_matches": [],
            "ai_provider": "mock",
            "ai_model": "mock-model",
            "analysis_duration": 1.5,
            "log_count": 1250,
            "timestamp": datetime.now().isoformat(),
        }

    def _apply_container_fix(
        self, workflow: Dict[str, Any], issue_id: str
    ) -> Dict[str, Any]:
        """
        Apply a fix for a specific container issue.

        Args:
            workflow: The active workflow data
            issue_id: ID of the issue to fix

        Returns:
            Result dictionary
        """
        # In a real implementation, this would apply the actual fix
        # For example, updating configuration files, restarting the container, etc.

        # Mock implementation
        logger.info(
            f"Applied fix for issue {issue_id} in container {workflow['container_id']}"
        )

        # Find the recommendation for this issue
        recommendation = None
        for rec in workflow["analysis_result"].get("recommendations", []):
            if rec.get("for_issue") == issue_id:
                recommendation = rec
                break

        # Simulate successful fix
        return {
            "success": True,
            "message": f"Applied fix: {recommendation['title'] if recommendation else 'Unknown fix'}",
            "steps_completed": (
                recommendation.get("steps", []) if recommendation else []
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def _verify_container_fixes(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that the applied fixes resolved the container issues.

        Args:
            workflow: The active workflow data

        Returns:
            Result dictionary
        """
        # In a real implementation, this would check the container status
        # and verify that the issues are resolved

        # Mock implementation
        logger.info(f"Verified fixes for container {workflow['container_id']}")

        # Simulate successful verification
        return {
            "success": True,
            "status": "running",
            "health": "healthy",
            "message": "Container is running properly with no detected issues",
            "timestamp": datetime.now().isoformat(),
        }


# Singleton instance
_chat_handler = None


def get_chat_handler() -> ChatHandler:
    """
    Get the chat handler instance.

    Returns:
        The chat handler instance
    """
    global _chat_handler
    if _chat_handler is None:
        _chat_handler = ChatHandler()
    return _chat_handler
