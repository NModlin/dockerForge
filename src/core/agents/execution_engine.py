"""
Execution Engine for the Agent Framework

This module provides the execution environment for agents to run their tasks
with proper monitoring, resource constraints, and error handling.
"""

import asyncio
import functools
import inspect
import logging
import resource
import signal
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from .agent_framework import Agent, AgentContext, AgentResult, AgentTask, TaskStatus

logger = logging.getLogger(__name__)


class ResourceLimits:
    """Configuration for resource limits during task execution"""

    def __init__(
        self,
        cpu_time: float = 30.0,
        memory_mb: int = 500,
        timeout: float = 60.0,
        max_subprocesses: int = 5,
    ):
        self.cpu_time = cpu_time  # seconds
        self.memory_mb = memory_mb  # MB
        self.timeout = timeout  # seconds
        self.max_subprocesses = max_subprocesses


class SecurityPolicy:
    """Security policy for agent task execution"""

    def __init__(
        self,
        allow_network: bool = False,
        allow_filesystem: bool = False,
        allowed_imports: Optional[Set[str]] = None,
        allowed_modules: Optional[Set[str]] = None,
        allowed_system_calls: Optional[Set[str]] = None,
    ):
        self.allow_network = allow_network
        self.allow_filesystem = allow_filesystem
        self.allowed_imports = allowed_imports or set()
        self.allowed_modules = allowed_modules or set()
        self.allowed_system_calls = allowed_system_calls or set()


class ExecutionStats:
    """Statistics about task execution"""

    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.cpu_time: float = 0.0
        self.memory_usage_mb: float = 0.0
        self.memory_peak_mb: float = 0.0
        self.io_read_bytes: int = 0
        self.io_write_bytes: int = 0
        self.error_count: int = 0
        self.warning_count: int = 0

    @property
    def execution_time(self) -> float:
        """Get total execution time in seconds"""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary representation"""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "cpu_time": self.cpu_time,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_peak_mb": self.memory_peak_mb,
            "io_read_bytes": self.io_read_bytes,
            "io_write_bytes": self.io_write_bytes,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }


class ExecutionLogger:
    """Logger for agent task execution"""

    def __init__(self, task_id: str, agent_id: str):
        self.task_id = task_id
        self.agent_id = agent_id
        self.logs: List[Dict[str, Any]] = []

    def log(self, level: str, message: str, **kwargs) -> None:
        """Add a log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            **kwargs,
        }
        self.logs.append(entry)

        # Also log to system logger
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(f"[{self.agent_id}:{self.task_id}] {message}")

    def info(self, message: str, **kwargs) -> None:
        """Log an info message"""
        self.log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message"""
        self.log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message"""
        self.log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message"""
        self.log("DEBUG", message, **kwargs)

    def get_logs(
        self, level: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get logs with optional filtering"""
        filtered = self.logs

        if level:
            filtered = [log for log in filtered if log["level"] == level]

        # Apply pagination
        return filtered[offset : offset + limit]


class ExecutionContext:
    """Context for agent task execution"""

    def __init__(
        self,
        task: AgentTask,
        agent: Agent,
        agent_context: AgentContext,
        resource_limits: Optional[ResourceLimits] = None,
        security_policy: Optional[SecurityPolicy] = None,
    ):
        self.task = task
        self.agent = agent
        self.agent_context = agent_context
        self.resource_limits = resource_limits or ResourceLimits()
        self.security_policy = security_policy or SecurityPolicy()
        self.stats = ExecutionStats()
        self.logger = ExecutionLogger(task.id, agent.agent_id)
        self.result: Optional[AgentResult] = None
        self._progress_callback: Optional[Callable[[float], None]] = None

    def set_progress(self, progress: float) -> None:
        """Update task progress (0.0 to 1.0)"""
        self.task.progress = max(0.0, min(1.0, progress))
        if self._progress_callback:
            self._progress_callback(self.task.progress)


@contextmanager
def timeout_context(seconds: float):
    """Context manager that raises TimeoutError if execution exceeds the limit"""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Execution timed out after {seconds} seconds")

    # Set the timeout handler
    original_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, timeout_handler)

    try:
        # Set the alarm
        signal.setitimer(signal.ITIMER_REAL, seconds)
        yield
    finally:
        # Cancel the alarm and restore the original handler
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, original_handler)


@contextmanager
def resource_limits_context(memory_mb: int, cpu_time: float):
    """Context manager that applies resource limits to the current process"""
    # Convert MB to bytes
    memory_bytes = memory_mb * 1024 * 1024

    # Set resource limits
    try:
        # Set CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))

        # Set memory limit (where supported)
        if hasattr(resource, "RLIMIT_AS"):
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

        yield
    finally:
        # Reset resource limits (set to maximum)
        resource.setrlimit(
            resource.RLIMIT_CPU, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        )
        if hasattr(resource, "RLIMIT_AS"):
            resource.setrlimit(
                resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
            )


class ExecutionEngine:
    """
    Engine for executing agent tasks with resource constraints,
    security policies, and monitoring.
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self._thread_pool = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self._task_stats: Dict[str, ExecutionStats] = {}
        self._active_executions: Dict[str, ExecutionContext] = {}
        self._observers: List[Callable[[str, Dict[str, Any]], None]] = []

    async def execute_task(
        self,
        context: ExecutionContext,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> AgentResult:
        """
        Execute an agent task with the given execution context.

        If a progress_callback is provided, it will be called whenever
        the task progress is updated.
        """
        # Set progress callback
        context._progress_callback = progress_callback

        # Store context in active executions
        task_id = context.task.id
        self._active_executions[task_id] = context

        # Initialize stats
        context.stats.start_time = datetime.now()
        context.logger.info(
            f"Starting execution of task {task_id} with agent {context.agent.agent_id}"
        )

        # Notify observers
        self._notify_observers(
            "task_started",
            {
                "task_id": task_id,
                "agent_id": context.agent.agent_id,
                "start_time": context.stats.start_time.isoformat(),
                "resource_limits": vars(context.resource_limits),
            },
        )

        try:
            # Apply timeout
            timeout_seconds = context.resource_limits.timeout

            # Execute the task with timeout
            try:
                # Run the agent's execute_task method with the given context
                context.logger.info(
                    f"Executing task with timeout of {timeout_seconds} seconds"
                )
                context.result = await asyncio.wait_for(
                    context.agent.execute_task(context.task, context.agent_context),
                    timeout=timeout_seconds,
                )

                if not context.result:
                    raise ValueError("Agent returned None instead of AgentResult")

                # Update task status based on result
                context.task.status = (
                    TaskStatus.COMPLETED
                    if context.result.success
                    else TaskStatus.FAILED
                )
                context.task.error = context.result.error
                context.task.output_data = context.result.data
                context.task.progress = (
                    1.0 if context.result.success else context.task.progress
                )

                context.logger.info(
                    f"Task execution completed with success={context.result.success}"
                )

            except asyncio.TimeoutError:
                context.logger.error(
                    f"Task execution timed out after {timeout_seconds} seconds"
                )
                context.result = AgentResult(
                    success=False,
                    task_id=task_id,
                    error=f"Execution timed out after {timeout_seconds} seconds",
                )
                context.task.status = TaskStatus.FAILED
                context.task.error = context.result.error

            except Exception as e:
                context.logger.error(f"Task execution failed with error: {str(e)}")
                context.logger.error(traceback.format_exc())
                context.result = AgentResult(
                    success=False, task_id=task_id, error=f"Execution error: {str(e)}"
                )
                context.task.status = TaskStatus.FAILED
                context.task.error = context.result.error

            # Finalize stats
            context.stats.end_time = datetime.now()
            context.stats.cpu_time = (
                context.stats.end_time - context.stats.start_time
            ).total_seconds()

            # Update error count from logs
            context.stats.error_count = len(
                [log for log in context.logger.logs if log["level"] == "ERROR"]
            )
            context.stats.warning_count = len(
                [log for log in context.logger.logs if log["level"] == "WARNING"]
            )

            # Add stats to result
            if context.result.data is None:
                context.result.data = {}
            context.result.data["execution_stats"] = context.stats.to_dict()

            # Notify observers
            event = "task_completed" if context.result.success else "task_failed"
            self._notify_observers(
                event,
                {
                    "task_id": task_id,
                    "agent_id": context.agent.agent_id,
                    "execution_time": context.stats.execution_time,
                    "result": context.result.to_dict(),
                    "stats": context.stats.to_dict(),
                },
            )

            # Store stats
            self._task_stats[task_id] = context.stats

            return context.result

        finally:
            # Remove from active executions
            if task_id in self._active_executions:
                del self._active_executions[task_id]

    def get_task_stats(self, task_id: str) -> Optional[ExecutionStats]:
        """Get execution stats for a task"""
        return self._task_stats.get(task_id)

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get information about active task executions"""
        result = []
        for task_id, context in self._active_executions.items():
            result.append(
                {
                    "task_id": task_id,
                    "agent_id": context.agent.agent_id,
                    "task_name": context.task.name,
                    "start_time": (
                        context.stats.start_time.isoformat()
                        if context.stats.start_time
                        else None
                    ),
                    "progress": context.task.progress,
                    "execution_time": context.stats.execution_time,
                }
            )
        return result

    def get_task_logs(
        self,
        task_id: str,
        level: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get logs for a specific task"""
        # Check if task is active
        if task_id in self._active_executions:
            return self._active_executions[task_id].logger.get_logs(
                level, limit, offset
            )

        # If not active, the logs would need to be retrieved from storage
        # This implementation would depend on how logs are persisted
        return []

    def add_observer(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add an observer for execution events"""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Remove an observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers of an event"""
        for callback in self._observers:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error in execution observer: {e}")
