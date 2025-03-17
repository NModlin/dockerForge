# Example_plugin Provider Plugin

A custom AI provider plugin for DockerForge.

## Installation

1. Copy this directory to your DockerForge plugins directory:
   ```
   cp -r example_plugin ~/.dockerforge/plugins/
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
provider = get_plugin_provider("example_plugin")

# Use provider
result = provider.analyze(context, query)
```

## Configuration

Add any configuration options to your DockerForge configuration:

```yaml
ai:
  providers:
    example_plugin:
      enabled: true
      # Add your configuration options here
```

## Development

Modify the `plugin.py` file to implement your custom provider.
