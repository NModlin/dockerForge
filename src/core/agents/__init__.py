"""
DockerForge Agent Framework - Autonomous task execution and automation

This package provides the agent framework for DockerForge, enabling autonomous 
task execution and intelligent automation of container management, security,
optimization, and documentation tasks.
"""

from .agent_framework import (
    Agent,
    AgentFramework,
    AgentContext,
    AgentTask,
    AgentResult
)

__all__ = [
    'Agent',
    'AgentFramework',
    'AgentContext',
    'AgentTask',
    'AgentResult'
]
