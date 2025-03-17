"""
DockerForge Compose Change Manager Module.

This module provides functionality for managing changes to Docker Compose files,
including automatic backups, diff generation, atomic updates, version history,
and restore capabilities.
"""

import os
import shutil
import tempfile
import datetime
import difflib
import json
import yaml
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)


class ChangeManager:
    """Manage changes to Docker Compose files."""

    def __init__(self, config: Dict = None):
        """Initialize ChangeManager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.backup_dir = self._get_backup_dir()
        self.history = {}
        self._load_history()

    def _get_backup_dir(self) -> str:
        """Get the backup directory path.

        Returns:
            Path to the backup directory
        """
        backup_dir = self.config.get('backup_dir', os.path.expanduser('~/.dockerforge/backups/compose'))
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def _load_history(self) -> None:
        """Load change history from disk."""
        history_file = os.path.join(self.backup_dir, 'history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.history = json.load(f)
                logger.debug(f"Loaded change history from {history_file}")
            except Exception as e:
                logger.warning(f"Failed to load change history: {e}")
                self.history = {}

    def _save_history(self) -> None:
        """Save change history to disk."""
        history_file = os.path.join(self.backup_dir, 'history.json')
        try:
            with open(history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.debug(f"Saved change history to {history_file}")
        except Exception as e:
            logger.warning(f"Failed to save change history: {e}")

    def backup_file(self, file_path: str, description: str = None) -> str:
        """Create a backup of a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            description: Optional description of the backup

        Returns:
            Path to the backup file
        """
        try:
            # Ensure file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Create backup filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = os.path.basename(file_path)
            backup_name = f"{file_name}.{timestamp}.bak"
            backup_path = os.path.join(self.backup_dir, backup_name)

            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup of {file_path} at {backup_path}")

            # Update history
            abs_path = os.path.abspath(file_path)
            if abs_path not in self.history:
                self.history[abs_path] = []

            self.history[abs_path].append({
                'timestamp': timestamp,
                'backup_path': backup_path,
                'description': description or 'Automatic backup before change',
            })

            # Save history
            self._save_history()

            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path}: {e}")
            raise

    def get_backup_history(self, file_path: str) -> List[Dict]:
        """Get backup history for a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file

        Returns:
            List of backup entries
        """
        abs_path = os.path.abspath(file_path)
        return self.history.get(abs_path, [])

    def restore_from_backup(self, file_path: str, backup_path: str) -> None:
        """Restore a Docker Compose file from a backup.

        Args:
            file_path: Path to the Docker Compose file
            backup_path: Path to the backup file
        """
        try:
            # Ensure backup exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup not found: {backup_path}")

            # Create a backup of the current file before restoring
            self.backup_file(file_path, description='Automatic backup before restore')

            # Copy backup to original location
            shutil.copy2(backup_path, file_path)
            logger.info(f"Restored {file_path} from backup {backup_path}")

            # Update history
            abs_path = os.path.abspath(file_path)
            if abs_path not in self.history:
                self.history[abs_path] = []

            self.history[abs_path].append({
                'timestamp': datetime.datetime.now().strftime('%Y%m%d_%H%M%S'),
                'backup_path': backup_path,
                'description': f'Restored from backup {os.path.basename(backup_path)}',
                'is_restore': True,
            })

            # Save history
            self._save_history()
        except Exception as e:
            logger.error(f"Failed to restore {file_path} from backup {backup_path}: {e}")
            raise

    def generate_diff(self, file_path: str, backup_path: str = None) -> str:
        """Generate a diff between a Docker Compose file and its backup.

        Args:
            file_path: Path to the Docker Compose file
            backup_path: Path to the backup file (optional, uses latest backup if not provided)

        Returns:
            Diff string
        """
        try:
            # Ensure file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Get backup path if not provided
            if not backup_path:
                history = self.get_backup_history(file_path)
                if not history:
                    raise ValueError(f"No backup history found for {file_path}")
                backup_path = history[-1]['backup_path']

            # Ensure backup exists
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup not found: {backup_path}")

            # Read files
            with open(file_path, 'r') as f:
                current_lines = f.readlines()
            with open(backup_path, 'r') as f:
                backup_lines = f.readlines()

            # Generate diff
            diff = difflib.unified_diff(
                backup_lines,
                current_lines,
                fromfile=f"a/{os.path.basename(file_path)}",
                tofile=f"b/{os.path.basename(file_path)}",
                n=3
            )

            return ''.join(diff)
        except Exception as e:
            logger.error(f"Failed to generate diff for {file_path}: {e}")
            raise

    def update_file(self, file_path: str, new_content: str, description: str = None) -> None:
        """Update a Docker Compose file atomically.

        Args:
            file_path: Path to the Docker Compose file
            new_content: New content for the file
            description: Optional description of the change
        """
        try:
            # Ensure file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Create a backup of the current file
            self.backup_file(file_path, description=description)

            # Write to a temporary file first
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(new_content)
                temp_path = temp_file.name

            # Replace the original file atomically
            shutil.move(temp_path, file_path)
            logger.info(f"Updated {file_path} atomically")
        except Exception as e:
            logger.error(f"Failed to update {file_path}: {e}")
            raise

    def update_yaml(self, file_path: str, yaml_data: Dict, description: str = None) -> None:
        """Update a Docker Compose file with new YAML data.

        Args:
            file_path: Path to the Docker Compose file
            yaml_data: New YAML data
            description: Optional description of the change
        """
        try:
            # Convert YAML data to string
            yaml_str = yaml.dump(yaml_data, default_flow_style=False, sort_keys=False)
            
            # Update the file
            self.update_file(file_path, yaml_str, description)
        except Exception as e:
            logger.error(f"Failed to update YAML in {file_path}: {e}")
            raise

    def get_latest_backup(self, file_path: str) -> Optional[str]:
        """Get the latest backup for a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file

        Returns:
            Path to the latest backup file or None if no backups exist
        """
        history = self.get_backup_history(file_path)
        if not history:
            return None
        return history[-1]['backup_path']

    def cleanup_old_backups(self, file_path: str, max_backups: int = 10) -> None:
        """Clean up old backups for a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            max_backups: Maximum number of backups to keep
        """
        try:
            abs_path = os.path.abspath(file_path)
            history = self.history.get(abs_path, [])
            
            # If we have more backups than the maximum, remove the oldest ones
            if len(history) > max_backups:
                # Sort by timestamp
                history.sort(key=lambda x: x['timestamp'])
                
                # Remove oldest backups
                backups_to_remove = history[:-max_backups]
                for backup in backups_to_remove:
                    backup_path = backup['backup_path']
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                        logger.debug(f"Removed old backup: {backup_path}")
                
                # Update history
                self.history[abs_path] = history[-max_backups:]
                self._save_history()
        except Exception as e:
            logger.warning(f"Failed to clean up old backups for {file_path}: {e}")
