"""
Command-line interface for checkpoint functionality.

This module provides a command-line interface for creating, comparing,
and restoring Docker containers, configurations and settings via checkpoints.
"""

import argparse
import datetime
import json
import os
import sys
from typing import Any, Dict, List, Optional

from src.backup.checkpoint_manager import get_checkpoint_manager
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("cli.checkpoint")


def setup_checkpoint_parser(subparsers):
    """Set up the checkpoint command parser."""
    parser = subparsers.add_parser(
        "checkpoint", help="Create, compare, and restore Docker state via checkpoints"
    )

    checkpoint_subparsers = parser.add_subparsers(dest="checkpoint_command")

    # Create checkpoint command
    create_parser = checkpoint_subparsers.add_parser(
        "create", help="Create a new checkpoint"
    )
    create_parser.add_argument("name", help="Name of the checkpoint")
    create_parser.add_argument("--description", help="Description of the checkpoint")
    create_parser.add_argument(
        "--no-containers",
        action="store_true",
        help="Don't include containers in the checkpoint",
    )
    create_parser.add_argument(
        "--no-volumes",
        action="store_true",
        help="Don't include volumes in the checkpoint",
    )
    create_parser.add_argument(
        "--no-configs",
        action="store_true",
        help="Don't include configuration files in the checkpoint",
    )
    create_parser.set_defaults(func=handle_create_checkpoint)

    # List checkpoints command
    list_parser = checkpoint_subparsers.add_parser("list", help="List all checkpoints")
    list_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    list_parser.set_defaults(func=handle_list_checkpoints)

    # Show checkpoint command
    show_parser = checkpoint_subparsers.add_parser(
        "show", help="Show checkpoint details"
    )
    show_parser.add_argument("checkpoint_id", help="ID of the checkpoint to show")
    show_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    show_parser.set_defaults(func=handle_show_checkpoint)

    # Delete checkpoint command
    delete_parser = checkpoint_subparsers.add_parser(
        "delete", help="Delete a checkpoint"
    )
    delete_parser.add_argument("checkpoint_id", help="ID of the checkpoint to delete")
    delete_parser.set_defaults(func=handle_delete_checkpoint)

    # Compare checkpoints command
    compare_parser = checkpoint_subparsers.add_parser(
        "compare", help="Compare two checkpoints"
    )
    compare_parser.add_argument("checkpoint_id_1", help="ID of the first checkpoint")
    compare_parser.add_argument("checkpoint_id_2", help="ID of the second checkpoint")
    compare_parser.add_argument(
        "--no-containers", action="store_true", help="Don't compare containers"
    )
    compare_parser.add_argument(
        "--no-volumes", action="store_true", help="Don't compare volumes"
    )
    compare_parser.add_argument(
        "--no-configs", action="store_true", help="Don't compare configuration files"
    )
    compare_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    compare_parser.set_defaults(func=handle_compare_checkpoints)

    # Restore checkpoint command
    restore_parser = checkpoint_subparsers.add_parser(
        "restore", help="Restore from a checkpoint"
    )
    restore_parser.add_argument(
        "checkpoint_id", help="ID of the checkpoint to restore from"
    )
    restore_parser.add_argument(
        "--no-containers", action="store_true", help="Don't restore containers"
    )
    restore_parser.add_argument(
        "--with-volumes", action="store_true", help="Restore volumes (use with caution)"
    )
    restore_parser.add_argument(
        "--no-configs", action="store_true", help="Don't restore configuration files"
    )
    restore_parser.set_defaults(func=handle_restore_checkpoint)

    return parser


def handle_create_checkpoint(args):
    """Handle the create checkpoint command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # Create checkpoint
        result = checkpoint_manager.create_checkpoint(
            name=args.name,
            description=args.description,
            include_containers=not args.no_containers,
            include_volumes=not args.no_volumes,
            include_configs=not args.no_configs,
        )

        print(f"Checkpoint created: {result['checkpoint_id']}")
        print(f"Path: {result['checkpoint_path']}")

        # Print included items
        if "included_items" in result:
            print("\nIncluded items:")
            for item_type, count in result["included_items"].items():
                print(f"  {item_type.capitalize()}: {count}")

    except Exception as e:
        logger.error(f"Error creating checkpoint: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_list_checkpoints(args):
    """Handle the list checkpoints command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # List checkpoints
        checkpoints = checkpoint_manager.list_checkpoints()

        if args.json:
            print(json.dumps(checkpoints, indent=2))
            return

        if not checkpoints:
            print("No checkpoints found.")
            return

        print(f"Found {len(checkpoints)} checkpoints:")
        print()

        # Print table header
        print(
            f"{'ID':<40} {'Name':<20} {'Description':<30} {'Timestamp':<25} {'Items'}"
        )
        print("-" * 120)

        # Print each checkpoint
        for cp in checkpoints:
            checkpoint_id = cp.get("checkpoint_id", "")
            name = cp.get("name", "")
            description = cp.get("description", "")
            if description and len(description) > 30:
                description = description[:27] + "..."

            timestamp_str = cp.get("timestamp", "")
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp_str)
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                pass

            included_items = cp.get("included_items", {})
            items_str = ", ".join([f"{k}: {v}" for k, v in included_items.items()])

            print(
                f"{checkpoint_id:<40} {name:<20} {description:<30} {timestamp_str:<25} {items_str}"
            )

    except Exception as e:
        logger.error(f"Error listing checkpoints: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_show_checkpoint(args):
    """Handle the show checkpoint command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # Get checkpoint
        checkpoint = checkpoint_manager.get_checkpoint(args.checkpoint_id)

        if args.json:
            print(json.dumps(checkpoint, indent=2))
            return

        print(f"Checkpoint: {checkpoint.get('checkpoint_id')}")
        print(f"Name: {checkpoint.get('name')}")
        if checkpoint.get("description"):
            print(f"Description: {checkpoint.get('description')}")

        timestamp_str = checkpoint.get("timestamp", "")
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            pass

        print(f"Created: {timestamp_str}")
        print(f"Path: {checkpoint.get('checkpoint_path')}")

        print("\nIncludes:")
        print(
            f"  Containers: {'Yes' if checkpoint.get('include_containers') else 'No'}"
        )
        print(f"  Volumes: {'Yes' if checkpoint.get('include_volumes') else 'No'}")
        print(f"  Configs: {'Yes' if checkpoint.get('include_configs') else 'No'}")

        included_items = checkpoint.get("included_items", {})
        if included_items:
            print("\nIncluded items:")
            for item_type, count in included_items.items():
                print(f"  {item_type.capitalize()}: {count}")

    except Exception as e:
        logger.error(f"Error showing checkpoint: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_delete_checkpoint(args):
    """Handle the delete checkpoint command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # Get checkpoint for confirmation
        try:
            checkpoint = checkpoint_manager.get_checkpoint(args.checkpoint_id)
            checkpoint_name = checkpoint.get("name", args.checkpoint_id)
        except:
            print(f"Checkpoint not found: {args.checkpoint_id}")
            sys.exit(1)

        # Confirm deletion
        confirm = input(
            f"Are you sure you want to delete checkpoint '{checkpoint_name}' ({args.checkpoint_id})? [y/N] "
        )
        if confirm.lower() not in ["y", "yes"]:
            print("Deletion canceled.")
            return

        # Delete checkpoint
        result = checkpoint_manager.delete_checkpoint(args.checkpoint_id)

        if result:
            print(f"Checkpoint deleted: {args.checkpoint_id}")
        else:
            print(f"Failed to delete checkpoint: {args.checkpoint_id}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error deleting checkpoint: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_compare_checkpoints(args):
    """Handle the compare checkpoints command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # Compare checkpoints
        comparison = checkpoint_manager.compare_checkpoints(
            checkpoint_id_1=args.checkpoint_id_1,
            checkpoint_id_2=args.checkpoint_id_2,
            compare_containers=not args.no_containers,
            compare_volumes=not args.no_volumes,
            compare_configs=not args.no_configs,
        )

        if args.json:
            print(json.dumps(comparison, indent=2))
            return

        # Print comparison summary
        checkpoint1 = comparison.get("checkpoint1", {})
        checkpoint2 = comparison.get("checkpoint2", {})

        print(f"Comparing checkpoints:")
        print(f"  1: {checkpoint1.get('name')} ({args.checkpoint_id_1})")
        print(f"  2: {checkpoint2.get('name')} ({args.checkpoint_id_2})")

        summary = comparison.get("summary", {})
        print("\nSummary:")
        print(f"  Added: {summary.get('added', 0)}")
        print(f"  Removed: {summary.get('removed', 0)}")
        print(f"  Modified: {summary.get('modified', 0)}")
        print(f"  Unchanged: {summary.get('unchanged', 0)}")

        # Print container comparison
        if comparison.get("containers") is not None:
            container_comparison = comparison.get("containers", {})

            print("\nContainers:")
            print(f"  Added: {len(container_comparison.get('added', []))}")
            print(f"  Removed: {len(container_comparison.get('removed', []))}")
            print(f"  Modified: {len(container_comparison.get('modified', []))}")
            print(f"  Unchanged: {len(container_comparison.get('unchanged', []))}")

            # List added containers
            if container_comparison.get("added"):
                print("\n  Added containers:")
                for container in container_comparison.get("added", []):
                    print(f"    {container.get('name')} ({container.get('image')})")

            # List removed containers
            if container_comparison.get("removed"):
                print("\n  Removed containers:")
                for container in container_comparison.get("removed", []):
                    print(f"    {container.get('name')} ({container.get('image')})")

            # List modified containers
            if container_comparison.get("modified"):
                print("\n  Modified containers:")
                for container in container_comparison.get("modified", []):
                    name = container.get("name")
                    details = container_comparison.get("details", {}).get(name, {})

                    print(f"    {name}:")
                    if details.get("modified_values"):
                        for key, value in details.get("modified_values", {}).items():
                            print(
                                f"      {key}: {value.get('old')} -> {value.get('new')}"
                            )

        # Print volume comparison
        if comparison.get("volumes") is not None:
            volume_comparison = comparison.get("volumes", {})

            print("\nVolumes:")
            print(f"  Added: {len(volume_comparison.get('added', []))}")
            print(f"  Removed: {len(volume_comparison.get('removed', []))}")
            print(f"  Modified: {len(volume_comparison.get('modified', []))}")
            print(f"  Unchanged: {len(volume_comparison.get('unchanged', []))}")

            # List added volumes
            if volume_comparison.get("added"):
                print("\n  Added volumes:")
                for volume in volume_comparison.get("added", []):
                    print(f"    {volume.get('name')} ({volume.get('driver')})")

            # List removed volumes
            if volume_comparison.get("removed"):
                print("\n  Removed volumes:")
                for volume in volume_comparison.get("removed", []):
                    print(f"    {volume.get('name')} ({volume.get('driver')})")

        # Print config comparison
        if comparison.get("configs") is not None:
            config_comparison = comparison.get("configs", {})

            print("\nConfiguration files:")
            print(f"  Added: {len(config_comparison.get('added', []))}")
            print(f"  Removed: {len(config_comparison.get('removed', []))}")
            print(f"  Modified: {len(config_comparison.get('modified', []))}")
            print(f"  Unchanged: {len(config_comparison.get('unchanged', []))}")

            # List added config files
            if config_comparison.get("added"):
                print("\n  Added configuration files:")
                for config in config_comparison.get("added", []):
                    print(f"    {config.get('file_name')}")

            # List removed config files
            if config_comparison.get("removed"):
                print("\n  Removed configuration files:")
                for config in config_comparison.get("removed", []):
                    print(f"    {config.get('file_name')}")

            # List modified config files
            if config_comparison.get("modified"):
                print("\n  Modified configuration files:")
                for config in config_comparison.get("modified", []):
                    print(f"    {config.get('file_name')}")

                # Ask if user wants to see diffs
                if config_comparison.get("diffs"):
                    show_diffs = input("\nDo you want to see file diffs? [y/N] ")
                    if show_diffs.lower() in ["y", "yes"]:
                        for file_name, diff in config_comparison.get(
                            "diffs", {}
                        ).items():
                            print(f"\nDiff for {file_name}:")
                            print(diff)

    except Exception as e:
        logger.error(f"Error comparing checkpoints: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_restore_checkpoint(args):
    """Handle the restore checkpoint command."""
    try:
        checkpoint_manager = get_checkpoint_manager()

        # Get checkpoint for confirmation
        try:
            checkpoint = checkpoint_manager.get_checkpoint(args.checkpoint_id)
            checkpoint_name = checkpoint.get("name", args.checkpoint_id)
        except:
            print(f"Checkpoint not found: {args.checkpoint_id}")
            sys.exit(1)

        # Confirm restoration
        print(
            f"You are about to restore from checkpoint '{checkpoint_name}' ({args.checkpoint_id})."
        )
        print(
            f"This will potentially stop and recreate containers and modify configuration files."
        )
        if args.with_volumes:
            print(
                f"WARNING: Volume data will also be restored. This is a destructive operation."
            )

        confirm = input("Are you sure you want to continue? [y/N] ")
        if confirm.lower() not in ["y", "yes"]:
            print("Restoration canceled.")
            return

        # Restore checkpoint
        result = checkpoint_manager.restore_from_checkpoint(
            checkpoint_id=args.checkpoint_id,
            restore_containers=not args.no_containers,
            restore_volumes=args.with_volumes,
            restore_configs=not args.no_configs,
        )

        print(f"Checkpoint restoration completed.")

        # Print restored containers
        if result.get("restored_items", {}).get("containers"):
            containers = result.get("restored_items", {}).get("containers", [])
            print(f"\nRestored {len(containers)} containers:")
            for container in containers:
                print(
                    f"  {container.get('name')} ({container.get('id')}) - {container.get('status')}"
                )

        # Print restored volumes
        if result.get("restored_items", {}).get("volumes"):
            volumes = result.get("restored_items", {}).get("volumes", [])
            print(f"\nRestored {len(volumes)} volumes:")
            for volume in volumes:
                print(f"  {volume.get('name')}")

        # Print restored configuration files
        if result.get("restored_items", {}).get("configs"):
            configs = result.get("restored_items", {}).get("configs", [])
            print(f"\nRestored {len(configs)} configuration files:")
            for config in configs:
                print(f"  {config.get('file_name')} -> {config.get('original_path')}")

        # Print errors
        if result.get("errors"):
            print(f"\nErrors occurred during restoration:")
            for error in result.get("errors", []):
                print(f"  {error}")

    except Exception as e:
        logger.error(f"Error restoring checkpoint: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)
