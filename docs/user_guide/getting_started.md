# Getting Started with DockerForge

This guide will help you quickly get up and running with DockerForge, a powerful tool for managing Docker containers and images with an intuitive web interface.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: Version 19.03 or higher
- **Python**: Version 3.8 or higher
- **pip**: Latest version

## Quick Installation

The fastest way to get started with DockerForge is to install it via pip:

```bash
pip install dockerforge
```

## First Launch

After installation, you can start DockerForge with:

```bash
dockerforge start
```

This will start the DockerForge server and automatically open the web interface in your default browser. If the browser doesn't open automatically, you can access the interface at `http://localhost:8080`.

## Initial Setup

When you first access DockerForge, you'll be guided through a setup wizard that will help you:

1. Connect to your Docker daemon
2. Configure basic settings
3. Set up your user account

### Connecting to Docker

DockerForge needs to connect to your Docker daemon to manage containers and images. By default, it will try to connect to the local Docker socket. If you're using a remote Docker host or a non-standard socket location, you can configure this in the settings.

### Basic Navigation

The DockerForge interface is organized into several main sections:

- **Dashboard**: Overview of your Docker environment
- **Containers**: Manage and monitor your containers
- **Images**: Browse, pull, and manage Docker images
- **Compose**: Create and manage Docker Compose projects
- **Templates**: Access pre-configured container templates
- **Settings**: Configure DockerForge to suit your needs

## Creating Your First Container

To create a container:

1. Go to the **Images** tab
2. Search for an image (e.g., "nginx")
3. Click "Pull" to download the image
4. Once downloaded, click "Create Container"
5. Configure the container settings (ports, volumes, etc.)
6. Click "Create" to launch the container

## Next Steps

Now that you have DockerForge up and running, you might want to:

- Explore the [Template Library](./template_library.md) to quickly deploy common applications
- Learn about [Resource Monitoring](./resource_monitoring.md) to keep track of container performance
- Set up [Notifications](./notifications.md) for important container events
- Check out the [Troubleshooting Guide](../TROUBLESHOOTING.md) if you encounter any issues

## Getting Help

If you need assistance, you can:

- Check the [Documentation](../index.md) for detailed information
- Join our community forum at [community.dockerforge.io](https://community.dockerforge.io)
- Report issues on our [GitHub repository](https://github.com/NModlin/dockerForge)
