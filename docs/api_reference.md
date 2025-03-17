# DockerForge API Reference

## Overview

DockerForge provides a comprehensive API for programmatic interaction with its features. This reference documents all available API endpoints, parameters, and response formats.

## API Basics

### Base URL

When running locally, the API is available at:

```
http://localhost:8080/api/v1
```

For Docker installations, the API is available at:

```
http://<docker-host>:8080/api/v1
```

### Authentication

API requests require authentication using an API key. The key can be provided in one of two ways:

1. **HTTP Header**: Include the API key in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

2. **Query Parameter**: Include the API key as a query parameter:

```
?api_key=your-api-key-here
```

### API Key Management

API keys can be managed using the CLI:

```bash
# Generate a new API key
dockerforge api key generate --name "My API Key"

# List all API keys
dockerforge api key list

# Revoke an API key
dockerforge api key revoke KEY_ID
```

### Response Format

All API responses are in JSON format with the following structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

For error responses:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  }
}
```

### Pagination

Endpoints that return lists support pagination using the following query parameters:

- `page`: Page number (default: 1)
- `limit`: Number of items per page (default: 20, max: 100)

Paginated responses include metadata:

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  },
  "error": null
}
```

## API Endpoints

### System

#### Get System Information

```
GET /system/info
```

Returns information about the DockerForge system.

**Response:**

```json
{
  "success": true,
  "data": {
    "version": "1.2.3",
    "docker_version": "24.0.5",
    "platform": "linux",
    "cpu_count": 8,
    "memory_total": 16384,
    "disk_free": 102400
  },
  "error": null
}
```

#### Get System Status

```
GET /system/status
```

Returns the current status of DockerForge services.

**Response:**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "api": "running",
      "daemon": "running",
      "docker_connection": "connected"
    },
    "uptime": 86400
  },
  "error": null
}
```

### Containers

#### List Containers

```
GET /containers
```

Returns a list of containers.

**Query Parameters:**

- `all`: Include stopped containers (default: false)
- `filter`: Filter containers by name, status, etc.

**Response:**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "abc123def456",
        "name": "web-server",
        "image": "nginx:latest",
        "status": "running",
        "created": "2023-01-01T00:00:00Z",
        "ports": [
          {
            "internal": 80,
            "external": 8080,
            "protocol": "tcp"
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1
    }
  },
  "error": null
}
```

#### Get Container Details

```
GET /containers/{id}
```

Returns detailed information about a specific container.

**Path Parameters:**

- `id`: Container ID or name

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "image": "nginx:latest",
    "status": "running",
    "created": "2023-01-01T00:00:00Z",
    "started": "2023-01-01T00:00:00Z",
    "ports": [
      {
        "internal": 80,
        "external": 8080,
        "protocol": "tcp"
      }
    ],
    "networks": [
      {
        "name": "bridge",
        "ip_address": "172.17.0.2"
      }
    ],
    "volumes": [
      {
        "source": "/path/on/host",
        "destination": "/path/in/container",
        "mode": "rw"
      }
    ],
    "environment": [
      {
        "key": "NGINX_HOST",
        "value": "example.com"
      }
    ],
    "resource_usage": {
      "cpu_percent": 0.5,
      "memory_usage": 25600000,
      "memory_limit": 512000000,
      "memory_percent": 5.0,
      "network_rx": 1024,
      "network_tx": 2048,
      "block_read": 512,
      "block_write": 1024
    }
  },
  "error": null
}
```

#### Start Container

```
POST /containers/{id}/start
```

Starts a stopped container.

**Path Parameters:**

- `id`: Container ID or name

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "status": "running"
  },
  "error": null
}
```

#### Stop Container

```
POST /containers/{id}/stop
```

Stops a running container.

**Path Parameters:**

- `id`: Container ID or name

**Query Parameters:**

- `timeout`: Seconds to wait before killing the container (default: 10)

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "status": "stopped"
  },
  "error": null
}
```

#### Restart Container

```
POST /containers/{id}/restart
```

Restarts a container.

**Path Parameters:**

- `id`: Container ID or name

**Query Parameters:**

- `timeout`: Seconds to wait before killing the container (default: 10)

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "status": "running"
  },
  "error": null
}
```

#### Get Container Logs

```
GET /containers/{id}/logs
```

Returns logs from a container.

**Path Parameters:**

- `id`: Container ID or name

**Query Parameters:**

- `tail`: Number of lines to return from the end of the logs (default: 100)
- `since`: Only return logs since this timestamp
- `until`: Only return logs before this timestamp
- `follow`: Stream logs (default: false)
- `stdout`: Include stdout logs (default: true)
- `stderr`: Include stderr logs (default: true)

**Response:**

```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2023-01-01T00:00:00Z",
        "stream": "stdout",
        "message": "Server started"
      },
      {
        "timestamp": "2023-01-01T00:00:01Z",
        "stream": "stderr",
        "message": "Warning: high memory usage"
      }
    ]
  },
  "error": null
}
```

### Images

#### List Images

```
GET /images
```

Returns a list of images.

**Query Parameters:**

- `all`: Include intermediate images (default: false)
- `filter`: Filter images by name, tag, etc.

**Response:**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "sha256:abc123def456",
        "repository": "nginx",
        "tag": "latest",
        "created": "2023-01-01T00:00:00Z",
        "size": 142000000
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1
    }
  },
  "error": null
}
```

#### Get Image Details

```
GET /images/{id}
```

Returns detailed information about a specific image.

**Path Parameters:**

- `id`: Image ID or name

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "sha256:abc123def456",
    "repository": "nginx",
    "tag": "latest",
    "created": "2023-01-01T00:00:00Z",
    "size": 142000000,
    "architecture": "amd64",
    "os": "linux",
    "author": "NGINX Docker Maintainers",
    "config": {
      "exposed_ports": {
        "80/tcp": {}
      },
      "env": [
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "NGINX_VERSION=1.21.6"
      ],
      "cmd": [
        "nginx",
        "-g",
        "daemon off;"
      ]
    },
    "history": [
      {
        "created": "2023-01-01T00:00:00Z",
        "created_by": "COPY file:abc123 /etc/nginx/conf.d/ #buildkit",
        "comment": ""
      }
    ]
  },
  "error": null
}
```

#### Pull Image

```
POST /images/pull
```

Pulls an image from a registry.

**Request Body:**

```json
{
  "repository": "nginx",
  "tag": "latest"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "sha256:abc123def456",
    "repository": "nginx",
    "tag": "latest",
    "size": 142000000
  },
  "error": null
}
```

#### Remove Image

```
DELETE /images/{id}
```

Removes an image.

**Path Parameters:**

- `id`: Image ID or name

**Query Parameters:**

- `force`: Force removal (default: false)
- `noprune`: Do not delete untagged parents (default: false)

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "sha256:abc123def456",
    "repository": "nginx",
    "tag": "latest"
  },
  "error": null
}
```

### Monitoring

#### Get Container Stats

```
GET /containers/{id}/stats
```

Returns real-time resource usage statistics for a container.

**Path Parameters:**

- `id`: Container ID or name

**Query Parameters:**

- `stream`: Stream stats (default: false)

**Response:**

```json
{
  "success": true,
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "timestamp": "2023-01-01T00:00:00Z",
    "cpu_stats": {
      "cpu_usage": {
        "total_usage": 100000000,
        "percpu_usage": [50000000, 50000000],
        "usage_in_kernelmode": 20000000,
        "usage_in_usermode": 80000000
      },
      "system_cpu_usage": 10000000000,
      "online_cpus": 2,
      "throttling_data": {
        "periods": 0,
        "throttled_periods": 0,
        "throttled_time": 0
      }
    },
    "memory_stats": {
      "usage": 25600000,
      "max_usage": 30000000,
      "limit": 512000000,
      "stats": {
        "active_anon": 25600000,
        "active_file": 0,
        "cache": 0,
        "dirty": 0,
        "inactive_anon": 0,
        "inactive_file": 0,
        "mapped_file": 0,
        "pgfault": 0,
        "pgmajfault": 0,
        "pgpgin": 0,
        "pgpgout": 0,
        "rss": 25600000,
        "rss_huge": 0,
        "total_active_anon": 25600000,
        "total_active_file": 0,
        "total_cache": 0,
        "total_dirty": 0,
        "total_inactive_anon": 0,
        "total_inactive_file": 0,
        "total_mapped_file": 0,
        "total_pgfault": 0,
        "total_pgmajfault": 0,
        "total_pgpgin": 0,
        "total_pgpgout": 0,
        "total_rss": 25600000,
        "total_rss_huge": 0,
        "total_unevictable": 0,
        "total_writeback": 0,
        "unevictable": 0,
        "writeback": 0
      }
    },
    "network_stats": {
      "rx_bytes": 1024,
      "rx_packets": 10,
      "rx_errors": 0,
      "rx_dropped": 0,
      "tx_bytes": 2048,
      "tx_packets": 20,
      "tx_errors": 0,
      "tx_dropped": 0
    },
    "io_stats": {
      "read": {
        "ops": 5,
        "bytes": 512
      },
      "write": {
        "ops": 10,
        "bytes": 1024
      }
    }
  },
  "error": null
}
```

#### Get System Stats

```
GET /system/stats
```

Returns system-wide resource usage statistics.

**Response:**

```json
{
  "success": true,
  "data": {
    "timestamp": "2023-01-01T00:00:00Z",
    "cpu": {
      "usage_percent": 25.5,
      "cores": 8
    },
    "memory": {
      "total": 16384000000,
      "used": 8192000000,
      "free": 8192000000,
      "usage_percent": 50.0
    },
    "disk": {
      "total": 1024000000000,
      "used": 512000000000,
      "free": 512000000000,
      "usage_percent": 50.0
    },
    "network": {
      "rx_bytes": 1024000,
      "tx_bytes": 2048000
    },
    "containers": {
      "total": 5,
      "running": 3,
      "paused": 0,
      "stopped": 2
    }
  },
  "error": null
}
```

### Security

#### Scan Image

```
POST /security/scan
```

Scans an image for vulnerabilities.

**Request Body:**

```json
{
  "image": "nginx:latest",
  "severity": "HIGH"  // Optional, default: all
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "image": "nginx:latest",
    "scan_id": "scan-123456",
    "status": "completed",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z",
    "vulnerabilities": [
      {
        "id": "CVE-2023-12345",
        "package": "openssl",
        "version": "1.1.1k",
        "fixed_version": "1.1.1l",
        "severity": "HIGH",
        "description": "Vulnerability in OpenSSL",
        "link": "https://nvd.nist.gov/vuln/detail/CVE-2023-12345"
      }
    ],
    "summary": {
      "critical": 0,
      "high": 1,
      "medium": 0,
      "low": 0
    }
  },
  "error": null
}
```

#### Get Scan Status

```
GET /security/scan/{scan_id}
```

Returns the status of a vulnerability scan.

**Path Parameters:**

- `scan_id`: Scan ID

**Response:**

```json
{
  "success": true,
  "data": {
    "scan_id": "scan-123456",
    "image": "nginx:latest",
    "status": "in_progress",
    "started_at": "2023-01-01T00:00:00Z",
    "progress": 50
  },
  "error": null
}
```

#### Audit Docker Configuration

```
POST /security/audit
```

Audits Docker configuration for security issues.

**Request Body:**

```json
{
  "components": ["host", "daemon", "containers"]  // Optional, default: all
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "audit_id": "audit-123456",
    "status": "completed",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z",
    "checks": [
      {
        "id": "docker-4.1",
        "description": "Ensure that a user for the container has been created",
        "status": "PASS",
        "severity": "HIGH",
        "remediation": "Create a dedicated user for the container"
      },
      {
        "id": "docker-4.2",
        "description": "Ensure that containers use trusted base images",
        "status": "FAIL",
        "severity": "HIGH",
        "remediation": "Use official or verified images from trusted sources"
      }
    ],
    "summary": {
      "pass": 1,
      "fail": 1,
      "warn": 0,
      "info": 0
    }
  },
  "error": null
}
```

### Backup

#### Create Backup

```
POST /backup/container
```

Creates a backup of a container.

**Request Body:**

```json
{
  "container": "web-server",
  "include_volumes": true,  // Optional, default: true
  "include_image": false    // Optional, default: false
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "backup_id": "backup-123456",
    "container": "web-server",
    "created_at": "2023-01-01T00:00:00Z",
    "size": 25600000,
    "includes_volumes": true,
    "includes_image": false
  },
  "error": null
}
```

#### List Backups

```
GET /backup
```

Returns a list of backups.

**Response:**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "backup_id": "backup-123456",
        "container": "web-server",
        "created_at": "2023-01-01T00:00:00Z",
        "size": 25600000,
        "includes_volumes": true,
        "includes_image": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1
    }
  },
  "error": null
}
```

#### Restore Backup

```
POST /backup/{backup_id}/restore
```

Restores a container from a backup.

**Path Parameters:**

- `backup_id`: Backup ID

**Request Body:**

```json
{
  "container_name": "web-server-restored",  // Optional, default: original name
  "force": false                           // Optional, default: false
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "backup_id": "backup-123456",
    "container": "web-server-restored",
    "restored_at": "2023-01-01T00:00:00Z",
    "status": "running"
  },
  "error": null
}
```

### Update

#### Check for Updates

```
GET /update/check
```

Checks for DockerForge updates.

**Response:**

```json
{
  "success": true,
  "data": {
    "current_version": "1.2.3",
    "latest_version": "1.3.0",
    "update_available": true,
    "release_notes": "# Release Notes for 1.3.0\n\n- New feature: X\n- Bug fix: Y",
    "release_date": "2023-01-01T00:00:00Z"
  },
  "error": null
}
```

#### Apply Update

```
POST /update/apply
```

Applies an available update.

**Request Body:**

```json
{
  "version": "1.3.0",  // Optional, default: latest
  "force": false,      // Optional, default: false
  "backup": true       // Optional, default: true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "update_id": "update-123456",
    "from_version": "1.2.3",
    "to_version": "1.3.0",
    "status": "in_progress",
    "backup_id": "backup-123456"
  },
  "error": null
}
```

#### Get Update Status

```
GET /update/{update_id}
```

Returns the status of an update.

**Path Parameters:**

- `update_id`: Update ID

**Response:**

```json
{
  "success": true,
  "data": {
    "update_id": "update-123456",
    "from_version": "1.2.3",
    "to_version": "1.3.0",
    "status": "completed",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z",
    "backup_id": "backup-123456"
  },
  "error": null
}
```

### AI and Monitoring

#### Get AI Provider Status

```
GET /monitoring/ai-status
```

Returns the status of all configured AI providers.

**Response:**

```json
{
  "success": true,
  "data": {
    "providers": {
      "claude": {
        "name": "claude",
        "enabled": true,
        "available": true,
        "type": "built-in",
        "model": "claude-3-opus",
        "capabilities": {
          "streaming": true,
          "vision": true,
          "batching": false,
          "function_calling": true,
          "token_counting": true,
          "free_to_use": false,
          "local_execution": false
        }
      },
      "gemini": {
        "name": "gemini",
        "enabled": true,
        "available": true,
        "type": "built-in",
        "model": "gemini-pro"
      },
      "ollama": {
        "name": "ollama",
        "enabled": true,
        "available": true,
        "type": "built-in",
        "model": "llama3",
        "capabilities": {
          "streaming": true,
          "vision": false,
          "batching": false,
          "function_calling": false,
          "token_counting": true,
          "free_to_use": true,
          "local_execution": true
        }
      }
    },
    "default_provider": "ollama"
  },
  "error": null
}
```

#### Get AI Usage Statistics

```
GET /monitoring/ai-usage
```

Returns AI usage statistics and budget information.

**Response:**

```json
{
  "success": true,
  "data": {
    "date": "2025-03-17",
    "daily_usage": {
      "date": "2025-03-17",
      "providers": {
        "claude": {
          "models": {
            "claude-3-opus": {
              "input_tokens": 5000,
              "output_tokens": 2000,
              "cost_usd": 0.1875
            }
          },
          "total_cost_usd": 0.1875
        },
        "ollama": {
          "models": {
            "llama3": {
              "input_tokens": 10000,
              "output_tokens": 5000,
              "cost_usd": 0.0
            }
          },
          "total_cost_usd": 0.0
        }
      },
      "total_cost_usd": 0.1875
    },
    "monthly_usage": {
      "year": 2025,
      "month": 3,
      "providers": {
        "claude": {
          "models": {
            "claude-3-opus": {
              "input_tokens": 50000,
              "output_tokens": 20000,
              "cost_usd": 1.875
            }
          },
          "total_cost_usd": 1.875
        },
        "ollama": {
          "models": {
            "llama3": {
              "input_tokens": 100000,
              "output_tokens": 50000,
              "cost_usd": 0.0
            }
          },
          "total_cost_usd": 0.0
        }
      },
      "total_cost_usd": 1.875,
      "budget": {
        "claude": 10.0
      },
      "total_budget_usd": 10.0
    },
    "budget_status": {
      "year": 2025,
      "month": 3,
      "providers": {
        "claude": {
          "usage_usd": 1.875,
          "budget_usd": 10.0,
          "remaining_usd": 8.125,
          "percentage": 18.75
        }
      },
      "total_usage_usd": 1.875,
      "total_budget_usd": 10.0,
      "total_remaining_usd": 8.125,
      "total_percentage": 18.75
    },
    "days_in_month": 31,
    "days_passed": 17,
    "days_remaining": 14,
    "daily_average_usd": 0.11029,
    "projected_total_usd": 3.42,
    "budget_remaining_usd": 8.125,
    "budget_percentage": 18.75,
    "projected_percentage": 34.2
  },
  "error": null
}
```

#### Analyze Container

```
POST /monitoring/troubleshoot/container/{container_id}
```

Analyzes a container using AI to identify issues and suggest solutions.

**Path Parameters:**

- `container_id`: Container ID or name

**Request Body:**

```json
{
  "confirm_cost": true  // Optional, default: true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "container_id": "abc123def456",
    "container_name": "web-server",
    "container_status": "running",
    "analysis": "The container is experiencing high memory usage (85% of limit). This appears to be caused by a memory leak in the application. The logs show repeated allocation of resources without proper cleanup. Consider implementing better memory management or increasing the container's memory limit.",
    "provider": "claude",
    "model": "claude-3-opus",
    "timestamp": "2025-03-17T11:30:00Z"
  },
  "error": null
}
```

#### Analyze Logs

```
POST /monitoring/troubleshoot/logs
```

Analyzes Docker logs using AI to identify issues and suggest solutions.

**Request Body:**

```json
{
  "logs": "2025-03-17T11:20:00Z ERROR Connection refused to database\n2025-03-17T11:21:00Z ERROR Retry failed after 3 attempts\n2025-03-17T11:22:00Z ERROR Connection refused to database",
  "confirm_cost": true  // Optional, default: true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis": "The logs show persistent database connection issues. The application is unable to connect to the database and is retrying but failing. This could be due to:\n\n1. The database service is not running\n2. Network connectivity issues between the container and database\n3. Incorrect database credentials or connection string\n\nRecommendations:\n- Verify the database service is running\n- Check network configuration and firewall rules\n- Validate database credentials and connection parameters",
    "provider": "claude",
    "model": "claude-3-opus",
    "timestamp": "2025-03-17T11:30:00Z"
  },
  "error": null
}
```

#### Analyze Docker Compose File

```
POST /monitoring/troubleshoot/compose
```

Analyzes a Docker Compose file using AI to identify issues and suggest improvements.

**Request Body:**

```json
{
  "content": "version: '3'\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - \"80:80\"\n  db:\n    image: mysql:5.7\n",
  "confirm_cost": true  // Optional, default: true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis": "The Docker Compose file has several areas for improvement:\n\n1. No environment variables for MySQL - The MySQL container requires environment variables like MYSQL_ROOT_PASSWORD\n2. No volumes defined - Data will be lost when containers are removed\n3. No healthchecks - Services don't wait for dependencies to be ready\n4. Using latest tag - This can lead to unexpected changes when rebuilding\n\nRecommendations:\n- Add required environment variables for MySQL\n- Define volumes for persistent data\n- Add healthchecks and depends_on\n- Use specific version tags instead of latest",
    "provider": "claude",
    "model": "claude-3-opus",
    "timestamp": "2025-03-17T11:30:00Z"
  },
  "error": null
}
```

#### Analyze Dockerfile

```
POST /monitoring/troubleshoot/dockerfile
```

Analyzes a Dockerfile using AI to identify issues and suggest improvements.

**Request Body:**

```json
{
  "content": "FROM ubuntu:latest\nRUN apt-get update\nRUN apt-get install -y nginx\nCOPY . /app\nCMD [\"nginx\", \"-g\", \"daemon off;\"]\n",
  "confirm_cost": true  // Optional, default: true
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis": "The Dockerfile has several issues and areas for improvement:\n\n1. Multiple RUN instructions - These should be combined to reduce image layers\n2. No cleanup of apt cache - This increases image size unnecessarily\n3. Using latest tag - This can lead to unexpected changes\n4. No WORKDIR defined - Files are copied to root directory\n5. No EXPOSE instruction - Port 80 should be exposed\n\nRecommendations:\n- Combine RUN instructions and clean up apt cache\n- Use specific version tags\n- Add WORKDIR /app before COPY\n- Add EXPOSE 80\n- Consider using a more specific base image like nginx:alpine",
    "provider": "claude",
    "model": "claude-3-opus",
    "timestamp": "2025-03-17T11:30:00Z"
  },
  "error": null
}
```

#### Check Docker Connection

```
GET /monitoring/troubleshoot/connection
```

Checks Docker connection and troubleshoots any issues.

**Response:**

```json
{
  "success": true,
  "data": {
    "connected": false,
    "issues": [
      "Docker socket not found at /var/run/docker.sock",
      "Docker service is not running"
    ],
    "fixes": [
      "Make sure Docker is installed and running",
      "sudo systemctl start docker",
      "Add user to the docker group: sudo usermod -aG docker $USER",
      "Log out and log back in for the changes to take effect"
    ]
  },
  "error": null
}
```

### AI Integration

#### Analyze Container Logs

```
POST /ai/analyze/logs
```

Analyzes container logs using AI.

**Request Body:**

```json
{
  "container": "web-server",
  "provider": "claude",  // Optional, default: configured default
  "tail": 100,           // Optional, default: 100
  "since": "2023-01-01T00:00:00Z"  // Optional
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis-123456",
    "container": "web-server",
    "provider": "claude",
    "status": "completed",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z",
    "issues": [
      {
        "type": "connection_refused",
        "severity": "high",
        "description": "Database connection failures",
        "evidence": [
          "2023-01-01T00:00:00Z Error: Connection refused to database"
        ],
        "recommendation": "Check if the database is running and accessible"
      }
    ],
    "summary": "The container is experiencing database connection issues"
  },
  "error": null
}
```

#### Troubleshoot Container

```
POST /ai/troubleshoot
```

Troubleshoots container issues using AI.

**Request Body:**

```json
{
  "container": "web-server",
  "provider": "claude",  // Optional, default: configured default
  "focus": "networking"  // Optional, default: general
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "troubleshoot_id": "troubleshoot-123456",
    "container": "web-server",
    "provider": "claude",
    "status": "completed",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:01:00Z",
    "diagnosis": "The container cannot connect to the database due to network configuration issues",
    "issues": [
      {
        "type": "network_configuration",
        "severity": "high",
        "description": "Container network configuration issue",
        "evidence": [
          "Container is using bridge network but cannot resolve database hostname"
        ]
      }
    ],
    "recommendations": [
      {
        "description": "Use Docker network for service discovery",
        "steps": [
          "Create a custom network: docker network create app-network",
          "Connect both containers to the network: docker network connect app-network web-server",
          "Connect both containers to the network: docker network connect app-network database"
        ],
        "commands": [
          "docker network create app-network",
          "docker network connect app-network web-server",
          "docker network connect app-network database"
        ]
      }
    ]
  },
  "error": null
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | API key is invalid or missing |
| `AUTHORIZATION_FAILED` | API key does not have permission for the requested operation |
| `RESOURCE_NOT_FOUND` | The requested resource was not found |
| `VALIDATION_ERROR` | Request validation failed |
| `DOCKER_ERROR` | Error communicating with Docker |
| `INTERNAL_ERROR` | Internal server error |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `OPERATION_IN_PROGRESS` | Another operation is already in progress |
| `OPERATION_FAILED` | The requested operation failed |
| `INVALID_PARAMETER` | One or more parameters are invalid |

## Rate Limiting

The API enforces rate limiting to prevent abuse. Rate limits are applied per API key.

Rate limit headers are included in all responses:

- `X-RateLimit-Limit`: Maximum number of requests allowed in the current period
- `X-RateLimit-Remaining`: Number of requests remaining in the current period
- `X-RateLimit-Reset`: Time in seconds until the rate limit resets

When a rate limit is exceeded, the API returns a `429 Too Many Requests` status code with an `RATE_LIMIT_EXCEEDED` error.

## Webhooks

DockerForge can send webhook notifications for various events. Webhooks can be configured using the CLI:

```bash
# Add a webhook
dockerforge webhook add --url https://example.com/webhook --events container.start,container.stop

# List webhooks
dockerforge webhook list

# Remove a webhook
dockerforge webhook remove WEBHOOK_ID
```

### Webhook Payload

Webhook payloads are sent as HTTP POST requests with a JSON body:

```json
{
  "event": "container.start",
  "timestamp": "2023-01-01T00:00:00Z",
  "data": {
    "id": "abc123def456",
    "name": "web-server",
    "status": "running"
  }
}
```

### Webhook Events

| Event | Description |
|-------|-------------|
| `container.start` | Container started |
| `container.stop` | Container stopped |
| `container.die` | Container died |
| `container.create` | Container created |
| `container.destroy` | Container destroyed |
| `image.pull` | Image pulled |
| `image.remove` | Image removed |
| `volume.create` | Volume created |
| `volume.remove` | Volume removed |
| `network.create` | Network created |
| `network.remove` | Network removed |
| `security.vulnerability` | Vulnerability detected |
| `security.audit` | Audit completed |
| `backup.create` | Backup created |
| `backup.restore` | Backup restored |
| `update.available` | Update available |
| `update.applied` | Update applied |
| `system.error` | System error occurred |

## Client Libraries

DockerForge provides official client libraries for several programming languages:

- [Python](https://github.com/dockerforge/dockerforge-python)
- [JavaScript/Node.js](https://github.com/dockerforge/dockerforge-node)
- [Go](https://github.com/dockerforge/dockerforge-go)

### Python Example

```python
from dockerforge import DockerForgeClient

# Initialize client
client = DockerForgeClient(api_key="your-api-key-here")

# List containers
containers = client.containers.list()

# Get container details
container = client.containers.get("web-server")

# Start container
client.containers.start("web-server")

# Analyze logs with AI
analysis = client.ai.analyze_logs("web-server")
```

### JavaScript Example

```javascript
const { DockerForgeClient } = require('dockerforge');

// Initialize client
const client = new DockerForgeClient({ apiKey: 'your-api-key-here' });

// List containers
client.containers.list()
  .then(containers => console.log(containers))
  .catch(error => console.error(error));

// Get container details
client.containers.get('web-server')
  .then(container => console.log(container))
  .catch(error => console.error(error));

// Start container
client.containers.start('web-server')
  .then(result => console.log(result))
  .catch(error => console.error(error));

// Analyze logs with AI
client.ai.analyzeLogs('web-server')
  .then(analysis => console.log(analysis))
  .catch(error => console.error(error));
```

### Go Example

```go
package main

import (
	"fmt"
	"log"

	"github.com/dockerforge/dockerforge-go"
)

func main() {
	// Initialize client
	client, err := dockerforge.NewClient("your-api-key-here")
	if err != nil {
		log.Fatal(err)
	}

	// List containers
	containers, err := client.Containers.List(nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(containers)

	// Get container details
	container, err := client.Containers.Get("web-server")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(container)

	// Start container
	result, err := client.Containers.Start("web-server")
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(result)

	// Analyze logs with AI
	analysis, err := client.AI.AnalyzeLogs("web-server", nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(analysis)
}
