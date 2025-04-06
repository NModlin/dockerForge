"""
Backup manager module for DockerForge.

This module provides functionality to backup and restore Docker containers,
images, and volumes.
"""

import datetime
import json
import logging
import os
import shutil
import tarfile
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

from src.config.config_manager import get_config
from src.docker.connection_manager import get_docker_client
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("backup.backup_manager")


class BackupManager:
    """
    Backup manager for Docker containers, images, and volumes.
    """

    def __init__(self):
        """Initialize the backup manager."""
        self.docker_client = get_docker_client()
        self.config = get_config("backup.backup_manager", {})
        self.backup_dir = self.config.get(
            "backup_dir", os.path.expanduser("~/.dockerforge/backups")
        )

        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_container(
        self,
        container_id_or_name: str,
        include_volumes: bool = True,
        include_image: bool = False,
        backup_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Backup a Docker container.

        Args:
            container_id_or_name: ID or name of the container to backup.
            include_volumes: Whether to include volumes in the backup.
            include_image: Whether to include the container's image in the backup.
            backup_name: Name of the backup. If not provided, a name will be generated.

        Returns:
            Dict containing backup information.
        """
        logger.info(f"Backing up container {container_id_or_name}")

        try:
            # Get container
            container = self.docker_client.containers.get(container_id_or_name)
            container_id = container.id
            container_name = container.name

            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{container_name}_{timestamp}"

            # Create backup directory
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)

            # Get container info
            container_info = container.attrs

            # Save container info
            with open(os.path.join(backup_path, "container_info.json"), "w") as f:
                json.dump(container_info, f, indent=2)

            # Backup volumes if requested
            volume_backups = []
            if include_volumes:
                volume_backups = self._backup_container_volumes(container, backup_path)

            # Backup image if requested
            image_backup = None
            if include_image:
                image_backup = self._backup_container_image(container, backup_path)

            # Create backup metadata
            metadata = {
                "backup_id": backup_name,
                "container_id": container_id,
                "container_name": container_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "include_volumes": include_volumes,
                "include_image": include_image,
                "volumes": volume_backups,
                "image": image_backup,
                "backup_path": backup_path,
            }

            # Save metadata
            with open(os.path.join(backup_path, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Container backup completed: {backup_path}")
            return metadata

        except Exception as e:
            logger.error(f"Error backing up container: {str(e)}")
            raise

    def _backup_container_volumes(
        self, container, backup_path: str
    ) -> List[Dict[str, Any]]:
        """
        Backup container volumes.

        Args:
            container: Docker container object.
            backup_path: Path to the backup directory.

        Returns:
            List of volume backup information.
        """
        logger.info(f"Backing up volumes for container {container.name}")

        # Create volumes directory
        volumes_path = os.path.join(backup_path, "volumes")
        os.makedirs(volumes_path, exist_ok=True)

        # Get container mounts
        mounts = container.attrs.get("Mounts", [])

        # Backup each volume
        volume_backups = []
        for mount in mounts:
            try:
                # Skip bind mounts
                if mount.get("Type") != "volume":
                    continue

                # Get volume info
                volume_name = mount.get("Name")
                volume = self.docker_client.volumes.get(volume_name)

                # Create volume backup directory
                volume_backup_path = os.path.join(volumes_path, volume_name)
                os.makedirs(volume_backup_path, exist_ok=True)

                # Create a temporary container to access the volume
                temp_container = self.docker_client.containers.create(
                    "alpine:latest",
                    command="sleep 1000",
                    volumes={volume_name: {"bind": "/volume", "mode": "ro"}},
                )

                try:
                    # Start the container
                    temp_container.start()

                    # Create a tar archive of the volume
                    tar_path = os.path.join(volume_backup_path, "volume.tar")
                    with open(tar_path, "wb") as f:
                        bits, stat = temp_container.get_archive("/volume")
                        for chunk in bits:
                            f.write(chunk)

                    # Save volume info
                    volume_info = volume.attrs
                    with open(
                        os.path.join(volume_backup_path, "volume_info.json"), "w"
                    ) as f:
                        json.dump(volume_info, f, indent=2)

                    # Add to volume backups
                    volume_backups.append(
                        {
                            "volume_name": volume_name,
                            "mount_point": mount.get("Destination"),
                            "backup_path": volume_backup_path,
                        }
                    )

                finally:
                    # Clean up temporary container
                    temp_container.stop()
                    temp_container.remove()

            except Exception as e:
                logger.error(f"Error backing up volume {mount.get('Name')}: {str(e)}")

        return volume_backups

    def _backup_container_image(self, container, backup_path: str) -> Dict[str, Any]:
        """
        Backup container image.

        Args:
            container: Docker container object.
            backup_path: Path to the backup directory.

        Returns:
            Dict containing image backup information.
        """
        logger.info(f"Backing up image for container {container.name}")

        # Create images directory
        images_path = os.path.join(backup_path, "images")
        os.makedirs(images_path, exist_ok=True)

        # Get image info
        image_id = container.image.id
        image_tags = container.image.tags
        image_name = image_tags[0] if image_tags else image_id.split(":")[-1]

        # Save image
        image_file = os.path.join(images_path, f"{image_name.replace('/', '_')}.tar")
        with open(image_file, "wb") as f:
            for chunk in container.image.save():
                f.write(chunk)

        # Save image info
        image_info = container.image.attrs
        with open(os.path.join(images_path, "image_info.json"), "w") as f:
            json.dump(image_info, f, indent=2)

        return {
            "image_id": image_id,
            "image_name": image_name,
            "image_tags": image_tags,
            "backup_path": image_file,
        }

    def restore_container(
        self,
        backup_id_or_path: str,
        restore_volumes: bool = True,
        restore_image: bool = True,
        new_container_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Restore a Docker container from backup.

        Args:
            backup_id_or_path: ID or path of the backup to restore.
            restore_volumes: Whether to restore volumes.
            restore_image: Whether to restore the container's image.
            new_container_name: Name for the restored container. If not provided,
                the original name will be used with a suffix.

        Returns:
            Dict containing restore information.
        """
        logger.info(f"Restoring container from backup {backup_id_or_path}")

        try:
            # Get backup path
            if os.path.isdir(backup_id_or_path):
                backup_path = backup_id_or_path
            else:
                backup_path = os.path.join(self.backup_dir, backup_id_or_path)

            if not os.path.exists(backup_path):
                raise ValueError(f"Backup not found: {backup_path}")

            # Load metadata
            metadata_file = os.path.join(backup_path, "metadata.json")
            if not os.path.exists(metadata_file):
                raise ValueError(f"Backup metadata not found: {metadata_file}")

            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Load container info
            container_info_file = os.path.join(backup_path, "container_info.json")
            if not os.path.exists(container_info_file):
                raise ValueError(f"Container info not found: {container_info_file}")

            with open(container_info_file, "r") as f:
                container_info = json.load(f)

            # Restore image if requested
            image_id = container_info.get("Image")
            if restore_image and metadata.get("image"):
                image_id = self._restore_image(metadata["image"])

            # Generate container name if not provided
            original_name = metadata.get("container_name")
            if not new_container_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_container_name = f"{original_name}_restored_{timestamp}"

            # Restore volumes if requested
            volume_map = {}
            if restore_volumes and metadata.get("volumes"):
                volume_map = self._restore_volumes(metadata["volumes"])

            # Create container config
            config = container_info.get("Config", {})
            host_config = container_info.get("HostConfig", {})

            # Update volume bindings
            if volume_map:
                # Update host config binds
                binds = []
                for mount in host_config.get("Mounts", []):
                    if (
                        mount.get("Type") == "volume"
                        and mount.get("Name") in volume_map
                    ):
                        mount["Name"] = volume_map[mount["Name"]]
                    binds.append(mount)
                host_config["Mounts"] = binds

            # Create container
            container = self.docker_client.containers.create(
                image=image_id,
                name=new_container_name,
                command=config.get("Cmd"),
                environment=config.get("Env"),
                ports=host_config.get("PortBindings"),
                volumes=volume_map,
                detach=True,
            )

            # Create restore metadata
            restore_info = {
                "backup_id": metadata.get("backup_id"),
                "original_container_id": metadata.get("container_id"),
                "original_container_name": metadata.get("container_name"),
                "restored_container_id": container.id,
                "restored_container_name": new_container_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "restored_volumes": volume_map,
                "restored_image": image_id,
            }

            logger.info(f"Container restored: {new_container_name} ({container.id})")
            return restore_info

        except Exception as e:
            logger.error(f"Error restoring container: {str(e)}")
            raise

    def _restore_image(self, image_backup: Dict[str, Any]) -> str:
        """
        Restore a Docker image from backup.

        Args:
            image_backup: Image backup information.

        Returns:
            ID of the restored image.
        """
        logger.info(f"Restoring image {image_backup.get('image_name')}")

        # Check if image file exists
        image_file = image_backup.get("backup_path")
        if not os.path.exists(image_file):
            raise ValueError(f"Image backup file not found: {image_file}")

        # Load image
        with open(image_file, "rb") as f:
            image = self.docker_client.images.load(f.read())[0]

        logger.info(f"Image restored: {image.id}")
        return image.id

    def _restore_volumes(self, volume_backups: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Restore Docker volumes from backup.

        Args:
            volume_backups: List of volume backup information.

        Returns:
            Dict mapping original volume names to restored volume names.
        """
        logger.info(f"Restoring {len(volume_backups)} volumes")

        volume_map = {}
        for volume_backup in volume_backups:
            try:
                volume_name = volume_backup.get("volume_name")
                backup_path = volume_backup.get("backup_path")

                # Check if volume backup exists
                tar_path = os.path.join(backup_path, "volume.tar")
                if not os.path.exists(tar_path):
                    logger.warning(f"Volume backup file not found: {tar_path}")
                    continue

                # Create a new volume
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_volume_name = f"{volume_name}_restored_{timestamp}"
                volume = self.docker_client.volumes.create(new_volume_name)

                # Create a temporary container to access the volume
                temp_container = self.docker_client.containers.create(
                    "alpine:latest",
                    command="sleep 1000",
                    volumes={new_volume_name: {"bind": "/volume", "mode": "rw"}},
                )

                try:
                    # Start the container
                    temp_container.start()

                    # Extract the tar archive to the volume
                    with open(tar_path, "rb") as f:
                        temp_container.put_archive("/volume", f.read())

                    # Add to volume map
                    volume_map[volume_name] = new_volume_name
                    logger.info(f"Volume restored: {volume_name} -> {new_volume_name}")

                finally:
                    # Clean up temporary container
                    temp_container.stop()
                    temp_container.remove()

            except Exception as e:
                logger.error(
                    f"Error restoring volume {volume_backup.get('volume_name')}: {str(e)}"
                )

        return volume_map

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all backups.

        Returns:
            List of backup metadata.
        """
        logger.info("Listing backups")

        backups = []
        for backup_id in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup_id)
            if not os.path.isdir(backup_path):
                continue

            metadata_file = os.path.join(backup_path, "metadata.json")
            if not os.path.exists(metadata_file):
                continue

            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                backups.append(metadata)
            except Exception as e:
                logger.error(f"Error loading backup metadata {metadata_file}: {str(e)}")

        return backups

    def get_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Get backup metadata.

        Args:
            backup_id: ID of the backup.

        Returns:
            Backup metadata.
        """
        logger.info(f"Getting backup {backup_id}")

        backup_path = os.path.join(self.backup_dir, backup_id)
        if not os.path.exists(backup_path):
            raise ValueError(f"Backup not found: {backup_id}")

        metadata_file = os.path.join(backup_path, "metadata.json")
        if not os.path.exists(metadata_file):
            raise ValueError(f"Backup metadata not found: {metadata_file}")

        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        return metadata

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: ID of the backup to delete.

        Returns:
            True if the backup was deleted, False otherwise.
        """
        logger.info(f"Deleting backup {backup_id}")

        backup_path = os.path.join(self.backup_dir, backup_id)
        if not os.path.exists(backup_path):
            logger.warning(f"Backup not found: {backup_id}")
            return False

        try:
            shutil.rmtree(backup_path)
            logger.info(f"Backup deleted: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting backup {backup_id}: {str(e)}")
            return False


# Singleton instance
_backup_manager = None


def get_backup_manager() -> BackupManager:
    """
    Get the backup manager instance.

    Returns:
        BackupManager: The backup manager instance.
    """
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
