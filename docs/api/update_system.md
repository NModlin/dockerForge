# Update System API Reference

This document provides a reference for the DockerForge Update System API.

## Version Checker

The `VersionChecker` class is responsible for checking for updates to the DockerForge application.

### Class: `VersionChecker`

```python
from src.update.version_checker import VersionChecker
from src.config.config_manager import ConfigManager

config_manager = ConfigManager()
version_checker = VersionChecker(config_manager)
```

#### Methods

##### `check_for_updates(force=False)`

Check if updates are available.

**Parameters:**
- `force` (bool): Force a check even if the cache is valid.

**Returns:**
- Tuple containing:
  - Boolean indicating if an update is available
  - The latest version string (or None if check failed)
  - The release URL (or None if check failed)

**Example:**
```python
update_available, latest_version, release_url = version_checker.check_for_updates()
if update_available:
    print(f"Update available: {latest_version}")
    print(f"Release URL: {release_url}")
else:
    print("No updates available")
```

##### `get_release_notes(version=None)`

Get the release notes for a specific version.

**Parameters:**
- `version` (str, optional): The version to get release notes for. If None, gets the latest version.

**Returns:**
- The release notes as a string.

**Example:**
```python
release_notes = version_checker.get_release_notes()
print(release_notes)
```

## Update Manager

The `UpdateManager` class is responsible for managing the update process for DockerForge.

### Class: `UpdateManager`

```python
from src.update.update_manager import UpdateManager
from src.config.config_manager import ConfigManager
from src.platforms.platform_adapter import PlatformAdapter

config_manager = ConfigManager()
platform_adapter = PlatformAdapter()
update_manager = UpdateManager(config_manager, platform_adapter)
```

#### Methods

##### `update(version=None, force=False)`

Update DockerForge to the specified version or the latest version.

**Parameters:**
- `version` (str, optional): The version to update to. If None, updates to the latest version.
- `force` (bool): Force the update even if already at the latest version.

**Returns:**
- Boolean indicating if the update was successful.

**Example:**
```python
success = update_manager.update()
if success:
    print("Update successful")
else:
    print("Update failed")
```

##### `rollback(backup_id=None)`

Rollback to a previous version using a backup.

**Parameters:**
- `backup_id` (str, optional): The backup ID to rollback to. If None, uses the most recent backup.

**Returns:**
- Boolean indicating if the rollback was successful.

**Example:**
```python
success = update_manager.rollback()
if success:
    print("Rollback successful")
else:
    print("Rollback failed")
```

##### `list_backups()`

List all available backups.

**Returns:**
- A list of dictionaries containing backup information.

**Example:**
```python
backups = update_manager.list_backups()
for backup in backups:
    print(f"Backup ID: {backup['id']}")
    print(f"Timestamp: {backup['timestamp']}")
    print(f"Version: {backup['version']}")
```

## CLI Interface

The update system is accessible through the DockerForge CLI.

### Command: `dockerforge update check`

Check if updates are available.

**Options:**
- `--force`: Force a check even if the cache is valid.

### Command: `dockerforge update apply`

Apply available updates.

**Options:**
- `--version VERSION`: Specific version to update to (default: latest).
- `--force`: Force update even if already at latest version.
- `--yes`, `-y`: Skip confirmation prompt.

### Command: `dockerforge update rollback`

Rollback to a previous version.

**Options:**
- `--backup-id BACKUP_ID`: Specific backup ID to rollback to (default: most recent).
- `--yes`, `-y`: Skip confirmation prompt.

### Command: `dockerforge update list-backups`

List all available backups.

## Configuration

The update system can be configured in the DockerForge configuration file:

```yaml
update:
  enabled: true
  check_on_startup: true
  auto_check_interval: 86400  # seconds (1 day)
  
  # Version checking settings
  api_url: "https://api.github.com/repos/dockerforge/dockerforge/releases/latest"
  release_url: "https://github.com/dockerforge/dockerforge/releases"
  cache_ttl: 24  # hours
  
  # Update application settings
  auto_backup: true
  backup_dir: ~/.dockerforge/backups/updates
  max_backups: 10
  
  # Notification settings
  notify_on_update: true
  notify_on_failure: true
  
  # Rollback settings
  auto_rollback_on_failure: true
  keep_failed_backups: true
