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
12. [Help Center and User Onboarding](#help-center-and-user-onboarding)
13. [Advanced Usage](#advanced-usage)

## Getting Started

### First Run

#### Local Installation

After [installing DockerForge](installation_guide.md) locally, run the initialization command:

```bash
dockerforge init
```

This will create the necessary configuration files and directories.

#### Docker Installation

If you're using the Docker image, the application is initialized automatically. You can access:

- CLI: `docker exec -it dockerforge python -m src.cli`
- Web UI: http://localhost:54321 in your browser

### Quick Check

Verify that DockerForge can connect to Docker:

```bash
# Local installation
dockerforge check

# Docker installation
docker exec dockerforge python -m src.cli check
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

### AI Chat System (CLI)

```bash
# Start interactive chat with the AI assistant
dockerforge chat

# Start chat with specific focus
dockerforge chat --focus security

# Start chat about a specific container
dockerforge chat --container CONTAINER_NAME

# Start chat with a specific agent
dockerforge chat --agent container

# Enable autonomous mode for agents
dockerforge chat --autonomous

# Set permission level for agent actions
dockerforge chat --permission-level medium
```

### AI Agent Framework

DockerForge includes a powerful agent framework that provides specialized AI agents for autonomous task execution.

#### Available Agents

```bash
# List all available agents
dockerforge agent list

# Show agent status
dockerforge agent status

# Show agent capabilities
dockerforge agent capabilities AGENT_NAME
```

#### Agent Operations

```bash
# Assign a task to a specific agent
dockerforge agent run AGENT_NAME TASK_DESCRIPTION

# View agent execution history
dockerforge agent history

# Configure agent settings
dockerforge agent configure AGENT_NAME SETTING_KEY SETTING_VALUE
```

#### Agent Types

- **Container Agent**: `dockerforge agent run container TASK`
  - Container lifecycle management
  - Performance optimization
  - Troubleshooting and diagnostics

- **Security Agent**: `dockerforge agent run security TASK`
  - Vulnerability scanning
  - Security remediation
  - Compliance checking

- **Optimization Agent**: `dockerforge agent run optimization TASK`
  - Resource usage analysis
  - Performance improvements
  - Configuration optimization

- **Documentation Agent**: `dockerforge agent run docs TASK`
  - Contextual help retrieval
  - Command suggestions
  - Best practices guidance

#### Agent Permissions

Configure how agents execute tasks:

```bash
# Set permission level globally
dockerforge config set agents.permission_level LEVEL

# Set permission level for specific agent
dockerforge config set agents.AGENT_NAME.permission_level LEVEL
```

Permission levels:
- `read-only`: Only information retrieval operations
- `low`: Minimal risk operations (pulling images, creating volumes)
- `medium`: Container state changes (starting/stopping)
- `high`: Data affecting operations (with approval)
- `critical`: Significant system changes (with detailed approval)

### Web UI Features

DockerForge provides comprehensive features through the web interface at http://localhost:54321. 

#### Web UI Access

- When running DockerForge with Docker Compose: http://localhost:54321
- When running the Docker container manually in 'web' or 'all' mode: http://localhost:54321

#### Web UI Main Features

The web interface provides access to all DockerForge features in a user-friendly dashboard:

1. **Dashboard**
   - Overview of your Docker environment
   - Quick access to containers, images, and volumes
   - System health metrics and alerts
   - Recent activity

2. **Container Management**
   - List, search, and filter containers
   - Start, stop, restart, and remove containers
   - View detailed container information
   - Access container logs and resource metrics

3. **Image Management**
   - Browse and search available images
   - Pull, build, and remove images
   - View detailed image information
   - Scan images for vulnerabilities

4. **Volume & Network Management**
   - Manage Docker volumes and networks
   - Create, modify, and remove volumes/networks
   - View detailed information

5. **Compose Projects**
   - Manage Docker Compose projects
   - Start, stop, and modify compose deployments
   - Visualize service relationships

6. **Security Center**
   - Security scanning and audit results
   - Vulnerability tracking and remediation
   - Security policy management
   - Compliance checking

7. **Settings**
   - Configuration management
   - User preferences
   - API keys and integration settings
   - AI provider configuration

#### AI Features in the Web UI

The web UI provides several AI-powered features:

1. **AI Chat System**
   - Interactive chat assistant
   - Context-aware help and recommendations
   - Specialized agents for different tasks
   - Command execution through chat

2. **Container Analysis**
   - Analyze running containers for issues
   - Get detailed recommendations for resolving problems
   - View container status and performance metrics alongside analysis

3. **Log Analysis**
   - Upload and analyze Docker logs
   - Identify patterns and issues in log data
   - Receive actionable recommendations

4. **Docker Compose Analysis**
   - Analyze Docker Compose files for best practices
   - Identify potential issues and security concerns
   - Get suggestions for improvements

5. **Dockerfile Analysis**
   - Analyze Dockerfiles for best practices
   - Identify inefficiencies and security issues
   - Get optimization recommendations

6. **AI Provider Management**
   - Configure and manage AI providers
   - View status of all configured AI providers
   - Monitor token usage and costs
   - Set budget limits and preferences

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

## Help Center and User Onboarding

DockerForge includes a comprehensive Help Center and user onboarding system to help you get the most out of the application.

### Help Center

Access the Help Center from any page by clicking the help icon (?) in the top-right corner or by using keyboard shortcut `F1`.

```bash
# Open Help Center from CLI
dockerforge help center
```

The Help Center provides:

- **General Help**: Overview of DockerForge features and concepts
- **Command Reference**: Detailed documentation for all CLI commands
- **Chat/Agent Help**: Guides for using the AI chat and agent system
- **Contextual Help**: Dynamic help based on your current activity
- **Troubleshooting FAQs**: Solutions to common problems

### Guided Tour

Take an interactive tour of DockerForge features:

```bash
# Start the guided tour from CLI
dockerforge help tour

# Start tour for a specific feature
dockerforge help tour --feature chat
```

In the web UI, you can start the guided tour by:
1. Clicking "Take a Tour" in the Help Center
2. Selecting "Guided Tour" from the user menu
3. Clicking tour prompts that appear for new users

### Contextual Help

Contextual help provides information relevant to your current activity:

- Help panels appear automatically in complex workflows
- Hover over interface elements to see tooltips with helpful information
- Click the "Help" button in any modal or page for specific guidance

```bash
# Get contextual help for a command
dockerforge COMMAND --help

# Get help for a specific topic
dockerforge help TOPIC
```

### Keyboard Shortcuts

View all keyboard shortcuts in the Help Center or by pressing `?` in the web UI.

Common shortcuts:
- `F1`: Open Help Center
- `Ctrl+/` or `Cmd+/`: Open command palette
- `Ctrl+Shift+C` or `Cmd+Shift+C`: Open chat interface
- `Ctrl+F` or `Cmd+F`: Search current view
- `Esc`: Close current panel or modal

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
