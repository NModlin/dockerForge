# DockerForge Installation Guide

This guide provides detailed instructions for installing DockerForge on different platforms and environments.

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Docker**: Docker Engine 19.03 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Disk Space**: At least 500MB for the application (plus additional space for Docker images and containers)

## Installation Methods

DockerForge can be installed using several methods, depending on your preferences and requirements.

### Method 1: Install from PyPI (Recommended for End Users)

The simplest way to install DockerForge is via pip:

```bash
pip install dockerforge
```

This will install the latest stable release of DockerForge and all its dependencies.

### Method 2: Install from Source (Recommended for Developers)

For the latest features or if you want to contribute to the project:

```bash
# Clone the repository
git clone https://github.com/dockerforge/dockerforge.git
cd dockerforge

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

For development with all extra dependencies:

```bash
pip install -e ".[dev]"
```

### Method 3: Docker Installation

DockerForge can also be run as a Docker container:

```bash
# Pull the Docker image
docker pull natedog115/dockerforge:latest

# Run with Docker Compose
curl -O https://raw.githubusercontent.com/dockerforge/dockerforge/main/docker-compose.yml
docker-compose up -d
```

Or run directly with Docker:

```bash
# CLI mode only
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest cli

# Web interface only
docker run -d -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest web

# Both CLI and web interface
docker run -d -p 8080:8080 -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest all
```

## Platform-Specific Instructions

### Linux

1. Ensure Docker is installed and running:
   ```bash
   sudo systemctl status docker
   ```

2. Make sure your user is in the docker group to avoid permission issues:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in for the changes to take effect
   ```

3. Install DockerForge using one of the methods above.

### macOS

1. Install Docker Desktop for Mac from the [official Docker website](https://www.docker.com/products/docker-desktop).

2. Ensure Docker is running by checking the Docker Desktop application.

3. Install DockerForge using one of the methods above.

### Windows

1. Install Docker Desktop for Windows from the [official Docker website](https://www.docker.com/products/docker-desktop).

2. Ensure Docker is running by checking the Docker Desktop application.

3. For the best experience, we recommend using Windows Subsystem for Linux (WSL2) with Docker Desktop.

4. Install DockerForge using one of the methods above.

## Verifying the Installation

After installation, verify that DockerForge is working correctly:

```bash
# Check the installed version
dockerforge --version

# Verify Docker connectivity
dockerforge check
```

## Configuration

DockerForge uses a configuration file located at `~/.config/dockerforge/config.yaml` (Linux/macOS) or `%APPDATA%\dockerforge\config.yaml` (Windows).

The configuration file is created automatically on first run, but you can customize it to suit your needs.

## Troubleshooting

### Common Issues

1. **Docker connectivity problems**:
   - Ensure Docker is running
   - Check that your user has permissions to access the Docker socket
   - On Linux, verify your user is in the docker group

2. **Python dependency conflicts**:
   - Use a virtual environment to isolate DockerForge dependencies
   - Try upgrading pip: `pip install --upgrade pip`

3. **Web interface not accessible**:
   - Check if the port 54321 is already in use
   - Verify firewall settings

For more detailed troubleshooting, refer to the [Troubleshooting Guide](TROUBLESHOOTING.md).

## Next Steps

- [User Guide](USER_GUIDE.md): Learn how to use DockerForge
- [API Documentation](API.md): Explore the DockerForge API
- [Contributing](CONTRIBUTING.md): Contribute to the DockerForge project
