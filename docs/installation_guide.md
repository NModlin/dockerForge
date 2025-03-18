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
- Docker Compose (recommended)

### Option 1: Using Docker Compose (Recommended)

1. Download the Docker Compose file:

```bash
curl -O https://raw.githubusercontent.com/dockerforge/dockerforge/main/docker-compose.yml
```

2. Start DockerForge with Docker Compose:

```bash
docker-compose up -d
```

This will automatically pull the required images and set up the necessary volumes and networks.

### Option 2: Manual Docker Setup

1. Pull the DockerForge image:

```bash
docker pull natedog115/dockerforge:latest
```

2. Create necessary Docker volumes:

```bash
docker volume create dockerforge-data
docker volume create postgres_data
docker volume create redis_data
docker volume create ollama-data
```

3. Create a Docker network:

```bash
docker network create dockerforge-network
```

4. Start the PostgreSQL database:

```bash
docker run -d \
  --name dockerforge-db \
  --network dockerforge-network \
  -v postgres_data:/var/lib/postgresql/data \
  -e POSTGRES_USER=dockerforge \
  -e POSTGRES_PASSWORD=dockerforge \
  -e POSTGRES_DB=dockerforge \
  postgres:15-alpine
```

5. Start the Redis instance:

```bash
docker run -d \
  --name dockerforge-redis \
  --network dockerforge-network \
  -v redis_data:/data \
  redis:alpine
```

6. Start the Ollama instance:

```bash
docker run -d \
  --name dockerforge-ollama \
  --network dockerforge-network \
  -v ollama-data:/root/.ollama \
  -p 11435:11434 \
  ollama/ollama:latest
```

7. Start DockerForge:

```bash
docker run -d \
  --name dockerforge \
  --network dockerforge-network \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ./config:/app/config \
  -v ./data:/app/data \
  -v ./media:/app/media \
  -p 8080:8080 \
  -p 54321:54321 \
  -e DOCKERFORGE_CONFIG_PATH=/app/config/dockerforge.yaml \
  -e DOCKERFORGE_DATA_DIR=/app/data \
  -e OLLAMA_API_HOST=http://dockerforge-ollama:11434 \
  -e DATABASE_URL=postgresql://dockerforge:dockerforge@dockerforge-db:5432/dockerforge \
  -e REDIS_URL=redis://dockerforge-redis:6379/0 \
  natedog115/dockerforge:latest
```

### Running DockerForge in Different Modes

The DockerForge Docker image supports different run modes:

1. Run both CLI and web UI (default):

```bash
docker run -d \
  --name dockerforge \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 8080:8080 \
  -p 54321:54321 \
  natedog115/dockerforge:latest all
```

2. Run only the CLI service:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  natedog115/dockerforge:latest cli check
```

3. Run only the web UI:

```bash
docker run -d \
  --name dockerforge-web \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 54321:54321 \
  natedog115/dockerforge:latest web
```

4. Verify the installation:

```bash
docker exec dockerforge python -m src.cli --version
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

#### Using Docker Compose

```bash
# Pull the latest images
docker-compose pull

# Restart the services
docker-compose down
docker-compose up -d
```

#### Manual Docker Setup

```bash
# Pull the latest image
docker pull natedog115/dockerforge:latest

# Restart the container
docker stop dockerforge
docker rm dockerforge
docker run -d \
  --name dockerforge \
  --network dockerforge-network \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ./config:/app/config \
  -v ./data:/app/data \
  -v ./media:/app/media \
  -p 8080:8080 \
  -p 54321:54321 \
  -e DOCKERFORGE_CONFIG_PATH=/app/config/dockerforge.yaml \
  -e DOCKERFORGE_DATA_DIR=/app/data \
  -e OLLAMA_API_HOST=http://dockerforge-ollama:11434 \
  -e DATABASE_URL=postgresql://dockerforge:dockerforge@dockerforge-db:5432/dockerforge \
  -e REDIS_URL=redis://dockerforge-redis:6379/0 \
  natedog115/dockerforge:latest
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

#### Using Docker Compose

```bash
# Stop and remove all services
docker-compose down -v
```

#### Manual Docker Setup

```bash
# Stop and remove containers
docker stop dockerforge dockerforge-db dockerforge-redis dockerforge-ollama
docker rm dockerforge dockerforge-db dockerforge-redis dockerforge-ollama

# Optionally remove the data volumes
docker volume rm dockerforge-data postgres_data redis_data ollama-data

# Optionally remove the network
docker network rm dockerforge-network
```

### From Source

```bash
pip uninstall dockerforge
```

## Next Steps

After installation, refer to the [User Manual](user_manual.md) to learn how to use DockerForge effectively.
