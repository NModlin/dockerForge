"""
DockerForge Compose Visualization Module.

This module provides functionality for generating visualizations of Docker Compose files,
including service dependency graphs, network relationship visualizations, volume mapping
diagrams, and resource allocation charts.
"""

import os
import json
import yaml
import tempfile
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from pathlib import Path

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)


class Visualization:
    """Generate visualizations for Docker Compose files."""

    def __init__(self, config: Dict = None):
        """Initialize Visualization.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.output_dir = self._get_output_dir()

    def _get_output_dir(self) -> str:
        """Get the output directory path.

        Returns:
            Path to the output directory
        """
        output_dir = self.config.get('output_dir', os.path.expanduser('~/.dockerforge/visualizations'))
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def generate_dependency_graph(self, compose_data: Dict, output_format: str = 'mermaid') -> str:
        """Generate a service dependency graph.

        Args:
            compose_data: Docker Compose data
            output_format: Output format ('mermaid', 'dot', 'json')

        Returns:
            Graph in the specified format
        """
        try:
            # Extract services and dependencies
            services = compose_data.get('services', {})
            dependencies = {}
            
            # Build dependency map
            for service_name, service_def in services.items():
                deps = []
                
                # Check 'depends_on'
                if 'depends_on' in service_def:
                    depends_on = service_def['depends_on']
                    if isinstance(depends_on, list):
                        deps.extend(depends_on)
                    elif isinstance(depends_on, dict):
                        deps.extend(depends_on.keys())
                
                # Check 'links'
                if 'links' in service_def:
                    links = service_def['links']
                    for link in links:
                        # Handle 'service:alias' format
                        if ':' in link:
                            service = link.split(':', 1)[0]
                            deps.append(service)
                        else:
                            deps.append(link)
                
                dependencies[service_name] = deps
            
            # Generate graph based on format
            if output_format == 'mermaid':
                return self._generate_mermaid_dependency_graph(services, dependencies)
            elif output_format == 'dot':
                return self._generate_dot_dependency_graph(services, dependencies)
            elif output_format == 'json':
                return json.dumps({
                    'services': list(services.keys()),
                    'dependencies': dependencies
                }, indent=2)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        except Exception as e:
            logger.error(f"Failed to generate dependency graph: {e}")
            raise

    def _generate_mermaid_dependency_graph(self, services: Dict, dependencies: Dict) -> str:
        """Generate a Mermaid dependency graph.

        Args:
            services: Services dictionary
            dependencies: Dependencies dictionary

        Returns:
            Mermaid graph string
        """
        mermaid = ["graph TD;"]
        
        # Add nodes
        for service_name in services:
            # Escape special characters in service names
            safe_name = service_name.replace('-', '_').replace(' ', '_')
            mermaid.append(f"    {safe_name}[\"{service_name}\"];")
        
        # Add edges
        for service_name, deps in dependencies.items():
            safe_name = service_name.replace('-', '_').replace(' ', '_')
            for dep in deps:
                safe_dep = dep.replace('-', '_').replace(' ', '_')
                mermaid.append(f"    {safe_dep} --> {safe_name};")
        
        return '\n'.join(mermaid)

    def _generate_dot_dependency_graph(self, services: Dict, dependencies: Dict) -> str:
        """Generate a DOT dependency graph.

        Args:
            services: Services dictionary
            dependencies: Dependencies dictionary

        Returns:
            DOT graph string
        """
        dot = ["digraph G {"]
        dot.append("    rankdir=LR;")
        
        # Add nodes
        for service_name in services:
            dot.append(f'    "{service_name}";')
        
        # Add edges
        for service_name, deps in dependencies.items():
            for dep in deps:
                dot.append(f'    "{dep}" -> "{service_name}";')
        
        dot.append("}")
        return '\n'.join(dot)

    def generate_network_graph(self, compose_data: Dict, output_format: str = 'mermaid') -> str:
        """Generate a network relationship visualization.

        Args:
            compose_data: Docker Compose data
            output_format: Output format ('mermaid', 'dot', 'json')

        Returns:
            Graph in the specified format
        """
        try:
            # Extract services and networks
            services = compose_data.get('services', {})
            networks = compose_data.get('networks', {})
            
            # Build network map
            service_networks = {}
            for service_name, service_def in services.items():
                if 'networks' in service_def:
                    service_networks[service_name] = list(service_def['networks'].keys()) if isinstance(service_def['networks'], dict) else service_def['networks']
                else:
                    # Default network
                    service_networks[service_name] = ['default']
            
            # Generate graph based on format
            if output_format == 'mermaid':
                return self._generate_mermaid_network_graph(services, networks, service_networks)
            elif output_format == 'dot':
                return self._generate_dot_network_graph(services, networks, service_networks)
            elif output_format == 'json':
                return json.dumps({
                    'services': list(services.keys()),
                    'networks': list(networks.keys()),
                    'service_networks': service_networks
                }, indent=2)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        except Exception as e:
            logger.error(f"Failed to generate network graph: {e}")
            raise

    def _generate_mermaid_network_graph(self, services: Dict, networks: Dict, service_networks: Dict) -> str:
        """Generate a Mermaid network graph.

        Args:
            services: Services dictionary
            networks: Networks dictionary
            service_networks: Service to networks mapping

        Returns:
            Mermaid graph string
        """
        mermaid = ["graph TD;"]
        
        # Add network nodes
        for network_name in networks:
            safe_name = f"net_{network_name.replace('-', '_').replace(' ', '_')}"
            mermaid.append(f"    {safe_name}[\"Network: {network_name}\"];")
        
        # Add default network if not defined but used
        if 'default' not in networks and any('default' in nets for nets in service_networks.values()):
            mermaid.append(f"    net_default[\"Network: default\"];")
        
        # Add service nodes
        for service_name in services:
            safe_name = f"svc_{service_name.replace('-', '_').replace(' ', '_')}"
            mermaid.append(f"    {safe_name}[\"{service_name}\"];")
        
        # Add edges
        for service_name, network_list in service_networks.items():
            safe_service = f"svc_{service_name.replace('-', '_').replace(' ', '_')}"
            for network in network_list:
                safe_network = f"net_{network.replace('-', '_').replace(' ', '_')}"
                mermaid.append(f"    {safe_service} --- {safe_network};")
        
        return '\n'.join(mermaid)

    def _generate_dot_network_graph(self, services: Dict, networks: Dict, service_networks: Dict) -> str:
        """Generate a DOT network graph.

        Args:
            services: Services dictionary
            networks: Networks dictionary
            service_networks: Service to networks mapping

        Returns:
            DOT graph string
        """
        dot = ["graph G {"]
        dot.append("    rankdir=LR;")
        
        # Add network nodes
        for network_name in networks:
            dot.append(f'    "{network_name}" [shape=cloud];')
        
        # Add default network if not defined but used
        if 'default' not in networks and any('default' in nets for nets in service_networks.values()):
            dot.append(f'    "default" [shape=cloud];')
        
        # Add service nodes
        for service_name in services:
            dot.append(f'    "{service_name}" [shape=box];')
        
        # Add edges
        for service_name, network_list in service_networks.items():
            for network in network_list:
                dot.append(f'    "{service_name}" -- "{network}";')
        
        dot.append("}")
        return '\n'.join(dot)

    def generate_volume_graph(self, compose_data: Dict, output_format: str = 'mermaid') -> str:
        """Generate a volume mapping diagram.

        Args:
            compose_data: Docker Compose data
            output_format: Output format ('mermaid', 'dot', 'json')

        Returns:
            Graph in the specified format
        """
        try:
            # Extract services and volumes
            services = compose_data.get('services', {})
            volumes = compose_data.get('volumes', {})
            
            # Build volume map
            service_volumes = {}
            for service_name, service_def in services.items():
                if 'volumes' in service_def:
                    service_volumes[service_name] = []
                    for volume in service_def['volumes']:
                        if isinstance(volume, str):
                            # Parse volume string
                            parts = volume.split(':')
                            if len(parts) >= 2:
                                source = parts[0]
                                if source in volumes:
                                    # Named volume
                                    service_volumes[service_name].append(source)
            
            # Generate graph based on format
            if output_format == 'mermaid':
                return self._generate_mermaid_volume_graph(services, volumes, service_volumes)
            elif output_format == 'dot':
                return self._generate_dot_volume_graph(services, volumes, service_volumes)
            elif output_format == 'json':
                return json.dumps({
                    'services': list(services.keys()),
                    'volumes': list(volumes.keys()),
                    'service_volumes': service_volumes
                }, indent=2)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        except Exception as e:
            logger.error(f"Failed to generate volume graph: {e}")
            raise

    def _generate_mermaid_volume_graph(self, services: Dict, volumes: Dict, service_volumes: Dict) -> str:
        """Generate a Mermaid volume graph.

        Args:
            services: Services dictionary
            volumes: Volumes dictionary
            service_volumes: Service to volumes mapping

        Returns:
            Mermaid graph string
        """
        mermaid = ["graph TD;"]
        
        # Add volume nodes
        for volume_name in volumes:
            safe_name = f"vol_{volume_name.replace('-', '_').replace(' ', '_')}"
            mermaid.append(f"    {safe_name}[\"Volume: {volume_name}\"];")
        
        # Add service nodes
        for service_name in services:
            safe_name = f"svc_{service_name.replace('-', '_').replace(' ', '_')}"
            mermaid.append(f"    {safe_name}[\"{service_name}\"];")
        
        # Add edges
        for service_name, volume_list in service_volumes.items():
            safe_service = f"svc_{service_name.replace('-', '_').replace(' ', '_')}"
            for volume in volume_list:
                safe_volume = f"vol_{volume.replace('-', '_').replace(' ', '_')}"
                mermaid.append(f"    {safe_service} --- {safe_volume};")
        
        return '\n'.join(mermaid)

    def _generate_dot_volume_graph(self, services: Dict, volumes: Dict, service_volumes: Dict) -> str:
        """Generate a DOT volume graph.

        Args:
            services: Services dictionary
            volumes: Volumes dictionary
            service_volumes: Service to volumes mapping

        Returns:
            DOT graph string
        """
        dot = ["graph G {"]
        dot.append("    rankdir=LR;")
        
        # Add volume nodes
        for volume_name in volumes:
            dot.append(f'    "{volume_name}" [shape=cylinder];')
        
        # Add service nodes
        for service_name in services:
            dot.append(f'    "{service_name}" [shape=box];')
        
        # Add edges
        for service_name, volume_list in service_volumes.items():
            for volume in volume_list:
                dot.append(f'    "{service_name}" -- "{volume}";')
        
        dot.append("}")
        return '\n'.join(dot)

    def generate_resource_chart(self, compose_data: Dict, output_format: str = 'mermaid') -> str:
        """Generate a resource allocation chart.

        Args:
            compose_data: Docker Compose data
            output_format: Output format ('mermaid', 'json')

        Returns:
            Chart in the specified format
        """
        try:
            # Extract services and resource limits
            services = compose_data.get('services', {})
            
            # Build resource map
            resources = {}
            for service_name, service_def in services.items():
                if 'deploy' in service_def and 'resources' in service_def['deploy']:
                    res = service_def['deploy']['resources']
                    limits = res.get('limits', {})
                    reservations = res.get('reservations', {})
                    
                    resources[service_name] = {
                        'limits': {
                            'cpu': limits.get('cpus', 'unlimited'),
                            'memory': limits.get('memory', 'unlimited')
                        },
                        'reservations': {
                            'cpu': reservations.get('cpus', 'none'),
                            'memory': reservations.get('memory', 'none')
                        }
                    }
            
            # Generate chart based on format
            if output_format == 'mermaid':
                return self._generate_mermaid_resource_chart(services, resources)
            elif output_format == 'json':
                return json.dumps({
                    'services': list(services.keys()),
                    'resources': resources
                }, indent=2)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
        except Exception as e:
            logger.error(f"Failed to generate resource chart: {e}")
            raise

    def _generate_mermaid_resource_chart(self, services: Dict, resources: Dict) -> str:
        """Generate a Mermaid resource chart.

        Args:
            services: Services dictionary
            resources: Resources dictionary

        Returns:
            Mermaid chart string
        """
        mermaid = ["graph TD;"]
        
        # Add service nodes with resource info
        for service_name, resource_info in resources.items():
            safe_name = service_name.replace('-', '_').replace(' ', '_')
            limits = resource_info['limits']
            reservations = resource_info['reservations']
            
            label = f"{service_name}<br/>CPU Limit: {limits['cpu']}<br/>Memory Limit: {limits['memory']}<br/>"
            label += f"CPU Reservation: {reservations['cpu']}<br/>Memory Reservation: {reservations['memory']}"
            
            mermaid.append(f"    {safe_name}[\"{label}\"];")
        
        return '\n'.join(mermaid)

    def save_visualization(self, content: str, filename: str, format_type: str) -> str:
        """Save a visualization to a file.

        Args:
            content: Visualization content
            filename: Base filename
            format_type: Format type ('mermaid', 'dot', 'json')

        Returns:
            Path to the saved file
        """
        try:
            # Create file path
            if format_type == 'mermaid':
                ext = '.mmd'
            elif format_type == 'dot':
                ext = '.dot'
            elif format_type == 'json':
                ext = '.json'
            else:
                ext = '.txt'
            
            file_path = os.path.join(self.output_dir, f"{filename}{ext}")
            
            # Save to file
            with open(file_path, 'w') as f:
                f.write(content)
            
            logger.info(f"Saved visualization to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save visualization: {e}")
            raise

    def render_visualization(self, content: str, format_type: str, output_format: str = 'png') -> Optional[str]:
        """Render a visualization to an image.

        Args:
            content: Visualization content
            format_type: Format type ('mermaid', 'dot')
            output_format: Output format ('png', 'svg', 'pdf')

        Returns:
            Path to the rendered image or None if rendering failed
        """
        try:
            # Create temporary file for content
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{format_type}") as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Create output file path
            output_path = os.path.join(self.output_dir, f"visualization.{output_format}")
            
            # Render based on format type
            if format_type == 'mermaid':
                # In a real implementation, we would use a Mermaid CLI tool or API
                # For now, we'll just return None
                logger.warning("Mermaid rendering not implemented")
                return None
            elif format_type == 'dot':
                # In a real implementation, we would use Graphviz
                # For now, we'll just return None
                logger.warning("DOT rendering not implemented")
                return None
            else:
                logger.warning(f"Unsupported format type for rendering: {format_type}")
                return None
        except Exception as e:
            logger.error(f"Failed to render visualization: {e}")
            return None
        finally:
            # Clean up temporary file
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
