# DockerForge Installation Guide

This guide provides detailed instructions for installing DockerForge on various platforms.

## System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Docker**: Docker Engine 20.10.0 or higher
- **Disk Space**: 100 MB for DockerForge + additional space for backups and data
- **Memory**: 512 MB RAM

### Recommended Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **Python**: 3.10 or higher
- **Docker**: Docker Engine 23.0.0 or higher
- **Disk Space**: 1 GB for DockerForge + additional space for backups and data
- **Memory**: 2 GB RAM

## Installation Methods

DockerForge can be installed using several methods:

1. [Using pip (Python Package Manager)](#installation-using-pip)
2. [Using Docker](#installation-using-docker)
3. [From Source](#installation-from-source)

Choose the method that best suits your environment and requirements.

## Installation Using pip

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Docker installed and running

### Steps

1. Install DockerForge using pip:

```bash
pip install dockerforge
```

2. Verify the installation:

```bash
dockerforge --version
```

3. Initialize DockerForge:

```bash
dockerforge init
```

This will create the necessary configuration files in `~/.dockerforge/`.

## Installation Using Docker

### Prerequisites

- Docker installed and running

### Steps

1. Pull the DockerForge image:

```bash
docker pull dockerforge/dockerforge:latest
```

2. Create a Docker volume for persistent data:

```bash
docker volume create dockerforge-data
```

3. Run DockerForge:

```bash
docker run -d \
  --name dockerforge \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockerforge-data:/var/lib/dockerforge \
  dockerforge/dockerforge:latest
```

4. Verify the installation:

```bash
docker exec dockerforge dockerforge --version
```

## Installation from Source

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Docker installed and running

### Steps

1. Clone the repository:

```bash
git clone https://github.com/dockerforge/dockerforge.git
cd dockerforge
```

2. Install the package in development mode:

```bash
pip install -e .
```

3. Verify the installation:

```bash
dockerforge --version
```

4. Initialize DockerForge:

```bash
dockerforge init
```

## Configuration

After installation, you can configure DockerForge by editing the configuration file:

- For pip and source installations: `~/.dockerforge/config.yaml`
- For Docker installations: Mount a custom configuration file to `/etc/dockerforge/config.yaml`

See the [User Manual](user_manual.md) for detailed configuration options.

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip docker.io

# Install DockerForge
pip3 install dockerforge

# Add user to docker group (optional, for non-root usage)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

#### CentOS/RHEL

```bash
# Install dependencies
sudo yum install -y python3 python3-pip docker

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Install DockerForge
pip3 install dockerforge

# Add user to docker group (optional, for non-root usage)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install Docker Desktop for Mac
# Download from https://www.docker.com/products/docker-desktop

# Install DockerForge
pip3 install dockerforge
```

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Docker Desktop for Windows from [docker.com](https://www.docker.com/products/docker-desktop)
3. Open Command Prompt or PowerShell:

```powershell
# Install DockerForge
pip install dockerforge
```

## Troubleshooting

### Common Issues

#### Permission Denied when Accessing Docker Socket

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

#### Python Version Conflict

```bash
# Create a virtual environment with the correct Python version
python3 -m venv dockerforge-env
source dockerforge-env/bin/activate
pip install dockerforge
```

#### Docker Connection Issues

Ensure Docker is running:

```bash
# Check Docker status
docker info
```

If Docker is not running, start it:

```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

### Getting Help

If you encounter issues not covered in this guide:

- Check the [Troubleshooting Guide](troubleshooting_guide.md)
- Visit our [GitHub repository](https://github.com/dockerforge/dockerforge)
- Join our [Community Forum](https://forum.dockerforge.example.com)

## Upgrading

To upgrade DockerForge to the latest version:

### Using pip

```bash
pip install --upgrade dockerforge
```

### Using Docker

```bash
docker pull dockerforge/dockerforge:latest
docker stop dockerforge
docker rm dockerforge
docker run -d \
  --name dockerforge \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v dockerforge-data:/var/lib/dockerforge \
  dockerforge/dockerforge:latest
```

### From Source

```bash
cd dockerforge
git pull
pip install -e .
```

## Uninstallation

### Using pip

```bash
pip uninstall dockerforge
```

### Using Docker

```bash
docker stop dockerforge
docker rm dockerforge
# Optionally remove the data volume
docker volume rm dockerforge-data
```

### From Source

```bash
pip uninstall dockerforge
```

## Next Steps

After installation, refer to the [User Manual](user_manual.md) to learn how to use DockerForge effectively.
