# DockerForge API Documentation

This document provides comprehensive documentation for the DockerForge API, which allows you to interact with DockerForge programmatically.

## API Overview

The DockerForge API is a RESTful API that provides access to all DockerForge functionality. The API is available at:

```
http://localhost:54321/api
```

## Authentication

Most API endpoints require authentication. DockerForge supports two authentication methods:

### API Key Authentication

Include your API key in the `X-API-Key` header:

```
X-API-Key: your-api-key
```

You can generate an API key in the DockerForge web interface under Settings > API Keys.

### JWT Authentication

For web applications, you can use JWT authentication:

1. Obtain a JWT token by authenticating with the `/api/auth/login` endpoint
2. Include the token in the `Authorization` header:

```
Authorization: Bearer your-jwt-token
```

## API Endpoints

### Health Check

```
GET /api/health
```

Returns the health status of the DockerForge API.

**Response:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### Authentication

#### Login

```
POST /api/auth/login
```

Authenticates a user and returns a JWT token.

**Request Body:**

```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Containers

#### List Containers

```
GET /api/containers
```

Returns a list of all containers.

**Query Parameters:**

- `all` (boolean): Include stopped containers (default: true)
- `limit` (integer): Maximum number of containers to return
- `offset` (integer): Number of containers to skip

**Response:**

```json
{
  "containers": [
    {
      "id": "abc123def456",
      "name": "nginx",
      "image": "nginx:latest",
      "status": "running",
      "created": "2023-01-01T00:00:00Z",
      "ports": [
        {
          "container_port": 80,
          "host_port": 8080,
          "protocol": "tcp"
        }
      ],
      "networks": ["bridge"],
      "volumes": ["/data:/data"]
    }
  ],
  "total": 1
}
```

#### Get Container Details

```
GET /api/containers/{id}
```

Returns detailed information about a specific container.

**Response:**

```json
{
  "id": "abc123def456",
  "name": "nginx",
  "image": "nginx:latest",
  "status": "running",
  "created": "2023-01-01T00:00:00Z",
  "started": "2023-01-01T00:00:00Z",
  "finished": null,
  "ports": [
    {
      "container_port": 80,
      "host_port": 8080,
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
      "container_path": "/data",
      "host_path": "/data"
    }
  ],
  "environment": [
    {
      "key": "NGINX_HOST",
      "value": "example.com"
    }
  ],
  "labels": {
    "com.example.description": "Nginx web server"
  },
  "resource_usage": {
    "cpu_percent": 0.5,
    "memory_usage": 10485760,
    "memory_limit": 104857600,
    "memory_percent": 10.0,
    "network_rx_bytes": 1024,
    "network_tx_bytes": 2048
  }
}
```

#### Start Container

```
POST /api/containers/{id}/start
```

Starts a stopped container.

**Response:**

```json
{
  "id": "abc123def456",
  "status": "running"
}
```

#### Stop Container

```
POST /api/containers/{id}/stop
```

Stops a running container.

**Query Parameters:**

- `timeout` (integer): Seconds to wait before killing the container (default: 10)

**Response:**

```json
{
  "id": "abc123def456",
  "status": "stopped"
}
```

#### Restart Container

```
POST /api/containers/{id}/restart
```

Restarts a container.

**Query Parameters:**

- `timeout` (integer): Seconds to wait before killing the container (default: 10)

**Response:**

```json
{
  "id": "abc123def456",
  "status": "running"
}
```

#### Remove Container

```
DELETE /api/containers/{id}
```

Removes a container.

**Query Parameters:**

- `force` (boolean): Force removal of running container (default: false)
- `volumes` (boolean): Remove associated volumes (default: false)

**Response:**

```json
{
  "id": "abc123def456",
  "removed": true
}
```

#### Get Container Logs

```
GET /api/containers/{id}/logs
```

Returns the logs of a container.

**Query Parameters:**

- `tail` (integer): Number of lines to show from the end of the logs (default: all)
- `since` (string): Show logs since timestamp (e.g., "2023-01-01T00:00:00Z")
- `until` (string): Show logs until timestamp (e.g., "2023-01-01T01:00:00Z")
- `follow` (boolean): Follow log output (default: false)

**Response:**

```json
{
  "id": "abc123def456",
  "logs": "2023-01-01T00:00:00Z INFO Starting nginx...\n2023-01-01T00:00:01Z INFO Nginx started successfully."
}
```

### Images

#### List Images

```
GET /api/images
```

Returns a list of all images.

**Query Parameters:**

- `all` (boolean): Include intermediate images (default: false)
- `limit` (integer): Maximum number of images to return
- `offset` (integer): Number of images to skip

**Response:**

```json
{
  "images": [
    {
      "id": "sha256:abc123def456",
      "repository": "nginx",
      "tag": "latest",
      "created": "2023-01-01T00:00:00Z",
      "size": 133456789
    }
  ],
  "total": 1
}
```

#### Get Image Details

```
GET /api/images/{id}
```

Returns detailed information about a specific image.

**Response:**

```json
{
  "id": "sha256:abc123def456",
  "repository": "nginx",
  "tag": "latest",
  "created": "2023-01-01T00:00:00Z",
  "size": 133456789,
  "author": "NGINX Docker Maintainers",
  "architecture": "amd64",
  "os": "linux",
  "layers": [
    "sha256:def456abc123",
    "sha256:789abc123def"
  ],
  "labels": {
    "maintainer": "NGINX Docker Maintainers"
  },
  "exposed_ports": [
    80,
    443
  ],
  "environment": [
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "NGINX_VERSION=1.21.0"
  ]
}
```

#### Pull Image

```
POST /api/images/pull
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
  "id": "sha256:abc123def456",
  "repository": "nginx",
  "tag": "latest",
  "status": "pulled"
}
```

#### Remove Image

```
DELETE /api/images/{id}
```

Removes an image.

**Query Parameters:**

- `force` (boolean): Force removal of the image (default: false)

**Response:**

```json
{
  "id": "sha256:abc123def456",
  "removed": true
}
```

### Volumes

#### List Volumes

```
GET /api/volumes
```

Returns a list of all volumes.

**Response:**

```json
{
  "volumes": [
    {
      "name": "my-volume",
      "driver": "local",
      "mountpoint": "/var/lib/docker/volumes/my-volume/_data",
      "created": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Get Volume Details

```
GET /api/volumes/{name}
```

Returns detailed information about a specific volume.

**Response:**

```json
{
  "name": "my-volume",
  "driver": "local",
  "mountpoint": "/var/lib/docker/volumes/my-volume/_data",
  "created": "2023-01-01T00:00:00Z",
  "labels": {
    "com.example.description": "My data volume"
  },
  "options": {
    "type": "nfs",
    "device": ":/path/to/dir",
    "o": "addr=192.168.1.1,rw"
  },
  "scope": "local",
  "status": {
    "hello": "world"
  }
}
```

#### Create Volume

```
POST /api/volumes
```

Creates a new volume.

**Request Body:**

```json
{
  "name": "my-volume",
  "driver": "local",
  "driver_opts": {
    "type": "nfs",
    "device": ":/path/to/dir",
    "o": "addr=192.168.1.1,rw"
  },
  "labels": {
    "com.example.description": "My data volume"
  }
}
```

**Response:**

```json
{
  "name": "my-volume",
  "driver": "local",
  "mountpoint": "/var/lib/docker/volumes/my-volume/_data",
  "created": "2023-01-01T00:00:00Z"
}
```

#### Remove Volume

```
DELETE /api/volumes/{name}
```

Removes a volume.

**Query Parameters:**

- `force` (boolean): Force removal of the volume (default: false)

**Response:**

```json
{
  "name": "my-volume",
  "removed": true
}
```

### Networks

#### List Networks

```
GET /api/networks
```

Returns a list of all networks.

**Response:**

```json
{
  "networks": [
    {
      "id": "abc123def456",
      "name": "bridge",
      "driver": "bridge",
      "scope": "local",
      "created": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Get Network Details

```
GET /api/networks/{id}
```

Returns detailed information about a specific network.

**Response:**

```json
{
  "id": "abc123def456",
  "name": "bridge",
  "driver": "bridge",
  "scope": "local",
  "created": "2023-01-01T00:00:00Z",
  "ipam": {
    "driver": "default",
    "config": [
      {
        "subnet": "172.17.0.0/16",
        "gateway": "172.17.0.1"
      }
    ]
  },
  "containers": {
    "abc123def456": {
      "name": "nginx",
      "endpoint_id": "def456abc123",
      "mac_address": "02:42:ac:11:00:02",
      "ipv4_address": "172.17.0.2/16",
      "ipv6_address": ""
    }
  },
  "options": {
    "com.docker.network.bridge.default_bridge": "true",
    "com.docker.network.bridge.enable_icc": "true",
    "com.docker.network.bridge.enable_ip_masquerade": "true",
    "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
    "com.docker.network.bridge.name": "docker0",
    "com.docker.network.driver.mtu": "1500"
  },
  "labels": {}
}
```

#### Create Network

```
POST /api/networks
```

Creates a new network.

**Request Body:**

```json
{
  "name": "my-network",
  "driver": "bridge",
  "ipam": {
    "driver": "default",
    "config": [
      {
        "subnet": "172.18.0.0/16",
        "gateway": "172.18.0.1"
      }
    ]
  },
  "options": {
    "com.docker.network.bridge.name": "my-bridge"
  },
  "labels": {
    "com.example.description": "My custom network"
  }
}
```

**Response:**

```json
{
  "id": "def456abc123",
  "name": "my-network",
  "driver": "bridge",
  "scope": "local",
  "created": "2023-01-01T00:00:00Z"
}
```

#### Remove Network

```
DELETE /api/networks/{id}
```

Removes a network.

**Response:**

```json
{
  "id": "def456abc123",
  "removed": true
}
```

### Compose

#### List Compose Projects

```
GET /api/compose
```

Returns a list of all Docker Compose projects.

**Response:**

```json
{
  "projects": [
    {
      "name": "my-project",
      "path": "/path/to/docker-compose.yml",
      "services": ["web", "db"],
      "status": "running"
    }
  ],
  "total": 1
}
```

#### Get Compose Project Details

```
GET /api/compose/{name}
```

Returns detailed information about a specific Docker Compose project.

**Response:**

```json
{
  "name": "my-project",
  "path": "/path/to/docker-compose.yml",
  "services": [
    {
      "name": "web",
      "image": "nginx:latest",
      "container_id": "abc123def456",
      "status": "running"
    },
    {
      "name": "db",
      "image": "postgres:latest",
      "container_id": "def456abc123",
      "status": "running"
    }
  ],
  "networks": ["my-project_default"],
  "volumes": ["my-project_db-data"]
}
```

#### Start Compose Project

```
POST /api/compose/{name}/up
```

Starts a Docker Compose project.

**Query Parameters:**

- `detach` (boolean): Run in detached mode (default: true)
- `build` (boolean): Build images before starting containers (default: false)

**Response:**

```json
{
  "name": "my-project",
  "status": "running",
  "services": ["web", "db"]
}
```

#### Stop Compose Project

```
POST /api/compose/{name}/down
```

Stops a Docker Compose project.

**Query Parameters:**

- `volumes` (boolean): Remove named volumes (default: false)
- `images` (string): Remove images, one of: "local", "all", "none" (default: "none")

**Response:**

```json
{
  "name": "my-project",
  "status": "stopped"
}
```

### Security

#### Scan Image

```
POST /api/security/scan
```

Scans an image for vulnerabilities.

**Request Body:**

```json
{
  "image": "nginx:latest"
}
```

**Response:**

```json
{
  "image": "nginx:latest",
  "scan_id": "abc123def456",
  "status": "completed",
  "vulnerabilities": [
    {
      "id": "CVE-2023-12345",
      "package": "openssl",
      "version": "1.1.1k-1",
      "fixed_version": "1.1.1l-1",
      "severity": "HIGH",
      "description": "Vulnerability in OpenSSL...",
      "link": "https://nvd.nist.gov/vuln/detail/CVE-2023-12345"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 5,
    "unknown": 0,
    "total": 8
  }
}
```

#### Audit Container

```
POST /api/security/audit
```

Audits a container for security issues.

**Request Body:**

```json
{
  "container": "abc123def456"
}
```

**Response:**

```json
{
  "container": "abc123def456",
  "name": "nginx",
  "audit_id": "def456abc123",
  "status": "completed",
  "issues": [
    {
      "id": "DOCKER-0001",
      "category": "configuration",
      "severity": "HIGH",
      "description": "Container is running as root",
      "recommendation": "Use a non-root user in the Dockerfile"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "total": 6
  }
}
```

### Backup

#### List Backups

```
GET /api/backup
```

Returns a list of all backups.

**Response:**

```json
{
  "backups": [
    {
      "id": "abc123def456",
      "type": "container",
      "name": "nginx",
      "created": "2023-01-01T00:00:00Z",
      "size": 10485760
    }
  ],
  "total": 1
}
```

#### Create Backup

```
POST /api/backup
```

Creates a new backup.

**Request Body:**

```json
{
  "type": "container",
  "name": "nginx",
  "description": "Nginx backup before update"
}
```

**Response:**

```json
{
  "id": "abc123def456",
  "type": "container",
  "name": "nginx",
  "created": "2023-01-01T00:00:00Z",
  "size": 10485760,
  "description": "Nginx backup before update",
  "status": "completed"
}
```

#### Restore Backup

```
POST /api/backup/{id}/restore
```

Restores a backup.

**Response:**

```json
{
  "id": "abc123def456",
  "type": "container",
  "name": "nginx",
  "status": "restored"
}
```

#### Delete Backup

```
DELETE /api/backup/{id}
```

Deletes a backup.

**Response:**

```json
{
  "id": "abc123def456",
  "removed": true
}
```

### Chat

#### Send Message

```
POST /api/chat/messages
```

Sends a message to the AI chat system.

**Request Body:**

```json
{
  "session_id": "abc123def456",
  "text": "How do I optimize my Nginx container?",
  "context": {
    "current_page": "containers",
    "current_container_id": "def456abc123"
  }
}
```

**Response:**

```json
{
  "message": {
    "id": "msg123",
    "type": "ai",
    "text": "To optimize your Nginx container, you can...",
    "timestamp": "2023-01-01T00:00:00Z"
  },
  "session_id": "abc123def456",
  "suggestions": [
    "Tell me more about Nginx caching",
    "How do I set up Nginx as a reverse proxy?"
  ]
}
```

#### Create Session

```
POST /api/chat/sessions
```

Creates a new chat session.

**Request Body:**

```json
{
  "title": "Nginx Optimization",
  "is_active": true
}
```

**Response:**

```json
{
  "id": "abc123def456",
  "title": "Nginx Optimization",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "messages": [
    {
      "id": "msg123",
      "type": "ai",
      "text": "Hello! I'm your DockerForge AI assistant. How can I help you with your Docker containers today?",
      "timestamp": "2023-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Sessions

```
GET /api/chat/sessions
```

Returns a list of all chat sessions.

**Response:**

```json
{
  "sessions": [
    {
      "id": "abc123def456",
      "title": "Nginx Optimization",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1
}
```

#### Get Session Messages

```
GET /api/chat/messages?session_id=abc123def456
```

Returns all messages in a chat session.

**Response:**

```json
{
  "messages": [
    {
      "id": "msg123",
      "type": "ai",
      "text": "Hello! I'm your DockerForge AI assistant. How can I help you with your Docker containers today?",
      "timestamp": "2023-01-01T00:00:00Z"
    },
    {
      "id": "msg124",
      "type": "user",
      "text": "How do I optimize my Nginx container?",
      "timestamp": "2023-01-01T00:00:01Z"
    },
    {
      "id": "msg125",
      "type": "ai",
      "text": "To optimize your Nginx container, you can...",
      "timestamp": "2023-01-01T00:00:02Z"
    }
  ],
  "total": 3
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of a request:

- `200 OK`: The request was successful
- `201 Created`: The resource was created successfully
- `400 Bad Request`: The request was invalid
- `401 Unauthorized`: Authentication is required
- `403 Forbidden`: The authenticated user does not have permission to access the resource
- `404 Not Found`: The resource was not found
- `409 Conflict`: The request could not be completed due to a conflict
- `500 Internal Server Error`: An error occurred on the server

Error responses include a JSON object with details about the error:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Container with ID 'abc123def456' not found",
    "details": {
      "resource_type": "container",
      "resource_id": "abc123def456"
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits are applied per API key or IP address.

Rate limit headers are included in all API responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current time window
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window
- `X-RateLimit-Reset`: The time at which the current rate limit window resets, in UTC epoch seconds

If you exceed the rate limit, you will receive a `429 Too Many Requests` response.

## Pagination

List endpoints support pagination using the `limit` and `offset` query parameters:

- `limit`: The maximum number of items to return (default: 100, max: 1000)
- `offset`: The number of items to skip (default: 0)

Paginated responses include metadata about the total number of items:

```json
{
  "containers": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

## Versioning

The API is versioned to ensure backward compatibility. The current version is v1.

You can specify the API version in the URL:

```
http://localhost:54321/api/v1/containers
```

If no version is specified, the latest version is used.

## WebSockets

The API provides WebSocket endpoints for real-time updates:

### Container Events

```
ws://localhost:54321/api/ws/containers
```

Provides real-time updates about container events (create, start, stop, die, etc.).

### Container Logs

```
ws://localhost:54321/api/ws/containers/{id}/logs
```

Streams the logs of a specific container in real-time.

### Chat

```
ws://localhost:54321/api/ws/chat/{session_id}
```

Provides real-time updates for a chat session.

## SDKs and Client Libraries

DockerForge provides official client libraries for several programming languages:

- [Python SDK](https://github.com/dockerforge/dockerforge-python)
- [JavaScript SDK](https://github.com/dockerforge/dockerforge-js)
- [Go SDK](https://github.com/dockerforge/dockerforge-go)

## API Changelog

### v1.0.0 (2023-01-01)

- Initial release of the DockerForge API

## Additional Resources

- [API Examples](API_EXAMPLES.md): Common API usage examples
- [API Troubleshooting](API_TROUBLESHOOTING.md): Solutions to common API issues
