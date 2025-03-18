"""
Checkpoint Manager module.

This module provides functionality for creating, managing, and restoring
Docker state via checkpoints. Checkpoints can include container state,
volumes, and configuration files.
"""

import os
import sys
import json
import shutil
import uuid
import datetime
import tempfile
import difflib
import logging
import docker
from typing import Dict, List, Any, Optional, Tuple, Set

from src.docker.connection_manager import get_docker_client
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("backup.checkpoint")


class CheckpointManager:
    """Manage Docker checkpoints for containers, volumes, and configurations."""

    def __init__(self):
        """Initialize the checkpoint manager."""
        self.docker_client = get_docker_client()
        
        # Set up checkpoint directory
        self.checkpoint_dir = os.path.expanduser("~/.dockerforge/checkpoints")
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Set up configuration
        self.config_file = os.path.join(self.checkpoint_dir, "checkpoint_config.json")
        self._init_config()

    def _init_config(self) -> None:
        """Initialize the checkpoint configuration file if it doesn't exist."""
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as f:
                json.dump({
                    "checkpoints": []
                }, f, indent=2)

    def _load_config(self) -> Dict[str, Any]:
        """Load the checkpoint configuration."""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error(f"Error loading checkpoint config from {self.config_file}, creating new one")
            self._init_config()
            return {"checkpoints": []}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save the checkpoint configuration."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def create_checkpoint(self, 
                          name: str, 
                          description: Optional[str] = None,
                          include_containers: bool = True,
                          include_volumes: bool = True,
                          include_configs: bool = True) -> Dict[str, Any]:
        """
        Create a new checkpoint of the current Docker state.
        
        Args:
            name: Name of the checkpoint
            description: Optional description
            include_containers: Whether to include containers in the checkpoint
            include_volumes: Whether to include volumes in the checkpoint
            include_configs: Whether to include configuration files in the checkpoint
            
        Returns:
            Dictionary with checkpoint information
        """
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        # Create checkpoint directory
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        os.makedirs(checkpoint_path, exist_ok=True)
        
        # Initialize metadata
        metadata = {
            "checkpoint_id": checkpoint_id,
            "name": name,
            "description": description,
            "timestamp": timestamp,
            "include_containers": include_containers,
            "include_volumes": include_volumes,
            "include_configs": include_configs,
            "checkpoint_path": checkpoint_path,
            "included_items": {}
        }
        
        # Collect container information
        containers_data = []
        if include_containers:
            containers_dir = os.path.join(checkpoint_path, "containers")
            os.makedirs(containers_dir, exist_ok=True)
            
            containers = self.docker_client.containers.list(all=True)
            for container in containers:
                container_info = self._get_container_info(container)
                containers_data.append(container_info)
                
                # Save container info to file
                container_file = os.path.join(containers_dir, f"{container.id}.json")
                with open(container_file, "w") as f:
                    json.dump(container_info, f, indent=2)
            
            metadata["included_items"]["containers"] = len(containers_data)
        
        # Collect volume information
        volumes_data = []
        if include_volumes:
            volumes_dir = os.path.join(checkpoint_path, "volumes")
            os.makedirs(volumes_dir, exist_ok=True)
            
            volumes = self.docker_client.volumes.list()
            for volume in volumes:
                volume_info = self._get_volume_info(volume)
                volumes_data.append(volume_info)
                
                # Save volume info to file
                volume_file = os.path.join(volumes_dir, f"{volume.id}.json")
                with open(volume_file, "w") as f:
                    json.dump(volume_info, f, indent=2)
            
            metadata["included_items"]["volumes"] = len(volumes_data)
        
        # Collect configuration files
        config_files_data = []
        if include_configs:
            configs_dir = os.path.join(checkpoint_path, "configs")
            os.makedirs(configs_dir, exist_ok=True)
            
            # Docker daemon.json
            daemon_json_path = "/etc/docker/daemon.json"
            if os.path.exists(daemon_json_path):
                config_info = self._backup_config_file(daemon_json_path, configs_dir)
                if config_info:
                    config_files_data.append(config_info)
            
            # Docker config.json
            config_json_path = os.path.expanduser("~/.docker/config.json")
            if os.path.exists(config_json_path):
                config_info = self._backup_config_file(config_json_path, configs_dir)
                if config_info:
                    config_files_data.append(config_info)
                    
            # Docker compose files (check common locations)
            for compose_path in ["docker-compose.yml", "docker-compose.yaml", 
                                 "docker-compose.override.yml", "docker-compose.override.yaml"]:
                if os.path.exists(compose_path):
                    config_info = self._backup_config_file(compose_path, configs_dir)
                    if config_info:
                        config_files_data.append(config_info)
            
            metadata["included_items"]["configs"] = len(config_files_data)
        
        # Save metadata to checkpoint directory
        metadata_file = os.path.join(checkpoint_path, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Update config file
        config = self._load_config()
        config["checkpoints"].append({
            "checkpoint_id": checkpoint_id,
            "name": name,
            "description": description,
            "timestamp": timestamp
        })
        self._save_config(config)
        
        logger.info(f"Created checkpoint {checkpoint_id} ({name})")
        return metadata

    def _get_container_info(self, container: docker.models.containers.Container) -> Dict[str, Any]:
        """Extract container information for a checkpoint."""
        info = {
            "id": container.id,
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else container.image.id,
            "status": container.status,
            "created": container.attrs["Created"],
            "command": container.attrs["Config"]["Cmd"],
            "entrypoint": container.attrs["Config"]["Entrypoint"],
            "env": container.attrs["Config"]["Env"],
            "labels": container.attrs["Config"]["Labels"],
            "volumes": container.attrs["HostConfig"]["Binds"],
            "ports": container.attrs["HostConfig"]["PortBindings"],
            "network_mode": container.attrs["HostConfig"]["NetworkMode"],
            "restart_policy": container.attrs["HostConfig"]["RestartPolicy"],
            "privileged": container.attrs["HostConfig"]["Privileged"],
            "networks": list(container.attrs["NetworkSettings"]["Networks"].keys())
        }
        return info

    def _get_volume_info(self, volume: docker.models.volumes.Volume) -> Dict[str, Any]:
        """Extract volume information for a checkpoint."""
        info = {
            "id": volume.id,
            "name": volume.name,
            "driver": volume.attrs["Driver"],
            "mountpoint": volume.attrs["Mountpoint"],
            "labels": volume.attrs["Labels"] if "Labels" in volume.attrs else {},
            "options": volume.attrs["Options"] if "Options" in volume.attrs else {}
        }
        return info

    def _backup_config_file(self, file_path: str, dest_dir: str) -> Optional[Dict[str, Any]]:
        """Backup a configuration file to the checkpoint directory."""
        try:
            # Get relative path for storage
            if os.path.isabs(file_path):
                rel_path = os.path.basename(file_path)
            else:
                rel_path = file_path
                
            # Create destination file path
            dest_file = os.path.join(dest_dir, os.path.basename(file_path))
            
            # Copy file
            shutil.copy2(file_path, dest_file)
            
            # Return file info
            return {
                "file_name": os.path.basename(file_path),
                "original_path": file_path,
                "checkpoint_path": dest_file
            }
        except Exception as e:
            logger.error(f"Error backing up config file {file_path}: {str(e)}")
            return None

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint information dictionaries
        """
        config = self._load_config()
        checkpoints = []
        
        for checkpoint_ref in config["checkpoints"]:
            checkpoint_id = checkpoint_ref["checkpoint_id"]
            checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
            metadata_file = os.path.join(checkpoint_path, "metadata.json")
            
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        checkpoints.append(metadata)
                except Exception as e:
                    logger.error(f"Error loading checkpoint {checkpoint_id}: {str(e)}")
        
        return checkpoints

    def get_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Get information about a specific checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to retrieve
            
        Returns:
            Checkpoint information dictionary
            
        Raises:
            ValueError: If the checkpoint is not found
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        metadata_file = os.path.join(checkpoint_path, "metadata.json")
        
        if not os.path.exists(metadata_file):
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        try:
            with open(metadata_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading checkpoint {checkpoint_id}: {str(e)}")
            raise ValueError(f"Error loading checkpoint {checkpoint_id}: {str(e)}")

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to delete
            
        Returns:
            True if the checkpoint was deleted, False otherwise
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        
        if not os.path.exists(checkpoint_path):
            logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        try:
            # Remove checkpoint directory
            shutil.rmtree(checkpoint_path)
            
            # Update config file
            config = self._load_config()
            config["checkpoints"] = [c for c in config["checkpoints"] 
                                     if c["checkpoint_id"] != checkpoint_id]
            self._save_config(config)
            
            logger.info(f"Deleted checkpoint {checkpoint_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting checkpoint {checkpoint_id}: {str(e)}")
            return False

    def compare_checkpoints(self, 
                           checkpoint_id_1: str, 
                           checkpoint_id_2: str,
                           compare_containers: bool = True,
                           compare_volumes: bool = True,
                           compare_configs: bool = True) -> Dict[str, Any]:
        """
        Compare two checkpoints and return the differences.
        
        Args:
            checkpoint_id_1: ID of the first checkpoint
            checkpoint_id_2: ID of the second checkpoint
            compare_containers: Whether to compare containers
            compare_volumes: Whether to compare volumes
            compare_configs: Whether to compare configuration files
            
        Returns:
            Dictionary with comparison results
            
        Raises:
            ValueError: If one of the checkpoints is not found
        """
        # Load checkpoint metadata
        checkpoint1 = self.get_checkpoint(checkpoint_id_1)
        checkpoint2 = self.get_checkpoint(checkpoint_id_2)
        
        comparison = {
            "checkpoint1": {
                "checkpoint_id": checkpoint_id_1,
                "name": checkpoint1["name"],
                "timestamp": checkpoint1["timestamp"]
            },
            "checkpoint2": {
                "checkpoint_id": checkpoint_id_2,
                "name": checkpoint2["name"],
                "timestamp": checkpoint2["timestamp"]
            },
            "summary": {
                "added": 0,
                "removed": 0,
                "modified": 0,
                "unchanged": 0
            }
        }
        
        # Compare containers
        if compare_containers and checkpoint1.get("include_containers") and checkpoint2.get("include_containers"):
            containers1 = self._load_checkpoint_items(checkpoint_id_1, "containers")
            containers2 = self._load_checkpoint_items(checkpoint_id_2, "containers")
            
            containers_comparison = self._compare_items(containers1, containers2, "id", ["status"])
            comparison["containers"] = containers_comparison
            
            comparison["summary"]["added"] += len(containers_comparison["added"])
            comparison["summary"]["removed"] += len(containers_comparison["removed"])
            comparison["summary"]["modified"] += len(containers_comparison["modified"])
            comparison["summary"]["unchanged"] += len(containers_comparison["unchanged"])
        
        # Compare volumes
        if compare_volumes and checkpoint1.get("include_volumes") and checkpoint2.get("include_volumes"):
            volumes1 = self._load_checkpoint_items(checkpoint_id_1, "volumes")
            volumes2 = self._load_checkpoint_items(checkpoint_id_2, "volumes")
            
            volumes_comparison = self._compare_items(volumes1, volumes2, "id", [])
            comparison["volumes"] = volumes_comparison
            
            comparison["summary"]["added"] += len(volumes_comparison["added"])
            comparison["summary"]["removed"] += len(volumes_comparison["removed"])
            comparison["summary"]["modified"] += len(volumes_comparison["modified"])
            comparison["summary"]["unchanged"] += len(volumes_comparison["unchanged"])
        
        # Compare config files
        if compare_configs and checkpoint1.get("include_configs") and checkpoint2.get("include_configs"):
            configs1 = self._load_checkpoint_items(checkpoint_id_1, "configs")
            configs2 = self._load_checkpoint_items(checkpoint_id_2, "configs")
            
            configs_comparison = self._compare_configs(configs1, configs2, checkpoint_id_1, checkpoint_id_2)
            comparison["configs"] = configs_comparison
            
            comparison["summary"]["added"] += len(configs_comparison["added"])
            comparison["summary"]["removed"] += len(configs_comparison["removed"])
            comparison["summary"]["modified"] += len(configs_comparison["modified"])
            comparison["summary"]["unchanged"] += len(configs_comparison["unchanged"])
        
        return comparison

    def _load_checkpoint_items(self, checkpoint_id: str, item_type: str) -> List[Dict[str, Any]]:
        """Load items from a checkpoint directory."""
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        items_dir = os.path.join(checkpoint_path, item_type)
        
        if not os.path.exists(items_dir):
            return []
        
        items = []
        for item_file in os.listdir(items_dir):
            if item_file.endswith(".json"):
                item_path = os.path.join(items_dir, item_file)
                try:
                    with open(item_path, "r") as f:
                        item = json.load(f)
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error loading {item_type} {item_file}: {str(e)}")
        
        return items

    def _compare_items(self, 
                      items1: List[Dict[str, Any]], 
                      items2: List[Dict[str, Any]],
                      id_field: str,
                      ignore_fields: List[str]) -> Dict[str, Any]:
        """Compare two lists of items and return the differences."""
        items1_dict = {item[id_field]: item for item in items1}
        items2_dict = {item[id_field]: item for item in items2}
        
        # Find added and removed items
        items1_ids = set(items1_dict.keys())
        items2_ids = set(items2_dict.keys())
        
        added_ids = items2_ids - items1_ids
        removed_ids = items1_ids - items2_ids
        common_ids = items1_ids.intersection(items2_ids)
        
        # Find modified and unchanged items
        modified_ids = []
        modified_details = {}
        unchanged_ids = []
        
        for item_id in common_ids:
            item1 = items1_dict[item_id]
            item2 = items2_dict[item_id]
            
            # Check if items are different (excluding ignored fields)
            diff = {}
            for key in set(item1.keys()).union(set(item2.keys())):
                if key in ignore_fields:
                    continue
                
                if key not in item1:
                    diff[key] = {"old": None, "new": item2[key]}
                elif key not in item2:
                    diff[key] = {"old": item1[key], "new": None}
                elif item1[key] != item2[key]:
                    diff[key] = {"old": item1[key], "new": item2[key]}
            
            if diff:
                modified_ids.append(item_id)
                modified_details[item1.get("name", item_id)] = {"modified_values": diff}
            else:
                unchanged_ids.append(item_id)
        
        return {
            "added": [items2_dict[item_id] for item_id in added_ids],
            "removed": [items1_dict[item_id] for item_id in removed_ids],
            "modified": [items2_dict[item_id] for item_id in modified_ids],
            "unchanged": [items2_dict[item_id] for item_id in unchanged_ids],
            "details": modified_details
        }

    def _compare_configs(self, 
                        configs1: List[Dict[str, Any]], 
                        configs2: List[Dict[str, Any]],
                        checkpoint_id_1: str,
                        checkpoint_id_2: str) -> Dict[str, Any]:
        """Compare configuration files between two checkpoints."""
        configs1_dict = {config["file_name"]: config for config in configs1}
        configs2_dict = {config["file_name"]: config for config in configs2}
        
        # Find added and removed configs
        configs1_names = set(configs1_dict.keys())
        configs2_names = set(configs2_dict.keys())
        
        added_names = configs2_names - configs1_names
        removed_names = configs1_names - configs2_names
        common_names = configs1_names.intersection(configs2_names)
        
        # Compare file contents for common configs
        modified_names = []
        unchanged_names = []
        diffs = {}
        
        checkpoint1_path = os.path.join(self.checkpoint_dir, checkpoint_id_1)
        checkpoint2_path = os.path.join(self.checkpoint_dir, checkpoint_id_2)
        
        for file_name in common_names:
            config1 = configs1_dict[file_name]
            config2 = configs2_dict[file_name]
            
            file1_path = os.path.join(checkpoint1_path, "configs", file_name)
            file2_path = os.path.join(checkpoint2_path, "configs", file_name)
            
            if os.path.exists(file1_path) and os.path.exists(file2_path):
                try:
                    with open(file1_path, "r") as f1, open(file2_path, "r") as f2:
                        content1 = f1.readlines()
                        content2 = f2.readlines()
                        
                        diff = list(difflib.unified_diff(
                            content1, content2, 
                            fromfile=f"Checkpoint 1: {file_name}", 
                            tofile=f"Checkpoint 2: {file_name}"
                        ))
                        
                        if diff:
                            modified_names.append(file_name)
                            diffs[file_name] = "".join(diff)
                        else:
                            unchanged_names.append(file_name)
                except Exception as e:
                    logger.error(f"Error comparing config files {file_name}: {str(e)}")
                    modified_names.append(file_name)
        
        return {
            "added": [configs2_dict[name] for name in added_names],
            "removed": [configs1_dict[name] for name in removed_names],
            "modified": [configs2_dict[name] for name in modified_names],
            "unchanged": [configs2_dict[name] for name in unchanged_names],
            "diffs": diffs
        }

    def restore_from_checkpoint(self, 
                               checkpoint_id: str,
                               restore_containers: bool = True,
                               restore_volumes: bool = False,
                               restore_configs: bool = True) -> Dict[str, Any]:
        """
        Restore Docker state from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore from
            restore_containers: Whether to restore containers
            restore_volumes: Whether to restore volumes (use with caution)
            restore_configs: Whether to restore configuration files
            
        Returns:
            Dictionary with restoration results
            
        Raises:
            ValueError: If the checkpoint is not found
        """
        # Load checkpoint metadata
        checkpoint = self.get_checkpoint(checkpoint_id)
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        
        result = {
            "checkpoint_id": checkpoint_id,
            "restored_items": {},
            "errors": []
        }
        
        # Restore containers
        if restore_containers and checkpoint.get("include_containers"):
            restored_containers = []
            containers = self._load_checkpoint_items(checkpoint_id, "containers")
            
            for container_info in containers:
                try:
                    # Check if container exists
                    existing_container = None
                    try:
                        existing_container = self.docker_client.containers.get(container_info["id"])
                    except docker.errors.NotFound:
                        pass
                    
                    # Stop and remove existing container if needed
                    if existing_container:
                        if existing_container.status == "running":
                            existing_container.stop()
                        existing_container.remove()
                    
                    # Reconstruct container run parameters
                    image = container_info["image"]
                    name = container_info["name"]
                    command = container_info["command"]
                    environment = container_info["env"] if "env" in container_info else []
                    ports = {}
                    if "ports" in container_info and container_info["ports"]:
                        for port_spec, bindings in container_info["ports"].items():
                            container_port = port_spec
                            if bindings:
                                for binding in bindings:
                                    host_port = binding.get("HostPort", "")
                                    host_ip = binding.get("HostIp", "")
                                    ports[container_port] = (host_ip, host_port) if host_ip else host_port
                    
                    volumes = container_info["volumes"] if "volumes" in container_info else []
                    network_mode = container_info["network_mode"] if "network_mode" in container_info else None
                    
                    # Create container
                    container = self.docker_client.containers.run(
                        image=image,
                        name=name,
                        command=command,
                        detach=True,
                        environment=environment,
                        ports=ports,
                        volumes=volumes,
                        network_mode=network_mode,
                        restart_policy=container_info.get("restart_policy", {"Name": "no"}),
                        privileged=container_info.get("privileged", False)
                    )
                    
                    # Add to restored containers
                    restored_containers.append({
                        "id": container.id,
                        "name": container.name,
                        "image": image,
                        "status": container.status
                    })
                    
                except Exception as e:
                    error_msg = f"Error restoring container {container_info.get('name', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            result["restored_items"]["containers"] = restored_containers
        
        # Restore volumes (with caution)
        if restore_volumes and checkpoint.get("include_volumes"):
            restored_volumes = []
            volumes = self._load_checkpoint_items(checkpoint_id, "volumes")
            
            for volume_info in volumes:
                try:
                    # Check if volume exists
                    existing_volume = None
                    try:
                        existing_volume = self.docker_client.volumes.get(volume_info["name"])
                    except docker.errors.NotFound:
                        pass
                    
                    # Remove existing volume if needed
                    if existing_volume:
                        existing_volume.remove()
                    
                    # Create volume
                    volume = self.docker_client.volumes.create(
                        name=volume_info["name"],
                        driver=volume_info["driver"],
                        driver_opts=volume_info.get("options", {}),
                        labels=volume_info.get("labels", {})
                    )
                    
                    # Add to restored volumes
                    restored_volumes.append({
                        "name": volume.name,
                        "driver": volume.attrs["Driver"]
                    })
                    
                except Exception as e:
                    error_msg = f"Error restoring volume {volume_info.get('name', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            result["restored_items"]["volumes"] = restored_volumes
        
        # Restore configuration files
        if restore_configs and checkpoint.get("include_configs"):
            restored_configs = []
            configs = self._load_checkpoint_items(checkpoint_id, "configs")
            
            for config_info in configs:
                try:
                    original_path = config_info["original_path"]
                    checkpoint_config_path = os.path.join(checkpoint_path, "configs", config_info["file_name"])
                    
                    # Create backup of current config file if it exists
                    if os.path.exists(original_path):
                        backup_path = f"{original_path}.backup.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        shutil.copy2(original_path, backup_path)
                    
                    # Copy restored config file
                    shutil.copy2(checkpoint_config_path, original_path)
                    
                    # Add to restored configs
                    restored_configs.append({
                        "file_name": config_info["file_name"],
                        "original_path": original_path
                    })
                    
                except Exception as e:
                    error_msg = f"Error restoring config file {config_info.get('file_name', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)
            
            result["restored_items"]["configs"] = restored_configs
        
        logger.info(f"Restored checkpoint {checkpoint_id}")
        return result


def get_checkpoint_manager() -> CheckpointManager:
    """Get or create the checkpoint manager instance."""
    return CheckpointManager()
