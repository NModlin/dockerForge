# DockerForge

A comprehensive Docker management and monitoring tool with AI-powered troubleshooting capabilities and an integrated web interface.

## Features

- **Cross-Platform Compatibility**: Works on Linux, Windows, and macOS
- **AI-Powered Analysis**: Multiple AI provider support (Claude, Gemini, extensible)
- **Advanced Monitoring**: Real-time log monitoring and resource tracking
- **Notification System**: Multi-channel notifications with intelligent alerting
- **Docker Compose Management**: Discovery, validation, and visualization
- **Security Module**: Vulnerability scanning, configuration auditing, and comprehensive reporting
- **Backup & Restore**: Container, image, and volume backup, restore, export, and import
- **Resource Optimization**: Intelligent resource monitoring and optimization recommendations
- **Update System**: Version checking, in-place updates, and rollback capability
- **User Experience**: Intuitive CLI interface and web UI with intelligent defaults
- **Advanced AI Chat System**: Multi-agent framework with contextual memory and specialized agents

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker installed and running
- Docker SDK for Python

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/dockerforge/dockerforge.git
cd dockerforge

# Install the package
pip install -e .
```

### Option 2: Docker Installation

```bash
# Pull the Docker image
docker pull natedog115/dockerforge:latest

# Run with Docker Compose
curl -O https://raw.githubusercontent.com/dockerforge/dockerforge/main/docker-compose.yml
docker-compose up -d
```

This will start DockerForge with both the CLI and web interface.

## Usage

### CLI Usage

```bash
# Get help
dockerforge --help

# Check Docker installation
dockerforge check

# Monitor containers
dockerforge monitor

# Analyze container logs with AI
dockerforge analyze <container_name>

# Manage Docker Compose files
dockerforge compose list

# Security scanning and auditing
dockerforge security scan --image nginx:latest
dockerforge security audit
dockerforge security report --format html --output security-report.html

# Backup and restore
dockerforge backup container my-container
dockerforge backup list
dockerforge backup restore <backup-id>

# Export and import
dockerforge backup export image nginx:latest --output nginx-backup.tar.gz
dockerforge backup import image nginx-backup.tar.gz --repository nginx --tag imported

# Check for updates
dockerforge update check
dockerforge update apply
dockerforge update rollback

# Use the AI chat system
dockerforge chat
```

### Docker Container Usage

```bash
# Run DockerForge in different modes:

# CLI mode only
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest cli check

# Web interface only
docker run -d -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest web

# Both CLI and web interface (default)
docker run -d -p 8080:8080 -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest all
```

### Web Interface

Access the web interface at http://localhost:54321 after starting DockerForge with web or all mode.

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/dockerforge/dockerforge.git
cd dockerforge

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

## License

MIT
