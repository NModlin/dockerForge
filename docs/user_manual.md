# DockerForge User Manual

## Introduction

DockerForge is a comprehensive Docker management and monitoring tool with AI-powered troubleshooting capabilities. This manual provides detailed information on how to use DockerForge effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Command Line Interface](#command-line-interface)
3. [Configuration](#configuration)
4. [Core Features](#core-features)
5. [Monitoring](#monitoring)
6. [Security](#security)
7. [Backup and Restore](#backup-and-restore)
8. [Docker Compose Management](#docker-compose-management)
9. [Update System](#update-system)
10. [AI Integration](#ai-integration)
11. [Troubleshooting](#troubleshooting)
12. [Advanced Usage](#advanced-usage)

## Getting Started

### First Run

After [installing DockerForge](installation_guide.md), run the initialization command:

```bash
dockerforge init
```

This will create the necessary configuration files and directories.

### Quick Check

Verify that DockerForge can connect to Docker:

```bash
dockerforge check
```

This command checks:
- Docker connection
- Docker API version compatibility
- Required permissions
- Available disk space
- Configuration validity

## Command Line Interface

DockerForge uses a command-line interface with subcommands for different features.

### General Syntax

```bash
dockerforge [global options] command [command options] [arguments...]
```

### Global Options

- `--help, -h`: Show help
- `--version, -v`: Show version
- `--config FILE`: Use specific config file
- `--verbose`: Enable verbose output
- `--quiet`: Suppress all output except errors
- `--json`: Output in JSON format
- `--no-color`: Disable colored output

### Getting Help

```bash
# General help
dockerforge --help

# Command-specific help
dockerforge COMMAND --help
```

## Configuration

DockerForge uses YAML configuration files.

### Configuration Locations

- Default: `~/.dockerforge/config.yaml`
- Custom: Specified with `--config` option

### Configuration Structure

The configuration file is organized into sections:

```yaml
# General settings
general:
  log_level: INFO
  data_dir: ~/.dockerforge/data

# Docker connection settings
docker:
  connection_type: auto  # auto, socket, tcp
  socket_path: /var/run/docker.sock

# AI provider settings
ai:
  default_provider: ollama
  providers:
    claude:
      enabled: false
      api_key: ""
    gemini:
      enabled: false
      api_key: ""
    ollama:
      enabled: true
      host: http://localhost:11434
      model: llama3

# Other sections...
```

### Editing Configuration

```bash
# Open configuration in default editor
dockerforge config edit

# Set a specific configuration value
dockerforge config set section.key value

# Get a configuration value
dockerforge config get section.key
```

## Core Features

### Container Management

```bash
# List containers
dockerforge container list

# Show container details
dockerforge container show CONTAINER_NAME

# Start/stop/restart containers
dockerforge container start CONTAINER_NAME
dockerforge container stop CONTAINER_NAME
dockerforge container restart CONTAINER_NAME
```

### Image Management

```bash
# List images
dockerforge image list

# Pull an image
dockerforge image pull IMAGE_NAME[:TAG]

# Remove an image
dockerforge image remove IMAGE_NAME[:TAG]
```

### Volume Management

```bash
# List volumes
dockerforge volume list

# Create a volume
dockerforge volume create VOLUME_NAME

# Remove a volume
dockerforge volume remove VOLUME_NAME
```

### Network Management

```bash
# List networks
dockerforge network list

# Create a network
dockerforge network create NETWORK_NAME

# Remove a network
dockerforge network remove NETWORK_NAME
```

## Monitoring

### Log Monitoring

```bash
# Monitor logs from a container
dockerforge monitor CONTAINER_NAME

# Monitor logs with AI analysis
dockerforge analyze CONTAINER_NAME

# Search for patterns in logs
dockerforge monitor search CONTAINER_NAME "pattern"
```

### Resource Monitoring

```bash
# Show resource usage for all containers
dockerforge stats

# Show resource usage for a specific container
dockerforge stats CONTAINER_NAME

# Start resource monitoring daemon
dockerforge daemon start

# Stop resource monitoring daemon
dockerforge daemon stop
```

### Anomaly Detection

```bash
# Enable anomaly detection
dockerforge config set monitoring.anomaly_detection.enabled true

# Set anomaly detection sensitivity
dockerforge config set monitoring.anomaly_detection.sensitivity medium  # low, medium, high
```

## Security

### Vulnerability Scanning

```bash
# Scan an image for vulnerabilities
dockerforge security scan IMAGE_NAME[:TAG]

# Scan with specific severity threshold
dockerforge security scan --severity HIGH IMAGE_NAME[:TAG]

# Export scan results
dockerforge security scan --output report.json --format json IMAGE_NAME[:TAG]
```

### Configuration Auditing

```bash
# Audit Docker configuration
dockerforge security audit

# Audit specific components
dockerforge security audit --components host,daemon,containers

# Export audit results
dockerforge security audit --output audit.html --format html
```

### Security Reporting

```bash
# Generate comprehensive security report
dockerforge security report

# Generate report with specific format
dockerforge security report --format html --output security-report.html
```

## Backup and Restore

### Container Backup

```bash
# Backup a container
dockerforge backup container CONTAINER_NAME

# List backups
dockerforge backup list

# Show backup details
dockerforge backup show BACKUP_ID

# Restore from backup
dockerforge backup restore BACKUP_ID
```

### Export and Import

```bash
# Export a container
dockerforge backup export container CONTAINER_NAME --output container.tar.gz

# Export an image
dockerforge backup export image IMAGE_NAME[:TAG] --output image.tar.gz

# Import a container
dockerforge backup import container container.tar.gz

# Import an image
dockerforge backup import image image.tar.gz
```

## Docker Compose Management

### Compose File Discovery

```bash
# Discover Docker Compose files
dockerforge compose discover

# Discover in specific directory
dockerforge compose discover --path /path/to/directory
```

### Compose Operations

```bash
# List compose projects
dockerforge compose list

# Show compose project details
dockerforge compose show PROJECT_NAME

# Up/down compose project
dockerforge compose up PROJECT_NAME
dockerforge compose down PROJECT_NAME
```

### Compose Visualization

```bash
# Generate visualization of compose project
dockerforge compose visualize PROJECT_NAME

# Export visualization to file
dockerforge compose visualize PROJECT_NAME --output compose.png
```

## Update System

### Checking for Updates

```bash
# Check for DockerForge updates
dockerforge update check
```

### Applying Updates

```bash
# Apply available updates
dockerforge update apply

# Apply specific version
dockerforge update apply --version 1.2.3
```

### Rollback

```bash
# Rollback to previous version
dockerforge update rollback

# Rollback to specific backup
dockerforge update rollback --backup-id BACKUP_ID
```

### Backup Management

```bash
# List update backups
dockerforge update list-backups

# Remove update backup
dockerforge update remove-backup BACKUP_ID
```

## AI Integration

### AI Provider Configuration

```bash
# Configure Claude provider
dockerforge config set ai.providers.claude.enabled true
dockerforge config set ai.providers.claude.api_key YOUR_API_KEY

# Configure Gemini provider
dockerforge config set ai.providers.gemini.enabled true
dockerforge config set ai.providers.gemini.api_key YOUR_API_KEY

# Configure Ollama provider
dockerforge config set ai.providers.ollama.enabled true
dockerforge config set ai.providers.ollama.host http://localhost:11434
```

### AI-Powered Analysis (CLI)

```bash
# Analyze container logs with AI
dockerforge analyze CONTAINER_NAME

# Analyze with specific provider
dockerforge analyze --provider claude CONTAINER_NAME

# Analyze Docker Compose file
dockerforge compose analyze docker-compose.yml
```

### AI-Powered Troubleshooting (CLI)

```bash
# Troubleshoot container issues
dockerforge troubleshoot CONTAINER_NAME

# Troubleshoot with specific focus
dockerforge troubleshoot --focus networking CONTAINER_NAME
```

### Web UI AI Features

DockerForge now provides AI troubleshooting capabilities through the web interface. Access these features by navigating to the Monitoring & AI section in the web UI.

#### AI Provider Status

The web UI displays the status of all configured AI providers, including:
- Availability status
- Model information
- Provider capabilities (streaming, vision, function calling, etc.)
- Default provider indication

#### AI Usage Statistics

Monitor your AI usage through the web UI:
- Daily and monthly token usage
- Cost tracking by provider and model
- Budget monitoring with visual indicators
- Usage projections and trends

#### Troubleshooting Tools

The web UI provides several AI-powered troubleshooting tools:

1. **Container Analysis**
   - Analyze running containers for issues
   - Get detailed recommendations for resolving problems
   - View container status and performance metrics alongside analysis

2. **Log Analysis**
   - Upload and analyze Docker logs
   - Identify patterns and issues in log data
   - Receive actionable recommendations

3. **Docker Compose Analysis**
   - Analyze Docker Compose files for best practices
   - Identify potential issues and security concerns
   - Get suggestions for improvements

4. **Dockerfile Analysis**
   - Analyze Dockerfiles for best practices
   - Identify inefficiencies and security issues
   - Get optimization recommendations

5. **Docker Connection Troubleshooting**
   - Diagnose Docker connection issues
   - Get step-by-step instructions to resolve connection problems

## Troubleshooting

### Common Issues

#### Docker Connection Issues

```bash
# Check Docker connection
dockerforge check

# Diagnose Docker connection issues
dockerforge diagnose docker-connection
```

#### Permission Issues

```bash
# Check permissions
dockerforge diagnose permissions

# Fix common permission issues
dockerforge fix permissions
```

#### Configuration Issues

```bash
# Validate configuration
dockerforge config validate

# Reset to default configuration
dockerforge config reset
```

### Logs and Diagnostics

```bash
# Show DockerForge logs
dockerforge logs

# Generate diagnostic report
dockerforge diagnose --full --output diagnostic-report.zip
```

## Advanced Usage

### Automation and Scripting

```bash
# Use JSON output for scripting
dockerforge --json container list

# Non-interactive mode
dockerforge --non-interactive update apply
```

### Custom Templates

```bash
# List available templates
dockerforge template list

# Create a template
dockerforge template create TEMPLATE_NAME

# Apply a template
dockerforge template apply TEMPLATE_NAME
```

### Plugin System

```bash
# List installed plugins
dockerforge plugin list

# Install a plugin
dockerforge plugin install PLUGIN_NAME

# Remove a plugin
dockerforge plugin remove PLUGIN_NAME
```

### Resource Optimization

```bash
# Get optimization recommendations
dockerforge optimize

# Apply optimization recommendations
dockerforge optimize --apply
```

## Appendix

### Environment Variables

- `DOCKERFORGE_CONFIG`: Path to configuration file
- `DOCKERFORGE_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR)
- `DOCKERFORGE_DATA_DIR`: Data directory
- `DOCKERFORGE_CLAUDE_API_KEY`: Claude API key
- `DOCKERFORGE_GEMINI_API_KEY`: Gemini API key
- `DOCKERFORGE_DOCKER_HOST`: Docker host (for TCP connection)

### Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Docker connection error
- `4`: Permission error
- `5`: Command not found
- `6`: Invalid argument

### File Locations

- Configuration: `~/.dockerforge/config.yaml`
- Logs: `~/.dockerforge/logs/`
- Data: `~/.dockerforge/data/`
- Backups: `~/.dockerforge/backups/`
- Plugins: `~/.dockerforge/plugins/`
