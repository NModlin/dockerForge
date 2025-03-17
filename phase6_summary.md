# DockerForge Phase 6: Resource Monitoring

## Overview

Phase 6 adds comprehensive resource monitoring capabilities to DockerForge, enabling users to track, analyze, and optimize Docker container resource usage. This phase introduces a new subsystem that monitors CPU, memory, disk, and network metrics, detects anomalies, and provides optimization recommendations.

## Key Components

### 1. Metrics Collection

The `MetricsCollector` class is responsible for collecting resource metrics from Docker containers:

- **CPU Usage**: Tracks CPU utilization percentage
- **Memory Usage**: Monitors memory consumption and limits
- **Disk I/O**: Measures read/write operations and throughput
- **Network I/O**: Tracks incoming and outgoing network traffic

Metrics are collected at configurable intervals and stored for analysis.

### 2. Anomaly Detection

The `AnomalyDetector` class identifies abnormal resource usage patterns:

- Uses statistical methods to detect outliers in resource usage
- Supports multiple detection algorithms (Z-score, IQR, moving average)
- Configurable sensitivity and thresholds
- Generates alerts for detected anomalies

### 3. Optimization Engine

The `OptimizationEngine` analyzes resource usage patterns and generates recommendations:

- **Resource Right-sizing**: Suggests appropriate CPU and memory limits
- **Cost Optimization**: Identifies opportunities to reduce resource waste
- **Performance Enhancement**: Recommends changes to improve container performance
- **Bottleneck Identification**: Pinpoints resource constraints
- **Impact Prediction**: Estimates the impact of recommended changes

### 4. Daemon Manager

The `DaemonManager` coordinates the resource monitoring components:

- Manages the lifecycle of monitoring components
- Provides a unified interface for starting/stopping monitoring
- Handles configuration and persistence
- Supports running as a background daemon or in the foreground

## CLI Integration

Resource monitoring is integrated into the DockerForge CLI in two ways:

### 1. Main CLI Integration

The main DockerForge CLI (`src.cli`) includes a new `resource` command group:

```
dockerforge resource [COMMAND]

Commands:
  start            Start the resource monitoring daemon
  stop             Stop the resource monitoring daemon
  status           Show the status of the resource monitoring daemon
  metrics          Show container resource metrics
  anomalies        Show detected resource anomalies
  recommendations  Show resource optimization recommendations
  report           Generate a resource optimization report
```

### 2. Standalone CLI

A dedicated CLI module (`src.cli_resource_monitoring`) provides standalone access to resource monitoring features:

```
python -m src.cli_resource_monitoring [COMMAND]

Commands:
  start            Start the monitoring daemon
  stop             Stop the monitoring daemon
  restart          Restart the monitoring daemon
  status           Show the daemon status
  metrics          Show container metrics
  anomalies        Show detected anomalies
  recommendations  Show optimization recommendations
  report           Generate an optimization report
```

## Configuration

Resource monitoring is configurable through the DockerForge configuration system:

```yaml
resource_monitoring:
  daemon:
    pid_file: ~/.dockerforge/daemon.pid
    log_file: ~/.dockerforge/daemon.log
    status_file: ~/.dockerforge/daemon_status.json
    status_interval: 60  # seconds
  
  metrics:
    collection_interval: 10  # seconds
    retention_period: 168  # hours (1 week)
    
  anomaly_detection:
    detection_interval: 60  # seconds
    algorithm: z_score  # z_score, iqr, moving_average
    sensitivity: medium  # low, medium, high
    
  optimization:
    analysis_interval: 3600  # seconds (1 hour)
    lookback_period: 168  # hours (1 week)
    cpu_threshold_high: 80  # percentage
    cpu_threshold_low: 20  # percentage
    memory_threshold_high: 80  # percentage
    memory_threshold_low: 20  # percentage
```

## Usage Examples

### Starting Resource Monitoring

```bash
# Using the main CLI
dockerforge resource start

# Using the standalone CLI
python -m src.cli_resource_monitoring start

# Run in foreground mode
dockerforge resource start --foreground
```

### Viewing Resource Metrics

```bash
# View metrics for all containers
dockerforge resource metrics

# View metrics for a specific container
dockerforge resource metrics --container my-container

# View specific metric type
dockerforge resource metrics --type cpu

# Filter by time range
dockerforge resource metrics --since 2025-03-15T00:00:00 --until 2025-03-16T00:00:00
```

### Viewing Anomalies

```bash
# View all detected anomalies
dockerforge resource anomalies

# Filter by container
dockerforge resource anomalies --container my-container

# Filter by severity
dockerforge resource anomalies --severity 3
```

### Viewing Optimization Recommendations

```bash
# View all recommendations
dockerforge resource recommendations

# Filter by recommendation type
dockerforge resource recommendations --type sizing

# Filter by resource type
dockerforge resource recommendations --resource cpu
```

### Generating Reports

```bash
# Generate a text report
dockerforge resource report

# Generate an HTML report
dockerforge resource report --format html --output report.html

# Generate a report for a specific container
dockerforge resource report --container my-container
```

## Testing

A test script (`test_phase6.sh`) is provided to verify the functionality of the resource monitoring system. The script tests:

- CLI command functionality
- Daemon management (start, stop, status)
- Metrics collection and retrieval
- Anomaly detection
- Optimization recommendations
- Report generation

## Future Enhancements

Potential future enhancements for the resource monitoring system include:

1. **Advanced Visualization**: Interactive dashboards for resource metrics
2. **Predictive Analytics**: Forecasting future resource needs based on historical data
3. **Auto-scaling Integration**: Automatically adjusting container resources based on recommendations
4. **Multi-host Monitoring**: Extending monitoring to Docker Swarm or Kubernetes clusters
5. **Custom Alerting Rules**: User-defined thresholds and notification preferences
6. **Resource Usage Profiling**: Identifying resource usage patterns by application type
7. **Comparative Analysis**: Comparing resource usage across similar containers
