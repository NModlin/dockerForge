"""
Configuration management module for DockerForge.

This module provides functionality to load, validate, and save
configuration files.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple

import yaml
from schema import Schema, And, Or, Use, Optional as SchemaOptional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class ConfigManager:
    """
    Manager for configuration files.
    
    This class handles loading, validating, and saving configuration files.
    """

    # Default configuration paths
    DEFAULT_CONFIG_PATHS = [
        # Current directory
        "./dockerforge.yaml",
        "./dockerforge.yml",
        "./config/dockerforge.yaml",
        "./config/dockerforge.yml",
        
        # User config directory
        "~/.config/dockerforge/config.yaml",
        "~/.config/dockerforge/config.yml",
        "~/.dockerforge/config.yaml",
        "~/.dockerforge/config.yml",
        
        # System config directory
        "/etc/dockerforge/config.yaml",
        "/etc/dockerforge/config.yml",
    ]
    
    # Default configuration schema
    DEFAULT_CONFIG_SCHEMA = Schema({
        # General settings
        SchemaOptional("general"): {
            SchemaOptional("log_level"): And(str, lambda s: s in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")),
            SchemaOptional("log_file"): str,
            SchemaOptional("data_dir"): str,
            SchemaOptional("backup_dir"): str,
            SchemaOptional("check_for_updates"): bool,
        },
        
        # Docker settings
        SchemaOptional("docker"): {
            SchemaOptional("host"): str,
            SchemaOptional("socket_path"): str,
            SchemaOptional("ssh_host"): str,
            SchemaOptional("tls"): {
                SchemaOptional("enabled"): bool,
                SchemaOptional("verify"): bool,
                SchemaOptional("cert_path"): str,
                SchemaOptional("key_path"): str,
                SchemaOptional("ca_path"): str,
            },
            SchemaOptional("compose"): {
                SchemaOptional("file_path"): str,
                SchemaOptional("project_name"): str,
                SchemaOptional("discovery"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("recursive"): bool,
                    SchemaOptional("include_common_locations"): bool,
                    SchemaOptional("search_paths"): [str],
                    SchemaOptional("exclude_patterns"): [str],
                },
                SchemaOptional("parser"): {
                    SchemaOptional("schema_dir"): str,
                    SchemaOptional("expand_env_vars"): bool,
                    SchemaOptional("validate"): bool,
                },
                SchemaOptional("change_management"): {
                    SchemaOptional("backup_dir"): str,
                    SchemaOptional("auto_backup"): bool,
                    SchemaOptional("max_backups"): int,
                    SchemaOptional("atomic_updates"): bool,
                },
                SchemaOptional("templates"): {
                    SchemaOptional("directory"): str,
                    SchemaOptional("auto_load"): bool,
                    SchemaOptional("variable_pattern"): str,
                },
                SchemaOptional("visualization"): {
                    SchemaOptional("output_dir"): str,
                    SchemaOptional("default_format"): str,
                    SchemaOptional("include_networks"): bool,
                    SchemaOptional("include_volumes"): bool,
                    SchemaOptional("include_resources"): bool,
                },
                SchemaOptional("operations"): {
                    SchemaOptional("validate_before_up"): bool,
                    SchemaOptional("health_check_timeout"): int,
                    SchemaOptional("controlled_restart"): bool,
                    SchemaOptional("remove_orphans"): bool,
                },
            },
        },
        
        # AI provider settings
        SchemaOptional("ai"): {
            SchemaOptional("default_provider"): str,
            SchemaOptional("providers"): {
                SchemaOptional("claude"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("api_key"): str,
                    SchemaOptional("model"): str,
                    SchemaOptional("max_tokens"): int,
                    SchemaOptional("temperature"): float,
                },
                SchemaOptional("gemini"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("api_key"): str,
                    SchemaOptional("model"): str,
                    SchemaOptional("max_tokens"): int,
                    SchemaOptional("temperature"): float,
                },
                SchemaOptional("ollama"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("endpoint"): str,
                    SchemaOptional("model"): str,
                    SchemaOptional("auto_discover"): bool,
                    SchemaOptional("container_discovery"): bool,
                    SchemaOptional("container_name_patterns"): [str],
                },
            },
            SchemaOptional("usage_limits"): {
                SchemaOptional("max_daily_requests"): int,
                SchemaOptional("max_monthly_cost_usd"): float,
            },
            SchemaOptional("cost_management"): {
                SchemaOptional("require_confirmation"): bool,
                SchemaOptional("confirmation_threshold_usd"): float,
                SchemaOptional("max_daily_cost_usd"): float,
                SchemaOptional("max_monthly_cost_usd"): float,
            },
            SchemaOptional("plugins"): {
                SchemaOptional("enabled"): bool,
                SchemaOptional("directory"): str,
                SchemaOptional("auto_discover"): bool,
            },
            SchemaOptional("templates"): {
                SchemaOptional("directory"): str,
                SchemaOptional("default_version"): str,
                SchemaOptional("track_performance"): bool,
            },
        },
        
        # Monitoring settings
        SchemaOptional("monitoring"): {
            SchemaOptional("enabled"): bool,
            SchemaOptional("check_interval_seconds"): int,
            SchemaOptional("alert_on_container_exit"): bool,
            SchemaOptional("notify_on_high_resource_usage"): bool,
            SchemaOptional("resource_thresholds"): {
                SchemaOptional("cpu_percent"): int,
                SchemaOptional("memory_percent"): int,
                SchemaOptional("disk_percent"): int,
            },
            # Log monitoring settings
            SchemaOptional("log_monitoring"): {
                SchemaOptional("enabled"): bool,
                SchemaOptional("log_buffer_size"): int,
                SchemaOptional("max_recent_matches"): int,
                SchemaOptional("max_analysis_history"): int,
                SchemaOptional("max_search_history"): int,
                SchemaOptional("container_filter"): dict,
            },
            # Pattern recognition settings
            SchemaOptional("patterns_dir"): str,
            # Log analysis settings
            SchemaOptional("templates_dir"): str,
            # Issue detection settings
            SchemaOptional("issues_dir"): str,
            # Recommendation settings
            SchemaOptional("recommendations_dir"): str,
            SchemaOptional("recommendation_templates_dir"): str,
        },
        
        # Notification settings
        SchemaOptional("notifications"): {
            SchemaOptional("enabled"): bool,
            SchemaOptional("default_channel"): str,
            SchemaOptional("channels"): {
                SchemaOptional("email"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("smtp_server"): str,
                    SchemaOptional("smtp_port"): int,
                    SchemaOptional("username"): str,
                    SchemaOptional("password"): str,
                    SchemaOptional("from_address"): str,
                    SchemaOptional("recipients"): [str],
                    SchemaOptional("use_tls"): bool,
                    SchemaOptional("use_ssl"): bool,
                },
                SchemaOptional("slack"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("webhook_url"): str,
                    SchemaOptional("channel"): str,
                    SchemaOptional("username"): str,
                    SchemaOptional("icon_emoji"): str,
                    SchemaOptional("icon_url"): str,
                },
                SchemaOptional("discord"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("webhook_url"): str,
                    SchemaOptional("username"): str,
                    SchemaOptional("avatar_url"): str,
                },
                SchemaOptional("webhook"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("url"): str,
                    SchemaOptional("headers"): dict,
                },
            },
            SchemaOptional("preferences"): {
                SchemaOptional("throttling"): {
                    SchemaOptional("enabled"): bool,
                    SchemaOptional("max_notifications_per_hour"): int,
                    SchemaOptional("max_notifications_per_day"): int,
                    SchemaOptional("group_similar"): bool,
                    SchemaOptional("quiet_hours"): {
                        SchemaOptional("enabled"): bool,
                        SchemaOptional("start"): str,
                        SchemaOptional("end"): str,
                    },
                },
                SchemaOptional("severity_thresholds"): {
                    SchemaOptional("info"): bool,
                    SchemaOptional("warning"): bool,
                    SchemaOptional("error"): bool,
                    SchemaOptional("critical"): bool,
                },
                SchemaOptional("notification_types"): {
                    SchemaOptional("container_exit"): bool,
                    SchemaOptional("container_oom"): bool,
                    SchemaOptional("high_resource_usage"): bool,
                    SchemaOptional("security_issue"): bool,
                    SchemaOptional("update_available"): bool,
                    SchemaOptional("fix_proposal"): bool,
                    SchemaOptional("fix_applied"): bool,
                    SchemaOptional("custom"): bool,
                },
            },
            SchemaOptional("templates"): {
                SchemaOptional("directory"): str,
                SchemaOptional("default_template"): str,
            },
            SchemaOptional("fixes"): {
                SchemaOptional("require_approval"): bool,
                SchemaOptional("auto_approve_low_risk"): bool,
                SchemaOptional("dry_run_by_default"): bool,
                SchemaOptional("backup_before_fix"): bool,
                SchemaOptional("rollback_on_failure"): bool,
                SchemaOptional("max_fix_attempts"): int,
            },
        },
    })
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "general": {
            "log_level": "INFO",
            "log_file": "dockerforge.log",
            "data_dir": "~/.dockerforge/data",
            "backup_dir": "~/.dockerforge/backups",
            "check_for_updates": True,
        },
        "docker": {
            "host": None,
            "socket_path": None,
            "ssh_host": None,
            "tls": {
                "enabled": False,
                "verify": True,
                "cert_path": None,
                "key_path": None,
                "ca_path": None,
            },
            "compose": {
                "file_path": None,
                "project_name": None,
                "discovery": {
                    "enabled": True,
                    "recursive": True,
                    "include_common_locations": True,
                    "search_paths": [".", "~/docker", "~/projects"],
                    "exclude_patterns": ["**/node_modules/**", "**/.git/**"],
                },
                "parser": {
                    "schema_dir": "~/.dockerforge/schemas/compose",
                    "expand_env_vars": True,
                    "validate": True,
                },
                "change_management": {
                    "backup_dir": "~/.dockerforge/backups/compose",
                    "auto_backup": True,
                    "max_backups": 10,
                    "atomic_updates": True,
                },
                "templates": {
                    "directory": "~/.dockerforge/templates/compose",
                    "auto_load": True,
                    "variable_pattern": "{{variable}}",
                },
                "visualization": {
                    "output_dir": "~/.dockerforge/visualizations",
                    "default_format": "mermaid",
                    "include_networks": True,
                    "include_volumes": True,
                    "include_resources": True,
                },
                "operations": {
                    "validate_before_up": True,
                    "health_check_timeout": 30,
                    "controlled_restart": True,
                    "remove_orphans": True,
                },
            },
        },
        "ai": {
            "default_provider": "claude",
            "providers": {
                "claude": {
                    "enabled": True,
                    "api_key": None,
                    "model": "claude-3-opus",
                    "max_tokens": 4000,
                    "temperature": 0.7,
                },
                "gemini": {
                    "enabled": False,
                    "api_key": None,
                    "model": "gemini-pro",
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
                "ollama": {
                    "enabled": False,
                    "endpoint": "http://localhost:11434",
                    "model": "llama3",
                    "auto_discover": True,
                    "container_discovery": True,
                    "container_name_patterns": ["ollama", "llama"],
                },
            },
            "usage_limits": {
                "max_daily_requests": 100,
                "max_monthly_cost_usd": 50,
            },
            "cost_management": {
                "require_confirmation": True,
                "confirmation_threshold_usd": 0.5,
                "max_daily_cost_usd": 10.0,
                "max_monthly_cost_usd": 50.0,
            },
            "plugins": {
                "enabled": True,
                "directory": "~/.dockerforge/plugins",
                "auto_discover": True,
            },
            "templates": {
                "directory": "~/.dockerforge/templates",
                "default_version": "1.0.0",
                "track_performance": True,
            },
        },
        "monitoring": {
            "enabled": True,
            "check_interval_seconds": 300,
            "alert_on_container_exit": True,
            "notify_on_high_resource_usage": True,
            "resource_thresholds": {
                "cpu_percent": 80,
                "memory_percent": 85,
                "disk_percent": 90,
            },
            "log_monitoring": {
                "enabled": True,
                "log_buffer_size": 100000,
                "max_recent_matches": 1000,
                "max_analysis_history": 100,
                "max_search_history": 100,
                "container_filter": {},
            },
            "patterns_dir": "~/.dockerforge/patterns",
            "templates_dir": "~/.dockerforge/templates",
            "issues_dir": "~/.dockerforge/issues",
            "recommendations_dir": "~/.dockerforge/recommendations",
            "recommendation_templates_dir": "~/.dockerforge/recommendation_templates",
        },
        "notifications": {
            "enabled": True,
            "default_channel": "slack",
            "channels": {
                "email": {
                    "enabled": False,
                    "smtp_server": None,
                    "smtp_port": 587,
                    "username": None,
                    "password": None,
                    "from_address": "dockerforge@example.com",
                    "recipients": [],
                    "use_tls": True,
                    "use_ssl": False,
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": None,
                    "channel": "#docker-alerts",
                    "username": "DockerForge",
                    "icon_emoji": ":whale:",
                },
                "discord": {
                    "enabled": False,
                    "webhook_url": None,
                    "username": "DockerForge",
                    "avatar_url": "https://www.docker.com/sites/default/files/d8/2019-07/Moby-logo.png",
                },
                "webhook": {
                    "enabled": False,
                    "url": None,
                    "headers": {},
                },
            },
            "preferences": {
                "throttling": {
                    "enabled": True,
                    "max_notifications_per_hour": 10,
                    "max_notifications_per_day": 50,
                    "group_similar": True,
                    "quiet_hours": {
                        "enabled": False,
                        "start": "22:00",
                        "end": "08:00",
                    },
                },
                "severity_thresholds": {
                    "info": False,
                    "warning": True,
                    "error": True,
                    "critical": True,
                },
                "notification_types": {
                    "container_exit": True,
                    "container_oom": True,
                    "high_resource_usage": True,
                    "security_issue": True,
                    "update_available": True,
                    "fix_proposal": True,
                    "fix_applied": True,
                    "custom": True,
                },
            },
            "templates": {
                "directory": "~/.dockerforge/notification_templates",
                "default_template": "default",
            },
            "fixes": {
                "require_approval": True,
                "auto_approve_low_risk": False,
                "dry_run_by_default": True,
                "backup_before_fix": True,
                "rollback_on_failure": True,
                "max_fix_attempts": 3,
            },
        },
    }

    def __init__(self, config_path: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
            env_file: Path to the .env file
        """
        self.config_path = config_path
        self.env_file = env_file
        self.config = {}
        
        # Load environment variables
        if env_file:
            self._load_env_file(env_file)
        
        # Load configuration
        self._load_config()

    def _load_env_file(self, env_file: str) -> None:
        """
        Load environment variables from a .env file.
        
        Args:
            env_file: Path to the .env file
        """
        env_path = os.path.expanduser(env_file)
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.debug(f"Loaded environment variables from {env_path}")
        else:
            logger.warning(f"Environment file not found: {env_path}")

    def _load_config(self) -> None:
        """
        Load configuration from file.
        
        Raises:
            ConfigError: If configuration file is invalid
        """
        # Start with default configuration
        self.config = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Find configuration file
        config_path = self._find_config_file()
        if not config_path:
            logger.warning("No configuration file found, using defaults")
            return
        
        # Load configuration from file
        try:
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
            
            if file_config:
                # Substitute environment variables
                file_config = self._substitute_env_vars(file_config)
                
                # Validate configuration
                self._validate_config(file_config)
                
                # Merge with default configuration
                self._merge_configs(self.config, file_config)
                
                logger.info(f"Loaded configuration from {config_path}")
            else:
                logger.warning(f"Empty configuration file: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise ConfigError(f"Error loading configuration: {str(e)}")

    def _find_config_file(self) -> Optional[str]:
        """
        Find the configuration file.
        
        Returns:
            Optional[str]: Path to the configuration file or None
        """
        # Use specified config path if provided
        if self.config_path:
            path = os.path.expanduser(self.config_path)
            if os.path.exists(path):
                return path
            else:
                logger.warning(f"Specified configuration file not found: {path}")
        
        # Try default paths
        for path in self.DEFAULT_CONFIG_PATHS:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path
        
        return None

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Substitute environment variables in configuration values.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict[str, Any]: Configuration with substituted values
        """
        if not isinstance(config, dict):
            return config
        
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                result[key] = self._substitute_env_vars(value)
            elif isinstance(value, list):
                # Process lists
                result[key] = [
                    self._substitute_env_vars(item) if isinstance(item, dict) else
                    self._substitute_env_var(item) if isinstance(item, str) else
                    item
                    for item in value
                ]
            elif isinstance(value, str):
                # Substitute environment variables in strings
                result[key] = self._substitute_env_var(value)
            else:
                # Keep other values as is
                result[key] = value
        
        return result

    def _substitute_env_var(self, value: str) -> str:
        """
        Substitute environment variables in a string.
        
        Args:
            value: String value
            
        Returns:
            str: String with substituted environment variables
        """
        if not isinstance(value, str):
            return value
        
        # Match ${VAR} or $VAR patterns
        pattern = r'\${([^}]+)}|\$([a-zA-Z0-9_]+)'
        
        def replace_var(match):
            var_name = match.group(1) or match.group(2)
            return os.environ.get(var_name, match.group(0))
        
        return re.sub(pattern, replace_var, value)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ConfigError: If configuration is invalid
        """
        try:
            self.DEFAULT_CONFIG_SCHEMA.validate(config)
        except Exception as e:
            logger.error(f"Invalid configuration: {str(e)}")
            raise ConfigError(f"Invalid configuration: {str(e)}")

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Merge override configuration into base configuration.
        
        Args:
            base: Base configuration dictionary (modified in place)
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                self._merge_configs(base[key], value)
            else:
                # Override or add value
                base[key] = value

    def _deep_copy(self, obj: Any) -> Any:
        """
        Create a deep copy of an object.
        
        Args:
            obj: Object to copy
            
        Returns:
            Any: Deep copy of the object
        """
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            default: Default value if key is not found
            
        Returns:
            Any: Configuration value or default
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested keys)
            value: Configuration value
        """
        keys = key.split(".")
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Path to save configuration to (defaults to loaded path)
            
        Raises:
            ConfigError: If configuration cannot be saved
        """
        save_path = path or self.config_path
        if not save_path:
            # Find first writable path
            for path in self.DEFAULT_CONFIG_PATHS:
                expanded_path = os.path.expanduser(path)
                try:
                    # Check if directory is writable
                    directory = os.path.dirname(expanded_path)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    
                    # Use this path
                    save_path = expanded_path
                    break
                except (IOError, OSError):
                    continue
        
        if not save_path:
            raise ConfigError("No writable configuration path found")
        
        # Ensure directory exists
        directory = os.path.dirname(os.path.expanduser(save_path))
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except (IOError, OSError) as e:
                raise ConfigError(f"Could not create directory {directory}: {str(e)}")
        
        # Save configuration
        try:
            with open(os.path.expanduser(save_path), "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Saved configuration to {save_path}")
            self.config_path = save_path
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise ConfigError(f"Error saving configuration: {str(e)}")

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config = self._deep_copy(self.DEFAULT_CONFIG)
        logger.info("Reset configuration to defaults")


# Singleton instance
_config_manager = None


def get_config_manager(config_path: Optional[str] = None, env_file: Optional[str] = None) -> ConfigManager:
    """
    Get the configuration manager (singleton).
    
    Args:
        config_path: Path to the configuration file
        env_file: Path to the .env file
        
    Returns:
        ConfigManager: Configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path, env_file)
    elif config_path is not None or env_file is not None:
        # Reinitialize with new paths
        _config_manager = ConfigManager(config_path, env_file)
    
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value.
    
    Args:
        key: Configuration key (dot-separated for nested keys)
        default: Default value if key is not found
        
    Returns:
        Any: Configuration value or default
    """
    manager = get_config_manager()
    return manager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """
    Set a configuration value.
    
    Args:
        key: Configuration key (dot-separated for nested keys)
        value: Configuration value
    """
    manager = get_config_manager()
    manager.set(key, value)


def save_config(path: Optional[str] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        path: Path to save configuration to (defaults to loaded path)
        
    Raises:
        ConfigError: If configuration cannot be saved
    """
    manager = get_config_manager()
    manager.save(path)


def reset_config() -> None:
    """Reset configuration to defaults."""
    manager = get_config_manager()
    manager.reset()
