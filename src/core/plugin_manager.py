"""
Plugin manager module for DockerForge.

This module provides functionality to load and manage AI provider plugins.
"""

import importlib
import importlib.util
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from src.config.config_manager import get_config
from src.core.ai_provider import AIProvider, AIProviderError
from src.utils.logging_manager import get_logger

logger = get_logger("plugin_manager")


class PluginError(Exception):
    """Exception raised for plugin errors."""

    pass


class PluginMetadata:
    """Metadata for a plugin."""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        provider_class: str,
        dependencies: List[str] = None,
    ):
        """
        Initialize plugin metadata.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description
            author: Plugin author
            provider_class: Provider class name
            dependencies: List of dependencies
        """
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.provider_class = provider_class
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary.

        Returns:
            Dict[str, Any]: Metadata as dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "provider_class": self.provider_class,
            "dependencies": self.dependencies,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """
        Create metadata from dictionary.

        Args:
            data: Metadata data

        Returns:
            PluginMetadata: Metadata instance
        """
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author", "Unknown"),
            provider_class=data["provider_class"],
            dependencies=data.get("dependencies", []),
        )

    @classmethod
    def from_file(cls, filepath: str) -> "PluginMetadata":
        """
        Create metadata from file.

        Args:
            filepath: Path to metadata file

        Returns:
            PluginMetadata: Metadata instance

        Raises:
            PluginError: If metadata file is invalid
        """
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            return cls.from_dict(data)
        except Exception as e:
            raise PluginError(f"Invalid plugin metadata file: {str(e)}")


class Plugin:
    """A plugin for DockerForge."""

    def __init__(self, metadata: PluginMetadata, module_path: str):
        """
        Initialize a plugin.

        Args:
            metadata: Plugin metadata
            module_path: Path to plugin module
        """
        self.metadata = metadata
        self.module_path = module_path
        self.module = None
        self.provider_class = None
        self.loaded = False

    def load(self) -> bool:
        """
        Load the plugin.

        Returns:
            bool: True if loaded successfully

        Raises:
            PluginError: If plugin cannot be loaded
        """
        if self.loaded:
            return True

        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                f"dockerforge_plugin_{self.metadata.name}", self.module_path
            )
            if spec is None:
                raise PluginError(f"Could not load plugin module: {self.module_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            self.module = module

            # Get the provider class
            if not hasattr(module, self.metadata.provider_class):
                raise PluginError(
                    f"Provider class not found: {self.metadata.provider_class}"
                )

            provider_class = getattr(module, self.metadata.provider_class)

            # Check if it's a subclass of AIProvider
            if not issubclass(provider_class, AIProvider):
                raise PluginError(
                    f"Provider class must be a subclass of AIProvider: {self.metadata.provider_class}"
                )

            self.provider_class = provider_class
            self.loaded = True

            logger.info(
                f"Loaded plugin: {self.metadata.name} (v{self.metadata.version})"
            )
            return True
        except Exception as e:
            raise PluginError(f"Error loading plugin {self.metadata.name}: {str(e)}")

    def create_provider(self, **kwargs) -> AIProvider:
        """
        Create a provider instance.

        Args:
            **kwargs: Provider constructor arguments

        Returns:
            AIProvider: Provider instance

        Raises:
            PluginError: If provider cannot be created
        """
        if not self.loaded:
            self.load()

        try:
            return self.provider_class(**kwargs)
        except Exception as e:
            raise PluginError(f"Error creating provider: {str(e)}")


class PluginManager:
    """Manager for DockerForge plugins."""

    def __init__(self):
        """Initialize the plugin manager."""
        # Get plugins directory from config
        plugins_dir = get_config("ai.plugins.directory", "~/.dockerforge/plugins")
        self.plugins_dir = os.path.expanduser(plugins_dir)
        os.makedirs(self.plugins_dir, exist_ok=True)

        # Add plugins directory to Python path
        if self.plugins_dir not in sys.path:
            sys.path.append(self.plugins_dir)

        # Load plugins
        self.plugins = {}
        if get_config("ai.plugins.enabled", True):
            self.discover_plugins()

    def discover_plugins(self):
        """Discover and load plugins."""
        if not os.path.exists(self.plugins_dir):
            return

        # Look for plugin directories
        for item in os.listdir(self.plugins_dir):
            plugin_dir = os.path.join(self.plugins_dir, item)

            # Check if it's a directory
            if not os.path.isdir(plugin_dir):
                continue

            # Check for metadata file
            metadata_file = os.path.join(plugin_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                continue

            try:
                # Load metadata
                metadata = PluginMetadata.from_file(metadata_file)

                # Check for main module
                module_file = os.path.join(plugin_dir, "plugin.py")
                if not os.path.exists(module_file):
                    logger.warning(f"Plugin module not found: {module_file}")
                    continue

                # Create plugin
                plugin = Plugin(metadata, module_file)

                # Add to plugins
                self.plugins[metadata.name] = plugin

                logger.debug(
                    f"Discovered plugin: {metadata.name} (v{metadata.version})"
                )
            except Exception as e:
                logger.error(f"Error discovering plugin in {plugin_dir}: {str(e)}")

    def load_plugin(self, name: str) -> bool:
        """
        Load a plugin by name.

        Args:
            name: Plugin name

        Returns:
            bool: True if loaded successfully

        Raises:
            PluginError: If plugin cannot be loaded
        """
        if name not in self.plugins:
            raise PluginError(f"Plugin not found: {name}")

        return self.plugins[name].load()

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Optional[Plugin]: Plugin or None if not found
        """
        return self.plugins.get(name)

    def create_provider(self, name: str, **kwargs) -> AIProvider:
        """
        Create a provider from a plugin.

        Args:
            name: Plugin name
            **kwargs: Provider constructor arguments

        Returns:
            AIProvider: Provider instance

        Raises:
            PluginError: If provider cannot be created
        """
        plugin = self.get_plugin(name)
        if plugin is None:
            raise PluginError(f"Plugin not found: {name}")

        return plugin.create_provider(**kwargs)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all plugins.

        Returns:
            List[Dict[str, Any]]: List of plugin information
        """
        return [
            {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "description": plugin.metadata.description,
                "author": plugin.metadata.author,
                "loaded": plugin.loaded,
            }
            for plugin in self.plugins.values()
        ]


# Singleton instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    Get the plugin manager (singleton).

    Returns:
        PluginManager: Plugin manager
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()

    return _plugin_manager


def get_plugin_provider(name: str, **kwargs) -> AIProvider:
    """
    Get a provider from a plugin.

    Args:
        name: Plugin name
        **kwargs: Provider constructor arguments

    Returns:
        AIProvider: Provider instance

    Raises:
        AIProviderError: If provider cannot be created
    """
    try:
        return get_plugin_manager().create_provider(name, **kwargs)
    except PluginError as e:
        raise AIProviderError(f"Error creating provider from plugin: {str(e)}")


def create_plugin_template(name: str, output_dir: Optional[str] = None) -> str:
    """
    Create a template for a new plugin.

    Args:
        name: Plugin name
        output_dir: Output directory (default: plugins directory)

    Returns:
        str: Path to created plugin directory

    Raises:
        PluginError: If plugin template cannot be created
    """
    # Normalize name
    name = name.lower().replace(" ", "_")

    # Get output directory
    if output_dir is None:
        output_dir = get_plugin_manager().plugins_dir

    # Create plugin directory
    plugin_dir = os.path.join(output_dir, name)
    if os.path.exists(plugin_dir):
        raise PluginError(f"Plugin directory already exists: {plugin_dir}")

    try:
        os.makedirs(plugin_dir, exist_ok=True)

        # Create metadata file
        metadata = {
            "name": name,
            "version": "0.1.0",
            "description": f"DockerForge AI provider plugin: {name}",
            "author": "Your Name",
            "provider_class": f"{name.capitalize()}Provider",
            "dependencies": [],
        }

        with open(os.path.join(plugin_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        # Create plugin module
        plugin_code = f'''"""
DockerForge AI provider plugin: {name}

This module provides a custom AI provider for DockerForge.
"""

from typing import Dict, Any, Optional

from src.core.ai_provider import AIProvider, AIProviderError


class {name.capitalize()}Provider(AIProvider):
    """Custom AI provider for DockerForge."""
    
    def __init__(self):
        """Initialize the provider."""
        # Add your initialization code here
        pass
    
    def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Analyze a query with context.
        
        Args:
            context: Context information
            query: Query to analyze
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        # Add your analysis code here
        return {{
            "provider": "{name}",
            "analysis": "This is a placeholder analysis.",
        }}
    
    def generate_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix for an issue.
        
        Args:
            issue: Issue information
            
        Returns:
            Dict[str, Any]: Fix information
        """
        # Add your fix generation code here
        return {{
            "provider": "{name}",
            "fix": "This is a placeholder fix.",
        }}
    
    def validate_credentials(self) -> bool:
        """
        Validate provider credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        # Add your credential validation code here
        return True
    
    def estimate_cost(self, input_text: str, expected_output_length: int = 500) -> Dict[str, Any]:
        """
        Estimate the cost of an API call.
        
        Args:
            input_text: Input text for the API call
            expected_output_length: Expected length of the output in tokens
            
        Returns:
            Dict[str, Any]: Cost estimation information
        """
        # Add your cost estimation code here
        return {{
            "provider": "{name}",
            "input_tokens": self.get_token_count(input_text),
            "output_tokens": expected_output_length,
            "input_cost_usd": 0.0,
            "output_cost_usd": 0.0,
            "estimated_cost_usd": 0.0,
        }}
    
    def report_capabilities(self) -> Dict[str, Any]:
        """
        Report provider capabilities.
        
        Returns:
            Dict[str, Any]: Provider capabilities
        """
        # Add your capabilities reporting code here
        return {{
            "streaming": False,
            "vision": False,
            "batching": False,
            "function_calling": False,
            "token_counting": False,
        }}
'''

        with open(os.path.join(plugin_dir, "plugin.py"), "w") as f:
            f.write(plugin_code)

        # Create README file
        readme = f"""# {name.capitalize()} Provider Plugin

A custom AI provider plugin for DockerForge.

## Installation

1. Copy this directory to your DockerForge plugins directory:
   ```
   cp -r {name} ~/.dockerforge/plugins/
   ```

2. Enable the plugin in your DockerForge configuration:
   ```yaml
   ai:
     plugins:
       enabled: true
       directory: ~/.dockerforge/plugins
   ```

3. Restart DockerForge.

## Usage

```python
from src.core.plugin_manager import get_plugin_provider

# Create provider
provider = get_plugin_provider("{name}")

# Use provider
result = provider.analyze(context, query)
```

## Configuration

Add any configuration options to your DockerForge configuration:

```yaml
ai:
  providers:
    {name}:
      enabled: true
      # Add your configuration options here
```

## Development

Modify the `plugin.py` file to implement your custom provider.
"""

        with open(os.path.join(plugin_dir, "README.md"), "w") as f:
            f.write(readme)

        logger.info(f"Created plugin template: {plugin_dir}")
        return plugin_dir
    except Exception as e:
        raise PluginError(f"Error creating plugin template: {str(e)}")
