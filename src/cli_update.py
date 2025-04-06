"""
DockerForge Update CLI

This module provides a command-line interface for the DockerForge update system.
"""

import logging
import os
import sys
from typing import Optional

import click
from tabulate import tabulate

from src.config.config_manager import ConfigManager
from src.platforms.platform_adapter import get_platform_adapter
from src.update.update_manager import UpdateManager
from src.update.version_checker import VersionChecker
from src.utils.logging_manager import get_logger

logger = get_logger(__name__)


@click.group(name="update")
@click.pass_context
def update_cli(ctx):
    """
    Update management commands.
    """
    # Initialize the configuration manager
    config_manager = ConfigManager()

    # Initialize the platform adapter
    platform_adapter = get_platform_adapter()

    # Initialize the version checker
    version_checker = VersionChecker(config_manager)

    # Initialize the update manager
    update_manager = UpdateManager(config_manager, platform_adapter)

    # Store in context
    ctx.obj = {
        "config_manager": config_manager,
        "platform_adapter": platform_adapter,
        "version_checker": version_checker,
        "update_manager": update_manager,
    }


@update_cli.command()
@click.option("--force", is_flag=True, help="Force check even if cache is valid")
@click.pass_context
def check(ctx, force):
    """
    Check if updates are available.
    """
    version_checker = ctx.obj["version_checker"]

    current_version = version_checker._get_current_version()
    click.echo(f"Current version: {current_version}")

    click.echo("Checking for updates...")
    update_available, latest_version, release_url = version_checker.check_for_updates(
        force=force
    )

    if update_available:
        click.echo(f"Update available: {latest_version}")
        click.echo(f"Release URL: {release_url}")

        # Get release notes
        release_notes = version_checker.get_release_notes()
        if release_notes:
            click.echo("\nRelease Notes:")
            click.echo("-" * 40)
            click.echo(release_notes)
            click.echo("-" * 40)

        click.echo("\nTo update, run: dockerforge update apply")
    else:
        click.echo("You are already running the latest version.")


@update_cli.command()
@click.option("--version", help="Specific version to update to (default: latest)")
@click.option(
    "--force", is_flag=True, help="Force update even if already at latest version"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def apply(ctx, version, force, yes):
    """
    Apply available updates.
    """
    update_manager = ctx.obj["update_manager"]
    version_checker = ctx.obj["version_checker"]

    current_version = version_checker._get_current_version()
    click.echo(f"Current version: {current_version}")

    if not version:
        # Check for updates
        update_available, latest_version, _ = version_checker.check_for_updates()

        if not update_available and not force:
            click.echo("You are already running the latest version.")
            return

        version = latest_version

    click.echo(f"Preparing to update to version {version}")

    # Confirm update
    if not yes:
        if not click.confirm("Do you want to continue with the update?"):
            click.echo("Update cancelled.")
            return

    click.echo("Creating backup before updating...")
    click.echo("Applying update...")

    success = update_manager.update(version=version, force=force)

    if success:
        click.echo(f"Successfully updated to version {version}")
    else:
        click.echo("Update failed. See logs for details.")


@update_cli.command()
@click.option(
    "--backup-id", help="Specific backup ID to rollback to (default: most recent)"
)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def rollback(ctx, backup_id, yes):
    """
    Rollback to a previous version.
    """
    update_manager = ctx.obj["update_manager"]

    # List available backups
    backups = update_manager.list_backups()

    if not backups:
        click.echo("No backups available for rollback.")
        return

    # Display available backups
    click.echo("Available backups:")

    table_data = []
    for i, backup in enumerate(backups):
        table_data.append(
            [
                i + 1,
                backup["id"],
                backup["timestamp"],
                backup["version"],
                backup["backup_type"],
            ]
        )

    click.echo(
        tabulate(
            table_data,
            headers=["#", "Backup ID", "Timestamp", "Version", "Type"],
            tablefmt="simple",
        )
    )

    # If no backup ID specified, use the most recent
    if not backup_id:
        if not yes:
            click.echo("\nNo backup ID specified. Will use the most recent backup.")
            if not click.confirm("Do you want to continue?"):
                click.echo("Rollback cancelled.")
                return
    else:
        # Verify the backup ID exists
        if not any(b["id"] == backup_id for b in backups):
            click.echo(f"Backup ID '{backup_id}' not found.")
            return

    click.echo("Rolling back...")
    success = update_manager.rollback(backup_id)

    if success:
        click.echo("Rollback completed successfully.")
    else:
        click.echo("Rollback failed. See logs for details.")


@update_cli.command(name="list-backups")
@click.pass_context
def list_backups(ctx):
    """
    List available backups.
    """
    update_manager = ctx.obj["update_manager"]

    backups = update_manager.list_backups()

    if not backups:
        click.echo("No backups available.")
        return

    table_data = []
    for i, backup in enumerate(backups):
        table_data.append(
            [
                i + 1,
                backup["id"],
                backup["timestamp"],
                backup["version"],
                backup["backup_type"],
                backup["path"],
            ]
        )

    click.echo(
        tabulate(
            table_data,
            headers=["#", "Backup ID", "Timestamp", "Version", "Type", "Path"],
            tablefmt="simple",
        )
    )


def main():
    """
    Main entry point for the CLI.
    """
    try:
        update_cli(obj={})
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
