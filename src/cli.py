"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
from src.cli_notifications import notify
from src.cli_compose import compose
from src.cli_security import main as security_main
from src.cli_backup import main as backup_main
from src.cli_update import update_cli
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
from src.cli_notifications import notify
from src.cli_compose import compose
from src.cli_security import main as security_main
from src.cli_backup import main as backup_main
from src.cli_update import update_cli
from src.cli_checkpoint import setup_checkpoint_parser
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
from src.cli_notifications import notify
from src.cli_compose import compose
from src.cli_security import main as security_main
from src.cli_backup import main as backup_main
from src.cli_update import update_cli
from src.cli_checkpoint import setup_checkpoint_parser
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
"""
Command-line interface module for DockerForge.

This module provides the command-line interface for the application.
"""

import os
import sys
import logging
import click
from typing import Optional, Dict, Any, List
from datetime import datetime
import time

from src.config.config_manager import get_config_manager, get_config, set_config, save_config
from src.utils.logging_manager import setup_logging, get_logger
from src.platforms.platform_detector import get_platform_info
from src.platforms.platform_adapter import get_platform_adapter
from src.docker.connection_manager import get_docker_client, DockerConnectionError
from src.cli_notifications import notify
from src.cli_compose import compose
from src.cli_security import main as security_main
from src.cli_backup import main as backup_main
from src.cli_update import update_cli

# Set up logging
setup_logging()
logger = get_logger("cli")


# Click context object
class CliContext:
    """Click context object for passing data between commands."""
    
    def __init__(self):
        """Initialize the CLI context."""
        self.config_path = None
        self.env_file = None
        self.verbose = False
        self.docker_client = None
        self.platform_info = None
        self.platform_adapter = None


# Click context callback
def init_context(ctx, param, value):
    """Initialize the CLI context."""
    if ctx.obj is None:
        ctx.obj = CliContext()
    return value


# Common options
def common_options(f):
    """Common command-line options."""
    f = click.option(
        "--config", "-c",
        help="Path to configuration file",
        callback=init_context,
        expose_value=False,
    )(f)
    f = click.option(
        "--env-file", "-e",
        help="Path to .env file",
        callback=init_context,
        expose_value=False,
    )(f)
    f = click.option(
        "--verbose", "-v",
        is_flag=True,
        help="Enable verbose output",
        callback=init_context,
        expose_value=False,
    )(f)
    return f


# Main command group
@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """
    DockerForge - A comprehensive Docker management tool with AI-powered troubleshooting.
    
    This tool provides functionality to monitor, troubleshoot, and maintain
    Docker environments.
    """
    # Ensure context object exists
    if ctx.obj is None:
        ctx.obj = CliContext()
    
    # Initialize platform info
    ctx.obj.platform_info = get_platform_info()
    ctx.obj.platform_adapter = get_platform_adapter()
    
    # Set up logging
    if ctx.obj.verbose:
        set_config("general.log_level", "DEBUG")
        setup_logging()
        logger.debug("Verbose logging enabled")


# Check command
@cli.command()
@common_options
@click.pass_obj
def check(obj):
    """Check Docker installation and connectivity."""
    logger.info("Checking Docker installation and connectivity")
    
    # Check platform
    platform_info = obj.platform_info
    logger.info(f"Platform: {platform_info.platform_type.value}")
    logger.info(f"Distribution: {platform_info.distribution} {platform_info.distribution_version}")
    logger.info(f"Init system: {platform_info.init_system.value}")
    
    # Check Docker connection
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get Docker version
        version = client.version()
        logger.info(f"Docker version: {version.get('Version', 'unknown')}")
        logger.info(f"API version: {version.get('ApiVersion', 'unknown')}")
        
        # Get Docker info
        info = client.info()
        logger.info(f"Containers: {info.get('Containers', 0)}")
        logger.info(f"Running: {info.get('ContainersRunning', 0)}")
        logger.info(f"Paused: {info.get('ContainersPaused', 0)}")
        logger.info(f"Stopped: {info.get('ContainersStopped', 0)}")
        logger.info(f"Images: {info.get('Images', 0)}")
        
        click.secho("Docker is installed and running correctly", fg="green")
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Info command
@cli.command()
@common_options
@click.pass_obj
def info(obj):
    """Show Docker and system information."""
    logger.info("Showing Docker and system information")
    
    # Get platform info
    platform_info = obj.platform_info
    
    click.secho("System Information", fg="blue", bold=True)
    click.echo(f"Platform: {platform_info.platform_type.value}")
    click.echo(f"Distribution: {platform_info.distribution} {platform_info.distribution_version}")
    click.echo(f"Init system: {platform_info.init_system.value}")
    click.echo(f"Docker socket: {platform_info.docker_socket_path}")
    click.echo(f"Docker config: {platform_info.docker_config_path}")
    click.echo(f"Home directory: {platform_info.home_dir}")
    click.echo(f"Root user: {platform_info.is_root}")
    click.echo(f"Sudo available: {platform_info.has_sudo}")
    
    # Check Docker connection
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        click.secho("\nDocker Information", fg="blue", bold=True)
        
        # Get Docker version
        version = client.version()
        click.echo(f"Docker version: {version.get('Version', 'unknown')}")
        click.echo(f"API version: {version.get('ApiVersion', 'unknown')}")
        click.echo(f"Go version: {version.get('GoVersion', 'unknown')}")
        click.echo(f"Git commit: {version.get('GitCommit', 'unknown')}")
        click.echo(f"Built: {version.get('BuildTime', 'unknown')}")
        click.echo(f"OS/Arch: {version.get('Os', 'unknown')}/{version.get('Arch', 'unknown')}")
        
        # Get Docker info
        info = client.info()
        click.secho("\nDocker Engine", fg="blue")
        click.echo(f"ID: {info.get('ID', 'unknown')}")
        click.echo(f"Containers: {info.get('Containers', 0)}")
        click.echo(f"Running: {info.get('ContainersRunning', 0)}")
        click.echo(f"Paused: {info.get('ContainersPaused', 0)}")
        click.echo(f"Stopped: {info.get('ContainersStopped', 0)}")
        click.echo(f"Images: {info.get('Images', 0)}")
        click.echo(f"Server Version: {info.get('ServerVersion', 'unknown')}")
        click.echo(f"Storage Driver: {info.get('Driver', 'unknown')}")
        click.echo(f"Logging Driver: {info.get('LoggingDriver', 'unknown')}")
        click.echo(f"Cgroup Driver: {info.get('CgroupDriver', 'unknown')}")
        
        # Show Docker plugins
        if "Plugins" in info:
            plugins = info["Plugins"]
            
            if "Volume" in plugins and plugins["Volume"]:
                click.secho("\nVolume Plugins", fg="blue")
                for plugin in plugins["Volume"]:
                    click.echo(f"- {plugin}")
            
            if "Network" in plugins and plugins["Network"]:
                click.secho("\nNetwork Plugins", fg="blue")
                for plugin in plugins["Network"]:
                    click.echo(f"- {plugin}")
        
        # Show Docker swarm status
        if "Swarm" in info:
            swarm = info["Swarm"]
            click.secho("\nSwarm", fg="blue")
            click.echo(f"Status: {swarm.get('LocalNodeState', 'inactive')}")
            
            if swarm.get("NodeID"):
                click.echo(f"Node ID: {swarm.get('NodeID')}")
                click.echo(f"Is Manager: {swarm.get('ControlAvailable', False)}")
        
        # Show Docker security options
        if "SecurityOptions" in info:
            click.secho("\nSecurity Options", fg="blue")
            for option in info["SecurityOptions"]:
                click.echo(f"- {option}")
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# List command
@cli.command()
@common_options
@click.option("--all", "-a", is_flag=True, help="Show all containers (default shows just running)")
@click.option("--quiet", "-q", is_flag=True, help="Only display container IDs")
@click.pass_obj
def list(obj, all, quiet):
    """List Docker containers."""
    logger.info("Listing Docker containers")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get containers
        containers = client.containers.list(all=all)
        
        if not containers:
            click.echo("No containers found")
            return
        
        if quiet:
            # Only show container IDs
            for container in containers:
                click.echo(container.id)
        else:
            # Show container details
            headers = ["CONTAINER ID", "IMAGE", "COMMAND", "CREATED", "STATUS", "PORTS", "NAMES"]
            rows = []
            
            for container in containers:
                # Get container details
                container_id = container.id[:12]
                image = container.image.tags[0] if container.image.tags else container.image.id[:12]
                command = container.attrs["Config"]["Cmd"][0] if container.attrs["Config"]["Cmd"] else ""
                created = container.attrs["Created"].split(".")[0].replace("T", " ")
                status = container.status
                
                # Format ports
                ports = []
                for port, bindings in container.ports.items():
                    if bindings:
                        for binding in bindings:
                            host_port = binding["HostPort"]
                            host_ip = binding["HostIp"]
                            host_ip = host_ip if host_ip else ""
                            ports.append(f"{host_ip}:{host_port}->{port}")
                    else:
                        ports.append(f"{port}")
                ports_str = ", ".join(ports)
                
                # Get container name
                name = container.name
                
                rows.append([container_id, image, command, created, status, ports_str, name])
            
            # Calculate column widths
            widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
            
            # Print headers
            header_row = " ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
            click.secho(header_row, fg="blue", bold=True)
            
            # Print rows
            for row in rows:
                row_str = " ".join(f"{str(row[i]):<{widths[i]}}" for i in range(len(headers)))
                click.echo(row_str)
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Logs command
@cli.command()
@common_options
@click.argument("container")
@click.option("--tail", "-n", default=100, help="Number of lines to show from the end of the logs")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.pass_obj
def logs(obj, container, tail, follow):
    """View logs for a container."""
    logger.info(f"Viewing logs for container {container}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Get logs
        logs = container.logs(tail=tail, stream=follow, timestamps=True)
        
        if follow:
            # Stream logs
            try:
                for line in logs:
                    click.echo(line.decode("utf-8").rstrip())
            except KeyboardInterrupt:
                # Exit gracefully on Ctrl+C
                pass
        else:
            # Print logs
            if isinstance(logs, bytes):
                click.echo(logs.decode("utf-8"))
            else:
                for line in logs:
                    click.echo(line.decode("utf-8").rstrip())
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Start command
@cli.command()
@common_options
@click.argument("container")
@click.pass_obj
def start(obj, container):
    """Start a container."""
    logger.info(f"Starting container {container}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Check if container is already running
        if container.status == "running":
            logger.info(f"Container {container.name} is already running")
            click.secho(f"Container {container.name} is already running", fg="yellow")
            return
        
        # Start container
        container.start()
        logger.info(f"Container {container.name} started")
        click.secho(f"Container {container.name} started", fg="green")
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Stop command
@cli.command()
@common_options
@click.argument("container")
@click.pass_obj
def stop(obj, container):
    """Stop a container."""
    logger.info(f"Stopping container {container}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Check if container is already stopped
        if container.status != "running":
            logger.info(f"Container {container.name} is not running")
            click.secho(f"Container {container.name} is not running", fg="yellow")
            return
        
        # Stop container
        container.stop()
        logger.info(f"Container {container.name} stopped")
        click.secho(f"Container {container.name} stopped", fg="green")
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Restart command
@cli.command()
@common_options
@click.argument("container")
@click.pass_obj
def restart(obj, container):
    """Restart a container."""
    logger.info(f"Restarting container {container}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Restart container
        container.restart()
        logger.info(f"Container {container.name} restarted")
        click.secho(f"Container {container.name} restarted", fg="green")
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Inspect command
@cli.command()
@common_options
@click.argument("container")
@click.option("--format", "-f", help="Format output using Go template")
@click.pass_obj
def inspect(obj, container, format):
    """Inspect a container."""
    logger.info(f"Inspecting container {container}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Get container details
        details = container.attrs
        
        # Format output if requested
        if format:
            # TODO: Implement Go template formatting
            click.secho("Format option not implemented yet", fg="yellow")
        
        # Print details
        import json
        click.echo(json.dumps(details, indent=2))
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Exec command
@cli.command()
@common_options
@click.argument("container")
@click.argument("command", nargs=-1)
@click.option("--interactive", "-i", is_flag=True, help="Keep STDIN open even if not attached")
@click.option("--tty", "-t", is_flag=True, help="Allocate a pseudo-TTY")
@click.pass_obj
def exec(obj, container, command, interactive, tty):
    """Execute a command in a running container."""
    command_str = " ".join(command)
    logger.info(f"Executing command in container {container}: {command_str}")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get container
        try:
            container = client.containers.get(container)
        except Exception as e:
            logger.error(f"Container not found: {container}")
            click.secho(f"Container not found: {container}", fg="red")
            sys.exit(1)
        
        # Check if container is running
        if container.status != "running":
            logger.error(f"Container {container.name} is not running")
            click.secho(f"Container {container.name} is not running", fg="red")
            sys.exit(1)
        
        # Execute command
        if not command:
            # Default to shell if no command specified
            if container.exec_run("which bash", stdout=False, stderr=False).exit_code == 0:
                command = ["bash"]
            else:
                command = ["sh"]
            logger.info(f"No command specified, using {command[0]}")
        
        # Execute command
        if interactive and tty:
            # Interactive mode with TTY
            import subprocess
            cmd = ["docker", "exec", "-it", container.id] + list(command)
            subprocess.run(cmd)
        else:
            # Non-interactive mode
            result = container.exec_run(command, stream=True, stdout=True, stderr=True)
            for output in result.output:
                click.echo(output.decode("utf-8").rstrip())
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Networks command
@cli.command()
@common_options
@click.pass_obj
def networks(obj):
    """List Docker networks."""
    logger.info("Listing Docker networks")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get networks
        networks = client.networks.list()
        
        if not networks:
            click.echo("No networks found")
            return
        
        # Show network details
        headers = ["NETWORK ID", "NAME", "DRIVER", "SCOPE"]
        rows = []
        
        for network in networks:
            # Get network details
            network_id = network.id[:12]
            name = network.name
            driver = network.attrs["Driver"]
            scope = network.attrs["Scope"]
            
            rows.append([network_id, name, driver, scope])
        
        # Calculate column widths
        widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
        
        # Print headers
        header_row = " ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
        click.secho(header_row, fg="blue", bold=True)
        
        # Print rows
        for row in rows:
            row_str = " ".join(f"{str(row[i]):<{widths[i]}}" for i in range(len(headers)))
            click.echo(row_str)
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Volumes command
@cli.command()
@common_options
@click.pass_obj
def volumes(obj):
    """List Docker volumes."""
    logger.info("Listing Docker volumes")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get volumes
        volumes = client.volumes.list()
        
        if not volumes:
            click.echo("No volumes found")
            return
        
        # Show volume details
        headers = ["VOLUME NAME", "DRIVER", "MOUNTPOINT"]
        rows = []
        
        for volume in volumes:
            # Get volume details
            name = volume.name
            driver = volume.attrs["Driver"]
            mountpoint = volume.attrs["Mountpoint"]
            
            rows.append([name, driver, mountpoint])
        
        # Calculate column widths
        widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
        
        # Print headers
        header_row = " ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
        click.secho(header_row, fg="blue", bold=True)
        
        # Print rows
        for row in rows:
            row_str = " ".join(f"{str(row[i]):<{widths[i]}}" for i in range(len(headers)))
            click.echo(row_str)
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Images command
@cli.command()
@common_options
@click.pass_obj
def images(obj):
    """List Docker images."""
    logger.info("Listing Docker images")
    
    try:
        client = get_docker_client()
        obj.docker_client = client
        
        # Get images
        images = client.images.list()
        
        if not images:
            click.echo("No images found")
            return
        
        # Show image details
        headers = ["IMAGE ID", "REPOSITORY", "TAG", "SIZE", "CREATED"]
        rows = []
        
        for image in images:
            # Get image details
            image_id = image.id.split(":")[-1][:12]
            
            # Handle multiple tags
            if image.tags:
                for tag in image.tags:
                    if ":" in tag:
                        repo, tag_name = tag.split(":", 1)
                    else:
                        repo, tag_name = tag, "latest"
                    
                    # Format size
                    size = image.attrs["Size"]
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f}KB"
                    elif size < 1024 * 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.1f}MB"
                    else:
                        size_str = f"{size / (1024 * 1024 * 1024):.1f}GB"
                    
                    # Format created time
                    created = image.attrs["Created"].split(".")[0].replace("T", " ")
                    
                    rows.append([image_id, repo, tag_name, size_str, created])
            else:
                # Handle untagged images
                # Format size
                size = image.attrs["Size"]
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f}KB"
                elif size < 1024 * 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f}MB"
                else:
                    size_str = f"{size / (1024 * 1024 * 1024):.1f}GB"
                
                # Format created time
                created = image.attrs["Created"].split(".")[0].replace("T", " ")
                
                rows.append([image_id, "<none>", "<none>", size_str, created])
        
        # Calculate column widths
        widths = [max(len(str(row[i])) for row in rows + [headers]) for i in range(len(headers))]
        
        # Print headers
        header_row = " ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
        click.secho(header_row, fg="blue", bold=True)
        
        # Print rows
        for row in rows:
            row_str = " ".join(f"{str(row[i]):<{widths[i]}}" for i in range(len(headers)))
            click.echo(row_str)
    
    except DockerConnectionError as e:
        logger.error(f"Docker connection error: {str(e)}")
        click.secho(f"Error connecting to Docker: {str(e)}", fg="red")
        sys.exit(1)


# Monitoring command group
@cli.group()
@common_options
@click.pass_context
def monitor(ctx):
    """Monitor Docker containers and analyze logs."""
    pass


# Monitor logs command
@monitor.command("logs")
@click.argument("container", required=False)
@click.option("--tail", "-n", default=100, help="Number of lines to show from the end of the logs")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--since", help="Show logs since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Show logs until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--search", "-s", help="Search logs for a string")
@click.option("--regex", "-r", help="Search logs using a regular expression")
@click.option("--export", "-e", help="Export logs to a file")
@click.option("--format", "-f", type=click.Choice(["text", "json", "csv"]), default="text", help="Export format")
@click.pass_obj
def monitor_logs(obj, container, tail, follow, since, until, search, regex, export, format):
    """Monitor and search container logs."""
    logger.info(f"Monitoring logs for container {container}")
    
    try:
        # Import monitoring modules
        from src.monitoring.log_collector import get_log_collection_manager
        from src.monitoring.log_explorer import get_log_explorer
        
        log_collection_manager = get_log_collection_manager()
        log_explorer = get_log_explorer()
        
        # Start log collection if not already running
        if not log_collection_manager.running:
            log_collection_manager.start()
            click.secho("Started log collection", fg="green")
        
        # Parse timestamps
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                click.secho(f"Invalid since timestamp: {since}", fg="red")
                sys.exit(1)
        
        until_dt = None
        if until:
            try:
                until_dt = datetime.fromisoformat(until)
            except ValueError:
                click.secho(f"Invalid until timestamp: {until}", fg="red")
                sys.exit(1)
        
        # Get logs
        if container:
            # Get logs for a specific container
            logs = log_collection_manager.get_container_logs(
                container_id=container,
                since=since_dt,
                until=until_dt,
                limit=tail if not follow else None,
            )
            
            if not logs:
                click.echo(f"No logs found for container {container}")
                return
        else:
            # Get logs for all containers
            logs = log_collection_manager.get_logs(
                since=since_dt,
                until=until_dt,
                limit=tail if not follow else None,
            )
            
            if not logs:
                click.echo("No logs found")
                return
        
        # Search logs if requested
        if search:
            search_result = log_explorer.search_logs(
                query=search,
                container_ids=[container] if container else None,
                since=since_dt,
                until=until_dt,
                limit=tail,
            )
            logs = search_result.logs
            click.secho(f"Found {search_result.total_matches} matches for '{search}'", fg="blue")
        
        if regex:
            search_result = log_explorer.search_logs(
                query=regex,
                container_ids=[container] if container else None,
                since=since_dt,
                until=until_dt,
                limit=tail,
                regex=True,
            )
            logs = search_result.logs
            click.secho(f"Found {search_result.total_matches} matches for regex '{regex}'", fg="blue")
        
        # Export logs if requested
        if export:
            log_explorer.export_logs(logs, format=format, file_path=export)
            click.secho(f"Exported {len(logs)} logs to {export}", fg="green")
            return
        
        # Print logs
        if not follow:
            for log in logs:
                click.echo(str(log))
        else:
            # Print existing logs
            for log in logs:
                click.echo(str(log))
            
            # Follow new logs
            def callback(log_entry):
                if container and log_entry.container_id != container:
                    return
                
                if search and search.lower() not in log_entry.message.lower():
                    return
                
                if regex:
                    import re
                    if not re.search(regex, log_entry.message, re.IGNORECASE):
                        return
                
                click.echo(str(log_entry))
            
            # Register callback
            log_collection_manager.add_callback(callback)
            
            try:
                click.secho("Following logs... Press Ctrl+C to stop", fg="yellow")
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                # Remove callback on exit
                log_collection_manager.remove_callback(callback)
                click.echo("\nStopped following logs")
    
    except Exception as e:
        logger.error(f"Error monitoring logs: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Monitor stats command
@monitor.command("stats")
@click.argument("container", required=False)
@click.option("--since", help="Show stats since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Show stats until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--interval", type=click.Choice(["minute", "hour", "day"]), default="hour", help="Time interval for stats")
@click.option("--export", "-e", help="Export stats to a file")
@click.pass_obj
def monitor_stats(obj, container, since, until, interval, export):
    """Show statistics for container logs."""
    logger.info(f"Showing statistics for container {container}")
    
    try:
        # Import monitoring modules
        from src.monitoring.log_explorer import get_log_explorer
        
        log_explorer = get_log_explorer()
        
        # Parse timestamps
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                click.secho(f"Invalid since timestamp: {since}", fg="red")
                sys.exit(1)
        
        until_dt = None
        if until:
            try:
                until_dt = datetime.fromisoformat(until)
            except ValueError:
                click.secho(f"Invalid until timestamp: {until}", fg="red")
                sys.exit(1)
        
        # Get container ID if name was provided
        if container:
            try:
                client = get_docker_client()
                container_obj = client.containers.get(container)
                container_id = container_obj.id
            except Exception as e:
                click.secho(f"Error getting container: {str(e)}", fg="red")
                sys.exit(1)
            
            # Get statistics
            try:
                stats = log_explorer.get_log_statistics(
                    container_id=container_id,
                    since=since_dt,
                    until=until_dt,
                )
                
                # Get timeline
                timeline = log_explorer.get_log_timeline(
                    container_id=container_id,
                    interval=interval,
                    since=since_dt,
                    until=until_dt,
                )
                
                # Export if requested
                if export:
                    import json
                    with open(export, "w") as f:
                        json.dump({
                            "statistics": stats.to_dict(),
                            "timeline": timeline,
                        }, f, indent=2)
                    click.secho(f"Exported statistics to {export}", fg="green")
                    return
                
                # Print statistics
                click.secho(f"Log Statistics for {stats.container_name} ({stats.container_id[:12]})", fg="blue", bold=True)
                click.echo(f"Log count: {stats.log_count}")
                click.echo(f"Time range: {stats.time_range[0].isoformat()} to {stats.time_range[1].isoformat()}")
                click.echo(f"Message length: avg={stats.message_length_avg:.1f}, min={stats.message_length_min}, max={stats.message_length_max}")
                click.echo(f"Error count: {stats.error_count}")
                click.echo(f"Warning count: {stats.warning_count}")
                
                # Print common terms
                click.secho("\nCommon Terms:", fg="blue", bold=True)
                for term, count in stats.common_terms[:10]:
                    click.echo(f"{term}: {count}")
                
                # Print timeline
                click.secho(f"\nLog Timeline ({interval}):", fg="blue", bold=True)
                for time_key, count in sorted(timeline.items()):
                    click.echo(f"{time_key}: {count}")
                
                # Print pattern matches
                if stats.pattern_matches:
                    click.secho("\nPattern Matches:", fg="blue", bold=True)
                    for pattern_id, count in stats.pattern_matches.items():
                        click.echo(f"{pattern_id}: {count}")
            except ValueError as e:
                click.secho(f"Error: {str(e)}", fg="red")
                sys.exit(1)
        else:
            click.secho("Container ID or name is required", fg="red")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error showing statistics: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Monitor analyze command
@monitor.command("analyze")
@click.argument("container")
@click.option("--since", help="Analyze logs since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Analyze logs until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--template", "-t", default="default", help="Analysis template to use")
@click.option("--provider", help="AI provider to use (claude, gemini, ollama)")
@click.option("--export", "-e", help="Export analysis to a file")
@click.pass_obj
def monitor_analyze(obj, container, since, until, template, provider, export):
    """Analyze container logs using AI."""
    logger.info(f"Analyzing logs for container {container}")
    
    try:
        # Import monitoring modules
        from src.monitoring.log_analyzer import get_log_analyzer
        
        log_analyzer = get_log_analyzer(provider)
        
        # Parse timestamps
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                click.secho(f"Invalid since timestamp: {since}", fg="red")
                sys.exit(1)
        
        until_dt = None
        if until:
            try:
                until_dt = datetime.fromisoformat(until)
            except ValueError:
                click.secho(f"Invalid until timestamp: {until}", fg="red")
                sys.exit(1)
        
        # Get container ID if name was provided
        try:
            client = get_docker_client()
            container_obj = client.containers.get(container)
            container_id = container_obj.id
        except Exception as e:
            click.secho(f"Error getting container: {str(e)}", fg="red")
            sys.exit(1)
        
        # Analyze logs
        click.echo(f"Analyzing logs for container {container}...")
        try:
            analysis = log_analyzer.analyze_container_logs(
                container_id=container_id,
                template_id=template,
                since=since_dt,
                until=until_dt,
            )
            
            # Export if requested
            if export:
                import json
                with open(export, "w") as f:
                    json.dump(analysis.to_dict(), f, indent=2)
                click.secho(f"Exported analysis to {export}", fg="green")
                return
            
            # Print analysis
            click.secho(f"Log Analysis for {analysis.container_name} ({analysis.container_id[:12]})", fg="blue", bold=True)
            click.echo(f"AI Provider: {analysis.ai_provider} ({analysis.ai_model})")
            click.echo(f"Log count: {analysis.log_count}")
            click.echo(f"Analysis time: {analysis.analysis_duration:.2f} seconds")
            
            click.secho("\nSummary:", fg="blue", bold=True)
            click.echo(analysis.summary)
            
            if analysis.issues:
                click.secho("\nIssues:", fg="blue", bold=True)
                for i, issue in enumerate(analysis.issues, 1):
                    click.secho(f"{i}. {issue.get('title', 'Untitled Issue')}", fg="yellow")
                    click.echo(f"   Severity: {issue.get('severity', 'unknown')}")
                    click.echo(f"   {issue.get('description', '')}")
                    if "evidence" in issue:
                        click.echo(f"   Evidence: {issue['evidence']}")
            
            if analysis.recommendations:
                click.secho("\nRecommendations:", fg="blue", bold=True)
                for i, rec in enumerate(analysis.recommendations, 1):
                    click.secho(f"{i}. {rec.get('title', 'Untitled Recommendation')}", fg="green")
                    click.echo(f"   {rec.get('description', '')}")
                    if "steps" in rec:
                        click.echo("   Steps:")
                        for j, step in enumerate(rec["steps"], 1):
                            click.echo(f"     {j}. {step}")
        except ValueError as e:
            click.secho(f"Error: {str(e)}", fg="red")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error analyzing logs: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Monitor issues command
@monitor.command("issues")
@click.option("--container", help="Filter issues by container")
@click.option("--status", type=click.Choice(["open", "acknowledged", "in_progress", "resolved", "closed"]), help="Filter issues by status")
@click.option("--severity", type=click.Choice(["info", "warning", "error", "critical"]), help="Filter issues by severity")
@click.option("--limit", type=int, default=10, help="Maximum number of issues to show")
@click.option("--export", "-e", help="Export issues to a file")
@click.pass_obj
def monitor_issues(obj, container, status, severity, limit, export):
    """Show detected issues in containers."""
    logger.info("Showing detected issues")
    
    try:
        # Import monitoring modules
        from src.monitoring.issue_detector import get_issue_detector
        
        issue_detector = get_issue_detector()
        
        # Get container ID if name was provided
        container_id = None
        if container:
            try:
                client = get_docker_client()
                container_obj = client.containers.get(container)
                container_id = container_obj.id
            except Exception as e:
                click.secho(f"Error getting container: {str(e)}", fg="red")
                sys.exit(1)
        
        # Get issues
        issues = issue_detector.get_issues(
            container_id=container_id,
            status=status,
            severity=severity,
            limit=limit,
        )
        
        # Export if requested
        if export:
            import json
            with open(export, "w") as f:
                json.dump([issue.to_dict() for issue in issues], f, indent=2)
            click.secho(f"Exported {len(issues)} issues to {export}", fg="green")
            return
        
        # Print issues
        if not issues:
            click.echo("No issues found")
            return
        
        click.secho(f"Found {len(issues)} issues", fg="blue", bold=True)
        
        for issue in issues:
            # Determine color based on severity
            if issue.severity.value == "critical":
                color = "red"
            elif issue.severity.value == "error":
                color = "bright_red"
            elif issue.severity.value == "warning":
                color = "yellow"
            else:
                color = "blue"
            
            click.secho(f"\nIssue: {issue.title}", fg=color, bold=True)
            click.echo(f"ID: {issue.id}")
            click.echo(f"Container: {issue.container_name} ({issue.container_id[:12]})")
            click.echo(f"Severity: {issue.severity.value}")
            click.echo(f"Status: {issue.status.value}")
            click.echo(f"Created: {issue.created_at.isoformat()}")
            click.echo(f"Updated: {issue.updated_at.isoformat()}")
            
            if issue.description:
                click.echo(f"\nDescription: {issue.description}")
            
            if issue.pattern_id:
                click.echo(f"Pattern: {issue.pattern_id}")
            
            if issue.resolution:
                click.echo(f"Resolution: {issue.resolution}")
    
    except Exception as e:
        logger.error(f"Error showing issues: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Monitor recommendations command
@monitor.command("recommendations")
@click.option("--issue", help="Get recommendations for a specific issue")
@click.option("--container", help="Filter recommendations by container")
@click.option("--export", "-e", help="Export recommendations to a file")
@click.pass_obj
def monitor_recommendations(obj, issue, container, export):
    """Show recommendations for resolving issues."""
    logger.info("Showing recommendations")
    
    try:
        # Import monitoring modules
        from src.monitoring.recommendation_engine import get_recommendation_engine
        from src.monitoring.issue_detector import get_issue_detector
        
        recommendation_engine = get_recommendation_engine()
        issue_detector = get_issue_detector()
        
        # Get container ID if name was provided
        container_id = None
        if container:
            try:
                client = get_docker_client()
                container_obj = client.containers.get(container)
                container_id = container_obj.id
            except Exception as e:
                click.secho(f"Error getting container: {str(e)}", fg="red")
                sys.exit(1)
        
        # Get recommendations for a specific issue
        if issue:
            issue_obj = issue_detector.get_issue(issue)
            if not issue_obj:
                click.secho(f"Issue not found: {issue}", fg="red")
                sys.exit(1)
            
            # Get or generate recommendation
            click.echo(f"Getting recommendation for issue: {issue_obj.title}")
            recommendation = recommendation_engine.get_recommendation_for_issue(issue)
            
            if not recommendation:
                click.secho("No recommendation available", fg="yellow")
                return
            
            # Export if requested
            if export:
                import json
                with open(export, "w") as f:
                    json.dump(recommendation.to_dict(), f, indent=2)
                click.secho(f"Exported recommendation to {export}", fg="green")
                return
            
            # Print recommendation
            click.secho(f"Recommendation: {recommendation.title}", fg="blue", bold=True)
            click.echo(f"ID: {recommendation.id}")
            click.echo(f"Issue: {issue_obj.title} ({issue})")
            click.echo(f"Source: {recommendation.source}")
            click.echo(f"Created: {recommendation.created_at.isoformat()}")
            
            if recommendation.description:
                click.echo(f"\nDescription: {recommendation.description}")
            
            if recommendation.steps:
                click.secho("\nSteps:", fg="blue")
                for i, step in enumerate(recommendation.steps, 1):
                    click.secho(f"{i}. {step.description}", fg="green")
                    
                    if step.command:
                        click.echo(f"   Command: {step.command}")
                    
                    if step.code:
                        click.echo(f"   Code: {step.code}")
                    
                    if step.manual_action:
                        click.echo(f"   Manual action: {step.manual_action}")
                    
                    if step.verification:
                        click.echo(f"   Verification: {step.verification}")
            
            # Ask if user wants to apply the recommendation
            if click.confirm("Do you want to apply this recommendation?"):
                recommendation_engine.apply_recommendation(recommendation.id)
                click.secho("Recommendation applied", fg="green")
        else:
            # Get all recommendations
            recommendations = recommendation_engine.get_all_recommendations()
            
            # Filter by container
            if container_id:
                # Get issues for container
                container_issues = issue_detector.get_container_issues(container_id)
                container_issue_ids = [issue.id for issue in container_issues]
                
                # Filter recommendations
                recommendations = [r for r in recommendations if r.issue_id in container_issue_ids]
            
            # Export if requested
            if export:
                import json
                with open(export, "w") as f:
                    json.dump([r.to_dict() for r in recommendations], f, indent=2)
                click.secho(f"Exported {len(recommendations)} recommendations to {export}", fg="green")
                return
            
            # Print recommendations
            if not recommendations:
                click.echo("No recommendations found")
                return
            
            click.secho(f"Found {len(recommendations)} recommendations", fg="blue", bold=True)
            
            for recommendation in recommendations:
                issue_obj = issue_detector.get_issue(recommendation.issue_id)
                issue_title = issue_obj.title if issue_obj else "Unknown issue"
                
                click.secho(f"\nRecommendation: {recommendation.title}", fg="blue")
                click.echo(f"ID: {recommendation.id}")
                click.echo(f"Issue: {issue_title} ({recommendation.issue_id})")
                click.echo(f"Source: {recommendation.source}")
                click.echo(f"Created: {recommendation.created_at.isoformat()}")
                
                if recommendation.applied_at:
                    click.secho(f"Applied: {recommendation.applied_at.isoformat()}", fg="green")
    
    except Exception as e:
        logger.error(f"Error showing recommendations: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Troubleshoot command group
@cli.group()
@common_options
@click.pass_context
def troubleshoot(ctx):
    """Troubleshoot Docker issues using AI."""
    pass


# Troubleshoot container command
@troubleshoot.command("container")
@click.argument("container")
@click.option("--provider", help="AI provider to use (claude, gemini, ollama)")
@click.pass_obj
def troubleshoot_container(obj, container, provider):
    """Analyze a container for issues using AI."""
    logger.info(f"Troubleshooting container {container}")
    
    try:
        # Import here to avoid circular imports
        from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
        
        troubleshooter = get_troubleshooter(provider)
        
        click.echo(f"Analyzing container {container}...")
        result = troubleshooter.analyze_container(container)
        
        click.secho("\nAnalysis Result", fg="blue", bold=True)
        click.echo(f"Container: {result['container_name']} ({result['container_id'][:12]})")
        click.echo(f"Status: {result['container_status']}")
        click.echo(f"AI Provider: {result['provider']} ({result['model']})")
        
        click.secho("\nAnalysis:", fg="blue", bold=True)
        click.echo(result["analysis"])
    
    except TroubleshooterError as e:
        logger.error(f"Troubleshooting error: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Troubleshoot logs command
@troubleshoot.command("logs")
@click.argument("file", type=click.Path(exists=True))
@click.option("--provider", help="AI provider to use (claude, gemini, ollama)")
@click.pass_obj
def troubleshoot_logs(obj, file, provider):
    """Analyze log file for issues using AI."""
    logger.info(f"Troubleshooting logs from {file}")
    
    try:
        # Import here to avoid circular imports
        from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
        
        # Read log file
        with open(file, "r") as f:
            logs = f.read()
        
        troubleshooter = get_troubleshooter(provider)
        
        click.echo(f"Analyzing logs from {file}...")
        result = troubleshooter.analyze_logs(logs)
        
        click.secho("\nAnalysis Result", fg="blue", bold=True)
        click.echo(f"Log File: {file}")
        click.echo(f"AI Provider: {result['provider']} ({result['model']})")
        
        click.secho("\nAnalysis:", fg="blue", bold=True)
        click.echo(result["analysis"])
    
    except TroubleshooterError as e:
        logger.error(f"Troubleshooting error: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Troubleshoot compose command
@troubleshoot.command("compose")
@click.argument("file", type=click.Path(exists=True))
@click.option("--provider", help="AI provider to use (claude, gemini, ollama)")
@click.pass_obj
def troubleshoot_compose(obj, file, provider):
    """Analyze Docker Compose file for issues using AI."""
    logger.info(f"Troubleshooting Docker Compose file {file}")
    
    try:
        # Import here to avoid circular imports
        from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
        
        troubleshooter = get_troubleshooter(provider)
        
        click.echo(f"Analyzing Docker Compose file {file}...")
        result = troubleshooter.analyze_docker_compose(file)
        
        click.secho("\nAnalysis Result", fg="blue", bold=True)
        click.echo(f"Compose File: {file}")
        click.echo(f"AI Provider: {result['provider']} ({result['model']})")
        
        click.secho("\nAnalysis:", fg="blue", bold=True)
        click.echo(result["analysis"])
    
    except TroubleshooterError as e:
        logger.error(f"Troubleshooting error: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Troubleshoot dockerfile command
@troubleshoot.command("dockerfile")
@click.argument("file", type=click.Path(exists=True))
@click.option("--provider", help="AI provider to use (claude, gemini, ollama)")
@click.pass_obj
def troubleshoot_dockerfile(obj, file, provider):
    """Analyze Dockerfile for issues using AI."""
    logger.info(f"Troubleshooting Dockerfile {file}")
    
    try:
        # Import here to avoid circular imports
        from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
        
        troubleshooter = get_troubleshooter(provider)
        
        click.echo(f"Analyzing Dockerfile {file}...")
        result = troubleshooter.analyze_dockerfile(file)
        
        click.secho("\nAnalysis Result", fg="blue", bold=True)
        click.echo(f"Dockerfile: {file}")
        click.echo(f"AI Provider: {result['provider']} ({result['model']})")
        
        click.secho("\nAnalysis:", fg="blue", bold=True)
        click.echo(result["analysis"])
    
    except TroubleshooterError as e:
        logger.error(f"Troubleshooting error: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Troubleshoot connection command
@troubleshoot.command("connection")
@click.pass_obj
def troubleshoot_connection(obj):
    """Troubleshoot Docker connection issues."""
    logger.info("Troubleshooting Docker connection issues")
    
    try:
        # Import here to avoid circular imports
        from src.core.troubleshooter import get_troubleshooter, TroubleshooterError
        
        troubleshooter = get_troubleshooter()
        
        click.echo("Troubleshooting Docker connection issues...")
        result = troubleshooter.troubleshoot_connection()
        
        if result["connected"]:
            click.secho("Docker is connected and running correctly", fg="green")
            return
        
        click.secho("\nIssues Found:", fg="yellow", bold=True)
        for issue in result["issues"]:
            click.echo(f"- {issue}")
        
        click.secho("\nRecommended Fixes:", fg="blue", bold=True)
        for fix in result["fixes"]:
            click.echo(f"- {fix}")
    
    except TroubleshooterError as e:
        logger.error(f"Troubleshooting error: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Config command
@cli.group()
@common_options
@click.pass_context
def config(ctx):
    """Manage DockerForge configuration."""
    pass


# Config get command
@config.command("get")
@click.argument("key")
@click.pass_obj
def config_get(obj, key):
    """Get a configuration value."""
    logger.info(f"Getting configuration value for {key}")
    
    value = get_config(key)
    if value is None:
        click.echo(f"Configuration key not found: {key}")
    else:
        click.echo(f"{key}: {value}")


# Config set command
@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_obj
def config_set(obj, key, value):
    """Set a configuration value."""
    logger.info(f"Setting configuration value for {key}")
    
    # Convert value to appropriate type
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    elif value.isdigit():
        value = int(value)
    elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
        value = float(value)
    
    set_config(key, value)
    save_config()
    
    click.secho(f"Configuration value set: {key} = {value}", fg="green")


# Config list command
@config.command("list")
@click.pass_obj
def config_list(obj):
    """List all configuration values."""
    logger.info("Listing all configuration values")
    
    config_manager = get_config_manager()
    
    def print_config(config, prefix=""):
        for key, value in config.items():
            if isinstance(value, dict):
                click.secho(f"{prefix}{key}:", fg="blue", bold=True)
                print_config(value, prefix + "  ")
            else:
                click.echo(f"{prefix}{key}: {value}")
    
    print_config(config_manager.config)


# Resource monitoring command group
@cli.group()
@common_options
@click.pass_context
def resource(ctx):
    """Monitor and optimize Docker container resources."""
    pass


# Resource monitoring start command
@resource.command("start")
@click.option("--foreground", "-f", is_flag=True, help="Run in the foreground")
@click.pass_obj
def resource_start(obj, foreground):
    """Start the resource monitoring daemon."""
    logger.info("Starting resource monitoring daemon")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        from src.notifications.notification_manager import NotificationManager
        
        # Initialize notification manager
        notification_manager = NotificationManager(get_config_manager())
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client(),
            notification_manager
        )
        
        # Check if daemon is already running
        if daemon_manager.is_running():
            click.secho("Resource monitoring daemon is already running", fg="yellow")
            return
        
        # Start daemon
        click.echo(f"Starting resource monitoring daemon{' in foreground' if foreground else ''}...")
        daemon_manager.start(foreground)
        
        if not foreground:
            # Wait a bit for the daemon to start
            time.sleep(1)
            
            if daemon_manager.is_running():
                click.secho("Resource monitoring daemon started successfully", fg="green")
            else:
                click.secho("Failed to start resource monitoring daemon", fg="red")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error starting resource monitoring daemon: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring stop command
@resource.command("stop")
@click.pass_obj
def resource_stop(obj):
    """Stop the resource monitoring daemon."""
    logger.info("Stopping resource monitoring daemon")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon is not running", fg="yellow")
            return
        
        # Stop daemon
        click.echo("Stopping resource monitoring daemon...")
        daemon_manager.stop()
        
        # Wait a bit for the daemon to stop
        time.sleep(1)
        
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon stopped successfully", fg="green")
        else:
            click.secho("Failed to stop resource monitoring daemon", fg="red")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error stopping resource monitoring daemon: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring status command
@resource.command("status")
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_obj
def resource_status(obj, json):
    """Show the status of the resource monitoring daemon."""
    logger.info("Showing resource monitoring daemon status")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            if json:
                import json as json_module
                click.echo(json_module.dumps({'running': False}, indent=2))
            else:
                click.secho("Resource monitoring daemon is not running", fg="yellow")
            return
        
        # Get status
        status = daemon_manager.get_status()
        
        if json:
            import json as json_module
            click.echo(json_module.dumps(status, indent=2))
        else:
            click.secho("Resource Monitoring Daemon Status", fg="blue", bold=True)
            click.echo(f"Running: {status['running']}")
            click.echo(f"PID: {status['pid']}")
            click.echo(f"Last Updated: {datetime.fromtimestamp(status['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}")
            
            click.secho("\nComponents:", fg="blue")
            for component, component_status in status['components'].items():
                click.echo(f"  {component.replace('_', ' ').title()}:")
                for key, value in component_status.items():
                    click.echo(f"    {key.replace('_', ' ').title()}: {value}")
    
    except Exception as e:
        logger.error(f"Error showing resource monitoring daemon status: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring metrics command
@resource.command("metrics")
@click.option("--container", help="Container ID or name to filter by")
@click.option("--type", "metric_type", type=click.Choice(["cpu", "memory", "disk", "network"]), help="Metric type to filter by")
@click.option("--since", help="Show metrics since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Show metrics until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_obj
def resource_metrics(obj, container, metric_type, since, until, json):
    """Show container resource metrics."""
    logger.info(f"Showing resource metrics for container {container}")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon is not running", fg="red")
            sys.exit(1)
        
        # Get metrics
        metrics = daemon_manager.get_metrics(
            container_id=container,
            metric_type=metric_type,
            start_time=since,
            end_time=until
        )
        
        if not metrics:
            click.echo("No metrics found")
            return
        
        if json:
            import json as json_module
            click.echo(json_module.dumps(metrics, indent=2))
        else:
            click.secho("Container Resource Metrics", fg="blue", bold=True)
            
            for container_id, container_metrics in metrics.items():
                click.echo(f"\nContainer: {container_id}")
                
                for metric_type, metric_data in container_metrics.items():
                    click.echo(f"  {metric_type.capitalize()} Metrics:")
                    
                    for i, entry in enumerate(metric_data[:5]):  # Show only the first 5 entries
                        click.echo(f"    Entry {i+1}:")
                        click.echo(f"      Timestamp: {entry['timestamp']}")
                        click.echo(f"      Data: {json_module.dumps(entry['data'], indent=8)[:100]}...")
                        
                    if len(metric_data) > 5:
                        click.echo(f"    ... and {len(metric_data) - 5} more entries")
    
    except Exception as e:
        logger.error(f"Error showing resource metrics: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring anomalies command
@resource.command("anomalies")
@click.option("--container", help="Container ID or name to filter by")
@click.option("--type", "metric_type", type=click.Choice(["cpu", "memory", "disk", "network"]), help="Metric type to filter by")
@click.option("--since", help="Show anomalies since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Show anomalies until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--severity", type=int, help="Severity level to filter by")
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_obj
def resource_anomalies(obj, container, metric_type, since, until, severity, json):
    """Show detected resource anomalies."""
    logger.info(f"Showing resource anomalies for container {container}")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon is not running", fg="red")
            sys.exit(1)
        
        # Get anomalies
        anomalies = daemon_manager.get_anomalies(
            container_id=container,
            metric_type=metric_type,
            start_time=since,
            end_time=until,
            severity=severity
        )
        
        if not anomalies:
            click.echo("No anomalies found")
            return
        
        if json:
            import json as json_module
            click.echo(json_module.dumps(anomalies, indent=2))
        else:
            click.secho("Detected Resource Anomalies", fg="blue", bold=True)
            
            for container_id, container_anomalies in anomalies.items():
                click.echo(f"\nContainer: {container_id}")
                click.echo(f"  Total Anomalies: {len(container_anomalies)}")
                
                # Group anomalies by type
                anomalies_by_type = {}
                for anomaly in container_anomalies:
                    anomaly_type = anomaly.get('type', 'unknown')
                    if anomaly_type not in anomalies_by_type:
                        anomalies_by_type[anomaly_type] = []
                    anomalies_by_type[anomaly_type].append(anomaly)
                    
                for anomaly_type, type_anomalies in anomalies_by_type.items():
                    click.echo(f"  {anomaly_type.capitalize()} Anomalies: {len(type_anomalies)}")
                    
                    for i, anomaly in enumerate(type_anomalies[:3]):  # Show only the first 3 anomalies of each type
                        click.echo(f"    {i+1}. {anomaly.get('description', 'No description')}")
                        click.echo(f"       Timestamp: {anomaly.get('timestamp', 'Unknown')}")
                        click.echo(f"       Severity: {anomaly.get('severity', 'Unknown')}")
                        click.echo(f"       Metric Type: {anomaly.get('metric_type', 'Unknown')}")
                        
                    if len(type_anomalies) > 3:
                        click.echo(f"    ... and {len(type_anomalies) - 3} more {anomaly_type} anomalies")
    
    except Exception as e:
        logger.error(f"Error showing resource anomalies: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring recommendations command
@resource.command("recommendations")
@click.option("--container", help="Container ID or name to filter by")
@click.option("--type", "recommendation_type", type=click.Choice(["sizing", "performance", "cost"]), help="Recommendation type to filter by")
@click.option("--resource", type=click.Choice(["cpu", "memory", "disk", "network", "general"]), help="Resource type to filter by")
@click.option("--since", help="Show recommendations since timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--until", help="Show recommendations until timestamp (e.g. 2021-01-01T12:00:00)")
@click.option("--json", is_flag=True, help="Output in JSON format")
@click.pass_obj
def resource_recommendations(obj, container, recommendation_type, resource, since, until, json):
    """Show resource optimization recommendations."""
    logger.info(f"Showing resource optimization recommendations for container {container}")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon is not running", fg="red")
            sys.exit(1)
        
        # Get recommendations
        recommendations = daemon_manager.get_recommendations(
            container_id=container,
            recommendation_type=recommendation_type,
            resource=resource,
            start_time=since,
            end_time=until
        )
        
        if not recommendations:
            click.echo("No recommendations found")
            return
        
        if json:
            import json as json_module
            click.echo(json_module.dumps(recommendations, indent=2))
        else:
            click.secho("Resource Optimization Recommendations", fg="blue", bold=True)
            
            for container_id, container_recs in recommendations.items():
                click.echo(f"\nContainer: {container_id}")
                click.echo(f"  Total Recommendations: {len(container_recs)}")
                
                # Group recommendations by type
                recs_by_type = {}
                for rec in container_recs:
                    rec_type = rec.get('type', 'unknown')
                    if rec_type not in recs_by_type:
                        recs_by_type[rec_type] = []
                    recs_by_type[rec_type].append(rec)
                    
                for rec_type, type_recs in recs_by_type.items():
                    click.echo(f"  {rec_type.capitalize()} Recommendations: {len(type_recs)}")
                    
                    for i, rec in enumerate(type_recs[:3]):  # Show only the first 3 recommendations of each type
                        click.echo(f"    {i+1}. {rec.get('description', 'No description')}")
                        click.echo(f"       Impact: {rec.get('impact', 'Unknown')}")
                        click.echo(f"       Resource: {rec.get('resource', 'Unknown')}")
                        
                        if 'command' in rec:
                            click.echo(f"       Command: {rec['command']}")
                            
                        if 'suggestions' in rec:
                            click.echo("       Suggestions:")
                            for suggestion in rec['suggestions'][:2]:  # Show only the first 2 suggestions
                                click.echo(f"         - {suggestion}")
                            if len(rec['suggestions']) > 2:
                                click.echo(f"         ... and {len(rec['suggestions']) - 2} more suggestions")
                                
                    if len(type_recs) > 3:
                        click.echo(f"    ... and {len(type_recs) - 3} more {rec_type} recommendations")
    
    except Exception as e:
        logger.error(f"Error showing resource recommendations: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Resource monitoring report command
@resource.command("report")
@click.option("--container", help="Container ID or name to filter by")
@click.option("--format", type=click.Choice(["text", "json", "html"]), default="text", help="Output format")
@click.option("--output", "-o", help="Output file path")
@click.pass_obj
def resource_report(obj, container, format, output):
    """Generate a resource optimization report."""
    logger.info(f"Generating resource optimization report for container {container}")
    
    try:
        # Import resource monitoring modules
        from src.resource_monitoring.daemon_manager import DaemonManager
        
        # Initialize daemon manager
        daemon_manager = DaemonManager(
            get_config_manager(),
            obj.docker_client or get_docker_client()
        )
        
        # Check if daemon is running
        if not daemon_manager.is_running():
            click.secho("Resource monitoring daemon is not running", fg="red")
            sys.exit(1)
        
        # Generate report
        report = daemon_manager.generate_optimization_report(
            container_id=container,
            format=format
        )
        
        if not report or report == "No optimization recommendations available.":
            click.echo("No optimization recommendations available")
            return
        
        if output:
            # Write report to file
            with open(output, 'w') as f:
                f.write(report)
            click.secho(f"Report written to {output}", fg="green")
        else:
            # Print report to stdout
            click.echo(report)
    
    except Exception as e:
        logger.error(f"Error generating resource optimization report: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


# Register notification commands
cli.add_command(notify)

# Register compose commands
cli.add_command(compose)

# Register update commands
cli.add_command(update_cli)

# Security command group
@cli.group()
@common_options
@click.pass_context
def security(ctx):
    """Manage Docker security scanning, auditing, and reporting."""
    pass

# Backup command group
@cli.group()
@common_options
@click.pass_context
def backup(ctx):
    """Manage Docker container, image, and volume backups."""
    pass

# Security scan command
@security.command("scan")
@click.option("--image", help="Name of the Docker image to scan. If not provided, all images will be scanned.")
@click.option("--severity", type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]), multiple=True, help="Severity levels to include in the report.")
@click.option("--format", type=click.Choice(["json", "html", "text"]), default="text", help="Output format for the report.")
@click.option("--output", help="Output file for the report. If not provided, the report will be printed to stdout.")
@click.option("--ignore-unfixed", is_flag=True, help="Ignore vulnerabilities that don't have a fix.")
@click.pass_obj
def security_scan(obj, image, severity, format, output, ignore_unfixed):
    """Scan Docker images for vulnerabilities."""
    # Convert to list for the CLI adapter
    severity_list = list(severity) if severity else None
    
    # Call the security CLI
    import sys
    args = ["scan"]
    if image:
        args.extend(["--image", image])
    if severity_list:
        for s in severity_list:
            args.extend(["--severity", s])
    if format:
        args.extend(["--format", format])
    if output:
        args.extend(["--output", output])
    if ignore_unfixed:
        args.append("--ignore-unfixed")
    
    sys.argv = ["security"] + args
    security_main()

# Security audit command
@security.command("audit")
@click.option("--check-type", type=click.Choice(["host", "container", "daemon", "images", "networks", "registries"]), help="Type of check to run. If not provided, all checks will be run.")
@click.option("--format", type=click.Choice(["json", "html", "text"]), default="text", help="Output format for the report.")
@click.option("--output", help="Output file for the report. If not provided, the report will be printed to stdout.")
@click.option("--no-summary", is_flag=True, help="Don't include a summary in the report.")
@click.option("--no-remediation", is_flag=True, help="Don't include remediation steps in the report.")
@click.pass_obj
def security_audit(obj, check_type, format, output, no_summary, no_remediation):
    """Audit Docker configuration for security best practices."""
    # Call the security CLI
    import sys
    args = ["audit"]
    if check_type:
        args.extend(["--check-type", check_type])
    if format:
        args.extend(["--format", format])
    if output:
        args.extend(["--output", output])
    if no_summary:
        args.append("--no-summary")
    if no_remediation:
        args.append("--no-remediation")
    
    sys.argv = ["security"] + args
    security_main()

# Security report command
@security.command("report")
@click.option("--image", help="Name of the Docker image to scan for vulnerabilities. If not provided, all images will be scanned.")
@click.option("--check-type", type=click.Choice(["host", "container", "daemon", "images", "networks", "registries"]), help="Type of check to run for audit. If not provided, all checks will be run.")
@click.option("--severity", type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]), multiple=True, help="Severity levels to include in the vulnerability report.")
@click.option("--format", type=click.Choice(["json", "html", "text"]), default="text", help="Output format for the report.")
@click.option("--output", help="Output file for the report. If not provided, the report will be printed to stdout.")
@click.pass_obj
def security_report(obj, image, check_type, severity, format, output):
    """Generate a comprehensive security report."""
    # Convert to list for the CLI adapter
    severity_list = list(severity) if severity else None
    
    # Call the security CLI
    import sys
    args = ["report"]
    if image:
        args.extend(["--image", image])
    if check_type:
        args.extend(["--check-type", check_type])
    if severity_list:
        for s in severity_list:
            args.extend(["--severity", s])
    if format:
        args.extend(["--format", format])
    if output:
        args.extend(["--output", output])
    
    sys.argv = ["security"] + args
    security_main()

# Backup container command
@backup.command("container")
@click.argument("container")
@click.option("--name", help="Name of the backup. If not provided, a name will be generated.")
@click.option("--no-volumes", is_flag=True, help="Don't include volumes in the backup.")
@click.option("--include-image", is_flag=True, help="Include the container's image in the backup.")
@click.pass_obj
def backup_container(obj, container, name, no_volumes, include_image):
    """Backup a Docker container."""
    # Call the backup CLI
    import sys
    args = ["backup", "container", container]
    if name:
        args.extend(["--name", name])
    if no_volumes:
        args.append("--no-volumes")
    if include_image:
        args.append("--include-image")
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup list command
@backup.command("list")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="Output format.")
@click.pass_obj
def backup_list(obj, format):
    """List all backups."""
    # Call the backup CLI
    import sys
    args = ["backup", "list"]
    if format:
        args.extend(["--format", format])
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup show command
@backup.command("show")
@click.argument("backup_id")
@click.option("--format", type=click.Choice(["json", "table"]), default="table", help="Output format.")
@click.pass_obj
def backup_show(obj, backup_id, format):
    """Show backup details."""
    # Call the backup CLI
    import sys
    args = ["backup", "show", backup_id]
    if format:
        args.extend(["--format", format])
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup delete command
@backup.command("delete")
@click.argument("backup_id")
@click.pass_obj
def backup_delete(obj, backup_id):
    """Delete a backup."""
    # Call the backup CLI
    import sys
    args = ["backup", "delete", backup_id]
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup restore command
@backup.command("restore")
@click.argument("backup_id")
@click.option("--name", help="Name for the restored container. If not provided, a name will be generated.")
@click.option("--no-volumes", is_flag=True, help="Don't restore volumes.")
@click.option("--no-image", is_flag=True, help="Don't restore the container's image.")
@click.pass_obj
def backup_restore(obj, backup_id, name, no_volumes, no_image):
    """Restore a Docker container from backup."""
    # Call the backup CLI
    import sys
    args = ["restore", backup_id]
    if name:
        args.extend(["--name", name])
    if no_volumes:
        args.append("--no-volumes")
    if no_image:
        args.append("--no-image")
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup export command
@backup.command("export")
@click.argument("type", type=click.Choice(["image", "container", "volume"]))
@click.argument("target")
@click.option("--output", help="Path to save the exported file. If not provided, a default path will be used.")
@click.option("--no-compress", is_flag=True, help="Don't compress the exported file.")
@click.pass_obj
def backup_export(obj, type, target, output, no_compress):
    """Export Docker containers, images, and volumes to files."""
    # Call the backup CLI
    import sys
    args = ["export", type, target]
    if output:
        args.extend(["--output", output])
    if no_compress:
        args.append("--no-compress")
    
    sys.argv = ["backup"] + args
    backup_main()

# Backup import command
@backup.command("import")
@click.argument("type", type=click.Choice(["image", "container", "volume"]))
@click.argument("file")
@click.option("--repository", help="Repository name for the imported image or container.")
@click.option("--tag", help="Tag for the imported image or container.")
@click.option("--name", help="Name for the imported container or volume.")
@click.pass_obj
def backup_import(obj, type, file, repository, tag, name):
    """Import Docker containers, images, and volumes from files."""
    # Call the backup CLI
    import sys
    args = ["import", type, file]
    if repository:
        args.extend(["--repository", repository])
    if tag:
        args.extend(["--tag", tag])
    if name:
        args.extend(["--name", name])
    
    sys.argv = ["backup"] + args
    backup_main()


# Main entry point
def main():
    """Main entry point for the application."""
    try:
        cli()
    except Exception as e:
        logger.exception(f"Unhandled exception: {str(e)}")
        click.secho(f"Error: {str(e)}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
