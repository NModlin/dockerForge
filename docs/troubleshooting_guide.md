# DockerForge Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using DockerForge.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Docker Connection Issues](#docker-connection-issues)
3. [Permission Issues](#permission-issues)
4. [Configuration Issues](#configuration-issues)
5. [Monitoring Issues](#monitoring-issues)
6. [Security Scanning Issues](#security-scanning-issues)
7. [Backup and Restore Issues](#backup-and-restore-issues)
8. [Update Issues](#update-issues)
9. [AI Integration Issues](#ai-integration-issues)
10. [Performance Issues](#performance-issues)
11. [Diagnostic Tools](#diagnostic-tools)
12. [Getting Help](#getting-help)

## Installation Issues

### Python Version Compatibility

**Issue**: Installation fails with Python version errors.

**Solution**:
- Ensure you have Python 3.8 or higher installed:
  ```bash
  python --version
  ```
- If needed, install a compatible Python version:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3.10
  
  # macOS
  brew install python@3.10
  
  # Windows
  # Download from python.org
  ```
- Create a virtual environment with the correct Python version:
  ```bash
  python3.10 -m venv dockerforge-env
  source dockerforge-env/bin/activate  # On Windows: dockerforge-env\Scripts\activate
  ```

### Dependency Conflicts

**Issue**: Installation fails due to dependency conflicts.

**Solution**:
- Install in a clean virtual environment:
  ```bash
  python -m venv dockerforge-env
  source dockerforge-env/bin/activate
  pip install dockerforge
  ```
- If installing from source, try:
  ```bash
  pip install -e . --no-dependencies
  pip install -r requirements.txt
  ```

### Installation Path Issues

**Issue**: DockerForge command not found after installation.

**Solution**:
- Ensure the installation directory is in your PATH:
  ```bash
  # Find where pip installed the package
  pip show dockerforge
  
  # Add to PATH if needed
  export PATH=$PATH:~/.local/bin  # Adjust as needed
  ```
- On Windows, you may need to:
  ```powershell
  # Add Python Scripts directory to PATH
  $env:PATH += ";$env:USERPROFILE\AppData\Local\Programs\Python\Python310\Scripts"
  ```

## Docker Connection Issues

### Docker Not Running

**Issue**: DockerForge cannot connect to Docker.

**Solution**:
- Check if Docker is running:
  ```bash
  docker info
  ```
- If Docker is not running, start it:
  ```bash
  # Linux
  sudo systemctl start docker
  
  # macOS/Windows
  # Start Docker Desktop application
  ```

### Docker Socket Permission Denied

**Issue**: Permission denied when accessing Docker socket.

**Solution**:
- Add your user to the docker group:
  ```bash
  sudo usermod -aG docker $USER
  # Log out and log back in for this to take effect
  ```
- Alternatively, run DockerForge with sudo (not recommended for regular use):
  ```bash
  sudo dockerforge
  ```
- Check socket permissions:
  ```bash
  ls -la /var/run/docker.sock
  # Should show something like: srw-rw---- 1 root docker
  ```

### Remote Docker Connection Issues

**Issue**: Cannot connect to remote Docker host.

**Solution**:
- Ensure Docker is configured to accept remote connections:
  ```bash
  # On the remote host, edit /etc/docker/daemon.json
  {
    "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
  }
  
  # Restart Docker
  sudo systemctl restart docker
  ```
- Configure DockerForge to use the remote host:
  ```bash
  dockerforge config set docker.connection_type tcp
  dockerforge config set docker.tcp_host your-remote-host
  dockerforge config set docker.tcp_port 2375
  ```
- For secure connections, set up TLS:
  ```bash
  dockerforge config set docker.tls_enabled true
  dockerforge config set docker.tls_cert_path /path/to/cert.pem
  dockerforge config set docker.tls_key_path /path/to/key.pem
  dockerforge config set docker.tls_ca_path /path/to/ca.pem
  ```

## Permission Issues

### File Permission Issues

**Issue**: Cannot write to configuration or data directories.

**Solution**:
- Check directory permissions:
  ```bash
  ls -la ~/.dockerforge/
  ```
- Fix permissions if needed:
  ```bash
  sudo chown -R $USER:$USER ~/.dockerforge/
  chmod -R 755 ~/.dockerforge/
  ```
- For Docker installations, check volume permissions:
  ```bash
  docker exec -it dockerforge ls -la /var/lib/dockerforge
  ```

### Docker API Permission Issues

**Issue**: Insufficient permissions for certain Docker operations.

**Solution**:
- Ensure your user has the necessary Docker permissions:
  ```bash
  # Check if you're in the docker group
  groups
  
  # Add user to docker group if needed
  sudo usermod -aG docker $USER
  # Log out and log back in for this to take effect
  ```
- For specific operations that require elevated privileges:
  ```bash
  # Run with sudo for specific commands
  sudo dockerforge security audit
  ```

## Configuration Issues

### Invalid Configuration

**Issue**: DockerForge fails to start due to invalid configuration.

**Solution**:
- Validate your configuration:
  ```bash
  dockerforge config validate
  ```
- Reset to default configuration:
  ```bash
  dockerforge config reset
  ```
- Edit the configuration manually:
  ```bash
  dockerforge config edit
  ```

### Missing Configuration

**Issue**: Configuration file is missing or incomplete.

**Solution**:
- Initialize DockerForge to create default configuration:
  ```bash
  dockerforge init
  ```
- Manually create the configuration directory:
  ```bash
  mkdir -p ~/.dockerforge
  ```
- Copy a sample configuration:
  ```bash
  cp /path/to/dockerforge/examples/configurations/quick_start.yaml ~/.dockerforge/config.yaml
  ```

### Environment Variable Issues

**Issue**: Environment variables not being recognized.

**Solution**:
- Check if environment variables are set:
  ```bash
  echo $DOCKERFORGE_CONFIG
  echo $DOCKERFORGE_CLAUDE_API_KEY
  ```
- Set environment variables properly:
  ```bash
  # Bash
  export DOCKERFORGE_CONFIG=/path/to/config.yaml
  
  # Windows PowerShell
  $env:DOCKERFORGE_CONFIG = "C:\path\to\config.yaml"
  ```
- Add to your shell profile for persistence:
  ```bash
  # Add to ~/.bashrc or ~/.zshrc
  echo 'export DOCKERFORGE_CONFIG=/path/to/config.yaml' >> ~/.bashrc
  ```

## Monitoring Issues

### Log Collection Issues

**Issue**: Cannot collect logs from containers.

**Solution**:
- Check if the container is running:
  ```bash
  docker ps | grep container-name
  ```
- Verify that the container is producing logs:
  ```bash
  docker logs container-name
  ```
- Check DockerForge log buffer settings:
  ```bash
  dockerforge config get monitoring.log_buffer_size
  # Increase if needed
  dockerforge config set monitoring.log_buffer_size 5000
  ```

### Resource Monitoring Issues

**Issue**: Resource statistics are not being collected.

**Solution**:
- Ensure the Docker stats API is working:
  ```bash
  docker stats --no-stream
  ```
- Check if the daemon is running:
  ```bash
  dockerforge daemon status
  # If not running, start it
  dockerforge daemon start
  ```
- Check daemon logs for errors:
  ```bash
  cat ~/.dockerforge/logs/daemon.log
  ```

### Anomaly Detection Issues

**Issue**: Anomaly detection is not working or generating false positives.

**Solution**:
- Adjust sensitivity settings:
  ```bash
  # Decrease sensitivity for fewer alerts
  dockerforge config set monitoring.anomaly_detection.sensitivity low
  
  # Increase learning period
  dockerforge config set monitoring.anomaly_detection.learning_period 7
  ```
- Reset anomaly detection baselines:
  ```bash
  dockerforge monitor reset-baselines
  ```

## Security Scanning Issues

### Vulnerability Scanner Connection Issues

**Issue**: Cannot connect to vulnerability database.

**Solution**:
- Check internet connectivity:
  ```bash
  ping -c 3 google.com
  ```
- Update vulnerability database manually:
  ```bash
  dockerforge security update-db
  ```
- Check proxy settings if applicable:
  ```bash
  # Set proxy if needed
  dockerforge config set security.proxy http://proxy.example.com:8080
  ```

### Slow Vulnerability Scans

**Issue**: Vulnerability scans take too long to complete.

**Solution**:
- Limit scan scope:
  ```bash
  # Scan only for high and critical vulnerabilities
  dockerforge security scan --severity HIGH,CRITICAL image-name
  ```
- Use cached results when possible:
  ```bash
  dockerforge security scan --use-cache image-name
  ```
- Adjust timeout settings:
  ```bash
  dockerforge config set security.scan_timeout 300
  ```

### False Positives in Security Audits

**Issue**: Security audits report false positives.

**Solution**:
- Customize audit checks:
  ```bash
  # Disable specific checks
  dockerforge security audit --disable-checks docker-4.1,docker-4.2
  ```
- Create a custom audit profile:
  ```bash
  dockerforge security create-profile custom
  # Edit the profile
  dockerforge security edit-profile custom
  ```
- Use the custom profile:
  ```bash
  dockerforge security audit --profile custom
  ```

## Backup and Restore Issues

### Backup Creation Failures

**Issue**: Cannot create backups of containers.

**Solution**:
- Check disk space:
  ```bash
  df -h
  ```
- Verify container status:
  ```bash
  docker inspect container-name
  ```
- Try with different options:
  ```bash
  # Exclude volumes to reduce size
  dockerforge backup container container-name --exclude-volumes
  ```

### Restore Failures

**Issue**: Cannot restore containers from backups.

**Solution**:
- Check if the backup exists:
  ```bash
  dockerforge backup list
  ```
- Verify backup integrity:
  ```bash
  dockerforge backup verify backup-id
  ```
- Try with force option:
  ```bash
  dockerforge backup restore backup-id --force
  ```
- Restore to a different name to avoid conflicts:
  ```bash
  dockerforge backup restore backup-id --name new-container-name
  ```

### Export/Import Issues

**Issue**: Cannot export or import containers/images.

**Solution**:
- Check file permissions:
  ```bash
  ls -la /path/to/export/directory
  ```
- Verify disk space:
  ```bash
  df -h
  ```
- Try without compression for troubleshooting:
  ```bash
  dockerforge backup export container container-name --output file.tar --no-compression
  ```

## Update Issues

### Update Check Failures

**Issue**: Cannot check for updates.

**Solution**:
- Check internet connectivity:
  ```bash
  ping -c 3 google.com
  ```
- Force update check:
  ```bash
  dockerforge update check --force
  ```
- Check proxy settings if applicable:
  ```bash
  # Set proxy if needed
  dockerforge config set update.proxy http://proxy.example.com:8080
  ```

### Update Application Failures

**Issue**: Cannot apply updates.

**Solution**:
- Check permissions:
  ```bash
  # If installed via pip
  pip install --user --upgrade dockerforge
  
  # If installed system-wide
  sudo pip install --upgrade dockerforge
  ```
- Try with force option:
  ```bash
  dockerforge update apply --force
  ```
- Update manually:
  ```bash
  pip install --upgrade dockerforge
  ```

### Rollback Issues

**Issue**: Cannot rollback to previous version.

**Solution**:
- Check available backups:
  ```bash
  dockerforge update list-backups
  ```
- Specify a backup ID:
  ```bash
  dockerforge update rollback --backup-id backup-id
  ```
- Install specific version manually:
  ```bash
  pip install dockerforge==1.2.3
  ```

## AI Integration Issues

### API Key Issues

**Issue**: AI providers not working due to API key issues.

**Solution**:
- Verify API keys are set:
  ```bash
  # Check if keys are configured (will show as masked)
  dockerforge config get ai.providers.claude.api_key
  ```
- Set API keys:
  ```bash
  # Set via CLI
  dockerforge config set ai.providers.claude.api_key your-api-key
  
  # Set via environment variable
  export DOCKERFORGE_CLAUDE_API_KEY=your-api-key
  ```
- Test API key validity:
  ```bash
  dockerforge ai test-provider claude
  ```
- In the web UI, check the AI Provider Status page to see if providers are available

### Ollama Connection Issues

**Issue**: Cannot connect to local Ollama instance.

**Solution**:
- Check if Ollama is running:
  ```bash
  curl http://localhost:11434/api/version
  ```
- Start Ollama if needed:
  ```bash
  ollama serve
  ```
- Configure correct Ollama host:
  ```bash
  dockerforge config set ai.providers.ollama.host http://localhost:11434
  ```
- If using Ollama in Docker, ensure network connectivity:
  ```bash
  # If Ollama is in a Docker container
  dockerforge config set ai.providers.ollama.host http://ollama-container:11434
  ```
- In the web UI, check the AI Provider Status page to verify Ollama connection

### AI Analysis Timeout

**Issue**: AI analysis operations timeout.

**Solution**:
- Increase timeout settings:
  ```bash
  dockerforge config set ai.request_timeout 120
  ```
- Reduce the amount of data being analyzed:
  ```bash
  dockerforge analyze container-name --tail 100
  ```
- Try a different AI provider:
  ```bash
  dockerforge analyze container-name --provider gemini
  ```
- In the web UI, try analyzing smaller portions of logs or files

### Web UI AI Features Not Working

**Issue**: AI troubleshooting features in the web UI are not functioning.

**Solution**:
- Check if the monitoring router is enabled in the API:
  ```bash
  # Check the main.py file
  grep "monitoring.router" /path/to/src/web/api/main.py
  ```
- Verify that the web server is running:
  ```bash
  # Check if the web server process is running
  ps aux | grep "uvicorn"
  ```
- Check browser console for JavaScript errors:
  - Open browser developer tools (F12)
  - Look for errors in the Console tab
- Verify API endpoints are accessible:
  ```bash
  # Test the AI status endpoint
  curl http://localhost:54321/api/monitoring/ai-status
  ```
- Restart the web server:
  ```bash
  # Stop and restart the web server
  docker restart dockerforge-web
  # Or if running directly
  kill -TERM $(pgrep -f "uvicorn main:app") && cd /path/to/src/web/api && uvicorn main:app --host 0.0.0.0 --port 54321
  ```

### AI Usage Statistics Not Showing

**Issue**: AI usage statistics are not displaying in the web UI.

**Solution**:
- Check if the AI usage tracker database exists:
  ```bash
  # Check if the database file exists
  ls -la ~/.dockerforge/data/ai_usage.db
  ```
- Initialize the database if needed:
  ```bash
  # Run a command that initializes the database
  dockerforge ai usage-report
  ```
- Check permissions on the database file:
  ```bash
  # Ensure the web server has read access
  chmod 644 ~/.dockerforge/data/ai_usage.db
  ```
- If running in Docker, ensure volume mounts are correct:
  ```bash
  # Check Docker volume mounts
  docker inspect dockerforge-web | grep -A 10 "Mounts"
  ```

## Performance Issues

### High CPU Usage

**Issue**: DockerForge uses excessive CPU resources.

**Solution**:
- Check which component is using resources:
  ```bash
  ps aux | grep dockerforge
  ```
- Adjust polling intervals:
  ```bash
  # Increase monitoring interval (seconds)
  dockerforge config set monitoring.poll_interval 30
  
  # Increase resource collection interval (seconds)
  dockerforge config set resource_monitoring.collection_interval 60
  ```
- Disable unused features:
  ```bash
  dockerforge config set monitoring.enabled false
  ```

### High Memory Usage

**Issue**: DockerForge uses excessive memory.

**Solution**:
- Adjust log buffer size:
  ```bash
  dockerforge config set monitoring.log_buffer_size 500
  ```
- Limit the number of containers monitored:
  ```bash
  dockerforge config set monitoring.max_containers 10
  ```
- Enable log rotation:
  ```bash
  dockerforge config set logging.rotation.enabled true
  dockerforge config set logging.rotation.max_size 10  # MB
  ```

### Slow Command Execution

**Issue**: DockerForge commands take too long to execute.

**Solution**:
- Use caching where available:
  ```bash
  dockerforge config set general.use_cache true
  ```
- Disable verbose output:
  ```bash
  dockerforge config set general.log_level WARNING
  ```
- Check for network issues:
  ```bash
  # If using remote Docker
  ping your-docker-host
  ```

## Diagnostic Tools

DockerForge provides several diagnostic tools to help troubleshoot issues:

### System Check

Run a comprehensive system check:

```bash
dockerforge check
```

This checks:
- Docker connection
- Configuration validity
- Required permissions
- Available disk space
- AI provider connectivity

### Diagnostic Report

Generate a diagnostic report:

```bash
dockerforge diagnose --output diagnostic-report.zip
```

This includes:
- System information
- DockerForge configuration (with sensitive data masked)
- Docker information
- Logs
- Error reports

### Log Inspection

View DockerForge logs:

```bash
# View main log
dockerforge logs

# View specific component log
dockerforge logs --component daemon

# View last 100 lines
dockerforge logs --tail 100

# Follow logs in real-time
dockerforge logs --follow
```

### Docker Diagnostics

Run Docker-specific diagnostics:

```bash
# Check Docker connection
dockerforge diagnose docker-connection

# Check Docker configuration
dockerforge diagnose docker-config

# Test Docker API
dockerforge diagnose docker-api
```

## Getting Help

If you're still experiencing issues after trying the solutions in this guide:

### Community Support

- Visit our [GitHub repository](https://github.com/dockerforge/dockerforge)
- Join our [Community Forum](https://forum.dockerforge.example.com)
- Check our [Stack Overflow tag](https://stackoverflow.com/questions/tagged/dockerforge)

### Official Support

- Email: support@dockerforge.example.com
- Documentation: https://docs.dockerforge.example.com
- Issue Tracker: https://github.com/dockerforge/dockerforge/issues

### Reporting Bugs

When reporting bugs, please include:

1. DockerForge version:
   ```bash
   dockerforge --version
   ```

2. Docker version:
   ```bash
   docker --version
   ```

3. Operating system and version:
   ```bash
   uname -a  # Linux/macOS
   ver       # Windows
   ```

4. Diagnostic report:
   ```bash
   dockerforge diagnose --output diagnostic-report.zip
   ```

5. Steps to reproduce the issue
6. Expected vs. actual behavior
