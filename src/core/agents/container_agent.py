"""
Container Management Agent for the Agent Framework

This module provides an agent specialized in Docker container management tasks,
including lifecycle management, troubleshooting, and optimization.
"""

import asyncio
import json
import logging
import re
import subprocess
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .agent_framework import Agent, AgentContext, AgentResult, AgentTask, TaskStatus
from .agent_memory import AgentMemory

logger = logging.getLogger(__name__)


class ContainerCommand:
    """Helper class for executing Docker container commands"""

    @staticmethod
    async def run_command(
        command: List[str], timeout: float = 30.0
    ) -> Tuple[int, str, str]:
        """
        Run a command asynchronously and return exit code, stdout, and stderr.

        Args:
            command: Command and arguments as a list
            timeout: Timeout in seconds

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            # Wait for the process to complete with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
                return (
                    process.returncode,
                    stdout.decode().strip(),
                    stderr.decode().strip(),
                )
            except asyncio.TimeoutError:
                # Kill the process if it times out
                process.kill()
                await process.wait()
                return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", f"Error executing command: {str(e)}"

    @staticmethod
    async def list_containers(
        all_containers: bool = False,
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        List Docker containers

        Args:
            all_containers: Whether to include stopped containers

        Returns:
            Tuple of (success, containers)
        """
        command = ["docker", "ps", "--format", "{{json .}}"]
        if all_containers:
            command.append("-a")

        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, []

        containers = []
        for line in stdout.splitlines():
            if line.strip():
                try:
                    container = json.loads(line)
                    containers.append(container)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse container JSON: {line}")

        return True, containers

    @staticmethod
    async def get_container_info(
        container_id: str,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Get detailed information about a container

        Args:
            container_id: Container ID or name

        Returns:
            Tuple of (success, container_info)
        """
        command = ["docker", "inspect", container_id]
        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, None

        try:
            containers = json.loads(stdout)
            if containers:
                return True, containers[0]
            return False, None
        except json.JSONDecodeError:
            return False, None

    @staticmethod
    async def get_container_logs(
        container_id: str, tail: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Get logs from a container

        Args:
            container_id: Container ID or name
            tail: Number of lines to retrieve from the end

        Returns:
            Tuple of (success, logs)
        """
        command = ["docker", "logs", container_id]
        if tail is not None:
            command.extend(["--tail", str(tail)])

        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, stdout

    @staticmethod
    async def start_container(container_id: str) -> Tuple[bool, str]:
        """
        Start a container

        Args:
            container_id: Container ID or name

        Returns:
            Tuple of (success, message)
        """
        command = ["docker", "start", container_id]
        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, f"Container {container_id} started"

    @staticmethod
    async def stop_container(container_id: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Stop a container

        Args:
            container_id: Container ID or name
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, message)
        """
        command = ["docker", "stop", f"--time={timeout}", container_id]
        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, f"Container {container_id} stopped"

    @staticmethod
    async def restart_container(
        container_id: str, timeout: int = 10
    ) -> Tuple[bool, str]:
        """
        Restart a container

        Args:
            container_id: Container ID or name
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, message)
        """
        command = ["docker", "restart", f"--time={timeout}", container_id]
        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, f"Container {container_id} restarted"

    @staticmethod
    async def remove_container(
        container_id: str, force: bool = False
    ) -> Tuple[bool, str]:
        """
        Remove a container

        Args:
            container_id: Container ID or name
            force: Whether to force removal

        Returns:
            Tuple of (success, message)
        """
        command = ["docker", "rm", container_id]
        if force:
            command.append("--force")

        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, f"Container {container_id} removed"

    @staticmethod
    async def exec_in_container(
        container_id: str, command_args: List[str]
    ) -> Tuple[bool, str]:
        """
        Execute a command in a running container

        Args:
            container_id: Container ID or name
            command_args: Command and arguments to execute

        Returns:
            Tuple of (success, output)
        """
        command = ["docker", "exec", container_id] + command_args
        exit_code, stdout, stderr = await ContainerCommand.run_command(command)

        if exit_code != 0:
            return False, stderr

        return True, stdout


class ContainerIssueDetector:
    """Helper class for detecting and diagnosing container issues"""

    @staticmethod
    def analyze_logs(logs: str) -> List[Dict[str, Any]]:
        """
        Analyze container logs for common issues

        Args:
            logs: Container logs

        Returns:
            List of detected issues with severity and recommendations
        """
        issues = []

        # Check for common error patterns
        error_patterns = [
            {"pattern": r"Error: .+", "type": "general_error", "severity": "medium"},
            {"pattern": r"Exception: .+", "type": "exception", "severity": "medium"},
            {
                "pattern": r"ERROR: .+",
                "type": "application_error",
                "severity": "medium",
            },
            {"pattern": r"FATAL: .+", "type": "fatal_error", "severity": "high"},
            {
                "pattern": r"connection refused",
                "type": "connection_error",
                "severity": "high",
            },
            {
                "pattern": r"permission denied",
                "type": "permission_error",
                "severity": "high",
            },
            {
                "pattern": r"out of memory",
                "type": "resource_error",
                "severity": "critical",
            },
            {
                "pattern": r"disk space",
                "type": "resource_error",
                "severity": "critical",
            },
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern["pattern"], logs, re.IGNORECASE)
            for match in matches:
                line = match.group(0)
                context_start = max(0, match.start() - 100)
                context_end = min(len(logs), match.end() + 100)
                context = logs[context_start:context_end]

                issue = {
                    "type": pattern["type"],
                    "severity": pattern["severity"],
                    "message": line.strip(),
                    "context": context.strip(),
                    "timestamp": datetime.now().isoformat(),
                }
                issues.append(issue)

        return issues

    @staticmethod
    def analyze_container_state(container_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze container state for issues

        Args:
            container_info: Container inspect information

        Returns:
            List of detected issues with severity and recommendations
        """
        issues = []
        state = container_info.get("State", {})

        # Check for restart issues
        restart_count = container_info.get("RestartCount", 0)
        if restart_count > 5:
            issues.append(
                {
                    "type": "high_restart_count",
                    "severity": "high",
                    "message": f"Container has restarted {restart_count} times",
                    "context": "Frequent restarts may indicate application crashes or issues",
                    "recommendation": "Check container logs for errors and consider adjusting application settings",
                }
            )

        # Check for exit code issues
        exit_code = state.get("ExitCode", 0)
        if exit_code != 0:
            issues.append(
                {
                    "type": "non_zero_exit",
                    "severity": "high",
                    "message": f"Container exited with code {exit_code}",
                    "context": f"Exit reason: {state.get('Error', 'Unknown')}",
                    "recommendation": "Check container logs and application configuration",
                }
            )

        # Check health status if available
        health = state.get("Health", {})
        if health:
            status = health.get("Status", "")
            if status != "healthy":
                issues.append(
                    {
                        "type": "health_check_failure",
                        "severity": "high",
                        "message": f"Container health check status is {status}",
                        "context": str(health.get("Log", [])),
                        "recommendation": "Review health check logs and fix the underlying issue",
                    }
                )

        return issues


class ContainerAgent(Agent):
    """
    Agent specialized in Docker container management tasks.

    This agent can perform container lifecycle management, troubleshoot issues,
    gather metrics, and optimize container configurations.
    """

    def __init__(self, agent_id: str = "docker-container-agent"):
        super().__init__(
            agent_id=agent_id,
            name="Docker Container Management Agent",
            description="Manages and troubleshoots Docker containers",
        )

        # Supported task types
        self.supported_task_types = [
            "container.list",
            "container.inspect",
            "container.logs",
            "container.start",
            "container.stop",
            "container.restart",
            "container.remove",
            "container.exec",
            "container.diagnose",
            "container.fix",
        ]

        # Agent capabilities
        self.capabilities = [
            "Container lifecycle management",
            "Container monitoring",
            "Issue detection and diagnosis",
            "Automated problem solving",
        ]

        # Initialize memory
        self.memory = AgentMemory(agent_id)

        logger.info(f"Initialized {self.name} with ID {self.agent_id}")

    async def execute_task(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """Execute a container management task"""
        logger.info(f"Executing task: {task.name} ({task.id})")

        # Extract task type from input data
        task_type = task.input_data.get("task_type", "")

        # Execute appropriate task handler
        try:
            if task_type == "container.list":
                return await self._handle_list_containers(task, context)
            elif task_type == "container.inspect":
                return await self._handle_inspect_container(task, context)
            elif task_type == "container.logs":
                return await self._handle_container_logs(task, context)
            elif task_type == "container.start":
                return await self._handle_start_container(task, context)
            elif task_type == "container.stop":
                return await self._handle_stop_container(task, context)
            elif task_type == "container.restart":
                return await self._handle_restart_container(task, context)
            elif task_type == "container.remove":
                return await self._handle_remove_container(task, context)
            elif task_type == "container.exec":
                return await self._handle_exec_in_container(task, context)
            elif task_type == "container.diagnose":
                return await self._handle_diagnose_container(task, context)
            elif task_type == "container.fix":
                return await self._handle_fix_container(task, context)
            else:
                return AgentResult(
                    success=False,
                    task_id=task.id,
                    error=f"Unsupported task type: {task_type}",
                )
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {str(e)}")
            return AgentResult(
                success=False, task_id=task.id, error=f"Error executing task: {str(e)}"
            )

    async def _handle_list_containers(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle listing containers"""
        all_containers = task.input_data.get("all", False)

        success, containers = await ContainerCommand.list_containers(all_containers)

        if not success:
            return AgentResult(
                success=False, task_id=task.id, error="Failed to list containers"
            )

        # Store result in memory for future reference
        timestamp = datetime.now().isoformat()
        self.memory.save_state(f"container_list_{timestamp}", containers)

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "containers": containers,
                "count": len(containers),
                "timestamp": timestamp,
            },
        )

    async def _handle_inspect_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle inspecting a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        success, container_info = await ContainerCommand.get_container_info(
            container_id
        )

        if not success or container_info is None:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to inspect container {container_id}",
            )

        # Store result in memory for future reference
        timestamp = datetime.now().isoformat()
        self.memory.save_state(
            f"container_info_{container_id}_{timestamp}", container_info
        )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "info": container_info,
                "timestamp": timestamp,
            },
        )

    async def _handle_container_logs(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle retrieving container logs"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        tail = task.input_data.get("tail")
        if tail is not None:
            try:
                tail = int(tail)
            except ValueError:
                tail = None

        success, logs = await ContainerCommand.get_container_logs(container_id, tail)

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to get logs for container {container_id}: {logs}",
            )

        # Store result in memory for future reference
        timestamp = datetime.now().isoformat()
        self.memory.save_state(f"container_logs_{container_id}_{timestamp}", logs)

        return AgentResult(
            success=True,
            task_id=task.id,
            data={"container_id": container_id, "logs": logs, "timestamp": timestamp},
        )

    async def _handle_start_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle starting a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        success, message = await ContainerCommand.start_container(container_id)

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to start container {container_id}: {message}",
            )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _handle_stop_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle stopping a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        timeout = task.input_data.get("timeout", 10)
        try:
            timeout = int(timeout)
        except ValueError:
            timeout = 10

        success, message = await ContainerCommand.stop_container(container_id, timeout)

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to stop container {container_id}: {message}",
            )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _handle_restart_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle restarting a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        timeout = task.input_data.get("timeout", 10)
        try:
            timeout = int(timeout)
        except ValueError:
            timeout = 10

        success, message = await ContainerCommand.restart_container(
            container_id, timeout
        )

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to restart container {container_id}: {message}",
            )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _handle_remove_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle removing a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        force = task.input_data.get("force", False)

        success, message = await ContainerCommand.remove_container(container_id, force)

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to remove container {container_id}: {message}",
            )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _handle_exec_in_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle executing a command in a container"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        command = task.input_data.get("command", [])
        if not command:
            return AgentResult(
                success=False, task_id=task.id, error="Missing command parameter"
            )

        if isinstance(command, str):
            command = command.split()

        success, output = await ContainerCommand.exec_in_container(
            container_id, command
        )

        if not success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to execute command in container {container_id}: {output}",
            )

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "command": command,
                "output": output,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def _handle_diagnose_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle diagnosing container issues"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        # Get container information
        success, container_info = await ContainerCommand.get_container_info(
            container_id
        )
        if not success or container_info is None:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to inspect container {container_id}",
            )

        # Get container logs
        log_success, logs = await ContainerCommand.get_container_logs(container_id)

        # Perform diagnosis
        issues = []

        # Analyze container state
        state_issues = ContainerIssueDetector.analyze_container_state(container_info)
        issues.extend(state_issues)

        # Analyze logs if available
        if log_success:
            log_issues = ContainerIssueDetector.analyze_logs(logs)
            issues.extend(log_issues)

        # Generate recommendations
        recommendations = []
        if issues:
            for issue in issues:
                if issue["type"] == "high_restart_count":
                    recommendations.append(
                        {
                            "action": "check_logs",
                            "description": "Check container logs for errors",
                            "priority": "high",
                        }
                    )
                    recommendations.append(
                        {
                            "action": "adjust_restart_policy",
                            "description": "Consider adjusting restart policy to prevent excessive restarts",
                            "priority": "medium",
                        }
                    )
                elif issue["type"] == "non_zero_exit":
                    recommendations.append(
                        {
                            "action": "check_logs",
                            "description": "Check container logs for errors",
                            "priority": "high",
                        }
                    )
                    recommendations.append(
                        {
                            "action": "restart",
                            "description": "Restart the container to see if the issue persists",
                            "priority": "medium",
                        }
                    )
                elif issue["type"] == "health_check_failure":
                    recommendations.append(
                        {
                            "action": "check_health_logs",
                            "description": "Review health check logs for specific issues",
                            "priority": "high",
                        }
                    )
                elif issue["type"] == "resource_error":
                    recommendations.append(
                        {
                            "action": "increase_resources",
                            "description": "Consider increasing container resource limits",
                            "priority": "high",
                        }
                    )
                elif issue["type"] == "connection_error":
                    recommendations.append(
                        {
                            "action": "check_networking",
                            "description": "Verify network connectivity and DNS settings",
                            "priority": "high",
                        }
                    )
                elif issue["type"] == "permission_error":
                    recommendations.append(
                        {
                            "action": "check_permissions",
                            "description": "Verify file and resource permissions",
                            "priority": "high",
                        }
                    )

        # Store diagnosis in memory
        diagnosis = {
            "container_id": container_id,
            "timestamp": datetime.now().isoformat(),
            "issues": issues,
            "recommendations": recommendations,
            "container_info": container_info,
        }
        self.memory.save_state(
            f"container_diagnosis_{container_id}_{diagnosis['timestamp']}", diagnosis
        )

        return AgentResult(success=True, task_id=task.id, data=diagnosis)

    async def _handle_fix_container(
        self, task: AgentTask, context: AgentContext
    ) -> AgentResult:
        """Handle fixing container issues"""
        container_id = task.input_data.get("container_id", "")
        if not container_id:
            return AgentResult(
                success=False, task_id=task.id, error="Missing container_id parameter"
            )

        issue_type = task.input_data.get("issue_type", "")
        if not issue_type:
            return AgentResult(
                success=False, task_id=task.id, error="Missing issue_type parameter"
            )

        # First, diagnose the container to see if the issue exists
        diagnosis_task = AgentTask(
            name="Diagnose container",
            description=f"Diagnose container {container_id}",
            input_data={
                "task_type": "container.diagnose",
                "container_id": container_id,
            },
        )
        diagnosis_result = await self._handle_diagnose_container(
            diagnosis_task, context
        )

        if not diagnosis_result.success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to diagnose container: {diagnosis_result.error}",
            )

        # Check if the issue exists
        issues = diagnosis_result.data.get("issues", [])
        matching_issues = [i for i in issues if i["type"] == issue_type]

        if not matching_issues:
            return AgentResult(
                success=True,
                task_id=task.id,
                data={
                    "container_id": container_id,
                    "issue_type": issue_type,
                    "fixed": False,
                    "message": f"Issue {issue_type} not found in container {container_id}",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        # Apply fixes based on issue type
        fix_result = None

        if issue_type == "high_restart_count" or issue_type == "non_zero_exit":
            # Try restarting the container
            restart_task = AgentTask(
                name="Restart container",
                description=f"Restart container {container_id}",
                input_data={
                    "task_type": "container.restart",
                    "container_id": container_id,
                },
            )
            fix_result = await self._handle_restart_container(restart_task, context)
        elif issue_type == "health_check_failure":
            # Try restarting the container
            restart_task = AgentTask(
                name="Restart container",
                description=f"Restart container {container_id}",
                input_data={
                    "task_type": "container.restart",
                    "container_id": container_id,
                },
            )
            fix_result = await self._handle_restart_container(restart_task, context)
        else:
            # Generic fix - just restart for now
            restart_task = AgentTask(
                name="Restart container",
                description=f"Restart container {container_id}",
                input_data={
                    "task_type": "container.restart",
                    "container_id": container_id,
                },
            )
            fix_result = await self._handle_restart_container(restart_task, context)

        if not fix_result or not fix_result.success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to apply fix for issue {issue_type}: {fix_result.error if fix_result else 'Unknown error'}",
            )

        # Check if the fix worked by re-diagnosing
        verification_task = AgentTask(
            name="Verify fix",
            description=f"Verify fix for container {container_id}",
            input_data={
                "task_type": "container.diagnose",
                "container_id": container_id,
            },
        )
        verification_result = await self._handle_diagnose_container(
            verification_task, context
        )

        if not verification_result.success:
            return AgentResult(
                success=False,
                task_id=task.id,
                error=f"Failed to verify fix: {verification_result.error}",
            )

        # Check if the issue still exists
        new_issues = verification_result.data.get("issues", [])
        still_exists = any(i["type"] == issue_type for i in new_issues)

        return AgentResult(
            success=True,
            task_id=task.id,
            data={
                "container_id": container_id,
                "issue_type": issue_type,
                "fixed": not still_exists,
                "message": f"Fix {'did not resolve' if still_exists else 'resolved'} issue {issue_type}",
                "original_diagnosis": diagnosis_result.data,
                "verification_diagnosis": verification_result.data,
                "timestamp": datetime.now().isoformat(),
            },
        )
