<!--
@doc-meta {
  "id": "[DOCUMENT_ID]",
  "version": "1.0",
  "last_updated": "[CURRENT_DATE]",
  "update_frequency": "with-api-changes",
  "maintainer": "system",
  "status": "current",
  "category": "api"
}
-->

# [DOCUMENT_TITLE]

<!-- 
@llm-instructions
DOCUMENT PURPOSE: Document API endpoints for developer integration
PRIMARY AUDIENCE: Developers integrating with the API
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
- docs/user-guide/integration.md: Update user guidance if endpoint behavior changes
-->

## Endpoint Overview

<!-- @llm-reference-section
This section contains core reference information about the endpoint.
- HTTP method must match the implementation exactly
- Path parameters must be clearly marked with {braces}
- Purpose description should be concise but complete
-->

**Method:** [HTTP METHOD]  
**Path:** `/api/path/to/endpoint/{parameter}`  
**Purpose:** [Brief description of what this endpoint does]

## Authentication

<!-- @llm-security-section
This section defines security requirements.
- Authentication requirements must be accurate
- Permission requirements must be clearly stated
- Any special security considerations must be highlighted
-->

[Describe authentication requirements]

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
| `parameter` | string | Yes | [Parameter description] |

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param1` | string | No | `null` | [Parameter description] |
| `param2` | integer | No | `0` | [Parameter description] |

## Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | [Authentication details] |
| `Content-Type` | Yes | Must be `application/json` |

## Request Body

[If applicable, describe the request body format]

```json
{
  "property1": "value1",
  "property2": 123,
  "property3": {
    "nested": "value"
  }
}
```

## Example Request

<!-- @llm-example-section
This section provides practical usage examples.
- Examples should be complete and valid
- Include all required parameters and headers
- Show proper formatting for the request
- Update examples when endpoint behavior changes
-->

```http
[HTTP METHOD] /api/path/to/endpoint/example?param1=value HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "property1": "value1",
  "property2": 123
}
```

## Success Response

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
  "id": "resource-id",
  "property1": "value1",
  "property2": 123,
  "created_at": "2025-03-18T12:00:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the resource |
| `property1` | string | [Description of property1] |
| `property2` | integer | [Description of property2] |
| `created_at` | string | ISO 8601 timestamp of resource creation |

## Error Responses

<!-- @llm-error-section
For each error response:
- Status code must be accurate and appropriate
- Error messages must be helpful
- Include all possible error codes
- Update when error handling changes
-->

### 400 Bad Request

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "property1",
        "issue": "Field is required"
      }
    ]
  }
}
```

### 401 Unauthorized

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Authentication required"
  }
}
```

### 403 Forbidden

```json
{
  "error": {
    "code": "forbidden",
    "message": "Insufficient permissions",
    "details": {
      "required_permission": "resource:write"
    }
  }
}
```

### 404 Not Found

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Resource not found"
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

[Describe rate limiting policies]

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
| 1.0 | [CURRENT_DATE] | Initial documentation |

## Notes

<!-- @llm-notes-section
This section contains additional information.
- Best practices for usage
- Common issues and workarounds
- Performance considerations
- Update when new information becomes available
-->

[Additional notes, best practices, or guidance]

## See Also

<!-- @llm-related-resources-section
This section contains related resources.
- Related endpoints should be linked
- Supporting documentation should be referenced
- Update when new related resources become available
-->

- [Related Endpoint 1](related-endpoint-1.md)
- [Related Endpoint 2](related-endpoint-2.md)
