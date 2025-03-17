# Update System Developer Guide

This guide provides information for developers who want to extend or modify the DockerForge Update System.

## Architecture Overview

The Update System consists of the following components:

1. **Version Checker**: Responsible for checking for available updates
2. **Update Manager**: Handles the update process, including backups and rollbacks
3. **CLI Interface**: Provides a command-line interface for users to interact with the update system

### Component Diagram

```
+-------------------+     +-------------------+     +-------------------+
| CLI Interface     |---->| Update Manager    |---->| Version Checker   |
| (cli_update.py)   |     | (update_manager.py)|     | (version_checker.py)|
+-------------------+     +-------------------+     +-------------------+
                           |         |
                           v         v
                  +-------------------+     +-------------------+
                  | Config Manager    |     | Platform Adapter  |
                  | (config_manager.py)|     | (platform_adapter.py)|
                  +-------------------+     +-------------------+
```

## Version Checker

The `VersionChecker` class is responsible for checking if updates are available for the DockerForge application. It communicates with the GitHub API to get information about the latest release.

### Key Features

- Caching of update information to reduce API calls
- Support for different version formats (semver, etc.)
- Release notes retrieval

### Extension Points

To extend the `VersionChecker` class:

1. **Add support for additional update sources**: Modify the `check_for_updates` method to support additional sources beyond GitHub.
2. **Implement additional version comparison logic**: Enhance the version comparison logic in the `check_for_updates` method.
3. **Add support for pre-release versions**: Modify the `check_for_updates` method to include pre-release versions.

## Update Manager

The `UpdateManager` class is responsible for managing the update process, including creating backups, applying updates, and handling rollbacks.

### Key Features

- Support for different installation methods (pip, Docker, git)
- Automatic backup creation before updates
- Configuration migration between versions
- Rollback capability

### Extension Points

To extend the `UpdateManager` class:

1. **Add support for additional installation methods**: Implement new methods similar to `_update_via_pip`, `_update_via_docker`, and `_update_via_git`.
2. **Enhance backup functionality**: Modify the `_create_backup` and `_restore_from_backup` methods.
3. **Implement additional configuration migration logic**: Enhance the `_migrate_configuration` method to handle specific version transitions.

## CLI Interface

The CLI interface provides a command-line interface for users to interact with the update system. It is implemented in the `cli_update.py` file.

### Key Features

- Check for updates
- Apply updates
- Rollback to previous versions
- List available backups

### Extension Points

To extend the CLI interface:

1. **Add new commands**: Add new commands to the `update_cli` group in `cli_update.py`.
2. **Enhance existing commands**: Modify the existing commands to add new options or functionality.
3. **Implement additional output formats**: Enhance the output formatting in the CLI commands.

## Configuration

The update system is configured through the DockerForge configuration file. The configuration is loaded by the `ConfigManager` class and passed to the `VersionChecker` and `UpdateManager` classes.

### Key Configuration Options

- `enabled`: Enable or disable the update system
- `check_on_startup`: Check for updates on startup
- `auto_check_interval`: Interval between automatic update checks
- `api_url`: URL for checking for updates
- `release_url`: URL for release information
- `cache_ttl`: Time-to-live for the update cache
- `auto_backup`: Automatically create backups before updates
- `backup_dir`: Directory for storing backups
- `max_backups`: Maximum number of backups to keep
- `notify_on_update`: Send notifications when updates are available
- `notify_on_failure`: Send notifications when updates fail
- `auto_rollback_on_failure`: Automatically rollback on update failure
- `keep_failed_backups`: Keep backups from failed updates

### Extension Points

To extend the configuration:

1. **Add new configuration options**: Add new options to the `update` section in the configuration file and update the `VersionChecker` and `UpdateManager` classes to use these options.
2. **Implement validation for configuration options**: Add validation logic to ensure that the configuration options are valid.
3. **Add support for environment variables**: Enhance the configuration loading to support environment variables for configuration options.

## Testing

The update system includes tests to verify its functionality. These tests are located in the `test_phase8.sh` file.

### Key Test Cases

- Test if the update CLI is registered
- Test if the update command is available in the main CLI
- Test version checker functionality
- Test Docker image build
- Test Docker Compose configuration
- Test update system backup functionality

### Extension Points

To extend the tests:

1. **Add new test cases**: Add new test cases to the `test_phase8.sh` file.
2. **Implement unit tests**: Create unit tests for the `VersionChecker` and `UpdateManager` classes.
3. **Implement integration tests**: Create integration tests for the update system.

## Best Practices

When extending or modifying the update system, follow these best practices:

1. **Error handling**: Ensure that all errors are properly handled and logged.
2. **Backup before updates**: Always create a backup before applying updates.
3. **Rollback capability**: Ensure that updates can be rolled back if they fail.
4. **Configuration validation**: Validate configuration options before using them.
5. **Testing**: Test all changes thoroughly before releasing them.
6. **Documentation**: Update the documentation to reflect any changes.

## Common Tasks

### Adding Support for a New Installation Method

To add support for a new installation method:

1. Add a new method to detect the installation method in the `UpdateManager` class:

```python
def _is_new_installation_method(self) -> bool:
    """
    Check if DockerForge is installed using the new method.

    Returns:
        True if installed using the new method, False otherwise.
    """
    # Implementation here
    return False
```

2. Add a new method to update using the new installation method:

```python
def _update_via_new_method(self, version: str) -> bool:
    """
    Update DockerForge using the new method.

    Args:
        version: The version to update to.

    Returns:
        True if the update was successful, False otherwise.
    """
    try:
        logger.info("Updating via new method")
        
        # Implementation here
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to update via new method: {e}")
        return False
```

3. Modify the `update` method to use the new installation method:

```python
def update(self, version: Optional[str] = None, force: bool = False) -> bool:
    # ...
    
    # Determine update method based on installation type
    if self._is_pip_installation():
        success = self._update_via_pip(version)
    elif self._is_docker_installation():
        success = self._update_via_docker(version)
    elif self._is_new_installation_method():
        success = self._update_via_new_method(version)
    else:
        success = self._update_via_git(version)
    
    # ...
```

### Adding a New CLI Command

To add a new CLI command:

1. Add a new command to the `update_cli` group in `cli_update.py`:

```python
@update_cli.command(name="new-command")
@click.option("--option", help="Option description")
@click.pass_context
def new_command(ctx, option):
    """
    New command description.
    """
    update_manager = ctx.obj["update_manager"]
    
    # Implementation here
    
    click.echo("Command executed successfully")
```

2. Update the documentation to reflect the new command.

### Implementing a New Version Comparison Algorithm

To implement a new version comparison algorithm:

1. Modify the `check_for_updates` method in the `VersionChecker` class:

```python
def check_for_updates(self, force: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
    # ...
    
    # Compare versions
    update_available = False
    if latest_version:
        try:
            # Use the new version comparison algorithm
            update_available = self._compare_versions(latest_version, self.current_version)
        except ValueError:
            # If the new algorithm fails, fall back to string comparison
            update_available = latest_version > self.current_version
    
    # ...

def _compare_versions(self, version1: str, version2: str) -> bool:
    """
    Compare two version strings using the new algorithm.

    Args:
        version1: The first version string.
        version2: The second version string.

    Returns:
        True if version1 is greater than version2, False otherwise.
    """
    # Implementation of the new algorithm
    return version1 > version2
```

2. Update the documentation to reflect the new version comparison algorithm.
