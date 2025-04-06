"""
Task Planner for the Agent Framework

This module provides functionality for breaking down high-level tasks
into smaller, executable subtasks, creating task execution plans,
and managing task dependencies.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .agent_framework import AgentTask, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class TaskRelationType(str, Enum):
    """Type of relationship between tasks"""

    SUBTASK = "subtask"  # Task is a subtask of another task
    DEPENDS_ON = "depends_on"  # Task depends on another task to complete first
    BLOCKS = "blocks"  # Task blocks another task from starting
    RELATED_TO = "related_to"  # Tasks are related but no specific dependency


class TaskPlan:
    """
    Represents a plan for executing a complex task, including subtasks,
    dependencies, and execution order.
    """

    def __init__(
        self, name: str, description: str = "", main_task_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.main_task_id = main_task_id
        self.tasks: Dict[str, AgentTask] = {}
        self.relations: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.execution_order: List[List[str]] = []  # List of batches of task IDs

    def add_task(self, task: AgentTask) -> str:
        """Add a task to the plan"""
        self.tasks[task.id] = task
        return task.id

    def add_relation(
        self,
        from_task_id: str,
        to_task_id: str,
        relation_type: TaskRelationType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a relation between two tasks"""
        if from_task_id not in self.tasks:
            raise ValueError(f"Task {from_task_id} not in plan")
        if to_task_id not in self.tasks:
            raise ValueError(f"Task {to_task_id} not in plan")

        # Check for cycles
        if relation_type == TaskRelationType.DEPENDS_ON:
            if self._would_create_cycle(from_task_id, to_task_id):
                raise ValueError("Adding this dependency would create a cycle")

        self.relations.append(
            {
                "from_task_id": from_task_id,
                "to_task_id": to_task_id,
                "relation_type": relation_type.value,
                "metadata": metadata or {},
            }
        )

        # If it's a subtask relation, update the parent_id
        if relation_type == TaskRelationType.SUBTASK:
            self.tasks[from_task_id].parent_id = to_task_id
            if to_task_id in self.tasks:
                self.tasks[to_task_id].subtasks.append(self.tasks[from_task_id])

        # Re-compute execution order if dependencies changed
        if relation_type == TaskRelationType.DEPENDS_ON:
            self._compute_execution_order()

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get a task from the plan"""
        return self.tasks.get(task_id)

    def get_related_tasks(
        self, task_id: str, relation_type: Optional[TaskRelationType] = None
    ) -> List[AgentTask]:
        """Get tasks related to the given task"""
        if task_id not in self.tasks:
            return []

        result = []

        for relation in self.relations:
            if relation["from_task_id"] == task_id:
                if (
                    relation_type is None
                    or relation["relation_type"] == relation_type.value
                ):
                    related_id = relation["to_task_id"]
                    if related_id in self.tasks:
                        result.append(self.tasks[related_id])
            elif relation["to_task_id"] == task_id:
                if (
                    relation_type is None
                    or relation["relation_type"] == relation_type.value
                ):
                    related_id = relation["from_task_id"]
                    if related_id in self.tasks:
                        result.append(self.tasks[related_id])

        return result

    def get_dependencies(self, task_id: str) -> List[AgentTask]:
        """Get tasks that this task depends on"""
        if task_id not in self.tasks:
            return []

        result = []

        for relation in self.relations:
            if (
                relation["from_task_id"] == task_id
                and relation["relation_type"] == TaskRelationType.DEPENDS_ON.value
            ):
                dep_id = relation["to_task_id"]
                if dep_id in self.tasks:
                    result.append(self.tasks[dep_id])

        return result

    def get_dependents(self, task_id: str) -> List[AgentTask]:
        """Get tasks that depend on this task"""
        if task_id not in self.tasks:
            return []

        result = []

        for relation in self.relations:
            if (
                relation["to_task_id"] == task_id
                and relation["relation_type"] == TaskRelationType.DEPENDS_ON.value
            ):
                dep_id = relation["from_task_id"]
                if dep_id in self.tasks:
                    result.append(self.tasks[dep_id])

        return result

    def get_next_tasks(self) -> List[AgentTask]:
        """Get tasks that are ready to execute (have no incomplete dependencies)"""
        result = []

        for task_id, task in self.tasks.items():
            if task.status == TaskStatus.PENDING:
                dependencies = self.get_dependencies(task_id)
                all_dependencies_complete = True

                for dep in dependencies:
                    if dep.status != TaskStatus.COMPLETED:
                        all_dependencies_complete = False
                        break

                if all_dependencies_complete:
                    result.append(task)

        # Sort by priority
        result.sort(key=lambda t: t.priority.value, reverse=True)

        return result

    def update_task(self, task: AgentTask) -> None:
        """Update a task in the plan"""
        if task.id not in self.tasks:
            raise ValueError(f"Task {task.id} not in plan")

        self.tasks[task.id] = task

    def get_completion_status(self) -> Dict[str, Any]:
        """Get the overall completion status of the plan"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED
        )
        failed_tasks = sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.FAILED
        )
        cancelled_tasks = sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.CANCELLED
        )
        pending_tasks = sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.PENDING
        )
        running_tasks = sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING
        )

        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "cancelled_tasks": cancelled_tasks,
            "pending_tasks": pending_tasks,
            "running_tasks": running_tasks,
            "completion_percentage": completion_percentage,
            "is_complete": completed_tasks + failed_tasks + cancelled_tasks
            == total_tasks,
            "is_successful": failed_tasks == 0
            and cancelled_tasks == 0
            and completed_tasks == total_tasks,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "main_task_id": self.main_task_id,
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "relations": self.relations,
            "created_at": self.created_at.isoformat(),
            "execution_order": self.execution_order,
            "completion_status": self.get_completion_status(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskPlan":
        """Create plan from dictionary representation"""
        plan = cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            main_task_id=data.get("main_task_id"),
        )

        plan.id = data.get("id", str(uuid.uuid4()))
        plan.created_at = datetime.fromisoformat(
            data.get("created_at", datetime.now().isoformat())
        )

        # Import tasks
        for task_data in data.get("tasks", {}).values():
            task = AgentTask.from_dict(task_data)
            plan.tasks[task.id] = task

        # Import relations
        for relation in data.get("relations", []):
            plan.relations.append(relation)

            # If it's a subtask relation, update the parent_id
            if relation["relation_type"] == TaskRelationType.SUBTASK.value:
                from_id = relation["from_task_id"]
                to_id = relation["to_task_id"]
                if from_id in plan.tasks and to_id in plan.tasks:
                    plan.tasks[from_id].parent_id = to_id
                    plan.tasks[to_id].subtasks.append(plan.tasks[from_id])

        # Import execution order
        plan.execution_order = data.get("execution_order", [])

        return plan

    def _compute_execution_order(self) -> None:
        """Compute a valid execution order for tasks based on dependencies"""
        # Use a topological sort to compute execution order
        visited: Set[str] = set()
        temp: Set[str] = set()
        order: List[str] = []

        def visit(task_id: str) -> None:
            """DFS helper function"""
            if task_id in temp:
                raise ValueError("Cycle detected in task dependencies")
            if task_id in visited:
                return

            temp.add(task_id)

            # Visit all dependencies
            for relation in self.relations:
                if (
                    relation["from_task_id"] == task_id
                    and relation["relation_type"] == TaskRelationType.DEPENDS_ON.value
                ):
                    visit(relation["to_task_id"])

            temp.remove(task_id)
            visited.add(task_id)
            order.append(task_id)

        # Visit all tasks
        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)

        # Reverse to get correct order
        order.reverse()

        # Group into batches that can be executed in parallel
        batches: List[List[str]] = []
        remaining = set(order)

        while remaining:
            batch = []
            for task_id in list(remaining):
                # Check if all dependencies are in previous batches
                can_execute = True
                for relation in self.relations:
                    if (
                        relation["from_task_id"] == task_id
                        and relation["relation_type"]
                        == TaskRelationType.DEPENDS_ON.value
                    ):
                        dep_id = relation["to_task_id"]
                        if dep_id in remaining:
                            can_execute = False
                            break

                if can_execute:
                    batch.append(task_id)
                    remaining.remove(task_id)

            if not batch:
                # No tasks can be executed, must be a cycle
                raise ValueError("Cycle detected in task dependencies")

            batches.append(batch)

        self.execution_order = batches

    def _would_create_cycle(self, from_task_id: str, to_task_id: str) -> bool:
        """Check if adding a dependency from from_task_id to to_task_id would create a cycle"""
        # If to_task_id depends on from_task_id (directly or indirectly),
        # adding a dependency from from_task_id to to_task_id would create a cycle

        # Use DFS to check for cycles
        visited: Set[str] = set()

        def has_path(start: str, end: str) -> bool:
            """Check if there is a path from start to end"""
            if start == end:
                return True
            if start in visited:
                return False

            visited.add(start)

            for relation in self.relations:
                if (
                    relation["from_task_id"] == start
                    and relation["relation_type"] == TaskRelationType.DEPENDS_ON.value
                ):
                    if has_path(relation["to_task_id"], end):
                        return True

            return False

        return has_path(to_task_id, from_task_id)


class TaskPlanner:
    """
    Service for planning and managing complex tasks by breaking them down
    into subtasks and defining dependencies.
    """

    def __init__(self):
        self.plans: Dict[str, TaskPlan] = {}

    def create_plan(self, name: str, description: str = "") -> TaskPlan:
        """Create a new task plan"""
        plan = TaskPlan(name=name, description=description)
        self.plans[plan.id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """Get a plan by ID"""
        return self.plans.get(plan_id)

    def list_plans(self) -> List[Dict[str, Any]]:
        """List all plans"""
        return [plan.to_dict() for plan in self.plans.values()]

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        if plan_id in self.plans:
            del self.plans[plan_id]
            return True
        return False

    def decompose_task(
        self, task: AgentTask, subtasks: List[Dict[str, Any]]
    ) -> TaskPlan:
        """
        Decompose a task into subtasks with dependencies.

        Args:
            task: The main task to decompose
            subtasks: List of subtask specifications with:
                - name: subtask name
                - description: subtask description
                - agent_id: (optional) ID of agent to handle subtask
                - depends_on: (optional) list of subtask indexes this depends on
                - priority: (optional) task priority
                - requires_approval: (optional) whether task requires approval
                - input_data: (optional) input data for the subtask

        Returns:
            TaskPlan: A plan for executing the task and its subtasks
        """
        plan = TaskPlan(
            name=f"Plan for {task.name}",
            description=f"Execution plan for task: {task.description}",
            main_task_id=task.id,
        )

        # Add main task
        plan.add_task(task)

        # Create subtasks
        created_subtasks = []
        for subtask_spec in subtasks:
            subtask = AgentTask(
                name=subtask_spec["name"],
                description=subtask_spec.get("description", ""),
                agent_id=subtask_spec.get("agent_id", ""),
                priority=subtask_spec.get("priority", TaskPriority.NORMAL),
                requires_approval=subtask_spec.get("requires_approval", False),
                input_data=subtask_spec.get("input_data", {}),
            )
            plan.add_task(subtask)
            created_subtasks.append(subtask)

            # Add subtask relation to main task
            plan.add_relation(
                from_task_id=subtask.id,
                to_task_id=task.id,
                relation_type=TaskRelationType.SUBTASK,
            )

        # Add dependencies between subtasks
        for i, subtask_spec in enumerate(subtasks):
            if "depends_on" in subtask_spec:
                for dep_idx in subtask_spec["depends_on"]:
                    if 0 <= dep_idx < len(created_subtasks):
                        plan.add_relation(
                            from_task_id=created_subtasks[i].id,
                            to_task_id=created_subtasks[dep_idx].id,
                            relation_type=TaskRelationType.DEPENDS_ON,
                        )

        # Store the plan
        self.plans[plan.id] = plan

        return plan

    def get_execution_plan(self, plan_id: str) -> List[List[AgentTask]]:
        """
        Get the execution plan for a task plan.

        Returns a list of batches, where each batch is a list of tasks
        that can be executed in parallel.
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return []

        result = []
        for batch_ids in plan.execution_order:
            batch = []
            for task_id in batch_ids:
                if task_id in plan.tasks:
                    batch.append(plan.tasks[task_id])
            result.append(batch)

        return result

    def update_plan_from_task(self, plan_id: str, task: AgentTask) -> bool:
        """Update a task in a plan"""
        plan = self.get_plan(plan_id)
        if not plan or task.id not in plan.tasks:
            return False

        plan.update_task(task)
        return True
