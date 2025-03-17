"""
DockerForge Optimization Engine

This module provides functionality for generating optimization recommendations for Docker containers
based on resource metrics, including resource right-sizing suggestions, cost optimization,
performance enhancement recommendations, bottleneck identification, and impact prediction.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading
from collections import defaultdict

from src.config.config_manager import ConfigManager
from src.resource_monitoring.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """
    Generates optimization recommendations for Docker containers.
    
    This class handles:
    - Resource right-sizing suggestions
    - Cost optimization
    - Performance enhancement recommendations
    - Bottleneck identification
    - Impact prediction
    """
    
    def __init__(self, config_manager: ConfigManager, metrics_collector: MetricsCollector):
        """
        Initialize the optimization engine.
        
        Args:
            config_manager: The configuration manager instance
            metrics_collector: The metrics collector instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.metrics_collector = metrics_collector
        
        # Optimization configuration
        self.optimization_config = self.config.get('resource_monitoring', {}).get('optimization', {})
        self.analysis_interval = self.optimization_config.get('analysis_interval', 3600)  # seconds
        self.lookback_period = self.optimization_config.get('lookback_period', 168)  # hours (1 week)
        self.cpu_threshold_high = self.optimization_config.get('cpu_threshold_high', 80)  # percentage
        self.cpu_threshold_low = self.optimization_config.get('cpu_threshold_low', 20)  # percentage
        self.memory_threshold_high = self.optimization_config.get('memory_threshold_high', 80)  # percentage
        self.memory_threshold_low = self.optimization_config.get('memory_threshold_low', 20)  # percentage
        self.disk_io_threshold = self.optimization_config.get('disk_io_threshold', 100000000)  # bytes per second
        self.network_io_threshold = self.optimization_config.get('network_io_threshold', 100000000)  # bytes per second
        
        # Analysis thread
        self.analysis_thread = None
        self.running = False
        
        # Recommendations history
        self.recommendations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    def start_analysis(self) -> None:
        """
        Start optimization analysis in a background thread.
        """
        if self.analysis_thread and self.analysis_thread.is_alive():
            logger.info("Optimization analysis is already running")
            return
            
        logger.info("Starting optimization analysis")
        self.running = True
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def stop_analysis(self) -> None:
        """
        Stop optimization analysis.
        """
        logger.info("Stopping optimization analysis")
        self.running = False
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
            
    def _analysis_loop(self) -> None:
        """
        Main optimization analysis loop.
        """
        while self.running:
            try:
                self.generate_recommendations()
                time.sleep(self.analysis_interval)
            except Exception as e:
                logger.error("Error in optimization analysis: %s", e)
                time.sleep(60)  # Wait a bit before retrying
                
    def generate_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate optimization recommendations for all containers.
        
        Returns:
            A dictionary of recommendations by container ID
        """
        # Get container metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=self.lookback_period)
        
        new_recommendations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Get all container summaries
        container_summaries = {}
        
        for container_id in self._get_active_containers():
            summary = self.metrics_collector.get_container_metrics_summary(container_id)
            if summary:
                container_summaries[container_id] = summary
                
        if not container_summaries:
            logger.info("No container metrics available for optimization analysis")
            return {}
            
        # Generate recommendations for each container
        for container_id, summary in container_summaries.items():
            # Resource right-sizing recommendations
            sizing_recs = self._generate_sizing_recommendations(container_id, summary)
            if sizing_recs:
                new_recommendations[container_id].extend(sizing_recs)
                
            # Performance recommendations
            perf_recs = self._generate_performance_recommendations(container_id, summary)
            if perf_recs:
                new_recommendations[container_id].extend(perf_recs)
                
            # Cost optimization recommendations
            cost_recs = self._generate_cost_recommendations(container_id, summary)
            if cost_recs:
                new_recommendations[container_id].extend(cost_recs)
                
        # Store recommendations
        for container_id, recs in new_recommendations.items():
            for rec in recs:
                rec['timestamp'] = datetime.now().isoformat()
                self.recommendations[container_id].append(rec)
                
        return new_recommendations
        
    def _get_active_containers(self) -> List[str]:
        """
        Get a list of active container IDs.
        
        Returns:
            A list of active container IDs
        """
        # Get system metrics to find active containers
        system_metrics = self.metrics_collector.get_system_metrics()
        
        # Extract container IDs from metrics data
        container_ids = []
        
        for container_id in self.metrics_collector.get_metrics().keys():
            container_ids.append(container_id)
            
        return container_ids
        
    def _generate_sizing_recommendations(self, container_id: str, 
                                        summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate resource right-sizing recommendations.
        
        Args:
            container_id: The container ID
            summary: The container metrics summary
            
        Returns:
            A list of sizing recommendations
        """
        recommendations = []
        
        # CPU right-sizing
        if 'cpu' in summary:
            cpu_data = summary['cpu']
            cpu_avg = cpu_data.get('average_usage_percent')
            cpu_max = cpu_data.get('max')
            
            if cpu_avg is not None and cpu_max is not None:
                # Check for CPU over-provisioning
                if cpu_max < self.cpu_threshold_low:
                    # Container is using less than 20% CPU even at peak
                    recommendations.append({
                        'type': 'sizing',
                        'resource': 'cpu',
                        'action': 'decrease',
                        'current_usage': cpu_max,
                        'recommended_limit': max(cpu_max * 1.5, 10),  # Add some headroom
                        'impact': 'low',
                        'description': f"CPU is over-provisioned. Maximum usage is {cpu_max:.1f}%, average is {cpu_avg:.1f}%. Consider reducing CPU limits.",
                        'command': f"docker update --cpus={max(cpu_max * 1.5, 10) / 100:.1f} {container_id[:12]}",
                    })
                    
                # Check for CPU under-provisioning
                elif cpu_max > self.cpu_threshold_high:
                    # Container is using more than 80% CPU at peak
                    recommendations.append({
                        'type': 'sizing',
                        'resource': 'cpu',
                        'action': 'increase',
                        'current_usage': cpu_max,
                        'recommended_limit': cpu_max * 1.5,  # Add 50% headroom
                        'impact': 'medium',
                        'description': f"CPU may be under-provisioned. Maximum usage is {cpu_max:.1f}%, average is {cpu_avg:.1f}%. Consider increasing CPU limits.",
                        'command': f"docker update --cpus={cpu_max * 1.5 / 100:.1f} {container_id[:12]}",
                    })
                    
        # Memory right-sizing
        if 'memory' in summary:
            memory_data = summary['memory']
            memory_avg = memory_data.get('average_usage_percent')
            memory_max = memory_data.get('max')
            
            if memory_avg is not None and memory_max is not None:
                # Check for memory over-provisioning
                if memory_max < self.memory_threshold_low:
                    # Container is using less than 20% memory even at peak
                    recommendations.append({
                        'type': 'sizing',
                        'resource': 'memory',
                        'action': 'decrease',
                        'current_usage': memory_max,
                        'recommended_limit': max(memory_max * 1.5, 10),  # Add some headroom
                        'impact': 'low',
                        'description': f"Memory is over-provisioned. Maximum usage is {memory_max:.1f}%, average is {memory_avg:.1f}%. Consider reducing memory limits.",
                        'command': f"docker update --memory={int(memory_max * 1.5)}m {container_id[:12]}",
                    })
                    
                # Check for memory under-provisioning
                elif memory_max > self.memory_threshold_high:
                    # Container is using more than 80% memory at peak
                    recommendations.append({
                        'type': 'sizing',
                        'resource': 'memory',
                        'action': 'increase',
                        'current_usage': memory_max,
                        'recommended_limit': memory_max * 1.5,  # Add 50% headroom
                        'impact': 'high',
                        'description': f"Memory may be under-provisioned. Maximum usage is {memory_max:.1f}%, average is {memory_avg:.1f}%. Consider increasing memory limits.",
                        'command': f"docker update --memory={int(memory_max * 1.5)}m {container_id[:12]}",
                    })
                    
        return recommendations
        
    def _generate_performance_recommendations(self, container_id: str, 
                                             summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate performance enhancement recommendations.
        
        Args:
            container_id: The container ID
            summary: The container metrics summary
            
        Returns:
            A list of performance recommendations
        """
        recommendations = []
        
        # Check for disk I/O bottlenecks
        if 'disk' in summary:
            disk_data = summary['disk']
            disk_read_rate = disk_data.get('read_rate_bytes_per_sec')
            disk_write_rate = disk_data.get('write_rate_bytes_per_sec')
            
            if disk_read_rate is not None and disk_write_rate is not None:
                total_io_rate = disk_read_rate + disk_write_rate
                
                if total_io_rate > self.disk_io_threshold:
                    # High disk I/O detected
                    recommendations.append({
                        'type': 'performance',
                        'resource': 'disk',
                        'issue': 'high_io',
                        'current_rate': total_io_rate,
                        'threshold': self.disk_io_threshold,
                        'impact': 'medium',
                        'description': f"High disk I/O detected: {total_io_rate / 1000000:.1f} MB/s. Consider using volume mounts with higher performance or optimizing I/O patterns.",
                        'suggestions': [
                            "Use volume mounts with higher performance",
                            "Optimize I/O patterns in the application",
                            "Consider using a tmpfs mount for temporary files",
                            "Use a volume driver optimized for your workload"
                        ]
                    })
                    
        # Check for network bottlenecks
        if 'network' in summary:
            network_data = summary['network']
            network_rx_rate = network_data.get('rx_rate_bytes_per_sec')
            network_tx_rate = network_data.get('tx_rate_bytes_per_sec')
            
            if network_rx_rate is not None and network_tx_rate is not None:
                total_network_rate = network_rx_rate + network_tx_rate
                
                if total_network_rate > self.network_io_threshold:
                    # High network I/O detected
                    recommendations.append({
                        'type': 'performance',
                        'resource': 'network',
                        'issue': 'high_io',
                        'current_rate': total_network_rate,
                        'threshold': self.network_io_threshold,
                        'impact': 'medium',
                        'description': f"High network I/O detected: {total_network_rate / 1000000:.1f} MB/s. Consider optimizing network usage or using a different network driver.",
                        'suggestions': [
                            "Optimize network usage in the application",
                            "Use a different network driver",
                            "Consider using a CDN for content delivery",
                            "Implement caching to reduce network traffic"
                        ]
                    })
                    
        # Check for CPU throttling
        if 'cpu' in summary:
            cpu_data = summary['cpu']
            cpu_max = cpu_data.get('max')
            
            if cpu_max is not None and cpu_max > 90:
                # CPU usage is very high, might be throttled
                recommendations.append({
                    'type': 'performance',
                    'resource': 'cpu',
                    'issue': 'potential_throttling',
                    'current_usage': cpu_max,
                    'impact': 'high',
                    'description': f"CPU usage is very high ({cpu_max:.1f}%), which may lead to throttling. Consider increasing CPU limits or optimizing the application.",
                    'suggestions': [
                        "Increase CPU limits",
                        "Optimize CPU-intensive operations",
                        "Consider scaling horizontally with multiple containers",
                        "Profile the application to identify CPU bottlenecks"
                    ]
                })
                
        return recommendations
        
    def _generate_cost_recommendations(self, container_id: str, 
                                      summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate cost optimization recommendations.
        
        Args:
            container_id: The container ID
            summary: The container metrics summary
            
        Returns:
            A list of cost optimization recommendations
        """
        recommendations = []
        
        # Check for resource utilization patterns
        cpu_avg = summary.get('cpu', {}).get('average_usage_percent')
        memory_avg = summary.get('memory', {}).get('average_usage_percent')
        
        if cpu_avg is not None and memory_avg is not None:
            # Check for consistently low resource utilization
            if cpu_avg < 10 and memory_avg < 10:
                # Very low resource utilization
                recommendations.append({
                    'type': 'cost',
                    'resource': 'general',
                    'issue': 'low_utilization',
                    'cpu_usage': cpu_avg,
                    'memory_usage': memory_avg,
                    'impact': 'medium',
                    'description': f"Container has very low resource utilization (CPU: {cpu_avg:.1f}%, Memory: {memory_avg:.1f}%). Consider consolidating with other containers or reducing resource limits.",
                    'suggestions': [
                        "Consolidate with other containers",
                        "Reduce resource limits",
                        "Consider using a smaller container image",
                        "Evaluate if this container is necessary"
                    ],
                    'estimated_savings': 'Medium'
                })
                
        # Check for potential resource sharing
        if 'metadata' in summary:
            # This is a simplified recommendation - in a real implementation,
            # you would analyze multiple containers to identify consolidation opportunities
            recommendations.append({
                'type': 'cost',
                'resource': 'general',
                'issue': 'consolidation_opportunity',
                'impact': 'low',
                'description': "Consider using Docker Compose or Kubernetes to manage related containers and optimize resource sharing.",
                'suggestions': [
                    "Use Docker Compose for related containers",
                    "Consider Kubernetes for orchestration",
                    "Implement resource quotas",
                    "Use resource limits consistently"
                ],
                'estimated_savings': 'Low to Medium'
            })
            
        return recommendations
        
    def get_recommendations(self, container_id: Optional[str] = None,
                           recommendation_type: Optional[str] = None,
                           resource: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get optimization recommendations.
        
        Args:
            container_id: Optional container ID to filter by
            recommendation_type: Optional recommendation type to filter by
            resource: Optional resource type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            
        Returns:
            A dictionary of recommendations by container ID
        """
        result = {}
        
        # Filter by container ID
        if container_id:
            if container_id in self.recommendations:
                result[container_id] = self._filter_recommendations(
                    self.recommendations[container_id],
                    recommendation_type,
                    resource,
                    start_time,
                    end_time
                )
        else:
            # Include all containers
            for c_id, recs in self.recommendations.items():
                filtered = self._filter_recommendations(
                    recs,
                    recommendation_type,
                    resource,
                    start_time,
                    end_time
                )
                
                if filtered:
                    result[c_id] = filtered
                    
        return result
        
    def _filter_recommendations(self, recommendations: List[Dict[str, Any]],
                               recommendation_type: Optional[str] = None,
                               resource: Optional[str] = None,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Filter recommendations by various criteria.
        
        Args:
            recommendations: The recommendations to filter
            recommendation_type: Optional recommendation type to filter by
            resource: Optional resource type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            
        Returns:
            Filtered recommendations
        """
        filtered = []
        
        for rec in recommendations:
            # Filter by recommendation type
            if recommendation_type and rec.get('type') != recommendation_type:
                continue
                
            # Filter by resource
            if resource and rec.get('resource') != resource:
                continue
                
            # Filter by time range
            if start_time or end_time:
                timestamp = datetime.fromisoformat(rec['timestamp'])
                
                if start_time and timestamp < start_time:
                    continue
                    
                if end_time and timestamp > end_time:
                    continue
                    
            filtered.append(rec)
            
        return filtered
        
    def generate_optimization_report(self, container_id: Optional[str] = None,
                                    format: str = 'text') -> str:
        """
        Generate an optimization report.
        
        Args:
            container_id: Optional container ID to filter by
            format: The output format ('text', 'json', 'html')
            
        Returns:
            The optimization report as a string
        """
        # Get recommendations
        recommendations = self.get_recommendations(container_id)
        
        if not recommendations:
            return "No optimization recommendations available."
            
        if format == 'json':
            return json.dumps(recommendations, indent=2)
        elif format == 'html':
            return self._generate_html_report(recommendations)
        else:
            return self._generate_text_report(recommendations)
            
    def _generate_text_report(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate a text-based optimization report.
        
        Args:
            recommendations: The recommendations by container ID
            
        Returns:
            The report as a string
        """
        lines = ["DockerForge Optimization Report", "=" * 80, ""]
        
        for container_id, container_recs in recommendations.items():
            lines.append(f"Container: {container_id}")
            lines.append("-" * 80)
            
            # Group recommendations by type
            recs_by_type = defaultdict(list)
            for rec in container_recs:
                recs_by_type[rec.get('type', 'other')].append(rec)
                
            # Process each type
            for rec_type, type_recs in recs_by_type.items():
                lines.append(f"\n{rec_type.capitalize()} Recommendations:")
                
                for i, rec in enumerate(type_recs, 1):
                    lines.append(f"\n{i}. {rec.get('description', 'No description')}")
                    
                    if 'impact' in rec:
                        lines.append(f"   Impact: {rec['impact'].capitalize()}")
                        
                    if 'suggestions' in rec:
                        lines.append("   Suggestions:")
                        for suggestion in rec['suggestions']:
                            lines.append(f"   - {suggestion}")
                            
                    if 'command' in rec:
                        lines.append(f"   Command: {rec['command']}")
                        
            lines.append("\n" + "=" * 80 + "\n")
            
        return "\n".join(lines)
        
    def _generate_html_report(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate an HTML optimization report.
        
        Args:
            recommendations: The recommendations by container ID
            
        Returns:
            The report as an HTML string
        """
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DockerForge Optimization Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        .container { margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .recommendation { margin-bottom: 20px; padding: 10px; border-left: 4px solid #ccc; }
        .sizing { border-left-color: #4CAF50; }
        .performance { border-left-color: #2196F3; }
        .cost { border-left-color: #FFC107; }
        .impact-low { color: #4CAF50; }
        .impact-medium { color: #FFC107; }
        .impact-high { color: #F44336; }
        .suggestions { margin-top: 10px; }
        .command { background-color: #f5f5f5; padding: 8px; border-radius: 4px; font-family: monospace; }
    </style>
</head>
<body>
    <h1>DockerForge Optimization Report</h1>
    <p>Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
"""
        
        for container_id, container_recs in recommendations.items():
            html += f"""
    <div class="container">
        <h2>Container: {container_id}</h2>
"""
            
            # Group recommendations by type
            recs_by_type = defaultdict(list)
            for rec in container_recs:
                recs_by_type[rec.get('type', 'other')].append(rec)
                
            # Process each type
            for rec_type, type_recs in recs_by_type.items():
                html += f"""
        <h3>{rec_type.capitalize()} Recommendations</h3>
"""
                
                for rec in type_recs:
                    impact = rec.get('impact', 'unknown')
                    html += f"""
        <div class="recommendation {rec_type}">
            <p>{rec.get('description', 'No description')}</p>
            <p>Impact: <span class="impact-{impact}">{impact.capitalize()}</span></p>
"""
                    
                    if 'suggestions' in rec:
                        html += """
            <div class="suggestions">
                <p>Suggestions:</p>
                <ul>
"""
                        for suggestion in rec['suggestions']:
                            html += f"""
                    <li>{suggestion}</li>
"""
                        html += """
                </ul>
            </div>
"""
                        
                    if 'command' in rec:
                        html += f"""
            <div class="command">{rec['command']}</div>
"""
                        
                    html += """
        </div>
"""
                    
            html += """
    </div>
"""
            
        html += """
</body>
</html>
"""
        
        return html
