# DockerForge Installation Requirements

This document outlines the system requirements and prerequisites for installing and running DockerForge in various environments.

## System Requirements

### Hardware Requirements

#### Minimum Hardware Requirements

- **CPU**: 2 cores
- **RAM**: 2 GB
- **Disk Space**: 500 MB for application + additional space for Docker images and containers
- **Network**: Internet connection for pulling images and updates

#### Recommended Hardware Requirements

- **CPU**: 4+ cores
- **RAM**: 8 GB or more
- **Disk Space**: 10 GB or more
- **Network**: High-speed internet connection

### Software Requirements

#### Operating System

DockerForge is compatible with the following operating systems:

- **Linux**:
  - Ubuntu 20.04 LTS or newer
  - Debian 11 or newer
  - CentOS 8 or newer
  - Fedora 34 or newer
  - Any Linux distribution with kernel 4.0 or newer

- **macOS**:
  - macOS Monterey (12) or newer
  - Both Intel and Apple Silicon (M1/M2) processors are supported

- **Windows**:
  - Windows 10 (Build 1909 or newer)
  - Windows 11
  - Windows Server 2019 or newer

#### Docker

- Docker Engine 19.03 or newer
- Docker Compose v2.0 or newer (for Compose features)

#### Python

- Python 3.8 or newer
- pip (latest version recommended)

#### Web Browsers

DockerForge's web interface is compatible with:

- Google Chrome 90+
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+

## Network Requirements

### Ports

DockerForge requires the following ports to be available:

- **8080**: Web interface (configurable)
- **8081**: API (configurable)
- **2375/2376**: Docker API (if using remote Docker host)

### Firewall Configuration

If you're running a firewall, ensure the following:

1. Allow incoming connections to ports 8080 and 8081 (or your configured ports)
2. Allow DockerForge to connect to the Docker socket
3. Allow outbound connections to Docker registries (Docker Hub, etc.)

### Proxy Configuration

If your environment uses a proxy server:

1. Configure HTTP_PROXY and HTTPS_PROXY environment variables
2. Configure Docker to use the proxy (in `/etc/docker/daemon.json`)
3. Configure pip to use the proxy for package installation

## Database Requirements

DockerForge uses a database to store its configuration and operational data:

- **Default**: SQLite (included, no additional setup required)
- **Optional**: PostgreSQL 12+ (for production/multi-user environments)

## User Permissions

### Linux

The user running DockerForge needs:

1. Membership in the `docker` group to access the Docker socket:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Read/write access to the DockerForge data directory:
   ```bash
   sudo chown -R $USER:$USER ~/.dockerforge
   ```

### macOS

On macOS, ensure:

1. Docker Desktop is installed and running
2. The user has permission to access the Docker socket

### Windows

On Windows, ensure:

1. Docker Desktop is installed and running
2. The user has administrator privileges or appropriate permissions

## Additional Dependencies

Depending on your usage, you might need:

- **Git**: For pulling configurations from repositories
- **SSH**: For secure connections to remote Docker hosts
- **OpenSSL**: For TLS certificate generation
- **Node.js**: For development and customization of the web interface

## Resource Considerations

### Container Resources

Consider the resources needed for your containers in addition to DockerForge itself:

- Each container will require additional CPU, memory, and disk space
- Plan your system resources accordingly based on your expected workload

### Multi-User Environments

For multi-user or production environments:

- Increase RAM to 16 GB or more
- Use PostgreSQL instead of SQLite
- Consider deploying DockerForge itself in a container or with Docker Compose
- Implement proper backup procedures

## Next Steps

After ensuring your system meets these requirements, proceed to the [Installation Guide](./installation_guide.md) for step-by-step installation instructions.
