"""
Core Agent Framework for DockerForge

This module defines the base architecture for the agent system, including
the Agent base class, task definition, context management, and orchestration.
"""

import abc
import asyncio
import enum
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Status of an agent task"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVAL_REQUIRED = "approval_required"


class TaskPriority(int, Enum):
    """Priority levels for tasks"""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class AgentTask:
    """
    Represents a task to be executed by an agent.

    Tasks can be composed of subtasks and form a directed acyclic graph
    of operations that need to be completed.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    agent_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parent_id: Optional[str] = None
    subtasks: List["AgentTask"] = field(default_factory=list)
    requires_approval: bool = False
    approved_by: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "parent_id": self.parent_id,
            "subtasks": [subtask.to_dict() for subtask in self.subtasks],
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "progress": self.progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTask":
        """Create task from dictionary representation"""
        task = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            agent_id=data.get("agent_id", ""),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            priority=TaskPriority(data.get("priority", TaskPriority.NORMAL.value)),
            created_at=datetime.fromisoformat(
                data.get("created_at", datetime.now().isoformat())
            ),
            parent_id=data.get("parent_id"),
            requires_approval=data.get("requires_approval", False),
            approved_by=data.get("approved_by"),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data"),
            error=data.get("error"),
            progress=data.get("progress", 0.0),
        )

        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])

        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])

        if "subtasks" in data:
            task.subtasks = [cls.from_dict(subtask) for subtask in data["subtasks"]]

        return task


@dataclass
class AgentResult:
    """Result of an agent task execution"""

    success: bool
    task_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            "success": self.success,
            "task_id": self.task_id,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentResult":
        """Create result from dictionary representation"""
        return cls(
            success=data.get("success", False),
            task_id=data.get("task_id", ""),
            data=data.get("data"),
            error=data.get("error"),
            execution_time=data.get("execution_time", 0.0),
        )


class AgentContext:
    """
    Provides context for agent execution including user information,
    system state, and conversation history.
    """

    def __init__(
        self,
        user_id: str = None,
        conversation_id: str = None,
        system_info: Dict[str, Any] = None,
    ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.system_info = system_info or {}
        self.history = []
        self.created_at = datetime.now()
        self.metadata = {}

    def add_to_history(
        self, action: str, data: Dict[str, Any], timestamp: Optional[datetime] = None
    ):
        """Add an entry to context history"""
        self.history.append(
            {"action": action, "data": data, "timestamp": timestamp or datetime.now()}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation"""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "system_info": self.system_info,
            "history": [
                {
                    "action": h["action"],
                    "data": h["data"],
                    "timestamp": h["timestamp"].isoformat(),
                }
                for h in self.history
            ],
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        """Create context from dictionary representation"""
        context = cls(
            user_id=data.get("user_id"),
            conversation_id=data.get("conversation_id"),
            system_info=data.get("system_info", {}),
        )

        context.created_at = datetime.fromisoformat(
            data.get("created_at", datetime.now().isoformat())
        )
        context.metadata = data.get("metadata", {})

        for h in data.get("history", []):
            context.history.append(
                {
                    "action": h["action"],
                    "data": h["data"],
                    "timestamp": datetime.fromisoformat(h["timestamp"]),
                }
            )

        return context


class Agent(abc.ABC):
    """
    Base class for all agents in the system.

    Agents are responsible for executing specific types of tasks and
    can be composed to solve complex problems.
    """

    def __init__(self, agent_id: str, name: str, description: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = []
        self.supported_task_types = []
        self._observers = []

    @abc.abstractmethod
    async def execute_task(self, task: AgentTask, context: AgentContext) -> AgentResult:
        """
        Execute the given task and return a result.

        Must be implemented by all agent subclasses.
        """
        pass

    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if this agent can handle the given task"""
        # Default implementation checks task type against supported types
        return True

    def estimate_completion_time(self, task: AgentTask) -> float:
        """
        Estimate the time in seconds this task will take to complete.

        Used for scheduling and prioritization.
        """
        return 60.0  # Default 1 minute

    def add_observer(self, callback: Callable[["Agent", AgentTask, str, Any], None]):
        """Add an observer to be notified of agent events"""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable[["Agent", AgentTask, str, Any], None]):
        """Remove an observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def notify_observers(self, task: AgentTask, event: str, data: Any = None):
        """Notify all observers of an event"""
        for callback in self._observers:
            try:
                callback(self, task, event, data)
            except Exception as e:
                logger.error(f"Error in agent observer: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "supported_task_types": self.supported_task_types,
        }


class AgentFramework:
    """
    Main framework for managing and orchestrating agents in the system.

    Handles task routing, execution, state management, and agent coordination.
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._task_queue = asyncio.Queue()
        self._running_tasks: Dict[str, Tuple[AgentTask, asyncio.Task]] = {}
        self._task_history: Dict[str, AgentTask] = {}
        self._running = False
        self._max_concurrent_tasks = 10
        self._observers = []

    def register_agent(self, agent: Agent) -> None:
        """Register an agent with the framework"""
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent with ID {agent.agent_id} already registered")

        self.agents[agent.agent_id] = agent
        # Register observer for task updates
        agent.add_observer(self._handle_agent_event)
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the framework"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.remove_observer(self._handle_agent_event)
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    async def submit_task(
        self, task: AgentTask, context: Optional[AgentContext] = None
    ) -> str:
        """
        Submit a task for execution by an appropriate agent.

        Returns the task ID which can be used to retrieve results.
        """
        if not context:
            context = AgentContext()

        # Find appropriate agent if not specified
        if not task.agent_id:
            agent = self._find_agent_for_task(task)
            if agent:
                task.agent_id = agent.agent_id
            else:
                raise ValueError("No suitable agent found for task")
        elif task.agent_id not in self.agents:
            raise ValueError(f"Agent with ID {task.agent_id} not found")

        # Store task
        self._task_history[task.id] = task

        # Add task to queue
        await self._task_queue.put((task, context))
        logger.info(f"Task {task.id} ({task.name}) submitted to queue")

        # Notify observers
        self._notify_observers("task_submitted", task)

        return task.id

    async def approve_task(self, task_id: str, user_id: str) -> bool:
        """Approve a task that requires user approval"""
        if task_id not in self._task_history:
            return False

        task = self._task_history[task_id]
        if task.status != TaskStatus.APPROVAL_REQUIRED:
            return False

        task.approved_by = user_id
        task.status = TaskStatus.PENDING

        # Resubmit task
        context = AgentContext(user_id=user_id)
        await self._task_queue.put((task, context))
        logger.info(f"Task {task_id} approved by {user_id}")

        # Notify observers
        self._notify_observers("task_approved", task)

        return True

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or pending task"""
        if task_id not in self._task_history:
            return False

        task = self._task_history[task_id]

        # If task is running, cancel it
        if task_id in self._running_tasks:
            _, running_task = self._running_tasks[task_id]
            running_task.cancel()
            try:
                await running_task
            except asyncio.CancelledError:
                pass

            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            del self._running_tasks[task_id]
            logger.info(f"Task {task_id} cancelled")

            # Notify observers
            self._notify_observers("task_cancelled", task)

            return True

        # If task is pending in queue, we'd need to filter it out
        # This is more complex with asyncio.Queue, and we'd need a custom
        # queue implementation to support easy removal
        # For now, we'll mark it as cancelled and it will be skipped
        # when processed
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        logger.info(f"Task {task_id} marked as cancelled")

        # Notify observers
        self._notify_observers("task_cancelled", task)

        return True

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID"""
        return self._task_history.get(task_id)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.to_dict() for agent in self.agents.values()]

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering"""
        tasks = list(self._task_history.values())

        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]

        # Sort by creation time
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Apply pagination
        tasks = tasks[offset : offset + limit]

        return [task.to_dict() for task in tasks]

    async def start(self) -> None:
        """Start the agent framework task processor"""
        if self._running:
            return

        self._running = True
        logger.info("Agent framework started")

        for _ in range(self._max_concurrent_tasks):
            asyncio.create_task(self._task_processor())

    async def stop(self) -> None:
        """Stop the agent framework"""
        if not self._running:
            return

        self._running = False
        logger.info("Agent framework stopping, cancelling tasks...")

        # Cancel all running tasks
        for task_id, (_, running_task) in list(self._running_tasks.items()):
            running_task.cancel()
            try:
                await running_task
            except asyncio.CancelledError:
                pass

        self._running_tasks.clear()
        logger.info("Agent framework stopped")

    def add_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Add an observer to be notified of framework events"""
        self._observers.append(callback)

    def remove_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Remove an observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    async def _task_processor(self) -> None:
        """Process tasks from the queue"""
        while self._running:
            try:
                # Get task from queue
                task, context = await self._task_queue.get()

                # Skip cancelled tasks
                if task.status == TaskStatus.CANCELLED:
                    self._task_queue.task_done()
                    continue

                # Check if task requires approval and hasn't been approved
                if task.requires_approval and not task.approved_by:
                    task.status = TaskStatus.APPROVAL_REQUIRED
                    self._notify_observers("task_requires_approval", task)
                    self._task_queue.task_done()
                    continue

                # Get agent
                agent = self.agents.get(task.agent_id)
                if not agent:
                    logger.error(f"Agent {task.agent_id} not found for task {task.id}")
                    task.status = TaskStatus.FAILED
                    task.error = f"Agent {task.agent_id} not found"
                    self._notify_observers("task_failed", task)
                    self._task_queue.task_done()
                    continue

                # Update task status
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                self._notify_observers("task_started", task)

                # Execute task in a separate task
                execution_task = asyncio.create_task(
                    self._execute_agent_task(agent, task, context)
                )
                self._running_tasks[task.id] = (task, execution_task)

                # Mark queue task as done
                self._task_queue.task_done()
            except asyncio.CancelledError:
                logger.info("Task processor cancelled")
                break
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                # Keep the loop running
                continue

    async def _execute_agent_task(
        self, agent: Agent, task: AgentTask, context: AgentContext
    ) -> None:
        """Execute a task with the given agent"""
        try:
            # Record start time
            start_time = time.time()

            # Execute task
            result = await agent.execute_task(task, context)

            # Update task with result
            task.output_data = result.data
            task.error = result.error
            task.completed_at = datetime.now()
            task.status = TaskStatus.COMPLETED if result.success else TaskStatus.FAILED
            task.progress = 1.0 if result.success else task.progress

            # Update execution time
            result.execution_time = time.time() - start_time

            logger.info(f"Task {task.id} completed with status: {task.status}")

            # Notify observers
            if result.success:
                self._notify_observers("task_completed", task)
            else:
                self._notify_observers("task_failed", task)
        except asyncio.CancelledError:
            # Task was cancelled
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            logger.info(f"Task {task.id} execution cancelled")
            self._notify_observers("task_cancelled", task)
        except Exception as e:
            # Task failed with exception
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Error executing task {task.id}: {e}")
            self._notify_observers("task_failed", task)
        finally:
            # Remove from running tasks
            if task.id in self._running_tasks:
                del self._running_tasks[task.id]

    def _find_agent_for_task(self, task: AgentTask) -> Optional[Agent]:
        """Find the most appropriate agent for a task"""
        candidates = []

        for agent in self.agents.values():
            if agent.can_handle_task(task):
                candidates.append(agent)

        if not candidates:
            return None

        # For now, just return the first candidate
        # In the future, we could use more sophisticated selection
        return candidates[0]

    def _handle_agent_event(
        self, agent: Agent, task: AgentTask, event: str, data: Any
    ) -> None:
        """Handle events from agents"""
        # Update task in history
        if task.id in self._task_history:
            self._task_history[task.id] = task

        # Notify framework observers
        self._notify_observers(
            f"agent_{event}",
            {"agent": agent.to_dict(), "task": task.to_dict(), "data": data},
        )

    def _notify_observers(self, event: str, data: Any) -> None:
        """Notify all observers of an event"""
        for callback in self._observers:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error in framework observer: {e}")
