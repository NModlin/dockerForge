"""
Docker daemon configuration router for the DockerForge Web UI.

This module provides API endpoints for managing Docker daemon configuration.
"""

# Set up logging
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config.config_manager import ConfigManager
from src.settings.daemon_config import DaemonConfigManager
from src.web.api.auth import check_permission, get_current_active_user
from src.web.api.database import get_db
from src.web.api.models.user import User
from src.web.api.schemas.daemon_config import (
    AvailableDrivers,
    ConfigUpdateResponse,
    DaemonConfig,
    DriverInfo,
    LoggingConfig,
    NetworkConfig,
    RegistryConfig,
    StorageConfig,
)

logger = logging.getLogger("api.routers.daemon_config")

# Create router
router = APIRouter()

# Initialize config manager
config_manager = ConfigManager()

# Initialize daemon config manager
daemon_config_manager = DaemonConfigManager(config_manager)


@router.get("/", response_model=DaemonConfig)
async def get_daemon_config(current_user: User = Depends(get_current_active_user)):
    """
    Get the current Docker daemon configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Get configuration components
        registry_config = daemon_config_manager.get_registry_config()
        logging_config = daemon_config_manager.get_logging_config()
        storage_config = daemon_config_manager.get_storage_config()
        network_config = daemon_config_manager.get_network_config()

        # Convert to schema format
        return {
            "registry": {
                "registry-mirrors": registry_config.get("registry-mirrors", []),
                "insecure-registries": registry_config.get("insecure-registries", []),
                "allow-nondistributable-artifacts": registry_config.get(
                    "allow-nondistributable-artifacts", []
                ),
            },
            "logging": {
                "log-driver": logging_config.get("log-driver", "json-file"),
                "log-opts": logging_config.get("log-opts", {}),
            },
            "storage": {
                "storage-driver": storage_config.get("storage-driver", ""),
                "storage-opts": storage_config.get("storage-opts", []),
                "data-root": storage_config.get("data-root", "/var/lib/docker"),
            },
            "network": network_config,
        }
    except Exception as e:
        logger.exception(f"Error getting daemon configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting daemon configuration: {str(e)}",
        )


@router.get("/registry", response_model=RegistryConfig)
async def get_registry_config(current_user: User = Depends(get_current_active_user)):
    """
    Get the current registry configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        registry_config = daemon_config_manager.get_registry_config()
        return {
            "registry-mirrors": registry_config.get("registry-mirrors", []),
            "insecure-registries": registry_config.get("insecure-registries", []),
            "allow-nondistributable-artifacts": registry_config.get(
                "allow-nondistributable-artifacts", []
            ),
        }
    except Exception as e:
        logger.exception(f"Error getting registry configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting registry configuration: {str(e)}",
        )


@router.put("/registry", response_model=ConfigUpdateResponse)
async def update_registry_config(
    registry_config: RegistryConfig,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the registry configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Convert to daemon config format
        config = {
            "registry-mirrors": registry_config.registry_mirrors,
            "insecure-registries": registry_config.insecure_registries,
            "allow-nondistributable-artifacts": registry_config.allow_nondistributable_artifacts,
        }

        # Update configuration
        success, message = daemon_config_manager.update_registry_config(config)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
            )

        return {"success": success, "message": message, "requires_restart": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating registry configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating registry configuration: {str(e)}",
        )


@router.get("/logging", response_model=LoggingConfig)
async def get_logging_config(current_user: User = Depends(get_current_active_user)):
    """
    Get the current logging configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        logging_config = daemon_config_manager.get_logging_config()
        return {
            "log-driver": logging_config.get("log-driver", "json-file"),
            "log-opts": logging_config.get("log-opts", {}),
        }
    except Exception as e:
        logger.exception(f"Error getting logging configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting logging configuration: {str(e)}",
        )


@router.put("/logging", response_model=ConfigUpdateResponse)
async def update_logging_config(
    logging_config: LoggingConfig, current_user: User = Depends(get_current_active_user)
):
    """
    Update the logging configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Convert to daemon config format
        config = {
            "log-driver": logging_config.log_driver,
            "log-opts": logging_config.log_opts,
        }

        # Update configuration
        success, message = daemon_config_manager.update_logging_config(config)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
            )

        return {"success": success, "message": message, "requires_restart": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating logging configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating logging configuration: {str(e)}",
        )


@router.get("/storage", response_model=StorageConfig)
async def get_storage_config(current_user: User = Depends(get_current_active_user)):
    """
    Get the current storage configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        storage_config = daemon_config_manager.get_storage_config()
        return {
            "storage-driver": storage_config.get("storage-driver", ""),
            "storage-opts": storage_config.get("storage-opts", []),
            "data-root": storage_config.get("data-root", "/var/lib/docker"),
        }
    except Exception as e:
        logger.exception(f"Error getting storage configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting storage configuration: {str(e)}",
        )


@router.put("/storage", response_model=ConfigUpdateResponse)
async def update_storage_config(
    storage_config: StorageConfig, current_user: User = Depends(get_current_active_user)
):
    """
    Update the storage configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Convert to daemon config format
        config = {
            "storage-driver": storage_config.storage_driver,
            "storage-opts": storage_config.storage_opts,
            "data-root": storage_config.data_root,
        }

        # Update configuration
        success, message = daemon_config_manager.update_storage_config(config)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
            )

        return {"success": success, "message": message, "requires_restart": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating storage configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating storage configuration: {str(e)}",
        )


@router.get("/network", response_model=NetworkConfig)
async def get_network_config(current_user: User = Depends(get_current_active_user)):
    """
    Get the current network configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        return daemon_config_manager.get_network_config()
    except Exception as e:
        logger.exception(f"Error getting network configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting network configuration: {str(e)}",
        )


@router.put("/network", response_model=ConfigUpdateResponse)
async def update_network_config(
    network_config: NetworkConfig, current_user: User = Depends(get_current_active_user)
):
    """
    Update the network configuration.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Convert to daemon config format
        config = network_config.dict(by_alias=True, exclude_none=True)

        # Update configuration
        success, message = daemon_config_manager.update_network_config(config)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
            )

        return {"success": success, "message": message, "requires_restart": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating network configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating network configuration: {str(e)}",
        )


@router.get("/drivers", response_model=AvailableDrivers)
async def get_available_drivers(current_user: User = Depends(get_current_active_user)):
    """
    Get available logging and storage drivers.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Get available drivers
        logging_drivers = daemon_config_manager.get_available_logging_drivers()
        storage_drivers = daemon_config_manager.get_available_storage_drivers()

        # Create driver info objects
        logging_driver_info = [
            {"name": "json-file", "description": "JSON File logging driver"},
            {"name": "syslog", "description": "Syslog logging driver"},
            {"name": "journald", "description": "Journald logging driver"},
            {"name": "gelf", "description": "GELF (Graylog) logging driver"},
            {"name": "fluentd", "description": "Fluentd logging driver"},
            {"name": "awslogs", "description": "Amazon CloudWatch Logs logging driver"},
            {"name": "splunk", "description": "Splunk logging driver"},
            {"name": "etwlogs", "description": "ETW logging driver (Windows)"},
            {"name": "gcplogs", "description": "Google Cloud Logging driver"},
            {"name": "logentries", "description": "Logentries logging driver"},
            {"name": "local", "description": "Local file logging driver"},
        ]

        storage_driver_info = [
            {"name": "overlay2", "description": "OverlayFS v2 storage driver"},
            {"name": "aufs", "description": "AUFS storage driver"},
            {"name": "btrfs", "description": "Btrfs storage driver"},
            {"name": "devicemapper", "description": "Device Mapper storage driver"},
            {"name": "vfs", "description": "VFS storage driver"},
            {"name": "zfs", "description": "ZFS storage driver"},
        ]

        # Filter to only include available drivers
        logging_driver_info = [
            d for d in logging_driver_info if d["name"] in logging_drivers
        ]
        storage_driver_info = [
            d for d in storage_driver_info if d["name"] in storage_drivers
        ]

        return {
            "logging_drivers": logging_driver_info,
            "storage_drivers": storage_driver_info,
        }
    except Exception as e:
        logger.exception(f"Error getting available drivers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available drivers: {str(e)}",
        )
