#!/usr/bin/env python3
"""
DockerForge Phase 2 Usage Examples

This script demonstrates how to use the new features implemented in Phase 2.
"""

import json
import os
from typing import Dict, Any, Callable

# Import DockerForge modules
from src.core.ai_provider import get_ai_provider, AIProviderFactory
from src.core.ai_usage_tracker import AIUsageTracker
from src.core.prompt_template import get_template_manager, render_template
from src.core.plugin_manager import get_plugin_manager, create_plugin_template
from src.core.troubleshooter import get_troubleshooter
from src.config.config_manager import get_config


def example_cost_management():
    """Example of using the cost management system."""
    print("\n=== Cost Management Example ===\n")
    
    # Get AI provider
    provider = get_ai_provider()
    
    # Estimate cost of a query
    query = "Analyze this Docker Compose file for security issues and best practices."
    compose_file = """
    version: '3'
    services:
      web:
        image: nginx:latest
        ports:
          - "80:80"
        volumes:
          - ./html:/usr/share/nginx/html
      db:
        image: postgres:13
        environment:
          POSTGRES_PASSWORD: example
    """
    
    # Combine for cost estimation
    input_text = f"{query}\n\n{compose_file}"
    
    # Estimate cost
    cost_info = provider.estimate_cost(input_text)
    
    # Print cost information
    print(f"Provider: {cost_info['provider']}")
    print(f"Model: {cost_info['model']}")
    print(f"Input tokens: {cost_info['input_tokens']}")
    print(f"Output tokens: {cost_info['output_tokens']}")
    print(f"Input cost: ${cost_info['input_cost_usd']:.6f}")
    print(f"Output cost: ${cost_info['output_cost_usd']:.6f}")
    print(f"Total estimated cost: ${cost_info['estimated_cost_usd']:.6f}")
    
    # Check if cost is within budget
    is_within_budget = provider.confirm_cost(cost_info)
    print(f"Is within budget: {is_within_budget}")
    
    # Get usage tracker
    if hasattr(provider, 'usage_tracker') and provider.usage_tracker:
        # Get daily usage
        daily_usage = provider.usage_tracker.get_daily_usage()
        print(f"\nDaily usage: ${daily_usage['total_cost_usd']:.4f}")
        
        # Get monthly usage
        import datetime
        now = datetime.datetime.now()
        monthly_usage = provider.usage_tracker.get_monthly_usage(now.year, now.month)
        print(f"Monthly usage: ${monthly_usage['total_cost_usd']:.4f}")
        
        # Get budget status
        budget_status = provider.usage_tracker.check_budget_status()
        print(f"Budget remaining: ${budget_status['total_remaining_usd']:.4f}")
        print(f"Budget usage: {budget_status['total_percentage']:.2f}%")


def example_template_system():
    """Example of using the template system."""
    print("\n=== Template System Example ===\n")
    
    # Get template manager
    template_manager = get_template_manager()
    
    # Create a template
    dockerfile_analysis_template = template_manager.create_template(
        name="dockerfile_analysis",
        template="""
You are DockerForge AI, an expert in Docker.

Analyze the following Dockerfile and provide insights on:
1. Security concerns
2. Performance optimizations
3. Best practices
4. Potential issues

Dockerfile:
```dockerfile
{dockerfile}
```

System information:
{system_info}

Provide a comprehensive analysis with specific recommendations for improvements.
        """,
        version="1.0.0",
        description="Template for analyzing Dockerfiles",
        variables=["dockerfile", "system_info"]
    )
    
    # Print template information
    print(f"Created template: {dockerfile_analysis_template.name} (v{dockerfile_analysis_template.version})")
    print(f"Description: {dockerfile_analysis_template.description}")
    print(f"Variables: {dockerfile_analysis_template.variables}")
    
    # Render the template
    dockerfile = """
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "app.py"]
    """
    
    system_info = {
        "platform": "linux",
        "architecture": "x86_64",
        "docker_version": "24.0.5"
    }
    
    rendered = render_template(
        "dockerfile_analysis",
        dockerfile=dockerfile,
        system_info=json.dumps(system_info, indent=2)
    )
    
    # Print rendered template
    print("\nRendered template:")
    print("------------------")
    print(rendered[:500] + "...\n")
    
    # Update template metrics
    dockerfile_analysis_template.update_metrics(success=True, tokens=1200)
    print(f"Updated metrics: {dockerfile_analysis_template.performance_metrics}")
    
    # List all templates
    templates = template_manager.list_templates()
    print(f"\nAvailable templates: {len(templates)}")
    for template in templates:
        print(f"- {template['name']} (v{template['version']}): {template['description']}")


def example_plugin_system():
    """Example of using the plugin system."""
    print("\n=== Plugin System Example ===\n")
    
    # Get plugin manager
    plugin_manager = get_plugin_manager()
    
    # List available plugins
    plugins = plugin_manager.list_plugins()
    print(f"Available plugins: {len(plugins)}")
    for plugin in plugins:
        print(f"- {plugin['name']} (v{plugin['version']}): {plugin['description']}")
    
    # Create a plugin template
    try:
        output_dir = os.path.join(os.getcwd(), "examples", "plugins")
        plugin_dir = create_plugin_template("example_plugin", output_dir)
        print(f"\nCreated plugin template at: {plugin_dir}")
    except Exception as e:
        print(f"Error creating plugin template: {str(e)}")
    
    # List available providers
    providers = AIProviderFactory.list_available_providers()
    print("\nAvailable AI providers:")
    for name, info in providers.items():
        status = "Enabled" if info["enabled"] else "Disabled"
        provider_type = info["type"].capitalize()
        print(f"- {name}: {status} ({provider_type})")


def example_streaming_response():
    """Example of using streaming responses."""
    print("\n=== Streaming Response Example ===\n")
    
    # Get AI provider
    provider = get_ai_provider()
    
    # Check if provider supports streaming
    capabilities = provider.report_capabilities()
    if not capabilities.get("streaming", False):
        print(f"Provider {provider.__class__.__name__} does not support streaming")
        return
    
    print(f"Provider {provider.__class__.__name__} supports streaming")
    
    # Define callback function
    def stream_callback(chunk: str):
        print(chunk, end="", flush=True)
    
    # Prepare context and query
    context = {
        "container": {
            "name": "example-container",
            "status": "exited",
            "logs": "Error: Connection refused"
        }
    }
    query = "What might be causing this container to exit?"
    
    print("\nStreaming response:")
    print("------------------")
    
    # Use streaming analysis (this would actually stream in a real environment)
    try:
        provider.streaming_analyze(context, query, stream_callback)
        print("\n")
    except Exception as e:
        print(f"\nError in streaming: {str(e)}")


def example_ollama_container_detection():
    """Example of Ollama container detection."""
    print("\n=== Ollama Container Detection Example ===\n")
    
    # Check if Ollama is enabled
    if not get_config("ai.providers.ollama.enabled", False):
        print("Ollama provider is not enabled")
        return
    
    # Check if container discovery is enabled
    if not get_config("ai.providers.ollama.container_discovery", False):
        print("Ollama container discovery is not enabled")
        return
    
    # Get Ollama provider
    try:
        from src.core.ai_provider import OllamaProvider
        provider = OllamaProvider()
        
        # Print endpoint information
        print(f"Ollama endpoint: {provider.endpoint}")
        print(f"Ollama model: {provider.model}")
        
        # Try to discover container
        provider._discover_ollama_container()
        
        # Print updated endpoint information
        print(f"After discovery:")
        print(f"Ollama endpoint: {provider.endpoint}")
        print(f"Ollama model: {provider.model}")
    except Exception as e:
        print(f"Error in Ollama container detection: {str(e)}")


def main():
    """Run all examples."""
    print("DockerForge Phase 2 Usage Examples")
    print("=================================")
    
    # Run examples
    try:
        example_cost_management()
    except Exception as e:
        print(f"Error in cost management example: {str(e)}")
    
    try:
        example_template_system()
    except Exception as e:
        print(f"Error in template system example: {str(e)}")
    
    try:
        example_plugin_system()
    except Exception as e:
        print(f"Error in plugin system example: {str(e)}")
    
    try:
        example_streaming_response()
    except Exception as e:
        print(f"Error in streaming response example: {str(e)}")
    
    try:
        example_ollama_container_detection()
    except Exception as e:
        print(f"Error in Ollama container detection example: {str(e)}")


if __name__ == "__main__":
    main()
