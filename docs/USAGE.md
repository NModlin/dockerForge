# DockerForge Usage Guide

This guide provides comprehensive instructions for using DockerForge's features and capabilities.

## Table of Contents

- [Command Line Interface](#command-line-interface)
- [Web Interface](#web-interface)
- [Docker Container Management](#docker-container-management)
- [Docker Compose Management](#docker-compose-management)
- [Security Scanning](#security-scanning)
- [Backup and Restore](#backup-and-restore)
- [Resource Monitoring](#resource-monitoring)
- [AI-Powered Analysis](#ai-powered-analysis)
- [Notifications](#notifications)
- [Update System](#update-system)

## Command Line Interface

DockerForge provides a powerful command-line interface (CLI) for managing Docker resources.

### Basic Commands

```bash
# Display help information
dockerforge --help

# Check Docker installation and connectivity
dockerforge check

# Display version information
dockerforge --version
```

### Command Structure

DockerForge commands follow this general structure:

```
dockerforge [global options] command [command options] [arguments...]
```

## Web Interface

DockerForge includes a web-based user interface for managing Docker resources visually.

### Accessing the Web Interface

After starting DockerForge with the web interface enabled, access it at:

```
http://localhost:54321
```

### Web Interface Features

- **Dashboard**: Overview of Docker resources and system status
- **Containers**: Manage and monitor containers
- **Images**: Browse, pull, and manage Docker images
- **Volumes**: Create and manage Docker volumes
- **Networks**: Configure and manage Docker networks
- **Compose**: Manage Docker Compose projects
- **Security**: Scan and audit Docker resources
- **Backup**: Create and restore backups
- **Settings**: Configure DockerForge

## Docker Container Management

### Listing Containers

```bash
# List all containers
dockerforge containers list

# List only running containers
dockerforge containers list --running
```

### Container Operations

```bash
# Start a container
dockerforge containers start <container_name>

# Stop a container
dockerforge containers stop <container_name>

# Restart a container
dockerforge containers restart <container_name>

# Remove a container
dockerforge containers rm <container_name>

# View container logs
dockerforge containers logs <container_name>

# Execute a command in a container
dockerforge containers exec <container_name> <command>
```

## Docker Compose Management

### Discovering Compose Files

```bash
# Discover Docker Compose files in the system
dockerforge compose discover

# List discovered Docker Compose projects
dockerforge compose list
```

### Compose Operations

```bash
# Validate a Docker Compose file
dockerforge compose validate <compose_file>

# Start services defined in a Docker Compose file
dockerforge compose up <compose_file>

# Stop services defined in a Docker Compose file
dockerforge compose down <compose_file>

# Visualize a Docker Compose file
dockerforge compose visualize <compose_file> --output compose-diagram.png
```

## Security Scanning

### Scanning Images

```bash
# Scan a Docker image for vulnerabilities
dockerforge security scan --image <image_name>

# Scan all images
dockerforge security scan --all-images
```

### Auditing Containers

```bash
# Audit container configurations
dockerforge security audit --container <container_name>

# Audit all containers
dockerforge security audit --all-containers
```

### Generating Reports

```bash
# Generate a security report
dockerforge security report --format html --output security-report.html
```

## Backup and Restore

### Creating Backups

```bash
# Backup a container
dockerforge backup container <container_name>

# Backup an image
dockerforge backup image <image_name>

# Backup a volume
dockerforge backup volume <volume_name>
```

### Managing Backups

```bash
# List all backups
dockerforge backup list

# Show backup details
dockerforge backup show <backup_id>

# Delete a backup
dockerforge backup delete <backup_id>
```

### Restoring Backups

```bash
# Restore a backup
dockerforge backup restore <backup_id>
```

### Exporting and Importing

```bash
# Export an image to a file
dockerforge backup export image <image_name> --output <filename.tar.gz>

# Import an image from a file
dockerforge backup import image <filename.tar.gz> --repository <repo> --tag <tag>
```

## Resource Monitoring

### Monitoring Containers

```bash
# Monitor all containers
dockerforge monitor

# Monitor specific containers
dockerforge monitor --containers <container1,container2>

# Monitor with specific metrics
dockerforge monitor --metrics cpu,memory,network
```

### Resource Optimization

```bash
# Get resource optimization recommendations
dockerforge optimize

# Apply recommended optimizations
dockerforge optimize --apply
```

## AI-Powered Analysis

### Log Analysis

```bash
# Analyze container logs with AI
dockerforge analyze logs <container_name>

# Analyze specific time range
dockerforge analyze logs <container_name> --since 1h --until 10m
```

### AI Chat

```bash
# Start an AI chat session
dockerforge chat

# Ask a specific question
dockerforge chat "How do I optimize my Nginx container?"
```

## Notifications

### Configuring Notifications

```bash
# Configure email notifications
dockerforge notifications config email --smtp-server smtp.example.com --smtp-port 587 --username user --password pass

# Configure Slack notifications
dockerforge notifications config slack --webhook-url https://hooks.slack.com/services/XXX/YYY/ZZZ
```

### Managing Notification Rules

```bash
# Add a notification rule
dockerforge notifications add-rule --event container_down --channel email,slack

# List notification rules
dockerforge notifications list-rules

# Remove a notification rule
dockerforge notifications remove-rule <rule_id>
```

## Update System

### Managing Updates

```bash
# Check for updates
dockerforge update check

# Apply available updates
dockerforge update apply

# Rollback to previous version
dockerforge update rollback
```

## Advanced Usage

### Using Environment Variables

DockerForge supports configuration via environment variables:

- `DOCKERFORGE_CONFIG`: Path to the configuration file
- `DOCKERFORGE_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DOCKERFORGE_API_KEY`: API key for external services

### Using Configuration Files

DockerForge uses a YAML configuration file located at:
- Linux/macOS: `~/.config/dockerforge/config.yaml`
- Windows: `%APPDATA%\dockerforge\config.yaml`

Example configuration:

```yaml
general:
  log_level: INFO
  data_dir: ~/.dockerforge/data

web:
  host: 0.0.0.0
  port: 54321
  enable_ssl: false

notifications:
  email:
    enabled: true
    smtp_server: smtp.example.com
    smtp_port: 587
    username: user@example.com
    password: password
  slack:
    enabled: true
    webhook_url: https://hooks.slack.com/services/XXX/YYY/ZZZ
```

## Next Steps

- [API Documentation](API.md): Explore the DockerForge API
- [Contributing](CONTRIBUTING.md): Contribute to the DockerForge project
