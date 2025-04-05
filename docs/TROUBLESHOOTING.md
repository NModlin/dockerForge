# DockerForge Troubleshooting Guide

This guide provides solutions to common issues you might encounter when using DockerForge.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Docker Connectivity Issues](#docker-connectivity-issues)
- [CLI Issues](#cli-issues)
- [Web Interface Issues](#web-interface-issues)
- [Container Management Issues](#container-management-issues)
- [Image Management Issues](#image-management-issues)
- [Compose Management Issues](#compose-management-issues)
- [Security Scanning Issues](#security-scanning-issues)
- [Backup and Restore Issues](#backup-and-restore-issues)
- [Monitoring Issues](#monitoring-issues)
- [AI Chat Issues](#ai-chat-issues)
- [Update System Issues](#update-system-issues)
- [Performance Issues](#performance-issues)
- [Logging and Debugging](#logging-and-debugging)
- [Getting Help](#getting-help)

## Installation Issues

### Package Installation Fails

**Problem**: Error when installing DockerForge via pip.

**Solution**:
1. Ensure you have Python 3.8 or higher:
   ```bash
   python --version
   ```

2. Update pip to the latest version:
   ```bash
   pip install --upgrade pip
   ```

3. Try installing with verbose output to see detailed errors:
   ```bash
   pip install dockerforge -v
   ```

4. If you encounter dependency conflicts, try using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install dockerforge
   ```

### Docker Container Installation Issues

**Problem**: Error when running DockerForge as a Docker container.

**Solution**:
1. Ensure Docker is running:
   ```bash
   docker info
   ```

2. Check if the Docker socket is accessible:
   ```bash
   ls -la /var/run/docker.sock
   ```

3. Try running with explicit permissions:
   ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --user $(id -u):$(id -g) natedog115/dockerforge:latest cli check
   ```

4. Check Docker logs for more information:
   ```bash
   docker logs <container_id>
   ```

## Docker Connectivity Issues

### DockerForge Cannot Connect to Docker

**Problem**: DockerForge reports that it cannot connect to Docker.

**Solution**:
1. Verify Docker is running:
   ```bash
   systemctl status docker  # Linux
   # or
   docker info
   ```

2. Check Docker socket permissions:
   ```bash
   ls -la /var/run/docker.sock
   ```

3. Ensure your user is in the docker group (Linux):
   ```bash
   groups  # Check if docker is listed
   sudo usermod -aG docker $USER  # Add user to docker group
   # Log out and log back in for changes to take effect
   ```

4. For Windows, ensure Docker Desktop is running and WSL integration is enabled.

5. For macOS, ensure Docker Desktop is running.

6. Try setting the DOCKER_HOST environment variable:
   ```bash
   export DOCKER_HOST=unix:///var/run/docker.sock  # Linux/macOS
   # or
   set DOCKER_HOST=tcp://localhost:2375  # Windows
   ```

### Docker API Version Mismatch

**Problem**: DockerForge reports a Docker API version mismatch.

**Solution**:
1. Check your Docker version:
   ```bash
   docker version
   ```

2. Update DockerForge to the latest version:
   ```bash
   pip install --upgrade dockerforge
   ```

3. If using a Docker container, pull the latest image:
   ```bash
   docker pull natedog115/dockerforge:latest
   ```

4. If the issue persists, try setting the DOCKER_API_VERSION environment variable:
   ```bash
   export DOCKER_API_VERSION=1.41  # Replace with your Docker API version
   ```

## CLI Issues

### Command Not Found

**Problem**: `dockerforge` command not found after installation.

**Solution**:
1. Ensure the installation directory is in your PATH:
   ```bash
   echo $PATH  # Linux/macOS
   # or
   echo %PATH%  # Windows
   ```

2. If using a virtual environment, ensure it's activated:
   ```bash
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. Try installing with the `--user` flag:
   ```bash
   pip install --user dockerforge
   ```

4. On Windows, you may need to add Python Scripts directory to your PATH:
   ```
   setx PATH "%PATH%;%APPDATA%\Python\Python39\Scripts"
   ```

### CLI Crashes or Hangs

**Problem**: DockerForge CLI crashes or hangs during operation.

**Solution**:
1. Run with debug logging:
   ```bash
   dockerforge --log-level DEBUG <command>
   ```

2. Check for error messages in the logs:
   ```bash
   cat ~/.dockerforge/logs/dockerforge.log  # Linux/macOS
   # or
   type %APPDATA%\dockerforge\logs\dockerforge.log  # Windows
   ```

3. Try updating to the latest version:
   ```bash
   pip install --upgrade dockerforge
   ```

4. If a specific command is causing issues, try alternative approaches or check the documentation for correct usage.

## Web Interface Issues

### Web Interface Not Starting

**Problem**: DockerForge web interface fails to start.

**Solution**:
1. Check if the port is already in use:
   ```bash
   netstat -tuln | grep 54321  # Linux/macOS
   # or
   netstat -an | findstr 54321  # Windows
   ```

2. Try specifying a different port:
   ```bash
   dockerforge web --port 8080
   ```

3. Check for error messages in the logs:
   ```bash
   cat ~/.dockerforge/logs/web.log  # Linux/macOS
   # or
   type %APPDATA%\dockerforge\logs\web.log  # Windows
   ```

4. Ensure you have the necessary permissions to bind to the port.

### Cannot Access Web Interface

**Problem**: Web interface is running but cannot be accessed in the browser.

**Solution**:
1. Verify the web interface is running:
   ```bash
   ps aux | grep dockerforge  # Linux/macOS
   # or
   tasklist | findstr dockerforge  # Windows
   ```

2. Check if you can access it locally:
   ```bash
   curl http://localhost:54321/api/health
   ```

3. Check firewall settings to ensure the port is allowed.

4. If running in a Docker container, ensure port mapping is correct:
   ```bash
   docker run -d -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest web
   ```

5. If running on a remote server, ensure the web interface is bound to 0.0.0.0 instead of localhost:
   ```bash
   dockerforge web --host 0.0.0.0
   ```

### Web Interface Performance Issues

**Problem**: Web interface is slow or unresponsive.

**Solution**:
1. Check system resources (CPU, memory) to ensure sufficient resources are available.

2. Reduce the number of containers being monitored.

3. Increase the polling interval in settings.

4. Clear browser cache and cookies.

5. Try a different browser.

6. Check network latency if accessing remotely.

## Container Management Issues

### Cannot Start/Stop Containers

**Problem**: Unable to start or stop containers through DockerForge.

**Solution**:
1. Verify you have permission to manage containers:
   ```bash
   docker ps  # Should work without errors
   ```

2. Check if the container exists:
   ```bash
   docker container inspect <container_name>
   ```

3. Try starting/stopping the container directly with Docker:
   ```bash
   docker start <container_name>
   # or
   docker stop <container_name>
   ```

4. Check for error messages in the logs:
   ```bash
   dockerforge --log-level DEBUG containers start <container_name>
   ```

5. Ensure the Docker daemon is responsive:
   ```bash
   docker info
   ```

### Container Logs Not Showing

**Problem**: Container logs are not visible in DockerForge.

**Solution**:
1. Verify the container is running:
   ```bash
   docker ps | grep <container_name>
   ```

2. Check if logs are available directly through Docker:
   ```bash
   docker logs <container_name>
   ```

3. Ensure the container is outputting logs to stdout/stderr.

4. Try specifying a time range:
   ```bash
   dockerforge containers logs <container_name> --since 1h
   ```

5. If the container has a large log file, try limiting the output:
   ```bash
   dockerforge containers logs <container_name> --tail 100
   ```

## Image Management Issues

### Cannot Pull Images

**Problem**: Unable to pull Docker images through DockerForge.

**Solution**:
1. Verify Docker can pull images directly:
   ```bash
   docker pull nginx:latest
   ```

2. Check network connectivity to Docker Hub or your private registry.

3. If using a private registry, ensure credentials are configured:
   ```bash
   docker login <registry_url>
   ```

4. Try specifying the full image path:
   ```bash
   dockerforge images pull registry.example.com/my-image:latest
   ```

5. Check for error messages in the logs:
   ```bash
   dockerforge --log-level DEBUG images pull nginx:latest
   ```

### Image Build Fails

**Problem**: Building an image through DockerForge fails.

**Solution**:
1. Verify the Dockerfile is valid:
   ```bash
   docker build -t test-image .
   ```

2. Check for syntax errors in the Dockerfile.

3. Ensure all referenced files exist in the build context.

4. Try building with more detailed output:
   ```bash
   dockerforge images build --verbose .
   ```

5. Check for network issues if the build requires downloading packages.

## Compose Management Issues

### Compose File Not Found

**Problem**: DockerForge cannot find Docker Compose files.

**Solution**:
1. Verify the Compose file exists:
   ```bash
   ls -la docker-compose.yml  # Linux/macOS
   # or
   dir docker-compose.yml  # Windows
   ```

2. Try specifying the full path to the Compose file:
   ```bash
   dockerforge compose up /path/to/docker-compose.yml
   ```

3. Check if the file is readable by the current user.

4. If using a different filename, specify it explicitly:
   ```bash
   dockerforge compose up -f compose.yaml
   ```

### Compose Services Not Starting

**Problem**: Services defined in a Docker Compose file fail to start.

**Solution**:
1. Validate the Compose file:
   ```bash
   dockerforge compose validate docker-compose.yml
   # or
   docker-compose -f docker-compose.yml config
   ```

2. Try starting the services directly with Docker Compose:
   ```bash
   docker-compose up
   ```

3. Check for error messages in the logs:
   ```bash
   dockerforge --log-level DEBUG compose up docker-compose.yml
   ```

4. Ensure all required images are available or can be pulled.

5. Check for port conflicts or resource constraints.

## Security Scanning Issues

### Vulnerability Scanning Fails

**Problem**: Image vulnerability scanning fails.

**Solution**:
1. Ensure the image exists locally:
   ```bash
   docker images | grep <image_name>
   ```

2. Try pulling the image again:
   ```bash
   docker pull <image_name>
   ```

3. Check network connectivity to vulnerability databases.

4. Try scanning with verbose output:
   ```bash
   dockerforge security scan --verbose --image <image_name>
   ```

5. If using a proxy, ensure it's configured correctly.

### False Positives in Security Scans

**Problem**: Security scans report vulnerabilities that are not applicable.

**Solution**:
1. Update DockerForge to the latest version for the most accurate vulnerability database.

2. Check if the vulnerability has been patched in the image.

3. Consider adding exceptions for known false positives in the configuration:
   ```yaml
   security:
     exceptions:
       - CVE-2023-12345
   ```

4. Verify the vulnerability details to understand if it applies to your use case.

## Backup and Restore Issues

### Backup Creation Fails

**Problem**: Unable to create backups of containers or images.

**Solution**:
1. Ensure sufficient disk space is available.

2. Check if the container or image exists:
   ```bash
   docker ps -a | grep <container_name>
   # or
   docker images | grep <image_name>
   ```

3. Try creating a backup with verbose output:
   ```bash
   dockerforge backup container <container_name> --verbose
   ```

4. Ensure you have permission to write to the backup directory.

5. If backing up a running container, try stopping it first:
   ```bash
   docker stop <container_name>
   dockerforge backup container <container_name>
   ```

### Restore Fails

**Problem**: Unable to restore from a backup.

**Solution**:
1. Verify the backup exists:
   ```bash
   dockerforge backup list
   ```

2. Check if the backup is corrupted:
   ```bash
   dockerforge backup verify <backup_id>
   ```

3. Ensure sufficient disk space is available.

4. Try restoring with verbose output:
   ```bash
   dockerforge backup restore <backup_id> --verbose
   ```

5. If restoring a container, ensure no container with the same name exists:
   ```bash
   docker rm <container_name>
   ```

## Monitoring Issues

### Monitoring Data Not Showing

**Problem**: Container monitoring data is not visible.

**Solution**:
1. Verify the container is running:
   ```bash
   docker ps | grep <container_name>
   ```

2. Check if Docker stats are available:
   ```bash
   docker stats <container_name> --no-stream
   ```

3. Ensure the monitoring service is running:
   ```bash
   ps aux | grep dockerforge-monitor  # Linux/macOS
   # or
   tasklist | findstr dockerforge-monitor  # Windows
   ```

4. Try restarting the monitoring service:
   ```bash
   dockerforge monitor --restart
   ```

5. Check for error messages in the logs:
   ```bash
   cat ~/.dockerforge/logs/monitor.log  # Linux/macOS
   # or
   type %APPDATA%\dockerforge\logs\monitor.log  # Windows
   ```

### High CPU Usage During Monitoring

**Problem**: DockerForge uses excessive CPU during monitoring.

**Solution**:
1. Reduce the number of containers being monitored.

2. Increase the polling interval in settings:
   ```yaml
   monitoring:
     interval: 30  # Seconds between polls
   ```

3. Disable detailed metrics collection for less important containers.

4. Ensure you're using the latest version of DockerForge, which may include performance improvements.

5. If running in a resource-constrained environment, consider limiting the metrics collected:
   ```bash
   dockerforge monitor --metrics cpu,memory
   ```

## AI Chat Issues

### AI Chat Not Responding

**Problem**: AI chat system does not respond to queries.

**Solution**:
1. Check if you have configured an AI provider:
   ```bash
   dockerforge config show
   ```

2. Ensure you have a valid API key for the configured provider.

3. Check network connectivity to the AI provider's API.

4. Try a simple query to test the system:
   ```bash
   dockerforge chat "Hello"
   ```

5. Check for error messages in the logs:
   ```bash
   cat ~/.dockerforge/logs/chat.log  # Linux/macOS
   # or
   type %APPDATA%\dockerforge\logs\chat.log  # Windows
   ```

### AI Responses Not Helpful

**Problem**: AI responses are not relevant or helpful.

**Solution**:
1. Try providing more context in your queries.

2. Use more specific questions rather than general ones.

3. Try a different AI provider if available:
   ```bash
   dockerforge config set ai.provider gemini
   ```

4. Ensure you're using the latest version of DockerForge, which may include improved prompts.

5. Provide feedback on unhelpful responses to help improve the system:
   ```bash
   dockerforge chat feedback <message_id> --rating 2 --comment "Response was not relevant"
   ```

## Update System Issues

### Update Check Fails

**Problem**: DockerForge cannot check for updates.

**Solution**:
1. Check network connectivity to the update server.

2. If using a proxy, ensure it's configured correctly.

3. Try checking for updates with verbose output:
   ```bash
   dockerforge update check --verbose
   ```

4. Temporarily disable any firewall or security software that might be blocking the connection.

5. If behind a corporate firewall, consult your IT department.

### Update Application Fails

**Problem**: DockerForge fails to apply updates.

**Solution**:
1. Ensure you have sufficient permissions to update the installation.

2. If installed via pip, try updating manually:
   ```bash
   pip install --upgrade dockerforge
   ```

3. If running as a Docker container, try pulling the latest image:
   ```bash
   docker pull natedog115/dockerforge:latest
   ```

4. Check for error messages in the logs:
   ```bash
   dockerforge update apply --verbose
   ```

5. If the update fails, try rolling back to the previous version:
   ```bash
   dockerforge update rollback
   ```

## Performance Issues

### DockerForge Running Slowly

**Problem**: DockerForge operations are slow or unresponsive.

**Solution**:
1. Check system resources (CPU, memory, disk I/O) to ensure sufficient resources are available.

2. Reduce the number of containers being monitored.

3. Increase polling intervals for monitoring and other periodic tasks.

4. Disable features you don't need:
   ```yaml
   features:
     security_scanning: false
     resource_monitoring: false
   ```

5. If using the web interface, try the CLI for better performance.

6. Consider running DockerForge on a more powerful machine.

### High Memory Usage

**Problem**: DockerForge uses excessive memory.

**Solution**:
1. Limit the number of containers being monitored.

2. Reduce the log retention period:
   ```yaml
   logging:
     retention_days: 7  # Reduce from default
   ```

3. Disable memory-intensive features like AI analysis if not needed.

4. Restart DockerForge periodically to release accumulated memory.

5. If running in a Docker container, set memory limits:
   ```bash
   docker run --memory 512m -d -p 54321:54321 -v /var/run/docker.sock:/var/run/docker.sock natedog115/dockerforge:latest
   ```

## Logging and Debugging

### Enabling Debug Logging

To enable debug logging for troubleshooting:

1. Set the log level to DEBUG:
   ```bash
   dockerforge --log-level DEBUG <command>
   ```

2. Or configure it permanently in the configuration file:
   ```yaml
   logging:
     level: DEBUG
     file: ~/.dockerforge/logs/dockerforge.log
   ```

3. View the logs:
   ```bash
   cat ~/.dockerforge/logs/dockerforge.log  # Linux/macOS
   # or
   type %APPDATA%\dockerforge\logs\dockerforge.log  # Windows
   ```

### Collecting Diagnostic Information

To collect diagnostic information for support:

```bash
dockerforge diagnostics
```

This will generate a diagnostic report with system information, configuration, and logs (with sensitive information redacted).

## Getting Help

If you're still experiencing issues after trying the solutions in this guide:

1. Check the [DockerForge Documentation](https://docs.dockerforge.io) for more detailed information.

2. Search for similar issues in the [GitHub Issues](https://github.com/dockerforge/dockerforge/issues).

3. Ask for help in the [DockerForge Community Forum](https://community.dockerforge.io).

4. Join the [DockerForge Discord Server](https://discord.gg/dockerforge) for real-time support.

5. If you believe you've found a bug, please [report it on GitHub](https://github.com/dockerforge/dockerforge/issues/new?template=bug_report.md) with detailed information about the issue and steps to reproduce it.
