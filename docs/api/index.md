<!--
@doc-meta {
  "id": "api-index",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "with-api-changes",
  "maintainer": "system",
  "status": "current",
  "category": "api"
}
-->

# DockerForge API Reference

This section contains comprehensive documentation for the DockerForge API, allowing developers to programmatically interact with DockerForge.

## API Overview

The DockerForge API is a RESTful HTTP API that provides access to DockerForge functionality. The API uses JSON for request and response bodies.

## Authentication

All API requests require authentication. See the [Authentication](api_reference.md#authentication) section in the API Reference for details.

## API Endpoints

### Core API

- [API Reference](api_reference.md) - Complete reference for all API endpoints

### System Management

- [Update System API](update_system.md) - API endpoints for managing DockerForge updates

## API Version History

| Version | Release Date | Notes |
|---------|--------------|-------|
| 1.0     | 2024-10-15   | Initial stable API release |

## Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - The request was successful |
| 201 | Created - Resource was successfully created |
| 400 | Bad Request - The request could not be understood or was missing required parameters |
| 401 | Unauthorized - Authentication failed or user lacks required permissions |
| 403 | Forbidden - Authentication succeeded but authenticated user doesn't have access |
| 404 | Not Found - Resource could not be found |
| 409 | Conflict - Request could not be completed due to a conflict with the current state of the resource |
| 500 | Internal Server Error - An unexpected error occurred on the server |

## Rate Limiting

API requests are subject to rate limiting to prevent abuse. See the [Rate Limiting](api_reference.md#rate-limiting) section in the API Reference for details.

<!-- 
@llm-instructions
This is the index file for DockerForge API documentation.
- Update the API Endpoints section when new API endpoint documentation is added
- Keep the API Version History table up-to-date with each release
- Maintain the Status Codes table with any new status codes added
- Update Rate Limiting information if rate limiting policies change
-->
