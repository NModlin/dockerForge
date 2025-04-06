# DockerForge Troubleshooting Guide

This guide provides solutions to common issues you might encounter while using DockerForge.

## Connection Issues

### Cannot Connect to Docker Daemon

**Symptoms:**
- Error message: "Cannot connect to the Docker daemon"
- DockerForge fails to start or shows no containers/images

**Possible Causes:**
1. Docker daemon is not running
2. Insufficient permissions to access Docker socket
3. Docker socket is at a non-standard location
4. Remote Docker host is unreachable

**Solutions:**

1. **Verify Docker is running:**
   ```bash
   sudo systemctl status docker
   # or on macOS
   docker info
   ```
   If Docker is not running, start it with:
   ```bash
   sudo systemctl start docker
   # or on macOS
   open -a Docker
   ```

2. **Check permissions:**
   Ensure your user has permissions to access the Docker socket:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in for changes to take effect
   ```

3. **Configure custom Docker socket path:**
   If your Docker socket is at a non-standard location, specify it in DockerForge settings or via environment variable:
   ```bash
   export DOCKER_HOST=unix:///path/to/docker.sock
   # or for remote Docker
   export DOCKER_HOST=tcp://remote-docker-host:2375
   ```

4. **Check network connectivity:**
   If using a remote Docker host, ensure network connectivity and proper TLS configuration if secured.

### Web Interface Not Loading

**Symptoms:**
- Browser shows "Cannot connect to server" or blank page
- DockerForge service is running but UI is inaccessible

**Solutions:**

1. **Check if service is running:**
   ```bash
   ps aux | grep dockerforge
   ```

2. **Verify port availability:**
   Ensure nothing else is using the DockerForge port (default: 8080):
   ```bash
   netstat -tuln | grep 8080
   ```

3. **Check firewall settings:**
   Ensure your firewall allows connections to the DockerForge port:
   ```bash
   sudo ufw status
   # If needed, allow the port
   sudo ufw allow 8080/tcp
   ```

4. **Check logs for errors:**
   ```bash
   cat ~/.dockerforge/logs/server.log
   ```

## Container Issues

### Container Won't Start

**Symptoms:**
- Container status shows "Error" or remains in "Creating" state
- Error messages in container logs

**Possible Causes:**
1. Port conflicts
2. Volume mount issues
3. Resource constraints
4. Image problems

**Solutions:**

1. **Check for port conflicts:**
   Ensure the ports the container wants to use aren't already in use:
   ```bash
   netstat -tuln | grep <port_number>
   ```
   If the port is in use, choose a different port or stop the conflicting service.

2. **Verify volume paths:**
   Ensure that volume paths exist and have proper permissions:
   ```bash
   ls -la /path/to/volume
   # Fix permissions if needed
   sudo chown -R $USER:$USER /path/to/volume
   ```

3. **Check resource availability:**
   Ensure your system has enough resources (memory, disk space) for the container:
   ```bash
   free -h
   df -h
   ```

4. **Inspect container logs:**
   Check container logs for specific error messages:
   ```bash
   docker logs <container_id>
   ```

### Container Performance Issues

**Symptoms:**
- Container runs slowly
- High CPU or memory usage
- Application timeouts

**Solutions:**

1. **Monitor resource usage:**
   Use DockerForge's monitoring features to identify resource bottlenecks.

2. **Adjust resource limits:**
   Increase CPU or memory limits for the container if needed.

3. **Check for resource contention:**
   Ensure other containers or processes aren't competing for resources.

4. **Optimize application configuration:**
   Tune the application inside the container for better performance.

## Image Issues

### Cannot Pull Images

**Symptoms:**
- Error messages when trying to pull images
- Images remain in "Downloading" state

**Possible Causes:**
1. Network connectivity issues
2. Registry authentication problems
3. Disk space limitations

**Solutions:**

1. **Check internet connectivity:**
   Ensure your system can reach Docker Hub or your private registry:
   ```bash
   ping registry-1.docker.io
   ```

2. **Verify registry credentials:**
   Ensure you're properly authenticated to private registries:
   ```bash
   docker login <registry_url>
   ```

3. **Check available disk space:**
   ```bash
   df -h
   ```
   Free up space if needed.

4. **Try with explicit version tag:**
   Instead of using `latest`, specify an exact version tag.

### Image Build Failures

**Symptoms:**
- Errors during image build process
- Build process hangs or times out

**Solutions:**

1. **Check Dockerfile syntax:**
   Ensure your Dockerfile follows proper syntax and best practices.

2. **Verify build context:**
   Make sure the build context doesn't include unnecessary large files.

3. **Check network connectivity:**
   Ensure your system can download dependencies during the build.

4. **Increase build timeout:**
   Adjust the build timeout settings for complex builds.

## Docker Compose Issues

### Compose Project Won't Start

**Symptoms:**
- Error messages when starting a compose project
- Some services start but others fail

**Solutions:**

1. **Check compose file syntax:**
   Validate your compose file syntax:
   ```bash
   docker-compose config
   ```

2. **Check service dependencies:**
   Ensure services with dependencies are properly configured with `depends_on`.

3. **Verify network configuration:**
   Check that network definitions are correct and not conflicting.

4. **Start services individually:**
   Try starting each service individually to identify the problematic one.

## Database Issues

### Database Connection Failures

**Symptoms:**
- Applications can't connect to database containers
- Error logs show connection timeouts or refusals

**Solutions:**

1. **Check database container status:**
   Ensure the database container is running and healthy.

2. **Verify network connectivity:**
   Ensure containers are on the same network or have proper port mappings.

3. **Check credentials:**
   Verify that applications are using the correct database credentials.

4. **Inspect database logs:**
   Check database container logs for authentication or configuration errors.

## System Issues

### High CPU or Memory Usage

**Symptoms:**
- System becomes slow or unresponsive
- DockerForge UI lags or crashes

**Solutions:**

1. **Identify resource-intensive containers:**
   Use DockerForge's monitoring to identify containers using excessive resources.

2. **Set resource limits:**
   Configure resource limits for containers to prevent them from consuming too much.

3. **Optimize DockerForge settings:**
   Adjust DockerForge's own resource usage in settings.

4. **Consider system upgrades:**
   If consistently hitting resource limits, consider upgrading your hardware.

### Disk Space Issues

**Symptoms:**
- "No space left on device" errors
- Containers fail to start or become unhealthy

**Solutions:**

1. **Clean up unused images:**
   Remove unused images to free up space:
   ```bash
   docker image prune -a
   ```

2. **Remove unused volumes:**
   Clean up volumes that are no longer associated with any container:
   ```bash
   docker volume prune
   ```

3. **Clear Docker build cache:**
   ```bash
   docker builder prune
   ```

4. **Configure log rotation:**
   Ensure container logs don't grow too large by configuring log rotation.

## Update Issues

### Update Failures

**Symptoms:**
- Errors during DockerForge updates
- Version mismatch after update attempt

**Solutions:**

1. **Check for dependencies:**
   Ensure all dependencies are up to date:
   ```bash
   pip install --upgrade pip
   ```

2. **Try force reinstall:**
   ```bash
   pip install --force-reinstall dockerforge
   ```

3. **Check for conflicting packages:**
   Identify and resolve package conflicts.

4. **Manual update:**
   If automatic updates fail, try manual update procedures from the documentation.

## Getting Additional Help

If you're still experiencing issues after trying these troubleshooting steps:

1. **Check the full documentation:**
   Review the complete documentation for more detailed information.

2. **Search the community forum:**
   Many common issues have already been solved by other users.

3. **Check GitHub issues:**
   Search existing issues or create a new one on our GitHub repository.

4. **Contact support:**
   For enterprise users, contact our support team with detailed information about your issue.
