"""
Command-line interface module for Docker Compose management in DockerForge.

This module provides the command-line interface for Docker Compose management.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml

from src.compose.change_manager import ChangeManager
from src.compose.compose_discovery import ComposeDiscovery
from src.compose.compose_operations import ComposeOperations
from src.compose.compose_parser import ComposeParser
from src.compose.template_manager import TemplateManager
from src.compose.visualization import Visualization
from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("cli_compose")


@click.group(name="compose")
@click.pass_context
def compose(ctx):
    """Manage Docker Compose files."""
    # Initialize compose managers
    if not hasattr(ctx.obj, "compose_discovery"):
        config = get_config("docker.compose")
        ctx.obj.compose_discovery = ComposeDiscovery(config)
        ctx.obj.compose_parser = ComposeParser(config)
        ctx.obj.change_manager = ChangeManager(config)
        ctx.obj.template_manager = TemplateManager(config)
        ctx.obj.visualization = Visualization(config)
        ctx.obj.compose_operations = ComposeOperations(config)


@compose.command("list")
@click.option("--recursive", "-r", is_flag=True, help="Search recursively")
@click.option(
    "--path", "-p", multiple=True, help="Paths to search for Docker Compose files"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_obj
def list_compose_files(obj, recursive, path, format):
    """List Docker Compose files."""
    logger.info("Listing Docker Compose files")

    # Discover Docker Compose files
    paths = list(path) if path else None
    compose_files = obj.compose_discovery.discover_files(
        paths=paths, recursive=recursive, include_common_locations=True
    )

    if not compose_files:
        click.echo("No Docker Compose files found")
        return

    if format == "json":
        # Output as JSON
        result = []
        for file_path, file_info in compose_files.items():
            result.append(
                {
                    "path": file_path,
                    "version": file_info.version,
                    "services": file_info.services,
                    "last_modified": file_info.last_modified,
                    "size": file_info.size,
                }
            )
        click.echo(json.dumps(result, indent=2))
    else:
        # Output as table
        headers = ["PATH", "VERSION", "SERVICES", "LAST MODIFIED", "SIZE"]
        rows = []

        for file_path, file_info in compose_files.items():
            # Format last modified time
            import datetime

            last_modified = datetime.datetime.fromtimestamp(
                file_info.last_modified
            ).strftime("%Y-%m-%d %H:%M:%S")

            # Format size
            size = file_info.size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f}KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f}MB"

            rows.append(
                [
                    file_path,
                    file_info.version or "N/A",
                    ", ".join(file_info.services) if file_info.services else "None",
                    last_modified,
                    size_str,
                ]
            )

        # Calculate column widths
        widths = [
            max(len(str(row[i])) for row in rows + [headers])
            for i in range(len(headers))
        ]

        # Print headers
        header_row = " ".join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
        click.secho(header_row, fg="blue", bold=True)

        # Print rows
        for row in rows:
            row_str = " ".join(
                f"{str(row[i]):<{widths[i]}}" for i in range(len(headers))
            )
            click.echo(row_str)


@compose.command("validate")
@click.argument("file", type=click.Path(exists=True))
@click.pass_obj
def validate_compose_file(obj, file):
    """Validate a Docker Compose file."""
    logger.info(f"Validating Docker Compose file: {file}")

    # Validate using Docker Compose CLI
    is_valid, errors = obj.compose_operations.validate_compose_file(file)

    if is_valid:
        click.secho(f"Docker Compose file {file} is valid", fg="green")
    else:
        click.secho(f"Docker Compose file {file} is invalid:", fg="red")
        for error in errors:
            click.echo(f"- {error}")

    # Validate using schema
    try:
        compose_data = obj.compose_parser.parse_file(file)
        schema_errors = obj.compose_parser.validate(compose_data)

        if schema_errors:
            click.secho("\nSchema validation errors:", fg="yellow")
            for error in schema_errors:
                click.echo(f"- {error}")
        else:
            click.secho("\nSchema validation passed", fg="green")
    except Exception as e:
        click.secho(f"\nError parsing Docker Compose file: {str(e)}", fg="red")


@compose.command("show")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format",
)
@click.pass_obj
def show_compose_file(obj, file, format):
    """Show the contents of a Docker Compose file."""
    logger.info(f"Showing Docker Compose file: {file}")

    try:
        # Parse Docker Compose file
        compose_data = obj.compose_parser.parse_file(file)

        # Output in requested format
        if format == "json":
            click.echo(json.dumps(compose_data, indent=2))
        else:
            click.echo(yaml.dump(compose_data, default_flow_style=False))
    except Exception as e:
        click.secho(f"Error parsing Docker Compose file: {str(e)}", fg="red")


@compose.command("up")
@click.argument("file", type=click.Path(exists=True))
@click.option("--service", "-s", multiple=True, help="Service to start")
@click.option("--detach", "-d", is_flag=True, default=True, help="Run in detached mode")
@click.option("--build", "-b", is_flag=True, help="Build images before starting")
@click.option("--validate", "-v", is_flag=True, help="Validate before starting")
@click.pass_obj
def up_compose_file(obj, file, service, detach, build, validate):
    """Start services defined in a Docker Compose file."""
    logger.info(f"Starting Docker Compose services from {file}")

    # Validate if requested
    if validate:
        is_valid, errors = obj.compose_operations.validate_compose_file(file)
        if not is_valid:
            click.secho(f"Docker Compose file {file} is invalid:", fg="red")
            for error in errors:
                click.echo(f"- {error}")
            if not click.confirm("Continue anyway?"):
                return

    # Start services
    services = list(service) if service else None
    success, output = obj.compose_operations.up(
        file, services=services, detach=detach, build=build
    )

    if success:
        click.secho("Docker Compose services started successfully", fg="green")

        # Show running containers
        success, ps_output = obj.compose_operations.ps(file)
        if success:
            click.echo("\nRunning containers:")
            click.echo(ps_output)
    else:
        click.secho("Failed to start Docker Compose services:", fg="red")
        click.echo(output)


@compose.command("down")
@click.argument("file", type=click.Path(exists=True))
@click.option("--volumes", "-v", is_flag=True, help="Remove volumes")
@click.option(
    "--remove-orphans",
    is_flag=True,
    default=True,
    help="Remove containers for services not defined in the Compose file",
)
@click.pass_obj
def down_compose_file(obj, file, volumes, remove_orphans):
    """Stop services defined in a Docker Compose file."""
    logger.info(f"Stopping Docker Compose services from {file}")

    # Stop services
    success, output = obj.compose_operations.down(
        file, volumes=volumes, remove_orphans=remove_orphans
    )

    if success:
        click.secho("Docker Compose services stopped successfully", fg="green")
    else:
        click.secho("Failed to stop Docker Compose services:", fg="red")
        click.echo(output)


@compose.command("restart")
@click.argument("file", type=click.Path(exists=True))
@click.option("--service", "-s", multiple=True, help="Service to restart")
@click.option(
    "--controlled",
    "-c",
    is_flag=True,
    help="Perform controlled restart with health checks",
)
@click.pass_obj
def restart_compose_file(obj, file, service, controlled):
    """Restart services defined in a Docker Compose file."""
    logger.info(f"Restarting Docker Compose services from {file}")

    services = list(service) if service else None

    if controlled:
        # Perform controlled restart
        success, health_status = obj.compose_operations.controlled_restart(
            file, services=services
        )

        if success:
            click.secho("Docker Compose services restarted successfully", fg="green")
            click.echo("\nHealth status:")
            for service_name, status in health_status.items():
                if status == "healthy":
                    color = "green"
                elif status == "unhealthy":
                    color = "red"
                else:
                    color = "yellow"
                click.secho(f"{service_name}: {status}", fg=color)
        else:
            click.secho("Failed to restart Docker Compose services", fg="red")
            click.echo("\nHealth status:")
            for service_name, status in health_status.items():
                if status == "healthy":
                    color = "green"
                elif status == "unhealthy":
                    color = "red"
                else:
                    color = "yellow"
                click.secho(f"{service_name}: {status}", fg=color)
    else:
        # Perform regular restart
        success, output = obj.compose_operations.restart(file, services=services)

        if success:
            click.secho("Docker Compose services restarted successfully", fg="green")
        else:
            click.secho("Failed to restart Docker Compose services:", fg="red")
            click.echo(output)


@compose.command("logs")
@click.argument("file", type=click.Path(exists=True))
@click.option("--service", "-s", multiple=True, help="Service to get logs for")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option(
    "--tail",
    "-n",
    default="all",
    help="Number of lines to show from the end of the logs",
)
@click.pass_obj
def logs_compose_file(obj, file, service, follow, tail):
    """Get logs for services defined in a Docker Compose file."""
    logger.info(f"Getting logs for Docker Compose services from {file}")

    services = list(service) if service else None
    success, output = obj.compose_operations.logs(
        file, services=services, follow=follow, tail=tail
    )

    if success:
        click.echo(output)
    else:
        click.secho("Failed to get logs for Docker Compose services:", fg="red")
        click.echo(output)


@compose.command("ps")
@click.argument("file", type=click.Path(exists=True))
@click.option("--service", "-s", multiple=True, help="Service to list")
@click.pass_obj
def ps_compose_file(obj, file, service):
    """List containers for services defined in a Docker Compose file."""
    logger.info(f"Listing containers for Docker Compose services from {file}")

    services = list(service) if service else None
    success, output = obj.compose_operations.ps(file, services=services)

    if success:
        click.echo(output)
    else:
        click.secho("Failed to list containers for Docker Compose services:", fg="red")
        click.echo(output)


@compose.command("exec")
@click.argument("file", type=click.Path(exists=True))
@click.argument("service")
@click.argument("command", nargs=-1)
@click.pass_obj
def exec_compose_file(obj, file, service, command):
    """Execute a command in a running container."""
    command_str = " ".join(command)
    logger.info(
        f"Executing command in Docker Compose service {service} from {file}: {command_str}"
    )

    success, output = obj.compose_operations.exec(file, service, command_str)

    if success:
        click.echo(output)
    else:
        click.secho("Failed to execute command in Docker Compose service:", fg="red")
        click.echo(output)


@compose.command("health")
@click.argument("file", type=click.Path(exists=True))
@click.option("--service", "-s", multiple=True, help="Service to check health for")
@click.pass_obj
def health_compose_file(obj, file, service):
    """Check the health status of services defined in a Docker Compose file."""
    logger.info(f"Checking health status for Docker Compose services from {file}")

    services = list(service) if service else None
    health_status = obj.compose_operations.check_health(file, services=services)

    if not health_status:
        click.echo("No health status available")
        return

    click.secho("Health status:", fg="blue", bold=True)
    for service_name, status in health_status.items():
        if status == "healthy":
            color = "green"
        elif status == "unhealthy":
            color = "red"
        else:
            color = "yellow"
        click.secho(f"{service_name}: {status}", fg=color)


@compose.command("config")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format",
)
@click.pass_obj
def config_compose_file(obj, file, format):
    """Get the resolved Docker Compose configuration."""
    logger.info(f"Getting resolved Docker Compose configuration from {file}")

    success, config_dict = obj.compose_operations.config(file)

    if success:
        if format == "json":
            click.echo(json.dumps(config_dict, indent=2))
        else:
            click.echo(yaml.dump(config_dict, default_flow_style=False))
    else:
        click.secho("Failed to get Docker Compose configuration", fg="red")


@compose.command("backup")
@click.argument("file", type=click.Path(exists=True))
@click.option("--description", "-d", help="Backup description")
@click.pass_obj
def backup_compose_file(obj, file, description):
    """Create a backup of a Docker Compose file."""
    logger.info(f"Creating backup of Docker Compose file {file}")

    try:
        backup_path = obj.change_manager.backup_file(file, description=description)
        click.secho(f"Backup created at {backup_path}", fg="green")
    except Exception as e:
        click.secho(f"Failed to create backup: {str(e)}", fg="red")


@compose.command("history")
@click.argument("file", type=click.Path(exists=True))
@click.pass_obj
def history_compose_file(obj, file):
    """Show backup history for a Docker Compose file."""
    logger.info(f"Showing backup history for Docker Compose file {file}")

    history = obj.change_manager.get_backup_history(file)

    if not history:
        click.echo("No backup history found")
        return

    click.secho(f"Backup history for {file}:", fg="blue", bold=True)
    for i, entry in enumerate(history, 1):
        timestamp = entry["timestamp"]
        backup_path = entry["backup_path"]
        description = entry["description"]
        is_restore = entry.get("is_restore", False)

        if is_restore:
            click.secho(f"{i}. {timestamp} - {description}", fg="yellow")
        else:
            click.echo(f"{i}. {timestamp} - {description}")
        click.echo(f"   Path: {backup_path}")


@compose.command("restore")
@click.argument("file", type=click.Path(exists=True))
@click.argument("backup_path", type=click.Path(exists=True))
@click.pass_obj
def restore_compose_file(obj, file, backup_path):
    """Restore a Docker Compose file from a backup."""
    logger.info(f"Restoring Docker Compose file {file} from backup {backup_path}")

    try:
        obj.change_manager.restore_from_backup(file, backup_path)
        click.secho(f"Restored {file} from backup {backup_path}", fg="green")
    except Exception as e:
        click.secho(f"Failed to restore from backup: {str(e)}", fg="red")


@compose.command("diff")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--backup", "-b", help="Backup file to compare with (defaults to latest backup)"
)
@click.pass_obj
def diff_compose_file(obj, file, backup):
    """Show differences between a Docker Compose file and its backup."""
    logger.info(f"Showing differences for Docker Compose file {file}")

    try:
        diff = obj.change_manager.generate_diff(file, backup_path=backup)

        if not diff:
            click.echo("No differences found")
            return

        click.echo(diff)
    except Exception as e:
        click.secho(f"Failed to generate diff: {str(e)}", fg="red")


@compose.command("templates")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_obj
def list_templates(obj, format):
    """List available Docker Compose templates."""
    logger.info("Listing Docker Compose templates")

    templates = obj.template_manager.list_templates()

    if not templates:
        click.echo("No templates found")
        return

    if format == "json":
        result = []
        for template_name in templates:
            template = obj.template_manager.get_template(template_name)
            result.append(
                {
                    "name": template_name,
                    "services": list(template.get("services", {}).keys()),
                    "variables": list(
                        obj.template_manager.extract_template_variables(template)
                    ),
                }
            )
        click.echo(json.dumps(result, indent=2))
    else:
        click.secho("Available templates:", fg="blue", bold=True)
        for template_name in templates:
            template = obj.template_manager.get_template(template_name)
            services = list(template.get("services", {}).keys())
            variables = obj.template_manager.extract_template_variables(template)

            click.secho(f"\n{template_name}", fg="green")
            if services:
                click.echo(f"Services: {', '.join(services)}")
            if variables:
                click.echo(f"Variables: {', '.join(variables)}")


@compose.command("create-template")
@click.argument("file", type=click.Path(exists=True))
@click.argument("service")
@click.argument("template_name")
@click.pass_obj
def create_template(obj, file, service, template_name):
    """Create a template from a service in a Docker Compose file."""
    logger.info(f"Creating template {template_name} from service {service} in {file}")

    try:
        # Parse Docker Compose file
        compose_data = obj.compose_parser.parse_file(file)

        # Create template
        template_path = obj.template_manager.create_template_from_service(
            compose_data, service, template_name
        )

        click.secho(f"Template {template_name} created at {template_path}", fg="green")
    except Exception as e:
        click.secho(f"Failed to create template: {str(e)}", fg="red")


@compose.command("apply-template")
@click.argument("template_name")
@click.argument("output_file")
@click.option(
    "--variable", "-v", multiple=True, help="Template variable in the format name=value"
)
@click.pass_obj
def apply_template(obj, template_name, output_file, variable):
    """Apply a template to create a Docker Compose file."""
    logger.info(f"Applying template {template_name} to create {output_file}")

    try:
        # Parse variables
        variables = {}
        for var in variable:
            if "=" in var:
                name, value = var.split("=", 1)
                variables[name] = value
            else:
                click.secho(f"Invalid variable format: {var}", fg="red")
                return

        # Create Docker Compose file from template
        compose_data = obj.template_manager.create_compose_from_template(
            template_name, variables
        )

        # Validate template
        errors = obj.template_manager.validate_template(compose_data)
        if errors:
            click.secho("Template validation errors:", fg="red")
            for error in errors:
                click.echo(f"- {error}")
            if not click.confirm("Continue anyway?"):
                return

        # Write to file
        with open(output_file, "w") as f:
            yaml.dump(compose_data, f, default_flow_style=False)

        click.secho(f"Docker Compose file created at {output_file}", fg="green")
    except Exception as e:
        click.secho(f"Failed to apply template: {str(e)}", fg="red")


@compose.command("visualize")
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--type",
    "-t",
    type=click.Choice(["dependency", "network", "volume", "resource"]),
    default="dependency",
    help="Visualization type",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["mermaid", "dot", "json"]),
    default="mermaid",
    help="Output format",
)
@click.option("--output", "-o", help="Output file")
@click.pass_obj
def visualize_compose_file(obj, file, type, format, output):
    """Generate a visualization of a Docker Compose file."""
    logger.info(f"Generating {type} visualization for Docker Compose file {file}")

    try:
        # Parse Docker Compose file
        compose_data = obj.compose_parser.parse_file(file)

        # Generate visualization
        if type == "dependency":
            visualization = obj.visualization.generate_dependency_graph(
                compose_data, output_format=format
            )
        elif type == "network":
            visualization = obj.visualization.generate_network_graph(
                compose_data, output_format=format
            )
        elif type == "volume":
            visualization = obj.visualization.generate_volume_graph(
                compose_data, output_format=format
            )
        elif type == "resource":
            visualization = obj.visualization.generate_resource_chart(
                compose_data, output_format=format
            )

        # Save to file if requested
        if output:
            output_path = obj.visualization.save_visualization(
                visualization, output, format
            )
            click.secho(f"Visualization saved to {output_path}", fg="green")
        else:
            # Print to console
            if format == "mermaid":
                click.secho("```mermaid", fg="blue")
                click.echo(visualization)
                click.secho("```", fg="blue")
            else:
                click.echo(visualization)
    except Exception as e:
        click.secho(f"Failed to generate visualization: {str(e)}", fg="red")


@compose.command("run")
@click.argument("file", type=click.Path(exists=True))
@click.argument("command", nargs=-1)
@click.pass_obj
def run_compose_command(obj, file, command):
    """Run a custom Docker Compose command."""
    command_str = " ".join(command)
    logger.info(f"Running Docker Compose command: {command_str}")

    success, output = obj.compose_operations.run_command(file, command_str)

    if success:
        click.echo(output)
    else:
        click.secho("Failed to run Docker Compose command:", fg="red")
        click.echo(output)
