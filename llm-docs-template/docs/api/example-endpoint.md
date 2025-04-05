<!--
@doc-meta {
  "id": "example-endpoint",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "with-api-changes",
  "maintainer": "system",
  "status": "current",
  "category": "api"
}
-->

# Example API Endpoint

This document demonstrates how API endpoint documentation should be structured and includes LLM instruction formats specific to API documentation.

<!-- 
@llm-instructions
DOCUMENT PURPOSE: Document an API endpoint for developer integration
PRIMARY AUDIENCE: Backend developers integrating with the API
MAINTENANCE PRIORITY: High (critical integration point)

MAINTENANCE GUIDELINES:
- All endpoint paths must match the implementation exactly
- Parameter names, types, and descriptions must be accurate
- All status codes and error responses must be documented
- Request and response examples must be up-to-date
- Authentication requirements must be clearly stated
- Rate limiting information must be accurate

CRITICAL CONSIDERATIONS:
- Security warnings must be preserved exactly as written
- Breaking changes must be clearly marked with version information
- Backward compatibility notes must be maintained
-->

<!-- @llm-related-docs
- docs/api/index.md: Update endpoint listing if this endpoint changes
- docs/user-guide/example-usage.md: Update usage examples if endpoint behavior changes
-->

## Endpoint Overview

<!-- @llm-reference-section
This section contains core reference information about the endpoint.
- HTTP method must match the implementation exactly
- Path parameters must be clearly marked with {braces}
- Purpose description should be concise but complete
-->

**Method:** GET  
**Path:** `/api/v1/examples/{id}`  
**Purpose:** Retrieve a specific example resource by its unique identifier.

## Authentication

<!-- @llm-security-section
This section defines security requirements.
- Authentication requirements must be accurate
- Permission requirements must be clearly stated
- Any special security considerations must be highlighted
-->

This endpoint requires authentication using a Bearer token with the `examples:read` permission.

```http
Authorization: Bearer YOUR_TOKEN_HERE
```

## Path Parameters

<!-- @llm-parameters-section
For each parameter:
- Name must match the implementation exactly
- Type must be accurate
- Required/optional status must be clear
- Description should explain purpose and constraints
- Include validation rules where applicable
-->

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | The unique identifier of the example resource. Must be a valid UUID v4. |

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_details` | boolean | No | `false` | Set to `true` to include additional details in the response. |
| `format` | string | No | `"standard"` | Response format. Valid values: `"standard"`, `"detailed"`, `"minimal"`. |

## Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer token for authentication. |
| `Accept` | No | Media type(s) accepted. Default: `application/json`. |

## Example Request

<!-- @llm-example-section
This section provides practical usage examples.
- Examples should be complete and valid
- Include all required parameters and headers
- Show proper formatting for the request
- Update examples when endpoint behavior changes
-->

```http
GET /api/v1/examples/123e4567-e89b-12d3-a456-426614174000?include_details=true HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

## Success Responses

<!-- @llm-response-section
For each response type:
- Status code must be accurate
- Content structure must match actual response
- Include all possible fields in the example
- Field descriptions should be clear and complete
- Update when response structure changes
-->

### 200 OK

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Example Resource",
  "status": "active",
  "created_at": "2025-03-15T08:30:00Z",
  "updated_at": "2025-03-18T14:25:00Z",
  "details": {
    "description": "This is a detailed description of the example resource.",
    "category": "demonstration",
    "properties": {
      "property1": "value1",
      "property2": "value2"
    }
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | The unique identifier (UUID v4) of the example resource. |
| `name` | string | The human-readable name of the resource. |
| `status` | string | Current status. Possible values: `active`, `inactive`, `pending`. |
| `created_at` | string | ISO 8601 timestamp when the resource was created. |
| `updated_at` | string | ISO 8601 timestamp when the resource was last updated. |
| `details` | object | Detailed information (only included when `include_details=true`). |
| `details.description` | string | Long-form description of the resource. |
| `details.category` | string | The category the resource belongs to. |
| `details.properties` | object | Key-value pairs of additional properties. |

## Error Responses

<!-- @llm-error-section
For each error response:
- Status code must be accurate and appropriate
- Error messages must be helpful
- Include all possible error codes
- Update when error handling changes
-->

### 400 Bad Request

Returned when the request contains invalid parameters.

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "id",
        "issue": "Must be a valid UUID v4"
      }
    ]
  }
}
```

### 401 Unauthorized

Returned when authentication is missing or invalid.

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
```

### 403 Forbidden

Returned when the authenticated user doesn't have sufficient permissions.

```json
{
  "error": {
    "code": "forbidden",
    "message": "Insufficient permissions",
    "details": {
      "required_permission": "examples:read"
    }
  }
}
```

### 404 Not Found

Returned when the requested resource doesn't exist.

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Example with the specified ID was not found"
  }
}
```

### 429 Too Many Requests

Returned when the rate limit has been exceeded.

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded",
    "details": {
      "retry_after": 30
    }
  }
}
```

## Rate Limiting

<!-- @llm-operational-section
This section contains operational information.
- Rate limiting rules must be accurate
- Quotas must match current implementation
- Include retry strategies
- Update when operational policies change
-->

This endpoint is subject to rate limiting. Default limits:

- 100 requests per minute per API key
- 1000 requests per hour per API key

Rate limit information is included in the response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616201820
```

If you exceed the rate limit, the API will respond with `429 Too Many Requests` and include a `Retry-After` header indicating how many seconds to wait before retrying.

## Changelog

<!-- @llm-update-section
This section tracks changes to the endpoint.
- All breaking changes must be clearly marked
- New features should be documented with version numbers
- Deprecation notices should include migration paths
- Keep in chronological order, newest first
-->

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-03-18 | Initial release of endpoint |

## Notes

<!-- @llm-notes-section
This section contains additional information.
- Best practices for usage
- Common issues and workarounds
- Performance considerations
- Update when new information becomes available
-->

- For bulk operations, consider using the `/api/v1/examples/batch` endpoint instead.
- This endpoint supports [conditional requests](../developer-guide/conditional-requests.md) using the `If-Modified-Since` and `If-None-Match` headers.
- Response size can be reduced by using the `format=minimal` parameter for bandwidth-constrained environments.

## See Also

<!-- @llm-related-resources-section
This section contains related resources.
- Related endpoints should be linked
- Supporting documentation should be referenced
- Update when new related resources become available
-->

- [List Examples](list-examples.md) - Retrieve multiple example resources
- [Create Example](create-example.md) - Create a new example resource
- [Update Example](update-example.md) - Update an existing example resource
- [Delete Example](delete-example.md) - Delete an example resource
