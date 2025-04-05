<!--
@doc-meta {
  "id": "llm-guide",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "with-structure-changes",
  "maintainer": "system",
  "status": "current",
  "category": null
}
-->

# LLM Documentation Maintenance Guide

This guide is specifically designed for Large Language Models (LLMs) that are tasked with maintaining, updating, or extending documentation. It explains the documentation structure, metadata format, instruction types, and best practices for documentation maintenance.

## Documentation Structure

The documentation is organized into the following structure:

```
docs/
├── index.md                           # Master index of all documentation
├── docs-metadata.json                 # Machine-readable metadata for all docs
├── llm-guide.md                       # This guide for LLMs
├── api/                               # API documentation
│   ├── index.md                       # API documentation index
│   └── [api-specific-docs].md         # Specific API documentation files
├── developer-guide/                   # Developer-focused documentation
│   ├── index.md                       # Developer guide index
│   └── [developer-specific-docs].md   # Specific developer documentation files
├── general/                           # General project documentation
│   ├── index.md                       # General documentation index
│   ├── contributing.md                # Contributing guidelines
│   └── code-of-conduct.md             # Code of conduct
├── project-plans/                     # Project planning documentation
│   ├── index.md                       # Project plans index
│   ├── [project-specific-plans].md    # Specific project plans
│   └── future-projects/               # Templates for future projects
│       └── template.md                # Project plan template
└── user-guide/                        # User-focused documentation
    ├── index.md                       # User guide index
    └── [user-specific-guides].md      # Specific user documentation files
```

## Document Metadata

Each document includes standardized metadata in a format at the beginning of the file:

```markdown
<!--
@doc-meta {
  "id": "unique-document-id",
  "version": "1.0",
  "last_updated": "YYYY-MM-DD",
  "update_frequency": "with-changes|weekly|monthly|quarterly|as-needed",
  "maintainer": "system|team-name",
  "status": "current|draft|deprecated",
  "category": "user-guide|api|developer-guide|project-plan|general"
}
-->
```

### Metadata Fields

- **id**: A unique identifier for the document (kebab-case)
- **version**: The document version (semantic versioning)
- **last_updated**: The date when the document was last updated (ISO format: YYYY-MM-DD)
- **update_frequency**: How often the document should be reviewed for updates
- **maintainer**: The entity responsible for maintaining the document
- **status**: The current status of the document
- **category**: The category the document belongs to (null for top-level docs)

## The docs-metadata.json File

The `docs-metadata.json` file contains a machine-readable index of all documentation files, including their metadata and relationships. This file should be your primary reference when working with the documentation system.

The file has the following structure:

```json
{
  "metadata_version": "1.0",
  "last_updated": "YYYY-MM-DD",
  "document_count": 15,
  "categories": [
    {
      "name": "user-guide",
      "title": "User Guides",
      "description": "Documentation for end users",
      "index_path": "docs/user-guide/index.md"
    },
    // Additional categories...
  ],
  "documents": [
    {
      "path": "docs/index.md",
      "title": "Project Documentation",
      "category": null,
      "status": "current",
      "last_updated": "YYYY-MM-DD",
      "update_frequency": "with-changes",
      "related_docs": []
    },
    // Additional documents...
  ]
}
```

## LLM Instruction Types

This documentation system includes several types of specialized instructions for LLMs. These instructions provide guidance on how to maintain and update the documentation effectively.

### 1. Document-Level Instructions

The primary instruction block appears at the beginning or end of each document:

```markdown
<!-- 
@llm-instructions
DOCUMENT PURPOSE: API reference documentation for authentication endpoints
PRIMARY AUDIENCE: Backend developers integrating with the API
MAINTENANCE PRIORITY: High (security-critical)

MAINTENANCE GUIDELINES:
- Do not modify the @doc-meta section except to update version and last_updated
- Maintain the existing structure and headers
- When adding new endpoints, follow the established pattern
- All authentication examples must include both success and error scenarios
- Security considerations section must be reviewed with every update
- When modifying parameters, update all examples to match
- Maintain backward compatibility notes for deprecated features

CRITICAL CONSIDERATIONS:
- All security-related warnings must be preserved exactly as written
- Rate limiting information must be accurate and consistent
- OAuth flow diagrams must match the implementation exactly
-->
```

### 2. Section-Specific Update Markers

Semantic markers indicate the purpose and update rules for specific sections:

```markdown
<!-- @llm-reference-section
This section contains factual reference information that should only change 
when the underlying system behavior changes.
- API endpoints should match the implementation exactly
- Response structure must reflect the actual API response
- Status codes must be comprehensive and accurate
-->

## Authentication API Reference

...content...

<!-- @llm-procedural-section
This section contains step-by-step procedures that users follow.
- Steps must be clear, concise, and in sequential order
- Each step should have a single action
- Include screenshots for UI-based steps
- Note prerequisites at the beginning
- Include verification steps to confirm success
-->

## Authentication Setup Process

...content...
```

### 3. Domain-Specific Instructions

For technical documentation about specific domains:

```markdown
<!-- @llm-oauth-instructions
When documenting OAuth flows:
- Always include the complete sequence diagram
- Specify all required and optional parameters
- Document both authorization code and implicit flows
- Include security considerations specific to each flow
- Document token lifecycle (issuance, refresh, revocation)
- For public clients, emphasize PKCE requirement
- Include rate limiting and abuse prevention notes
-->
```

### 4. Content Pattern Templates

Templates for common content patterns:

```markdown
<!-- @llm-api-endpoint-template
### [METHOD] /path/to/endpoint

**Description:** Purpose of this endpoint

**Authentication:** Required authentication method

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1`  | string | Yes | Description of parameter |

**Example Request:**
```http
[METHOD] /path/to/endpoint?param1=value
Authorization: Bearer {token}
```

**Success Response:**
```json
{
  "status": "success",
  "data": {
    "property": "value"
  }
}
```

**Error Responses:**
| Status Code | Description | Conditions |
|-------------|-------------|------------|
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing or invalid token |
-->
```

### 5. Conditional Instructions

Instructions that specify different handling based on the type of change:

```markdown
<!-- @llm-conditional-instructions
IF changing authentication method:
- Update all security documentation
- Update client SDK examples
- Check all API endpoint authentication references

IF adding rate limiting:
- Include limits in each affected endpoint
- Add rate limiting section to API overview
- Update error responses to include rate limit errors
-->
```

### 6. Reasoning Prompts

Prompts that encourage reasoning through complex updates:

```markdown
<!-- @llm-reasoning-guide
When updating this architectural diagram:
1. First analyze how the change affects existing components
2. Consider the data flow through the system
3. Identify any new interfaces or connections
4. Verify backwards compatibility with existing clients
5. Ensure security boundaries are clearly marked
-->
```

### 7. Document Relationships

Instructions about related documents that should be updated:

```markdown
<!-- 
@llm-related-docs
- docs/api/auth.md: Update this if authentication flow changes
- docs/user-guide/login.md: Update screenshots and process if UI changes
- docs/developer-guide/auth-module.md: Update implementation details if code changes
-->
```

## Documentation Update Process

When updating documentation, follow these steps:

1. **Check docs-metadata.json**: Start by examining the metadata file to understand the document structure and relationships
2. **Identify documents to update**: Based on the change, identify all documents that need updating
3. **Check document metadata**: Review the metadata of each document to understand its purpose and update frequency
4. **Check document instructions**: Look for LLM instructions in the document
5. **Make necessary updates**: Follow the document-specific instructions when making changes
6. **Update metadata**: Update the `last_updated` field and increment `version` if significant changes are made
7. **Update related documents**: Check for related documents that might need updates
8. **Update index files**: If adding new documents or changing document status, update the relevant index files
9. **Update docs-metadata.json**: Finally, update the metadata file with any changes to documents or relationships

## Best Practices for Documentation Maintenance

1. **Preserve Structure**: Maintain the existing documentation structure and organization
2. **Respect Metadata**: Always update document metadata when making changes
3. **Follow Instructions**: Adhere to document-specific LLM instructions
4. **Keep Relationships**: Maintain document relationships and update related documents
5. **Use Templates**: When creating new documents, use existing documents as templates
6. **Index Consistency**: Keep index files consistent with the documents they reference
7. **Metadata File Accuracy**: Ensure docs-metadata.json accurately reflects the current documentation state
8. **Chunking Complex Instructions**: Break complex instructions into logical chunks for better processing
9. **Context Before Rules**: Understand the context behind rules before applying them
10. **Progressive Disclosure**: Process information from general to specific when making updates

## Adding New Documentation

When adding new documentation:

1. Determine the appropriate category for the new document
2. Create the document using the appropriate template from `_templates/`
3. Add metadata to the document
4. Add the document to the relevant index file
5. Add the document to docs-metadata.json
6. Update any related documents to reference the new document

## Removing Documentation

When removing documentation:

1. Mark the document as deprecated in its metadata
2. Update any indexes or documents that reference the deprecated document
3. Update docs-metadata.json to reflect the deprecated status

## Special Considerations for Different Document Types

### API Documentation

- Maintain exact parameter names, types, and descriptions
- Keep request/response examples synchronized with actual API behavior
- Document all status codes and error conditions
- Preserve security and authentication information
- Update rate limiting information accurately

### User Guides

- Ensure procedures match the current user interface
- Keep screenshots up-to-date with the latest UI
- Organize information in a task-oriented manner
- Use clear, non-technical language appropriate for the audience
- Maintain troubleshooting information for common issues

### Developer Guides

- Ensure code examples are accurate and follow current best practices
- Keep architectural diagrams synchronized with the codebase
- Document design patterns, extension points, and interfaces clearly
- Provide context for implementation decisions
- Maintain backward compatibility information

### Project Plans

- Update status information as projects progress
- Move projects between different status categories as appropriate
- Preserve implementation details and decision rationales
- Keep timelines and milestones updated
- Document learnings and outcomes from completed projects

## Conclusion

By following this guide, you'll help maintain the consistency, accuracy, and usability of the documentation. If you encounter any ambiguities or special cases not covered by this guide, apply best judgment based on the existing documentation patterns.

<!-- 
@llm-instructions
This is the master guide for LLMs maintaining documentation.
- Keep this document up-to-date with any changes to documentation structure
- Update the file tree if directories or key files change
- Keep the metadata description current with any metadata format changes
- Add examples and clarifications if common LLM maintenance issues are identified
- Do not modify the core instruction formats without approval
-->
