"""
Command-line interface for Docker backup features.

This module provides a command-line interface for Docker container, image,
and volume backup, restore, export, and import.
"""

import argparse
import json
import logging
import os
import sys
from typing import List, Optional, Dict, Any

from src.utils.logging_manager import get_logger
from src.backup import get_backup_manager, get_export_import_manager

# Set up logging
logger = get_logger("cli_backup")


def setup_backup_parser(subparsers):
    """Set up the backup command parser."""
    parser = subparsers.add_parser(
        "backup",
        help="Backup Docker containers, images, and volumes"
    )
    
    # Set up subparsers for backup commands
    backup_subparsers = parser.add_subparsers(
        title="backup commands",
        dest="backup_command",
        help="Backup command to run"
    )
    backup_subparsers.required = True
    
    # Backup container
    container_parser = backup_subparsers.add_parser(
        "container",
        help="Backup a Docker container"
    )
    container_parser.add_argument(
        "container",
        help="ID or name of the container to backup"
    )
    container_parser.add_argument(
        "--name",
        help="Name of the backup. If not provided, a name will be generated."
    )
    container_parser.add_argument(
        "--no-volumes",
        action="store_true",
        help="Don't include volumes in the backup"
    )
    container_parser.add_argument(
        "--include-image",
        action="store_true",
        help="Include the container's image in the backup"
    )
    container_parser.set_defaults(func=handle_backup_container)
    
    # List backups
    list_parser = backup_subparsers.add_parser(
        "list",
        help="List all backups"
    )
    list_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Output format"
    )
    list_parser.set_defaults(func=handle_list_backups)
    
    # Show backup
    show_parser = backup_subparsers.add_parser(
        "show",
        help="Show backup details"
    )
    show_parser.add_argument(
        "backup_id",
        help="ID of the backup to show"
    )
    show_parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="table",
        help="Output format"
    )
    show_parser.set_defaults(func=handle_show_backup)
    
    # Delete backup
    delete_parser = backup_subparsers.add_parser(
        "delete",
        help="Delete a backup"
    )
    delete_parser.add_argument(
        "backup_id",
        help="ID of the backup to delete"
    )
    delete_parser.set_defaults(func=handle_delete_backup)


def setup_restore_parser(subparsers):
    """Set up the restore command parser."""
    parser = subparsers.add_parser(
        "restore",
        help="Restore Docker containers, images, and volumes from backup"
    )
    parser.add_argument(
        "backup_id",
        help="ID of the backup to restore"
    )
    parser.add_argument(
        "--name",
        help="Name for the restored container. If not provided, a name will be generated."
    )
    parser.add_argument(
        "--no-volumes",
        action="store_true",
        help="Don't restore volumes"
    )
    parser.add_argument(
        "--no-image",
        action="store_true",
        help="Don't restore the container's image"
    )
    parser.set_defaults(func=handle_restore)


def setup_export_parser(subparsers):
    """Set up the export command parser."""
    parser = subparsers.add_parser(
        "export",
        help="Export Docker containers, images, and volumes to files"
    )
    
    # Set up subparsers for export commands
    export_subparsers = parser.add_subparsers(
        title="export commands",
        dest="export_command",
        help="Export command to run"
    )
    export_subparsers.required = True
    
    # Export image
    image_parser = export_subparsers.add_parser(
        "image",
        help="Export a Docker image to a file"
    )
    image_parser.add_argument(
        "image",
        help="ID or name of the image to export"
    )
    image_parser.add_argument(
        "--output",
        help="Path to save the exported image. If not provided, a default path will be used."
    )
    image_parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Don't compress the exported image"
    )
    image_parser.set_defaults(func=handle_export_image)
    
    # Export container
    container_parser = export_subparsers.add_parser(
        "container",
        help="Export a Docker container to a file"
    )
    container_parser.add_argument(
        "container",
        help="ID or name of the container to export"
    )
    container_parser.add_argument(
        "--output",
        help="Path to save the exported container. If not provided, a default path will be used."
    )
    container_parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Don't compress the exported container"
    )
    container_parser.set_defaults(func=handle_export_container)
    
    # Export volume
    volume_parser = export_subparsers.add_parser(
        "volume",
        help="Export a Docker volume to a file"
    )
    volume_parser.add_argument(
        "volume",
        help="Name of the volume to export"
    )
    volume_parser.add_argument(
        "--output",
        help="Path to save the exported volume. If not provided, a default path will be used."
    )
    volume_parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Don't compress the exported volume"
    )
    volume_parser.set_defaults(func=handle_export_volume)


def setup_import_parser(subparsers):
    """Set up the import command parser."""
    parser = subparsers.add_parser(
        "import",
        help="Import Docker containers, images, and volumes from files"
    )
    
    # Set up subparsers for import commands
    import_subparsers = parser.add_subparsers(
        title="import commands",
        dest="import_command",
        help="Import command to run"
    )
    import_subparsers.required = True
    
    # Import image
    image_parser = import_subparsers.add_parser(
        "image",
        help="Import a Docker image from a file"
    )
    image_parser.add_argument(
        "file",
        help="Path to the image file to import"
    )
    image_parser.add_argument(
        "--repository",
        help="Repository name for the imported image"
    )
    image_parser.add_argument(
        "--tag",
        help="Tag for the imported image"
    )
    image_parser.set_defaults(func=handle_import_image)
    
    # Import container
    container_parser = import_subparsers.add_parser(
        "container",
        help="Import a Docker container from a file"
    )
    container_parser.add_argument(
        "file",
        help="Path to the container file to import"
    )
    container_parser.add_argument(
        "--repository",
        help="Repository name for the imported container image"
    )
    container_parser.add_argument(
        "--tag",
        help="Tag for the imported container image"
    )
    container_parser.add_argument(
        "--name",
        help="Name for the imported container"
    )
    container_parser.set_defaults(func=handle_import_container)
    
    # Import volume
    volume_parser = import_subparsers.add_parser(
        "volume",
        help="Import a Docker volume from a file"
    )
    volume_parser.add_argument(
        "file",
        help="Path to the volume file to import"
    )
    volume_parser.add_argument(
        "--name",
        help="Name for the imported volume"
    )
    volume_parser.set_defaults(func=handle_import_volume)


def handle_backup_container(args):
    """Handle the backup container command."""
    try:
        # Get the backup manager
        backup_manager = get_backup_manager()
        
        # Backup container
        result = backup_manager.backup_container(
            container_id_or_name=args.container,
            include_volumes=not args.no_volumes,
            include_image=args.include_image,
            backup_name=args.name
        )
        
        print(f"Container backup completed: {result['backup_id']}")
        print(f"Backup path: {result['backup_path']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error backing up container: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_list_backups(args):
    """Handle the list backups command."""
    try:
        # Get the backup manager
        backup_manager = get_backup_manager()
        
        # List backups
        backups = backup_manager.list_backups()
        
        if args.format == "json":
            print(json.dumps(backups, indent=2))
        else:
            # Print table
            if not backups:
                print("No backups found.")
                return 0
            
            # Print header
            print(f"{'ID':<30} {'Container':<30} {'Timestamp':<25} {'Volumes':<10} {'Image':<10}")
            print("-" * 105)
            
            # Print backups
            for backup in backups:
                print(
                    f"{backup.get('backup_id', ''):<30} "
                    f"{backup.get('container_name', ''):<30} "
                    f"{backup.get('timestamp', ''):<25} "
                    f"{'Yes' if backup.get('include_volumes') else 'No':<10} "
                    f"{'Yes' if backup.get('include_image') else 'No':<10}"
                )
        
        return 0
    
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_show_backup(args):
    """Handle the show backup command."""
    try:
        # Get the backup manager
        backup_manager = get_backup_manager()
        
        # Get backup
        backup = backup_manager.get_backup(args.backup_id)
        
        if args.format == "json":
            print(json.dumps(backup, indent=2))
        else:
            # Print backup details
            print(f"Backup ID: {backup.get('backup_id', '')}")
            print(f"Container ID: {backup.get('container_id', '')}")
            print(f"Container Name: {backup.get('container_name', '')}")
            print(f"Timestamp: {backup.get('timestamp', '')}")
            print(f"Backup Path: {backup.get('backup_path', '')}")
            print(f"Include Volumes: {'Yes' if backup.get('include_volumes') else 'No'}")
            print(f"Include Image: {'Yes' if backup.get('include_image') else 'No'}")
            
            # Print volumes
            if backup.get('include_volumes') and backup.get('volumes'):
                print("\nVolumes:")
                for volume in backup.get('volumes', []):
                    print(f"  {volume.get('volume_name', '')}: {volume.get('mount_point', '')}")
            
            # Print image
            if backup.get('include_image') and backup.get('image'):
                print("\nImage:")
                image = backup.get('image', {})
                print(f"  ID: {image.get('image_id', '')}")
                print(f"  Name: {image.get('image_name', '')}")
                print(f"  Tags: {', '.join(image.get('image_tags', []))}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error showing backup: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_delete_backup(args):
    """Handle the delete backup command."""
    try:
        # Get the backup manager
        backup_manager = get_backup_manager()
        
        # Delete backup
        result = backup_manager.delete_backup(args.backup_id)
        
        if result:
            print(f"Backup {args.backup_id} deleted.")
        else:
            print(f"Backup {args.backup_id} not found.")
        
        return 0 if result else 1
    
    except Exception as e:
        logger.error(f"Error deleting backup: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_restore(args):
    """Handle the restore command."""
    try:
        # Get the backup manager
        backup_manager = get_backup_manager()
        
        # Restore container
        result = backup_manager.restore_container(
            backup_id_or_path=args.backup_id,
            restore_volumes=not args.no_volumes,
            restore_image=not args.no_image,
            new_container_name=args.name
        )
        
        print(f"Container restored: {result['restored_container_name']} ({result['restored_container_id']})")
        
        # Print restored volumes
        if not args.no_volumes and result.get('restored_volumes'):
            print("\nRestored volumes:")
            for original, restored in result.get('restored_volumes', {}).items():
                print(f"  {original} -> {restored}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error restoring container: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_export_image(args):
    """Handle the export image command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Export image
        result = export_import_manager.export_image(
            image_id_or_name=args.image,
            output_path=args.output,
            compress=not args.no_compress
        )
        
        print(f"Image exported to: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error exporting image: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_export_container(args):
    """Handle the export container command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Export container
        result = export_import_manager.export_container(
            container_id_or_name=args.container,
            output_path=args.output,
            compress=not args.no_compress
        )
        
        print(f"Container exported to: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error exporting container: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_export_volume(args):
    """Handle the export volume command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Export volume
        result = export_import_manager.export_volume(
            volume_name=args.volume,
            output_path=args.output,
            compress=not args.no_compress
        )
        
        print(f"Volume exported to: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error exporting volume: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_import_image(args):
    """Handle the import image command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Import image
        result = export_import_manager.import_image(
            input_path=args.file,
            repository=args.repository,
            tag=args.tag
        )
        
        print(f"Image imported: {result}")
        
        if args.repository and args.tag:
            print(f"Image tagged as: {args.repository}:{args.tag}")
        elif args.repository:
            print(f"Image tagged as: {args.repository}:latest")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error importing image: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_import_container(args):
    """Handle the import container command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Import container
        result = export_import_manager.import_container(
            input_path=args.file,
            repository=args.repository,
            tag=args.tag,
            container_name=args.name
        )
        
        print(f"Container imported: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error importing container: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def handle_import_volume(args):
    """Handle the import volume command."""
    try:
        # Get the export/import manager
        export_import_manager = get_export_import_manager()
        
        # Import volume
        result = export_import_manager.import_volume(
            input_path=args.file,
            volume_name=args.name
        )
        
        print(f"Volume imported: {result}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error importing volume: {str(e)}")
        print(f"Error: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="DockerForge Backup CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Set up subparsers
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Command to run"
    )
    subparsers.required = True
    
    # Set up command parsers
    setup_backup_parser(subparsers)
    setup_restore_parser(subparsers)
    setup_export_parser(subparsers)
    setup_import_parser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
