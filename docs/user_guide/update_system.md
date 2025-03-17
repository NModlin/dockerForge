# DockerForge Update System

The DockerForge Update System provides a comprehensive solution for managing updates to your DockerForge installation. This guide explains how to use the update system to check for updates, apply updates, and rollback if necessary.

## Checking for Updates

To check if updates are available for your DockerForge installation, use the following command:

```bash
dockerforge update check
```

This command will:
- Display your current version
- Check for available updates from the official repository
- Show the latest version if an update is available
- Display release notes for the new version

By default, update information is cached for 24 hours to reduce API calls. To force a fresh check, use the `--force` flag:

```bash
dockerforge update check --force
```

## Applying Updates

When an update is available, you can apply it using the following command:

```bash
dockerforge update apply
```

This will:
1. Create a backup of your current configuration
2. Download and install the latest version
3. Migrate your configuration to the new version if needed
4. Verify the update was successful

You can also specify a particular version to update to:

```bash
dockerforge update apply --version 0.2.0
```

To skip the confirmation prompt, use the `--yes` or `-y` flag:

```bash
dockerforge update apply --yes
```

## Rollback

If you encounter issues after an update, you can rollback to a previous version:

```bash
dockerforge update rollback
```

This will restore your system to the state it was in before the update, including your configuration.

You can also specify a particular backup to rollback to:

```bash
dockerforge update rollback --backup-id backup_20250315_120000
```

To list all available backups:

```bash
dockerforge update list-backups
```

## Configuration

The update system can be configured in the DockerForge configuration file (`~/.dockerforge/config/dockerforge.yaml`):

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
```

## Installation Methods

The update system supports different installation methods:

### Pip Installation

If you installed DockerForge using pip, the update system will use pip to install the new version:

```bash
pip install --upgrade dockerforge
```

### Git Installation

If you installed DockerForge from a git repository, the update system will:
1. Fetch the latest changes
2. Checkout the specified version tag
3. Reinstall the package

### Docker Installation

If you're running DockerForge in a Docker container, the update system will provide instructions for updating the container:

```bash
docker pull dockerforge/dockerforge:latest
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Update Fails

If an update fails, the system will automatically attempt to rollback to the previous version. You can also manually rollback using the `rollback` command.

### Backup Management

Backups are stored in the directory specified in the configuration file (`~/.dockerforge/backups/updates` by default). You can manage these backups using the `list-backups` command.

### Configuration Migration Issues

If you encounter issues with configuration migration, you can manually edit your configuration file to match the new version's requirements.
