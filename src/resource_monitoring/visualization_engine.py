"""
DockerForge Visualization Engine

This module provides functionality for visualizing and reporting Docker container resource metrics,
including time-series charts, resource heatmaps, comparative analysis, and scheduled report generation.
"""

import base64
import csv
import io
import json
import logging
import os
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.config.config_manager import ConfigManager
from src.resource_monitoring.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Generates visualizations and reports for Docker container resource metrics.

    This class handles:
    - Time-series charts
    - Resource heatmaps
    - Comparative analysis
    - Scheduled report generation
    - Export to multiple formats
    """

    def __init__(
        self, config_manager: ConfigManager, metrics_collector: MetricsCollector
    ):
        """
        Initialize the visualization engine.

        Args:
            config_manager: The configuration manager instance
            metrics_collector: The metrics collector instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.metrics_collector = metrics_collector

        # Visualization configuration
        self.visualization_config = self.config.get("resource_monitoring", {}).get(
            "visualization", {}
        )
        self.output_dir = self.visualization_config.get(
            "output_dir", "~/.dockerforge/visualizations"
        )
        self.output_dir = os.path.expanduser(self.output_dir)
        self.default_format = self.visualization_config.get("default_format", "png")
        self.chart_width = self.visualization_config.get("chart_width", 800)
        self.chart_height = self.visualization_config.get("chart_height", 400)
        self.color_scheme = self.visualization_config.get("color_scheme", "default")

        # Scheduled reports
        self.scheduled_reports = self.visualization_config.get("scheduled_reports", [])
        self.report_thread = None
        self.running = False

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Optional dependencies
        self.has_matplotlib = False
        self.has_plotly = False
        self.has_pandas = False

        try:
            import matplotlib

            self.has_matplotlib = True
        except ImportError:
            logger.warning(
                "Matplotlib not available, some visualization features will be limited"
            )

        try:
            import plotly

            self.has_plotly = True
        except ImportError:
            logger.warning(
                "Plotly not available, some visualization features will be limited"
            )

        try:
            import pandas

            self.has_pandas = True
        except ImportError:
            logger.warning(
                "Pandas not available, some data processing features will be limited"
            )

    def start_scheduled_reports(self) -> None:
        """
        Start the scheduled report generation thread.
        """
        if self.report_thread and self.report_thread.is_alive():
            logger.info("Scheduled reports are already running")
            return

        logger.info("Starting scheduled report generation")
        self.running = True
        self.report_thread = threading.Thread(target=self._report_loop)
        self.report_thread.daemon = True
        self.report_thread.start()

    def stop_scheduled_reports(self) -> None:
        """
        Stop the scheduled report generation thread.
        """
        logger.info("Stopping scheduled report generation")
        self.running = False
        if self.report_thread:
            self.report_thread.join(timeout=5)

    def _report_loop(self) -> None:
        """
        Main loop for scheduled report generation.
        """
        last_run_times = {report["name"]: None for report in self.scheduled_reports}

        while self.running:
            try:
                current_time = datetime.now()

                for report in self.scheduled_reports:
                    report_name = report["name"]
                    interval = report.get(
                        "interval", 24 * 60 * 60
                    )  # Default: daily (in seconds)

                    # Check if it's time to run this report
                    if (
                        last_run_times[report_name] is None
                        or (current_time - last_run_times[report_name]).total_seconds()
                        >= interval
                    ):

                        # Generate the report
                        try:
                            self.generate_report(
                                report.get("containers", []),
                                report.get(
                                    "metrics", ["cpu", "memory", "disk", "network"]
                                ),
                                report.get("duration", 24),  # Default: 24 hours
                                report.get("format", self.default_format),
                                report.get(
                                    "output_file",
                                    f"{report_name}_{current_time.strftime('%Y%m%d_%H%M%S')}",
                                ),
                            )
                            last_run_times[report_name] = current_time
                            logger.info("Generated scheduled report: %s", report_name)
                        except Exception as e:
                            logger.error(
                                "Error generating scheduled report %s: %s",
                                report_name,
                                e,
                            )

                # Sleep for a minute before checking again
                time.sleep(60)
            except Exception as e:
                logger.error("Error in report scheduler: %s", e)
                time.sleep(60)  # Wait a bit before retrying

    def generate_time_series_chart(
        self,
        container_id: str,
        metric_type: str,
        duration: int = 1,  # hours
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a time-series chart for a specific container and metric.

        Args:
            container_id: The container ID
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The duration to look back in hours
            format: The output format (png, svg, html, json)
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Get metrics data
        metrics_data = self.metrics_collector.get_metrics_history(
            container_id, metric_type, timedelta(hours=duration)
        )

        if not metrics_data:
            logger.warning(
                "No metrics data available for container %s, metric %s",
                container_id,
                metric_type,
            )
            return None

        # Prepare data for visualization
        timestamps = []
        values = {}

        for entry in metrics_data:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            timestamps.append(timestamp)

            data = entry["data"]
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    if key not in values:
                        values[key] = []
                    values[key].append(value)

        # Select appropriate visualization method based on available libraries
        if format.lower() in ["json", "csv"]:
            return self._export_time_series_data(
                container_id, metric_type, timestamps, values, format, output_file
            )
        elif self.has_plotly and format.lower() in ["html", "interactive"]:
            return self._generate_plotly_time_series(
                container_id, metric_type, timestamps, values, output_file
            )
        elif self.has_matplotlib:
            return self._generate_matplotlib_time_series(
                container_id, metric_type, timestamps, values, format, output_file
            )
        else:
            # Fallback to text-based visualization
            return self._generate_text_time_series(
                container_id, metric_type, timestamps, values, output_file
            )

    def _generate_matplotlib_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a time-series chart using Matplotlib.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter

            # Create figure and axis
            fig, ax = plt.subplots(
                figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100
            )

            # Plot each metric
            for key, vals in values.items():
                if len(timestamps) == len(vals):
                    ax.plot(timestamps, vals, label=key)

            # Format the chart
            ax.set_title(
                f"{metric_type.capitalize()} Usage for Container {container_id[:12]}"
            )
            ax.set_xlabel("Time")

            # Set y-axis label based on metric type
            if metric_type == "cpu":
                ax.set_ylabel("CPU Usage (%)")
            elif metric_type == "memory":
                ax.set_ylabel("Memory Usage (%)")
            elif metric_type == "disk":
                ax.set_ylabel("Disk I/O (bytes)")
            elif metric_type == "network":
                ax.set_ylabel("Network Traffic (bytes)")
            else:
                ax.set_ylabel("Value")

            # Format x-axis
            ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
            plt.xticks(rotation=45)

            # Add legend if multiple metrics
            if len(values) > 1:
                ax.legend()

            # Adjust layout
            plt.tight_layout()

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format}"):
                    output_file = f"{output_file}.{format}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save the figure
            plt.savefig(output_file, format=format)
            plt.close(fig)

            return output_file
        except Exception as e:
            logger.error("Error generating Matplotlib time series: %s", e)
            return None

    def _generate_plotly_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an interactive time-series chart using Plotly.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # Create figure
            fig = make_subplots(specs=[[{"secondary_y": False}]])

            # Add traces for each metric
            for key, vals in values.items():
                if len(timestamps) == len(vals):
                    fig.add_trace(
                        go.Scatter(x=timestamps, y=vals, name=key, mode="lines"),
                        secondary_y=False,
                    )

            # Update layout
            fig.update_layout(
                title=f"{metric_type.capitalize()} Usage for Container {container_id[:12]}",
                xaxis_title="Time",
                legend_title="Metrics",
                width=self.chart_width,
                height=self.chart_height,
                hovermode="x unified",
            )

            # Set y-axis title based on metric type
            if metric_type == "cpu":
                fig.update_yaxes(title_text="CPU Usage (%)", secondary_y=False)
            elif metric_type == "memory":
                fig.update_yaxes(title_text="Memory Usage (%)", secondary_y=False)
            elif metric_type == "disk":
                fig.update_yaxes(title_text="Disk I/O (bytes)", secondary_y=False)
            elif metric_type == "network":
                fig.update_yaxes(
                    title_text="Network Traffic (bytes)", secondary_y=False
                )
            else:
                fig.update_yaxes(title_text="Value", secondary_y=False)

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".html"):
                    output_file = f"{output_file}.html"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            fig.write_html(output_file)

            return output_file
        except Exception as e:
            logger.error("Error generating Plotly time series: %s", e)
            return None

    def _generate_text_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a text-based time-series visualization.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            output_file: Optional output file path

        Returns:
            The path to the generated file, or None if generation failed
        """
        try:
            # Create a simple text-based visualization
            lines = [
                f"{metric_type.capitalize()} Usage for Container {container_id[:12]}"
            ]
            lines.append("=" * 80)
            lines.append(
                "Timestamp"
                + " " * 20
                + " | "
                + " | ".join(f"{key:>10}" for key in values.keys())
            )
            lines.append("-" * 80)

            # Add data rows
            for i, timestamp in enumerate(timestamps):
                if i < len(timestamps):
                    row = [timestamp.strftime("%Y-%m-%d %H:%M:%S")]
                    for key in values.keys():
                        if i < len(values[key]):
                            row.append(f"{values[key][i]:10.2f}")
                        else:
                            row.append(" " * 10)
                    lines.append(" | ".join(row))

            # Save the text visualization
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".txt"):
                    output_file = f"{output_file}.txt"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            return output_file
        except Exception as e:
            logger.error("Error generating text time series: %s", e)
            return None

    def _export_time_series_data(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export time-series data to a file.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            format: The output format (json or csv)
            output_file: Optional output file path

        Returns:
            The path to the exported file, or None if export failed
        """
        try:
            # Prepare data for export
            export_data = []
            for i, timestamp in enumerate(timestamps):
                if i < len(timestamps):
                    row = {
                        "timestamp": timestamp.isoformat(),
                        "container_id": container_id,
                        "metric_type": metric_type,
                    }
                    for key in values.keys():
                        if i < len(values[key]):
                            row[key] = values[key][i]
                    export_data.append(row)

            # Save the data
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format.lower()}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format.lower()}"):
                    output_file = f"{output_file}.{format.lower()}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            if format.lower() == "json":
                with open(output_file, "w") as f:
                    json.dump(export_data, f, indent=2)
            elif format.lower() == "csv":
                with open(output_file, "w", newline="") as f:
                    if export_data:
                        fieldnames = export_data[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(export_data)

            return output_file
        except Exception as e:
            logger.error("Error exporting time series data: %s", e)
            return None

    def generate_resource_heatmap(
        self,
        metric_type: str,
        duration: int = 24,
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a resource heatmap showing usage across all containers.

        Args:
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The duration to look back in hours
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Get metrics data for all containers
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=duration)

        metrics = self.metrics_collector.get_metrics(
            container_id=None,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
        )

        if not metrics:
            logger.warning("No metrics data available for heatmap generation")
            return None

        # Prepare data for heatmap
        container_data = {}
        all_timestamps = set()

        for container_id, container_metrics in metrics.items():
            if metric_type in container_metrics:
                container_data[container_id] = {}

                for entry in container_metrics[metric_type]:
                    timestamp = datetime.fromisoformat(entry["timestamp"])
                    all_timestamps.add(timestamp)

                    # Extract the main value based on metric type
                    if metric_type == "cpu":
                        value = entry["data"].get("usage_percent", 0)
                    elif metric_type == "memory":
                        value = entry["data"].get("usage_percent", 0)
                    elif metric_type == "disk":
                        value = entry["data"].get("read_bytes", 0) + entry["data"].get(
                            "write_bytes", 0
                        )
                    elif metric_type == "network":
                        value = entry["data"].get("rx_bytes", 0) + entry["data"].get(
                            "tx_bytes", 0
                        )
                    else:
                        # Try to find a numeric value
                        for k, v in entry["data"].items():
                            if isinstance(v, (int, float)):
                                value = v
                                break
                        else:
                            value = 0

                    container_data[container_id][timestamp] = value

        # Convert to sorted lists for visualization
        sorted_timestamps = sorted(all_timestamps)
        sorted_containers = sorted(container_data.keys())

        # Create the heatmap data matrix
        heatmap_data = []
        for container_id in sorted_containers:
            container_values = []
            for timestamp in sorted_timestamps:
                container_values.append(
                    container_data.get(container_id, {}).get(timestamp, 0)
                )
            heatmap_data.append(container_values)

        # Select appropriate visualization method based on available libraries
        if self.has_matplotlib:
            return self._generate_matplotlib_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                format,
                output_file,
            )
        elif self.has_plotly:
            return self._generate_plotly_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                output_file,
            )
        else:
            # Fallback to text-based visualization
            return self._generate_text_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                output_file,
            )

    def _generate_matplotlib_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a heatmap using Matplotlib.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.dates import DateFormatter

            # Create figure and axis
            fig, ax = plt.subplots(
                figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100
            )

            # Create the heatmap
            im = ax.imshow(data, aspect="auto", cmap="viridis")

            # Set labels
            ax.set_title(f"{metric_type.capitalize()} Usage Heatmap")
            ax.set_xlabel("Time")
            ax.set_ylabel("Container")

            # Set y-axis ticks (container IDs)
            ax.set_yticks(np.arange(len(containers)))
            ax.set_yticklabels([c[:12] for c in containers])

            # Set x-axis ticks (timestamps)
            # Use a subset of timestamps to avoid overcrowding
            num_ticks = min(10, len(timestamps))
            if num_ticks > 0:
                tick_indices = np.linspace(0, len(timestamps) - 1, num_ticks, dtype=int)
                ax.set_xticks(tick_indices)
                ax.set_xticklabels(
                    [timestamps[i].strftime("%H:%M:%S") for i in tick_indices]
                )
                plt.xticks(rotation=45)

            # Add colorbar
            cbar = ax.figure.colorbar(im, ax=ax)
            if metric_type == "cpu" or metric_type == "memory":
                cbar.ax.set_ylabel("Usage (%)", rotation=-90, va="bottom")
            elif metric_type == "disk":
                cbar.ax.set_ylabel("Disk I/O (bytes)", rotation=-90, va="bottom")
            elif metric_type == "network":
                cbar.ax.set_ylabel("Network Traffic (bytes)", rotation=-90, va="bottom")
            else:
                cbar.ax.set_ylabel("Value", rotation=-90, va="bottom")

            # Adjust layout
            plt.tight_layout()

            # Save the heatmap
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"heatmap_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format}"):
                    output_file = f"{output_file}.{format}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save the figure
            plt.savefig(output_file, format=format)
            plt.close(fig)

            return output_file
        except Exception as e:
            logger.error("Error generating Matplotlib heatmap: %s", e)
            return None

    def _generate_plotly_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an interactive heatmap using Plotly.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        try:
            import numpy as np
            import plotly.graph_objects as go

            # Format timestamps
            time_labels = [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps]

            # Format container IDs
            container_labels = [c[:12] for c in containers]

            # Create the heatmap
            fig = go.Figure(
                data=go.Heatmap(
                    z=data,
                    x=time_labels,
                    y=container_labels,
                    colorscale="Viridis",
                    hovertemplate="Container: %{y}<br>Time: %{x}<br>Value: %{z}<extra></extra>",
                )
            )

            # Update layout
            fig.update_layout(
                title=f"{metric_type.capitalize()} Usage Heatmap",
                xaxis_title="Time",
                yaxis_title="Container",
                width=self.chart_width,
                height=self.chart_height,
            )

            # Set colorbar title based on metric type
            if metric_type == "cpu" or metric_type == "memory":
                fig.update_traces(colorbar_title="Usage (%)")
            elif metric_type == "disk":
                fig.update_traces(colorbar_title="Disk I/O (bytes)")
            elif metric_type == "network":
                fig.update_traces(colorbar_title="Network Traffic (bytes)")
            else:
                fig.update_traces(colorbar_title="Value")

            # Save the heatmap
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"heatmap_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".html"):
                    output_file = f"{output_file}.html"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            fig.write_html(output_file)

            return output_file
        except Exception as e:
            logger.error("Error generating Plotly heatmap: %s", e)
            return None

    def _generate_text_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a text-based heatmap visualization.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            output_file: Optional output file path

        Returns:
            The path to the generated file, or None if generation failed
        """
        try:
            # Create a simple text-based visualization
            lines = [f"{metric_type.capitalize()} Usage Heatmap"]
            lines.append("=" * 80)

            # Add header row with timestamps
            # Use a subset of timestamps to avoid overcrowding
            num_ticks = min(10, len(timestamps))
            if num_ticks > 0:
                import numpy as np

                tick_indices = np.linspace(0, len(timestamps) - 1, num_ticks, dtype=int)
                header = "Container" + " " * 10 + " | "
                header += " | ".join(
                    f"{timestamps[i].strftime('%H:%M:%S'):>8}" for i in tick_indices
                )
                lines.append(header)
                lines.append("-" * 80)

                # Add data rows
                for i, container_id in enumerate(containers):
                    if i < len(data):
                        row = f"{container_id[:12]:<20} | "
                        row_values = []
                        for idx in tick_indices:
                            if idx < len(data[i]):
                                # Format the value based on magnitude
                                value = data[i][idx]
                                if value < 0.01:
                                    row_values.append("       .")
                                elif value < 1:
                                    row_values.append("      *")
                                elif value < 10:
                                    row_values.append("     **")
                                elif value < 100:
                                    row_values.append("    ***")
                                elif value < 1000:
                                    row_values.append("   ****")
                                else:
                                    row_values.append("  *****")
                            else:
                                row_values.append("        ")
                        row += " | ".join(row_values)
                        lines.append(row)

            # Save the text visualization
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"heatmap_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".txt"):
                    output_file = f"{output_file}.txt"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            return output_file
        except Exception as e:
            logger.error("Error generating text heatmap: %s", e)
            return None

    def generate_comparative_analysis(
        self,
        container_ids: List[str],
        metric_type: str,
        duration: int = 24,
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a comparative analysis of multiple containers for a specific metric.

        Args:
            container_ids: List of container IDs to compare
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The duration to look back in hours
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated analysis file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Get metrics data for all specified containers
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=duration)

        all_metrics = {}
        for container_id in container_ids:
            metrics = self.metrics_collector.get_metrics(
                container_id=container_id,
                metric_type=metric_type,
                start_time=start_time,
                end_time=end_time,
            )
            if (
                metrics
                and container_id in metrics
                and metric_type in metrics[container_id]
            ):
                all_metrics[container_id] = metrics[container_id][metric_type]

        if not all_metrics:
            logger.warning("No metrics data available for comparative analysis")
            return None

        # Prepare data for visualization
        container_data = {}
        all_timestamps = set()

        for container_id, metrics_data in all_metrics.items():
            container_data[container_id] = {}

            for entry in metrics_data:
                timestamp = datetime.fromisoformat(entry["timestamp"])
                all_timestamps.add(timestamp)

                # Extract the main value based on metric type
                if metric_type == "cpu":
                    value = entry["data"].get("usage_percent", 0)
                elif metric_type == "memory":
                    value = entry["data"].get("usage_percent", 0)
                elif metric_type == "disk":
                    value = entry["data"].get("read_bytes", 0) + entry["data"].get(
                        "write_bytes", 0
                    )
                elif metric_type == "network":
                    value = entry["data"].get("rx_bytes", 0) + entry["data"].get(
                        "tx_bytes", 0
                    )
                else:
                    # Try to find a numeric value
                    for k, v in entry["data"].items():
                        if isinstance(v, (int, float)):
                            value = v
                            break
                    else:
                        value = 0

                container_data[container_id][timestamp] = value

        # Convert to sorted lists for visualization
        sorted_timestamps = sorted(all_timestamps)

        # Create the data for visualization
        plot_data = {}
        for container_id, timestamps_data in container_data.items():
            values = []
            for timestamp in sorted_timestamps:
                values.append(timestamps_data.get(timestamp, 0))
            plot_data[container_id] = values

        # Select appropriate visualization method based on available libraries
        if format.lower() in ["json", "csv"]:
            return self._export_comparative_data(
                container_ids,
                metric_type,
                sorted_timestamps,
                plot_data,
                format,
                output_file,
            )
        elif self.has_plotly and format.lower() in ["html", "interactive"]:
            return self._generate_plotly_comparative(
                container_ids, metric_type, sorted_timestamps, plot_data, output_file
            )
        elif self.has_matplotlib:
            return self._generate_matplotlib_comparative(
                container_ids,
                metric_type,
                sorted_timestamps,
                plot_data,
                format,
                output_file,
            )
        else:
            # Fallback to text-based visualization
            return self._generate_text_comparative(
                container_ids, metric_type, sorted_timestamps, plot_data, output_file
            )

    def _generate_matplotlib_comparative(
        self,
        container_ids: List[str],
        metric_type: str,
        timestamps: List[datetime],
        data: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a comparative analysis chart using Matplotlib.

        Args:
            container_ids: The container IDs
            metric_type: The metric type
            timestamps: The timestamps
            data: The data for each container
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter

            # Create figure and axis
            fig, ax = plt.subplots(
                figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100
            )

            # Plot each container's data
            for container_id, values in data.items():
                if len(timestamps) == len(values):
                    ax.plot(timestamps, values, label=container_id[:12])

            # Format the chart
            ax.set_title(f"Comparative {metric_type.capitalize()} Usage")
            ax.set_xlabel("Time")

            # Set y-axis label based on metric type
            if metric_type == "cpu":
                ax.set_ylabel("CPU Usage (%)")
            elif metric_type == "memory":
                ax.set_ylabel("Memory Usage (%)")
            elif metric_type == "disk":
                ax.set_ylabel("Disk I/O (bytes)")
            elif metric_type == "network":
                ax.set_ylabel("Network Traffic (bytes)")
            else:
                ax.set_ylabel("Value")

            # Format x-axis
            ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
            plt.xticks(rotation=45)

            # Add legend
            ax.legend()

            # Adjust layout
            plt.tight_layout()

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"comparative_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format}"):
                    output_file = f"{output_file}.{format}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save the figure
            plt.savefig(output_file, format=format)
            plt.close(fig)

            return output_file
        except Exception as e:
            logger.error("Error generating Matplotlib comparative analysis: %s", e)
            return None

    def _generate_plotly_comparative(
        self,
        container_ids: List[str],
        metric_type: str,
        timestamps: List[datetime],
        data: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an interactive comparative analysis chart using Plotly.

        Args:
            container_ids: The container IDs
            metric_type: The metric type
            timestamps: The timestamps
            data: The data for each container
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import plotly.graph_objects as go

            # Create figure
            fig = go.Figure()

            # Add traces for each container
            for container_id, values in data.items():
                if len(timestamps) == len(values):
                    fig.add_trace(
                        go.Scatter(
                            x=timestamps, y=values, name=container_id[:12], mode="lines"
                        )
                    )

            # Update layout
            fig.update_layout(
                title=f"Comparative {metric_type.capitalize()} Usage",
                xaxis_title="Time",
                yaxis_title=self._get_metric_label(metric_type),
                legend_title="Containers",
                width=self.chart_width,
                height=self.chart_height,
                hovermode="x unified",
            )

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"comparative_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".html"):
                    output_file = f"{output_file}.html"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            fig.write_html(output_file)

            return output_file
        except Exception as e:
            logger.error("Error generating Plotly comparative analysis: %s", e)
            return None

    def _generate_text_comparative(
        self,
        container_ids: List[str],
        metric_type: str,
        timestamps: List[datetime],
        data: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a text-based comparative analysis.

        Args:
            container_ids: The container IDs
            metric_type: The metric type
            timestamps: The timestamps
            data: The data for each container
            output_file: Optional output file path

        Returns:
            The path to the generated file, or None if generation failed
        """
        try:
            # Create a simple text-based visualization
            lines = [f"Comparative {metric_type.capitalize()} Usage"]
            lines.append("=" * 80)

            # Add header row with timestamps
            # Use a subset of timestamps to avoid overcrowding
            num_ticks = min(10, len(timestamps))
            if num_ticks > 0:
                import numpy as np

                tick_indices = np.linspace(0, len(timestamps) - 1, num_ticks, dtype=int)
                header = "Container" + " " * 10 + " | "
                header += " | ".join(
                    f"{timestamps[i].strftime('%H:%M:%S'):>8}" for i in tick_indices
                )
                lines.append(header)
                lines.append("-" * 80)

                # Add data rows for each container
                for container_id, values in data.items():
                    row = f"{container_id[:12]:<20} | "
                    row_values = []
                    for idx in tick_indices:
                        if idx < len(values):
                            row_values.append(f"{values[idx]:8.2f}")
                        else:
                            row_values.append(" " * 8)
                    row += " | ".join(row_values)
                    lines.append(row)

            # Save the text visualization
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"comparative_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".txt"):
                    output_file = f"{output_file}.txt"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            return output_file
        except Exception as e:
            logger.error("Error generating text comparative analysis: %s", e)
            return None

    def _export_comparative_data(
        self,
        container_ids: List[str],
        metric_type: str,
        timestamps: List[datetime],
        data: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export comparative analysis data to a file.

        Args:
            container_ids: The container IDs
            metric_type: The metric type
            timestamps: The timestamps
            data: The data for each container
            format: The output format (json or csv)
            output_file: Optional output file path

        Returns:
            The path to the exported file, or None if export failed
        """
        try:
            # Prepare data for export
            export_data = []
            for i, timestamp in enumerate(timestamps):
                if i < len(timestamps):
                    row = {
                        "timestamp": timestamp.isoformat(),
                        "metric_type": metric_type,
                    }
                    for container_id, values in data.items():
                        if i < len(values):
                            row[container_id] = values[i]
                    export_data.append(row)

            # Save the data
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"comparative_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format.lower()}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format.lower()}"):
                    output_file = f"{output_file}.{format.lower()}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            if format.lower() == "json":
                with open(output_file, "w") as f:
                    json.dump(export_data, f, indent=2)
            elif format.lower() == "csv":
                with open(output_file, "w", newline="") as f:
                    if export_data:
                        fieldnames = export_data[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(export_data)

            return output_file
        except Exception as e:
            logger.error("Error exporting comparative data: %s", e)
            return None

    def _get_metric_label(self, metric_type: str) -> str:
        """
        Get a human-readable label for a metric type.

        Args:
            metric_type: The metric type

        Returns:
            A human-readable label
        """
        if metric_type == "cpu":
            return "CPU Usage (%)"
        elif metric_type == "memory":
            return "Memory Usage (%)"
        elif metric_type == "disk":
            return "Disk I/O (bytes)"
        elif metric_type == "network":
            return "Network Traffic (bytes)"
        else:
            return "Value"

    def generate_report(
        self,
        container_ids: List[str],
        metric_types: List[str],
        duration: int = 24,
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a comprehensive report with multiple visualizations.

        Args:
            container_ids: List of container IDs to include in the report
            metric_types: List of metric types to include in the report
            duration: The duration to look back in hours
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated report file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Create a temporary directory for report components
        with tempfile.TemporaryDirectory() as temp_dir:
            report_components = []

            # Generate time series charts for each container and metric
            for container_id in container_ids:
                for metric_type in metric_types:
                    chart_file = self.generate_time_series_chart(
                        container_id,
                        metric_type,
                        duration,
                        format,
                        os.path.join(
                            temp_dir, f"timeseries_{container_id[:12]}_{metric_type}"
                        ),
                    )
                    if chart_file:
                        report_components.append(
                            {
                                "type": "time_series",
                                "container_id": container_id,
                                "metric_type": metric_type,
                                "file": chart_file,
                            }
                        )

            # Generate comparative analysis for each metric
            for metric_type in metric_types:
                if len(container_ids) > 1:
                    chart_file = self.generate_comparative_analysis(
                        container_ids,
                        metric_type,
                        duration,
                        format,
                        os.path.join(temp_dir, f"comparative_{metric_type}"),
                    )
                    if chart_file:
                        report_components.append(
                            {
                                "type": "comparative",
                                "metric_type": metric_type,
                                "file": chart_file,
                            }
                        )

            # Generate heatmaps for each metric
            for metric_type in metric_types:
                chart_file = self.generate_resource_heatmap(
                    metric_type,
                    duration,
                    format,
                    os.path.join(temp_dir, f"heatmap_{metric_type}"),
                )
                if chart_file:
                    report_components.append(
                        {
                            "type": "heatmap",
                            "metric_type": metric_type,
                            "file": chart_file,
                        }
                    )

            # Compile the report based on the format
            if format.lower() in ["html", "interactive"]:
                return self._compile_html_report(
                    report_components,
                    container_ids,
                    metric_types,
                    duration,
                    output_file,
                )
            elif format.lower() in ["pdf", "png", "jpg", "svg"]:
                return self._compile_image_report(
                    report_components,
                    container_ids,
                    metric_types,
                    duration,
                    format,
                    output_file,
                )
            else:
                return self._compile_text_report(
                    report_components,
                    container_ids,
                    metric_types,
                    duration,
                    output_file,
                )

    def _compile_html_report(
        self,
        components: List[Dict[str, Any]],
        container_ids: List[str],
        metric_types: List[str],
        duration: int,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Compile an HTML report from the generated components.

        Args:
            components: The report components
            container_ids: The container IDs included in the report
            metric_types: The metric types included in the report
            duration: The duration in hours
            output_file: Optional output file path

        Returns:
            The path to the compiled report file, or None if compilation failed
        """
        try:
            # Create HTML content
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DockerForge Resource Monitoring Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .section {{ margin-bottom: 30px; }}
        .chart {{ margin-bottom: 20px; }}
        .chart img {{ max-width: 100%; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>DockerForge Resource Monitoring Report</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Duration: {duration} hours</p>
"""

            # Add container list section
            html_content += """    <div class="section">
        <h2>Containers</h2>
        <ul>"""

            for container_id in container_ids:
                html_content += f"\n            <li>{container_id}</li>"

            html_content += """\n        </ul>
    </div>"""

            # Add comparative analysis section
            comparative_components = [
                c for c in components if c.get("type") == "comparative"
            ]
            if comparative_components:
                html_content += """\n    <div class="section">
        <h2>Comparative Analysis</h2>"""

                for component in comparative_components:
                    metric_type = component.get("metric_type", "")
                    file_path = component.get("file", "")

                    if file_path and file_path.endswith(".html"):
                        # For HTML files, embed using iframe
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Comparison</h3>
            <iframe src="{os.path.basename(file_path)}" width="100%" height="500px" frameborder="0"></iframe>
        </div>"""
                    elif file_path:
                        # For image files, embed using img tag
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Comparison</h3>
            <img src="{os.path.basename(file_path)}" alt="{metric_type.capitalize()} Comparison">
        </div>"""

                html_content += """\n    </div>"""

            # Add heatmap section
            heatmap_components = [c for c in components if c.get("type") == "heatmap"]
            if heatmap_components:
                html_content += """\n    <div class="section">
        <h2>Resource Heatmaps</h2>"""

                for component in heatmap_components:
                    metric_type = component.get("metric_type", "")
                    file_path = component.get("file", "")

                    if file_path and file_path.endswith(".html"):
                        # For HTML files, embed using iframe
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Heatmap</h3>
            <iframe src="{os.path.basename(file_path)}" width="100%" height="500px" frameborder="0"></iframe>
        </div>"""
                    elif file_path:
                        # For image files, embed using img tag
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Heatmap</h3>
            <img src="{os.path.basename(file_path)}" alt="{metric_type.capitalize()} Heatmap">
        </div>"""

                html_content += """\n    </div>"""

            # Add individual container sections
            for container_id in container_ids:
                html_content += f"""\n    <div class="section">
        <h2>Container: {container_id[:12] if len(container_id) > 12 else container_id}</h2>"""

                container_components = [
                    c
                    for c in components
                    if c.get("type") == "time_series"
                    and c.get("container_id") == container_id
                ]
                for component in container_components:
                    metric_type = component.get("metric_type", "")
                    file_path = component.get("file", "")

                    if file_path and file_path.endswith(".html"):
                        # For HTML files, embed using iframe
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Usage</h3>
            <iframe src="{os.path.basename(file_path)}" width="100%" height="500px" frameborder="0"></iframe>
        </div>"""
                    elif file_path:
                        # For image files, embed using img tag
                        html_content += f"""\n        <div class="chart">
            <h3>{metric_type.capitalize()} Usage</h3>
            <img src="{os.path.basename(file_path)}" alt="{metric_type.capitalize()} Usage for {container_id[:12] if len(container_id) > 12 else container_id}">
        </div>"""

                html_content += """\n    </div>"""

            # Close HTML document
            html_content += """\n</body>\n</html>"""

            # Save the HTML report
            if output_file is None:
                # Use mkstemp instead of mktemp for security
                fd, output_file = tempfile.mkstemp(suffix=".html")
                os.close(fd)  # Close the file descriptor

            with open(output_file, "w") as f:
                f.write(html_content)

            # Copy component files to the same directory as the report
            report_dir = os.path.dirname(output_file)
            for component in components:
                file_path = component.get("file", "")
                if file_path and os.path.exists(file_path):
                    import shutil

                    shutil.copy2(
                        file_path, os.path.join(report_dir, os.path.basename(file_path))
                    )

            return output_file
        except Exception as e:
            logger.error(f"Error compiling HTML report: {e}")
            return None


from src.config.config_manager import ConfigManager
from src.resource_monitoring.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """
    Generates visualizations and reports for Docker container resource metrics.

    This class handles:
    - Time-series charts
    - Resource heatmaps
    - Comparative analysis
    - Scheduled report generation
    - Export to multiple formats
    """

    def __init__(
        self, config_manager: ConfigManager, metrics_collector: MetricsCollector
    ):
        """
        Initialize the visualization engine.

        Args:
            config_manager: The configuration manager instance
            metrics_collector: The metrics collector instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.metrics_collector = metrics_collector

        # Visualization configuration
        self.visualization_config = self.config.get("resource_monitoring", {}).get(
            "visualization", {}
        )
        self.output_dir = self.visualization_config.get(
            "output_dir", "~/.dockerforge/visualizations"
        )
        self.output_dir = os.path.expanduser(self.output_dir)
        self.default_format = self.visualization_config.get("default_format", "png")
        self.chart_width = self.visualization_config.get("chart_width", 800)
        self.chart_height = self.visualization_config.get("chart_height", 400)
        self.color_scheme = self.visualization_config.get("color_scheme", "default")

        # Scheduled reports
        self.scheduled_reports = self.visualization_config.get("scheduled_reports", [])
        self.report_thread = None
        self.running = False

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Optional dependencies
        self.has_matplotlib = False
        self.has_plotly = False
        self.has_pandas = False

        try:
            import matplotlib

            self.has_matplotlib = True
        except ImportError:
            logger.warning(
                "Matplotlib not available, some visualization features will be limited"
            )

        try:
            import plotly

            self.has_plotly = True
        except ImportError:
            logger.warning(
                "Plotly not available, some visualization features will be limited"
            )

        try:
            import pandas

            self.has_pandas = True
        except ImportError:
            logger.warning(
                "Pandas not available, some data processing features will be limited"
            )

    def start_scheduled_reports(self) -> None:
        """
        Start the scheduled report generation thread.
        """
        if self.report_thread and self.report_thread.is_alive():
            logger.info("Scheduled reports are already running")
            return

        logger.info("Starting scheduled report generation")
        self.running = True
        self.report_thread = threading.Thread(target=self._report_loop)
        self.report_thread.daemon = True
        self.report_thread.start()

    def stop_scheduled_reports(self) -> None:
        """
        Stop the scheduled report generation thread.
        """
        logger.info("Stopping scheduled report generation")
        self.running = False
        if self.report_thread:
            self.report_thread.join(timeout=5)

    def _report_loop(self) -> None:
        """
        Main loop for scheduled report generation.
        """
        last_run_times = {report["name"]: None for report in self.scheduled_reports}

        while self.running:
            try:
                current_time = datetime.now()

                for report in self.scheduled_reports:
                    report_name = report["name"]
                    interval = report.get(
                        "interval", 24 * 60 * 60
                    )  # Default: daily (in seconds)

                    # Check if it's time to run this report
                    if (
                        last_run_times[report_name] is None
                        or (current_time - last_run_times[report_name]).total_seconds()
                        >= interval
                    ):

                        # Generate the report
                        try:
                            self.generate_report(
                                report.get("containers", []),
                                report.get(
                                    "metrics", ["cpu", "memory", "disk", "network"]
                                ),
                                report.get("duration", 24),  # Default: 24 hours
                                report.get("format", self.default_format),
                                report.get(
                                    "output_file",
                                    f"{report_name}_{current_time.strftime('%Y%m%d_%H%M%S')}",
                                ),
                            )
                            last_run_times[report_name] = current_time
                            logger.info("Generated scheduled report: %s", report_name)
                        except Exception as e:
                            logger.error(
                                "Error generating scheduled report %s: %s",
                                report_name,
                                e,
                            )

                # Sleep for a minute before checking again
                time.sleep(60)
            except Exception as e:
                logger.error("Error in report scheduler: %s", e)
                time.sleep(60)  # Wait a bit before retrying

    def generate_time_series_chart(
        self,
        container_id: str,
        metric_type: str,
        duration: int = 1,  # hours
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a time-series chart for a specific container and metric.

        Args:
            container_id: The container ID
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The duration to look back in hours
            format: The output format (png, svg, html, json)
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Get metrics data
        metrics_data = self.metrics_collector.get_metrics_history(
            container_id, metric_type, timedelta(hours=duration)
        )

        if not metrics_data:
            logger.warning(
                "No metrics data available for container %s, metric %s",
                container_id,
                metric_type,
            )
            return None

        # Prepare data for visualization
        timestamps = []
        values = {}

        for entry in metrics_data:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            timestamps.append(timestamp)

            data = entry["data"]
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    if key not in values:
                        values[key] = []
                    values[key].append(value)

        # Select appropriate visualization method based on available libraries
        if format.lower() in ["json", "csv"]:
            return self._export_time_series_data(
                container_id, metric_type, timestamps, values, format, output_file
            )
        elif self.has_plotly and format.lower() in ["html", "interactive"]:
            return self._generate_plotly_time_series(
                container_id, metric_type, timestamps, values, output_file
            )
        elif self.has_matplotlib:
            return self._generate_matplotlib_time_series(
                container_id, metric_type, timestamps, values, format, output_file
            )
        else:
            # Fallback to text-based visualization
            return self._generate_text_time_series(
                container_id, metric_type, timestamps, values, output_file
            )

    def _generate_matplotlib_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a time-series chart using Matplotlib.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.dates import DateFormatter

            # Create figure and axis
            fig, ax = plt.subplots(
                figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100
            )

            # Plot each metric
            for key, vals in values.items():
                if len(timestamps) == len(vals):
                    ax.plot(timestamps, vals, label=key)

            # Format the chart
            ax.set_title(
                f"{metric_type.capitalize()} Usage for Container {container_id[:12]}"
            )
            ax.set_xlabel("Time")

            # Set y-axis label based on metric type
            if metric_type == "cpu":
                ax.set_ylabel("CPU Usage (%)")
            elif metric_type == "memory":
                ax.set_ylabel("Memory Usage (%)")
            elif metric_type == "disk":
                ax.set_ylabel("Disk I/O (bytes)")
            elif metric_type == "network":
                ax.set_ylabel("Network Traffic (bytes)")
            else:
                ax.set_ylabel("Value")

            # Format x-axis
            ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
            plt.xticks(rotation=45)

            # Add legend if multiple metrics
            if len(values) > 1:
                ax.legend()

            # Adjust layout
            plt.tight_layout()

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format}"):
                    output_file = f"{output_file}.{format}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save the figure
            plt.savefig(output_file, format=format)
            plt.close(fig)

            return output_file
        except Exception as e:
            logger.error("Error generating Matplotlib time series: %s", e)
            return None

    def _generate_plotly_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an interactive time-series chart using Plotly.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            output_file: Optional output file path

        Returns:
            The path to the generated chart file, or None if generation failed
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            # Create figure
            fig = make_subplots(specs=[[{"secondary_y": False}]])

            # Add traces for each metric
            for key, vals in values.items():
                if len(timestamps) == len(vals):
                    fig.add_trace(
                        go.Scatter(x=timestamps, y=vals, name=key, mode="lines"),
                        secondary_y=False,
                    )

            # Update layout
            fig.update_layout(
                title=f"{metric_type.capitalize()} Usage for Container {container_id[:12]}",
                xaxis_title="Time",
                legend_title="Metrics",
                width=self.chart_width,
                height=self.chart_height,
                hovermode="x unified",
            )

            # Set y-axis title based on metric type
            if metric_type == "cpu":
                fig.update_yaxes(title_text="CPU Usage (%)", secondary_y=False)
            elif metric_type == "memory":
                fig.update_yaxes(title_text="Memory Usage (%)", secondary_y=False)
            elif metric_type == "disk":
                fig.update_yaxes(title_text="Disk I/O (bytes)", secondary_y=False)
            elif metric_type == "network":
                fig.update_yaxes(
                    title_text="Network Traffic (bytes)", secondary_y=False
                )
            else:
                fig.update_yaxes(title_text="Value", secondary_y=False)

            # Save the chart
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".html"):
                    output_file = f"{output_file}.html"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            fig.write_html(output_file)

            return output_file
        except Exception as e:
            logger.error("Error generating Plotly time series: %s", e)
            return None

    def _generate_text_time_series(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a text-based time-series visualization.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            output_file: Optional output file path

        Returns:
            The path to the generated file, or None if generation failed
        """
        try:
            # Create a simple text-based visualization
            lines = [
                f"{metric_type.capitalize()} Usage for Container {container_id[:12]}"
            ]
            lines.append("=" * 80)
            lines.append(
                "Timestamp"
                + " " * 20
                + " | "
                + " | ".join(f"{key:>10}" for key in values.keys())
            )
            lines.append("-" * 80)

            # Add data rows
            for i, timestamp in enumerate(timestamps):
                if i < len(timestamps):
                    row = [timestamp.strftime("%Y-%m-%d %H:%M:%S")]
                    for key in values.keys():
                        if i < len(values[key]):
                            row.append(f"{values[key][i]:10.2f}")
                        else:
                            row.append(" " * 10)
                    lines.append(" | ".join(row))

            # Save the text visualization
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".txt"):
                    output_file = f"{output_file}.txt"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            with open(output_file, "w") as f:
                f.write("\n".join(lines))

            return output_file
        except Exception as e:
            logger.error("Error generating text time series: %s", e)
            return None

    def _export_time_series_data(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: Dict[str, List[float]],
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export time-series data to a file.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            format: The output format (json or csv)
            output_file: Optional output file path

        Returns:
            The path to the exported file, or None if export failed
        """
        try:
            # Prepare data for export
            export_data = []
            for i, timestamp in enumerate(timestamps):
                if i < len(timestamps):
                    row = {
                        "timestamp": timestamp.isoformat(),
                        "container_id": container_id,
                        "metric_type": metric_type,
                    }
                    for key in values.keys():
                        if i < len(values[key]):
                            row[key] = values[key][i]
                    export_data.append(row)

            # Save the data
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"{container_id[:12]}_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format.lower()}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format.lower()}"):
                    output_file = f"{output_file}.{format.lower()}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            if format.lower() == "json":
                with open(output_file, "w") as f:
                    json.dump(export_data, f, indent=2)
            elif format.lower() == "csv":
                with open(output_file, "w", newline="") as f:
                    if export_data:
                        fieldnames = export_data[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(export_data)

            return output_file
        except Exception as e:
            logger.error("Error exporting time series data: %s", e)
            return None

    def generate_resource_heatmap(
        self,
        metric_type: str,
        duration: int = 24,
        format: str = None,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a resource heatmap showing usage across all containers.

        Args:
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The duration to look back in hours
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        if not format:
            format = self.default_format

        # Get metrics data for all containers
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=duration)

        metrics = self.metrics_collector.get_metrics(
            container_id=None,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
        )

        if not metrics:
            logger.warning("No metrics data available for heatmap generation")
            return None

        # Prepare data for heatmap
        container_data = {}
        all_timestamps = set()

        for container_id, container_metrics in metrics.items():
            if metric_type in container_metrics:
                container_data[container_id] = {}

                for entry in container_metrics[metric_type]:
                    timestamp = datetime.fromisoformat(entry["timestamp"])
                    all_timestamps.add(timestamp)

                    # Extract the main value based on metric type
                    if metric_type == "cpu":
                        value = entry["data"].get("usage_percent", 0)
                    elif metric_type == "memory":
                        value = entry["data"].get("usage_percent", 0)
                    elif metric_type == "disk":
                        value = entry["data"].get("read_bytes", 0) + entry["data"].get(
                            "write_bytes", 0
                        )
                    elif metric_type == "network":
                        value = entry["data"].get("rx_bytes", 0) + entry["data"].get(
                            "tx_bytes", 0
                        )
                    else:
                        # Try to find a numeric value
                        for k, v in entry["data"].items():
                            if isinstance(v, (int, float)):
                                value = v
                                break
                        else:
                            value = 0

                    container_data[container_id][timestamp] = value

        # Convert to sorted lists for visualization
        sorted_timestamps = sorted(all_timestamps)
        sorted_containers = sorted(container_data.keys())

        # Create the heatmap data matrix
        heatmap_data = []
        for container_id in sorted_containers:
            container_values = []
            for timestamp in sorted_timestamps:
                container_values.append(
                    container_data.get(container_id, {}).get(timestamp, 0)
                )
            heatmap_data.append(container_values)

        # Select appropriate visualization method based on available libraries
        if self.has_matplotlib:
            return self._generate_matplotlib_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                format,
                output_file,
            )
        elif self.has_plotly:
            return self._generate_plotly_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                output_file,
            )
        else:
            # Fallback to text-based visualization
            return self._generate_text_heatmap(
                sorted_containers,
                sorted_timestamps,
                heatmap_data,
                metric_type,
                output_file,
            )

    def _generate_matplotlib_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        format: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a heatmap using Matplotlib.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            format: The output format
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.dates import DateFormatter

            # Create figure and axis
            fig, ax = plt.subplots(
                figsize=(self.chart_width / 100, self.chart_height / 100), dpi=100
            )

            # Create the heatmap
            im = ax.imshow(data, aspect="auto", cmap="viridis")

            # Set labels
            ax.set_title(f"{metric_type.capitalize()} Usage Heatmap")
            ax.set_xlabel("Time")
            ax.set_ylabel("Container")

            # Set y-axis ticks (container IDs)
            ax.set_yticks(np.arange(len(containers)))
            ax.set_yticklabels([c[:12] for c in containers])

            # Set x-axis ticks (timestamps)
            # Use a subset of timestamps to avoid overcrowding
            num_ticks = min(10, len(timestamps))
            if num_ticks > 0:
                tick_indices = np.linspace(0, len(timestamps) - 1, num_ticks, dtype=int)
                ax.set_xticks(tick_indices)
                ax.set_xticklabels(
                    [timestamps[i].strftime("%H:%M:%S") for i in tick_indices]
                )
                plt.xticks(rotation=45)

            # Add colorbar
            cbar = ax.figure.colorbar(im, ax=ax)
            if metric_type == "cpu" or metric_type == "memory":
                cbar.ax.set_ylabel("Usage (%)", rotation=-90, va="bottom")
            elif metric_type == "disk":
                cbar.ax.set_ylabel("Disk I/O (bytes)", rotation=-90, va="bottom")
            elif metric_type == "network":
                cbar.ax.set_ylabel("Network Traffic (bytes)", rotation=-90, va="bottom")
            else:
                cbar.ax.set_ylabel("Value", rotation=-90, va="bottom")

            # Adjust layout
            plt.tight_layout()

            # Save the heatmap
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"heatmap_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(f".{format}"):
                    output_file = f"{output_file}.{format}"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Save the figure
            plt.savefig(output_file, format=format)
            plt.close(fig)

            return output_file
        except Exception as e:
            logger.error("Error generating Matplotlib heatmap: %s", e)
            return None

    def _generate_plotly_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate an interactive heatmap using Plotly.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            output_file: Optional output file path

        Returns:
            The path to the generated heatmap file, or None if generation failed
        """
        try:
            import numpy as np
            import plotly.graph_objects as go

            # Format timestamps
            time_labels = [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps]

            # Format container IDs
            container_labels = [c[:12] for c in containers]

            # Create the heatmap
            fig = go.Figure(
                data=go.Heatmap(
                    z=data,
                    x=time_labels,
                    y=container_labels,
                    colorscale="Viridis",
                    hovertemplate="Container: %{y}<br>Time: %{x}<br>Value: %{z}<extra></extra>",
                )
            )

            # Update layout
            fig.update_layout(
                title=f"{metric_type.capitalize()} Usage Heatmap",
                xaxis_title="Time",
                yaxis_title="Container",
                width=self.chart_width,
                height=self.chart_height,
            )

            # Set colorbar title based on metric type
            if metric_type == "cpu" or metric_type == "memory":
                fig.update_traces(colorbar_title="Usage (%)")
            elif metric_type == "disk":
                fig.update_traces(colorbar_title="Disk I/O (bytes)")
            elif metric_type == "network":
                fig.update_traces(colorbar_title="Network Traffic (bytes)")
            else:
                fig.update_traces(colorbar_title="Value")

            # Save the heatmap
            if not output_file:
                output_file = os.path.join(
                    self.output_dir,
                    f"heatmap_{metric_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                )
            else:
                # Ensure the output file has the correct extension
                if not output_file.endswith(".html"):
                    output_file = f"{output_file}.html"

                # If output_file doesn't include a path, add the default output directory
                if not os.path.dirname(output_file):
                    output_file = os.path.join(self.output_dir, output_file)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Write to file
            fig.write_html(output_file)

            return output_file
        except Exception as e:
            logger.error("Error generating Plotly heatmap: %s", e)
            return None

    def _generate_text_heatmap(
        self,
        containers: List[str],
        timestamps: List[datetime],
        data: List[List[float]],
        metric_type: str,
        output_file: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a text-based heatmap visualization.

        Args:
            containers: The container IDs
            timestamps: The timestamps
            data: The heatmap data matrix
            metric_type: The metric type
            output_file: Optional output file path

        Returns:
            The path to the generated file, or None if generation failed
        """
        try:
            # Create a simple text-based visualization
            lines = [f"{metric_type.capitalize()} Usage Heatmap"]
            lines.append("=" * 80)

            # Add header row with timestamps
            # Use a subset of timestamps to avoid overcrowding
            num_ticks = min(10, len(timestamps))
            if num_ticks > 0:
                import numpy as np

                tick_indices = np.linspace(0, len(timestamps) - 1, num_ticks, dtype=int)
                header = "Container" + " " * 10 + " | "
                header += " | ".join(
                    f"{timestamps[i].strftime('%H:%M:%S'):>8}" for i in tick_indices
                )
                lines.append(header)

            # Return the file path
            return output_file
        except Exception as e:
            logger.error(f"Error generating text heatmap: {e}")
            return None
