"""
Fix application system for DockerForge.

This package provides functionality for proposing, approving, and applying fixes
to Docker-related issues.
"""

from src.fixes.fix_applier import FixApplier, get_fix_applier
from src.fixes.fix_proposal import FixProposalManager, get_fix_proposal_manager
