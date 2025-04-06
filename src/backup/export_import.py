"""
Export and import module for DockerForge.

This module provides functionality to export and import Docker containers,
images, and volumes to/from files.
"""

import datetime
import json
import logging
import os
import shutil
import tarfile
import tempfile
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

from src.config.config_manager import get_config
from src.docker.connection_manager import get_docker_client
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("backup.export_import")


class ExportImportManager:
    """
    Export and import manager for Docker containers, images, and volumes.
    """

    def __init__(self):
        """Initialize the export/import manager."""
        self.docker_client = get_docker_client()
        self.config = get_config("backup.export_import", {})
        self.export_dir = self.config.get(
            "export_dir", os.path.expanduser("~/.dockerforge/exports")
        )

        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)

    def export_image(
        self,
        image_id_or_name: str,
        output_path: Optional[str] = None,
        compress: bool = True,
    ) -> str:
        """
        Export a Docker image to a file.

        Args:
            image_id_or_name: ID or name of the image to export.
            output_path: Path to save the exported image. If not provided,
                a default path will be used.
            compress: Whether to compress the exported image.

        Returns:
            Path to the exported image file.
        """
        logger.info(f"Exporting image {image_id_or_name}")

        try:
            # Get image
            image = self.docker_client.images.get(image_id_or_name)
            image_id = image.id
            image_tags = image.tags
            image_name = image_tags[0] if image_tags else image_id.split(":")[-1]

            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = (
                    f"{image_name.replace('/', '_').replace(':', '_')}_{timestamp}.tar"
                )
                if compress:
                    filename += ".gz"
                output_path = os.path.join(self.export_dir, filename)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Export image
            with open(output_path, "wb") as f:
                for chunk in image.save():
                    f.write(chunk)

            # Compress if requested
            if compress and not output_path.endswith(".gz"):
                compressed_path = output_path + ".gz"
                with open(output_path, "rb") as f_in:
                    with tarfile.open(compressed_path, "w:gz") as f_out:
                        info = tarfile.TarInfo(os.path.basename(output_path))
                        info.size = os.path.getsize(output_path)
                        f_out.addfile(info, f_in)

                # Remove uncompressed file
                os.unlink(output_path)
                output_path = compressed_path

            logger.info(f"Image exported to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting image: {str(e)}")
            raise

    def import_image(
        self,
        input_path: str,
        repository: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> str:
        """
        Import a Docker image from a file.

        Args:
            input_path: Path to the image file to import.
            repository: Repository name for the imported image.
            tag: Tag for the imported image.

        Returns:
            ID of the imported image.
        """
        logger.info(f"Importing image from {input_path}")

        try:
            # Check if file exists
            if not os.path.exists(input_path):
                raise ValueError(f"Image file not found: {input_path}")

            # Handle compressed files
            if input_path.endswith(".gz"):
                # Create temporary file for decompressed image
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    # Decompress file
                    with tarfile.open(input_path, "r:gz") as f_in:
                        # Validate tarfile members to prevent path traversal attacks
                        # Validate and extract files one by one
                        extract_dir = os.path.dirname(temp_path)
                        for member in f_in.getmembers():
                            # Check for path traversal attempts
                            if member.name.startswith("/") or ".." in member.name:
                                raise ValueError(
                                    f"Potentially insecure path in archive: {member.name}"
                                )
                            # Extract only safe files
                            f_in.extract(member, path=extract_dir)

                    # Find extracted file
                    extracted_files = os.listdir(os.path.dirname(temp_path))
                    if not extracted_files:
                        raise ValueError(
                            f"No files found in compressed archive: {input_path}"
                        )

                    # Use first extracted file
                    extracted_path = os.path.join(
                        os.path.dirname(temp_path), extracted_files[0]
                    )

                    # Import image
                    with open(extracted_path, "rb") as f:
                        images = self.docker_client.images.load(f.read())

                finally:
                    # Clean up temporary files
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

                    for file in os.listdir(os.path.dirname(temp_path)):
                        file_path = os.path.join(os.path.dirname(temp_path), file)
                        if os.path.isfile(file_path) and file_path != temp_path:
                            os.unlink(file_path)
            else:
                # Import image directly
                with open(input_path, "rb") as f:
                    images = self.docker_client.images.load(f.read())

            # Get imported image
            if not images:
                raise ValueError(f"No images found in file: {input_path}")

            image = images[0]
            image_id = image.id

            # Tag image if requested
            if repository:
                tag_name = tag or "latest"
                image.tag(repository, tag_name)
                logger.info(f"Image tagged as {repository}:{tag_name}")

            logger.info(f"Image imported: {image_id}")
            return image_id

        except Exception as e:
            logger.error(f"Error importing image: {str(e)}")
            raise

    def export_container(
        self,
        container_id_or_name: str,
        output_path: Optional[str] = None,
        compress: bool = True,
    ) -> str:
        """
        Export a Docker container to a file.

        Args:
            container_id_or_name: ID or name of the container to export.
            output_path: Path to save the exported container. If not provided,
                a default path will be used.
            compress: Whether to compress the exported container.

        Returns:
            Path to the exported container file.
        """
        logger.info(f"Exporting container {container_id_or_name}")

        try:
            # Get container
            container = self.docker_client.containers.get(container_id_or_name)
            container_id = container.id
            container_name = container.name

            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{container_name}_{timestamp}.tar"
                if compress:
                    filename += ".gz"
                output_path = os.path.join(self.export_dir, filename)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create temporary directory for export
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export container filesystem
                fs_path = os.path.join(temp_dir, "fs.tar")
                with open(fs_path, "wb") as f:
                    for chunk in container.export():
                        f.write(chunk)

                # Export container config
                config_path = os.path.join(temp_dir, "config.json")
                with open(config_path, "w") as f:
                    json.dump(container.attrs, f, indent=2)

                # Create archive
                if compress:
                    with tarfile.open(output_path, "w:gz") as tar:
                        tar.add(fs_path, arcname="fs.tar")
                        tar.add(config_path, arcname="config.json")
                else:
                    with tarfile.open(output_path, "w") as tar:
                        tar.add(fs_path, arcname="fs.tar")
                        tar.add(config_path, arcname="config.json")

            logger.info(f"Container exported to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting container: {str(e)}")
            raise

    def import_container(
        self,
        input_path: str,
        repository: Optional[str] = None,
        tag: Optional[str] = None,
        container_name: Optional[str] = None,
    ) -> str:
        """
        Import a Docker container from a file.

        Args:
            input_path: Path to the container file to import.
            repository: Repository name for the imported container image.
            tag: Tag for the imported container image.
            container_name: Name for the imported container.

        Returns:
            ID of the imported container.
        """
        logger.info(f"Importing container from {input_path}")

        try:
            # Check if file exists
            if not os.path.exists(input_path):
                raise ValueError(f"Container file not found: {input_path}")

            # Create temporary directory for import
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract archive
                if input_path.endswith(".gz"):
                    with tarfile.open(input_path, "r:gz") as tar:
                        # Validate and extract files one by one
                        for member in tar.getmembers():
                            # Check for path traversal attempts
                            if member.name.startswith("/") or ".." in member.name:
                                raise ValueError(
                                    f"Potentially insecure path in archive: {member.name}"
                                )
                            # Extract only safe files
                            tar.extract(member, path=temp_dir)
                else:
                    with tarfile.open(input_path, "r") as tar:
                        # Validate and extract files one by one
                        for member in tar.getmembers():
                            # Check for path traversal attempts
                            if member.name.startswith("/") or ".." in member.name:
                                raise ValueError(
                                    f"Potentially insecure path in archive: {member.name}"
                                )
                            # Extract only safe files
                            tar.extract(member, path=temp_dir)

                # Check if required files exist
                fs_path = os.path.join(temp_dir, "fs.tar")
                config_path = os.path.join(temp_dir, "config.json")

                if not os.path.exists(fs_path):
                    raise ValueError(
                        f"Container filesystem not found in archive: {input_path}"
                    )

                if not os.path.exists(config_path):
                    raise ValueError(
                        f"Container config not found in archive: {input_path}"
                    )

                # Load container config
                with open(config_path, "r") as f:
                    config = json.load(f)

                # Import container filesystem as image
                image_tag = (
                    f"{repository}:{tag}" if repository and tag else "imported:latest"
                )
                with open(fs_path, "rb") as f:
                    image = self.docker_client.images.import_image(
                        f.read(), repository=repository, tag=tag or "latest"
                    )

                # Generate container name if not provided
                if not container_name:
                    original_name = config.get("Name", "").strip("/")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    container_name = f"{original_name}_imported_{timestamp}"

                # Create container
                container_config = config.get("Config", {})
                host_config = config.get("HostConfig", {})

                container = self.docker_client.containers.create(
                    image=image_tag,
                    name=container_name,
                    command=container_config.get("Cmd"),
                    environment=container_config.get("Env"),
                    ports=host_config.get("PortBindings"),
                    volumes=host_config.get("Binds"),
                    detach=True,
                )

                logger.info(f"Container imported: {container.id}")
                return container.id

        except Exception as e:
            logger.error(f"Error importing container: {str(e)}")
            raise

    def export_volume(
        self, volume_name: str, output_path: Optional[str] = None, compress: bool = True
    ) -> str:
        """
        Export a Docker volume to a file.

        Args:
            volume_name: Name of the volume to export.
            output_path: Path to save the exported volume. If not provided,
                a default path will be used.
            compress: Whether to compress the exported volume.

        Returns:
            Path to the exported volume file.
        """
        logger.info(f"Exporting volume {volume_name}")

        try:
            # Get volume
            volume = self.docker_client.volumes.get(volume_name)

            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{volume_name}_{timestamp}.tar"
                if compress:
                    filename += ".gz"
                output_path = os.path.join(self.export_dir, filename)

            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create temporary directory for export
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a temporary container to access the volume
                temp_container = self.docker_client.containers.create(
                    "alpine:latest",
                    command="sleep 1000",
                    volumes={volume_name: {"bind": "/volume", "mode": "ro"}},
                )

                try:
                    # Start the container
                    temp_container.start()

                    # Export volume data
                    data_path = os.path.join(temp_dir, "data.tar")
                    with open(data_path, "wb") as f:
                        bits, stat = temp_container.get_archive("/volume")
                        for chunk in bits:
                            f.write(chunk)

                    # Export volume info
                    info_path = os.path.join(temp_dir, "info.json")
                    with open(info_path, "w") as f:
                        json.dump(volume.attrs, f, indent=2)

                    # Create archive
                    if compress:
                        with tarfile.open(output_path, "w:gz") as tar:
                            tar.add(data_path, arcname="data.tar")
                            tar.add(info_path, arcname="info.json")
                    else:
                        with tarfile.open(output_path, "w") as tar:
                            tar.add(data_path, arcname="data.tar")
                            tar.add(info_path, arcname="info.json")

                finally:
                    # Clean up temporary container
                    temp_container.stop()
                    temp_container.remove()

            logger.info(f"Volume exported to {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error exporting volume: {str(e)}")
            raise

    def import_volume(self, input_path: str, volume_name: Optional[str] = None) -> str:
        """
        Import a Docker volume from a file.

        Args:
            input_path: Path to the volume file to import.
            volume_name: Name for the imported volume.

        Returns:
            Name of the imported volume.
        """
        logger.info(f"Importing volume from {input_path}")

        try:
            # Check if file exists
            if not os.path.exists(input_path):
                raise ValueError(f"Volume file not found: {input_path}")

            # Create temporary directory for import
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract archive
                if input_path.endswith(".gz"):
                    with tarfile.open(input_path, "r:gz") as tar:
                        # Validate and extract files one by one
                        for member in tar.getmembers():
                            # Check for path traversal attempts
                            if member.name.startswith("/") or ".." in member.name:
                                raise ValueError(
                                    f"Potentially insecure path in archive: {member.name}"
                                )
                            # Extract only safe files
                            tar.extract(member, path=temp_dir)
                else:
                    with tarfile.open(input_path, "r") as tar:
                        # Validate and extract files one by one
                        for member in tar.getmembers():
                            # Check for path traversal attempts
                            if member.name.startswith("/") or ".." in member.name:
                                raise ValueError(
                                    f"Potentially insecure path in archive: {member.name}"
                                )
                            # Extract only safe files
                            tar.extract(member, path=temp_dir)

                # Check if required files exist
                data_path = os.path.join(temp_dir, "data.tar")
                info_path = os.path.join(temp_dir, "info.json")

                if not os.path.exists(data_path):
                    raise ValueError(f"Volume data not found in archive: {input_path}")

                if not os.path.exists(info_path):
                    raise ValueError(f"Volume info not found in archive: {input_path}")

                # Load volume info
                with open(info_path, "r") as f:
                    info = json.load(f)

                # Generate volume name if not provided
                if not volume_name:
                    original_name = info.get("Name", "unknown")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    volume_name = f"{original_name}_imported_{timestamp}"

                # Create volume
                volume = self.docker_client.volumes.create(volume_name)

                # Create a temporary container to access the volume
                temp_container = self.docker_client.containers.create(
                    "alpine:latest",
                    command="sleep 1000",
                    volumes={volume_name: {"bind": "/volume", "mode": "rw"}},
                )

                try:
                    # Start the container
                    temp_container.start()

                    # Import volume data
                    with open(data_path, "rb") as f:
                        temp_container.put_archive("/volume", f.read())

                finally:
                    # Clean up temporary container
                    temp_container.stop()
                    temp_container.remove()

                logger.info(f"Volume imported: {volume_name}")
                return volume_name

        except Exception as e:
            logger.error(f"Error importing volume: {str(e)}")
            raise


# Singleton instance
_export_import_manager = None


def get_export_import_manager() -> ExportImportManager:
    """
    Get the export/import manager instance.

    Returns:
        ExportImportManager: The export/import manager instance.
    """
    global _export_import_manager
    if _export_import_manager is None:
        _export_import_manager = ExportImportManager()
    return _export_import_manager
