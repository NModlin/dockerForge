"""
Fix applier module for DockerForge.

This module provides functionality for applying fixes to Docker-related issues.
"""

import os
import json
import logging
import threading
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.fixes.fix_proposal import get_fix_proposal_manager, FixProposal, FixStatus, FixStep
from src.notifications.notification_manager import get_notification_manager, Notification, NotificationSeverity, NotificationType

# Set up logging
logger = get_logger("fix_applier")


class FixApplier:
    """Applier for Docker-related fixes."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create a new FixApplier instance (singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FixApplier, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the fix applier."""
        if self._initialized:
            return
        
        self._initialized = True
        self._fix_proposal_manager = get_fix_proposal_manager()
        self._notification_manager = get_notification_manager()
        self._backup_dir = os.path.expanduser(get_config("general.backup_dir"))
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self._backup_dir):
            os.makedirs(self._backup_dir, exist_ok=True)
        
        logger.info("Fix applier initialized")
    
    def _backup_file(self, file_path: str) -> Optional[str]:
        """Backup a file before modifying it.
        
        Args:
            file_path: The path to the file to backup
            
        Returns:
            The path to the backup file, or None if backup failed
        """
        if not os.path.exists(file_path):
            logger.warning(f"File not found for backup: {file_path}")
            return None
        
        try:
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_filename = f"{filename}.{timestamp}.bak"
            backup_path = os.path.join(self._backup_dir, backup_filename)
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Backed up file {file_path} to {backup_path}")
            
            return backup_path
        except Exception as e:
            logger.error(f"Error backing up file {file_path}: {str(e)}")
            return None
    
    def _execute_command(self, command: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a command.
        
        Args:
            command: The command to execute
            
        Returns:
            Tuple of (success, result)
        """
        try:
            # Execute command
            process = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            
            # Check result
            success = process.returncode == 0
            
            # Create result
            result = {
                "command": command,
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "success": success,
            }
            
            if success:
                logger.info(f"Command executed successfully: {command}")
            else:
                logger.warning(f"Command failed: {command}, returncode: {process.returncode}")
                logger.warning(f"stderr: {process.stderr}")
            
            return success, result
        except Exception as e:
            logger.error(f"Error executing command {command}: {str(e)}")
            
            result = {
                "command": command,
                "error": str(e),
                "success": False,
            }
            
            return False, result
    
    def _modify_file(self, file_path: str, code: str) -> Tuple[bool, Dict[str, Any]]:
        """Modify a file with the given code.
        
        Args:
            file_path: The path to the file to modify
            code: The new content for the file
            
        Returns:
            Tuple of (success, result)
        """
        try:
            # Backup file
            backup_path = self._backup_file(file_path)
            
            if not backup_path and os.path.exists(file_path):
                logger.warning(f"Failed to backup file {file_path}, aborting modification")
                
                result = {
                    "file_path": file_path,
                    "error": "Failed to backup file",
                    "success": False,
                }
                
                return False, result
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write new content to file
            with open(file_path, "w") as f:
                f.write(code)
            
            logger.info(f"Modified file {file_path}")
            
            result = {
                "file_path": file_path,
                "backup_path": backup_path,
                "success": True,
            }
            
            return True, result
        except Exception as e:
            logger.error(f"Error modifying file {file_path}: {str(e)}")
            
            result = {
                "file_path": file_path,
                "error": str(e),
                "success": False,
            }
            
            return False, result
    
    def _apply_step(self, step: FixStep) -> Tuple[bool, Dict[str, Any]]:
        """Apply a fix step.
        
        Args:
            step: The fix step to apply
            
        Returns:
            Tuple of (success, result)
        """
        # Check if step has a command
        if step.command:
            return self._execute_command(step.command)
        
        # Check if step has code and file path
        if step.code and step.file_path:
            return self._modify_file(step.file_path, step.code)
        
        # Check if step has manual action
        if step.manual_action:
            logger.info(f"Manual action required: {step.manual_action}")
            
            result = {
                "manual_action": step.manual_action,
                "success": True,
                "note": "Manual action marked as successful, but requires user verification",
            }
            
            return True, result
        
        # No action to take
        logger.warning(f"No action to take for step: {step.title}")
        
        result = {
            "step": step.title,
            "error": "No action to take",
            "success": False,
        }
        
        return False, result
    
    def _verify_step(self, step: FixStep) -> Tuple[bool, Dict[str, Any]]:
        """Verify a fix step.
        
        Args:
            step: The fix step to verify
            
        Returns:
            Tuple of (success, result)
        """
        # Check if step has verification
        if not step.verification:
            logger.info(f"No verification for step: {step.title}")
            
            result = {
                "step": step.title,
                "note": "No verification specified",
                "success": True,
            }
            
            return True, result
        
        # Check if verification is a command
        if step.verification.startswith("$"):
            command = step.verification[1:].strip()
            return self._execute_command(command)
        
        # Otherwise, it's a manual verification
        logger.info(f"Manual verification required: {step.verification}")
        
        result = {
            "verification": step.verification,
            "success": True,
            "note": "Manual verification marked as successful, but requires user confirmation",
        }
        
        return True, result
    
    def apply_fix(self, fix_id: str, dry_run: bool = None) -> Dict[str, Any]:
        """Apply a fix.
        
        Args:
            fix_id: The ID of the fix to apply
            dry_run: Whether to perform a dry run (if None, use config setting)
            
        Returns:
            Result of applying the fix
        """
        # Get fix
        fix = self._fix_proposal_manager.get_fix(fix_id)
        
        if not fix:
            logger.warning(f"Fix not found: {fix_id}")
            return {
                "success": False,
                "error": f"Fix not found: {fix_id}",
            }
        
        # Check if fix is approved
        if fix.status != FixStatus.APPROVED:
            logger.warning(f"Fix {fix_id} is not approved: {fix.status.value}")
            return {
                "success": False,
                "error": f"Fix is not approved: {fix.status.value}",
            }
        
        # Determine if this is a dry run
        if dry_run is None:
            dry_run = get_config("notifications.fixes.dry_run_by_default", True)
        
        # Log start of fix application
        if dry_run:
            logger.info(f"Starting dry run of fix: {fix_id} - {fix.title}")
        else:
            logger.info(f"Starting application of fix: {fix_id} - {fix.title}")
        
        # Initialize results
        results = {
            "fix_id": fix_id,
            "title": fix.title,
            "dry_run": dry_run,
            "steps": [],
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Apply each step
        for i, step in enumerate(fix.steps):
            step_result = {
                "step_index": i,
                "title": step.title,
                "description": step.description,
            }
            
            # Log step
            logger.info(f"Applying step {i+1}/{len(fix.steps)}: {step.title}")
            
            # Apply step
            if dry_run:
                # In dry run mode, just log what would be done
                if step.command:
                    step_result["command"] = step.command
                    step_result["dry_run"] = True
                    step_result["success"] = True
                    logger.info(f"Dry run: Would execute command: {step.command}")
                elif step.code and step.file_path:
                    step_result["file_path"] = step.file_path
                    step_result["dry_run"] = True
                    step_result["success"] = True
                    logger.info(f"Dry run: Would modify file: {step.file_path}")
                elif step.manual_action:
                    step_result["manual_action"] = step.manual_action
                    step_result["dry_run"] = True
                    step_result["success"] = True
                    logger.info(f"Dry run: Would require manual action: {step.manual_action}")
                else:
                    step_result["error"] = "No action to take"
                    step_result["dry_run"] = True
                    step_result["success"] = False
                    logger.warning(f"Dry run: No action to take for step: {step.title}")
                    results["success"] = False
            else:
                # Apply step for real
                success, step_details = self._apply_step(step)
                
                # Update step result
                step_result.update(step_details)
                step_result["success"] = success
                
                # If step failed, mark fix as failed
                if not success:
                    results["success"] = False
                    
                    # Add error message
                    if "error" in step_details:
                        step_result["error"] = step_details["error"]
                    
                    # Stop applying steps
                    break
                
                # Verify step if it succeeded
                if success and step.verification:
                    logger.info(f"Verifying step {i+1}/{len(fix.steps)}: {step.title}")
                    
                    verify_success, verify_details = self._verify_step(step)
                    
                    # Update step result with verification details
                    step_result["verification"] = {
                        "success": verify_success,
                    }
                    
                    if "command" in verify_details:
                        step_result["verification"]["command"] = verify_details["command"]
                    
                    if "stdout" in verify_details:
                        step_result["verification"]["stdout"] = verify_details["stdout"]
                    
                    if "stderr" in verify_details:
                        step_result["verification"]["stderr"] = verify_details["stderr"]
                    
                    if "error" in verify_details:
                        step_result["verification"]["error"] = verify_details["error"]
                    
                    if "note" in verify_details:
                        step_result["verification"]["note"] = verify_details["note"]
                    
                    # If verification failed, mark fix as failed
                    if not verify_success:
                        results["success"] = False
                        
                        # Add error message
                        if "error" in verify_details:
                            step_result["verification"]["error"] = verify_details["error"]
                        
                        # Stop applying steps
                        break
            
            # Add step result to results
            results["steps"].append(step_result)
        
        # Update fix status
        if not dry_run:
            if results["success"]:
                self._fix_proposal_manager.update_fix_status(fix_id, FixStatus.APPLIED, results)
                logger.info(f"Fix applied successfully: {fix_id} - {fix.title}")
            else:
                self._fix_proposal_manager.update_fix_status(fix_id, FixStatus.FAILED, results)
                logger.warning(f"Fix application failed: {fix_id} - {fix.title}")
        
        return results
    
    def rollback_fix(self, fix_id: str) -> Dict[str, Any]:
        """Roll back a fix.
        
        Args:
            fix_id: The ID of the fix to roll back
            
        Returns:
            Result of rolling back the fix
        """
        # Get fix
        fix = self._fix_proposal_manager.get_fix(fix_id)
        
        if not fix:
            logger.warning(f"Fix not found: {fix_id}")
            return {
                "success": False,
                "error": f"Fix not found: {fix_id}",
            }
        
        # Check if fix is applied
        if fix.status != FixStatus.APPLIED:
            logger.warning(f"Fix {fix_id} is not applied: {fix.status.value}")
            return {
                "success": False,
                "error": f"Fix is not applied: {fix.status.value}",
            }
        
        # Check if fix has result
        if not fix.result:
            logger.warning(f"Fix {fix_id} has no result")
            return {
                "success": False,
                "error": "Fix has no result",
            }
        
        # Log start of rollback
        logger.info(f"Starting rollback of fix: {fix_id} - {fix.title}")
        
        # Initialize results
        results = {
            "fix_id": fix_id,
            "title": fix.title,
            "steps": [],
            "success": True,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Roll back each step in reverse order
        for i, step_result in reversed(list(enumerate(fix.result.get("steps", [])))):
            rollback_result = {
                "step_index": i,
                "title": step_result.get("title", f"Step {i+1}"),
            }
            
            # Log step
            logger.info(f"Rolling back step {i+1}/{len(fix.result['steps'])}: {rollback_result['title']}")
            
            # Check if step was successful
            if not step_result.get("success", False):
                rollback_result["skipped"] = True
                rollback_result["reason"] = "Step was not successfully applied"
                rollback_result["success"] = True
                logger.info(f"Skipping rollback of step {i+1}: Step was not successfully applied")
                results["steps"].append(rollback_result)
                continue
            
            # Roll back step
            if "file_path" in step_result and "backup_path" in step_result:
                # Roll back file modification
                file_path = step_result["file_path"]
                backup_path = step_result["backup_path"]
                
                try:
                    # Check if backup exists
                    if not os.path.exists(backup_path):
                        rollback_result["error"] = f"Backup file not found: {backup_path}"
                        rollback_result["success"] = False
                        results["success"] = False
                        logger.warning(f"Backup file not found: {backup_path}")
                    else:
                        # Restore from backup
                        shutil.copy2(backup_path, file_path)
                        rollback_result["file_path"] = file_path
                        rollback_result["backup_path"] = backup_path
                        rollback_result["success"] = True
                        logger.info(f"Restored file {file_path} from backup {backup_path}")
                except Exception as e:
                    rollback_result["error"] = str(e)
                    rollback_result["success"] = False
                    results["success"] = False
                    logger.error(f"Error restoring file {file_path} from backup {backup_path}: {str(e)}")
            elif "command" in step_result:
                # No automatic rollback for commands
                rollback_result["command"] = step_result["command"]
                rollback_result["manual_rollback"] = True
                rollback_result["success"] = True
                rollback_result["note"] = "Command execution cannot be automatically rolled back"
                logger.info(f"Command execution cannot be automatically rolled back: {step_result['command']}")
            else:
                # No rollback needed
                rollback_result["skipped"] = True
                rollback_result["reason"] = "No rollback needed for this step"
                rollback_result["success"] = True
                logger.info(f"No rollback needed for step {i+1}")
            
            # Add rollback result to results
            results["steps"].append(rollback_result)
        
        # Update fix status
        if results["success"]:
            self._fix_proposal_manager.update_fix_status(fix_id, FixStatus.ROLLED_BACK, results)
            logger.info(f"Fix rolled back successfully: {fix_id} - {fix.title}")
        else:
            # Still mark as rolled back, but with errors
            results["partial"] = True
            self._fix_proposal_manager.update_fix_status(fix_id, FixStatus.ROLLED_BACK, results)
            logger.warning(f"Fix rollback had errors: {fix_id} - {fix.title}")
        
        return results


def get_fix_applier() -> FixApplier:
    """Get the fix applier instance.
    
    Returns:
        The fix applier instance
    """
    return FixApplier()
