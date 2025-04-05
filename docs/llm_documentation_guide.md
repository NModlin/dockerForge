<!--
@doc-meta {
  "id": "llm-documentation-guide",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "with-structure-changes",
  "maintainer": "system",
  "status": "current",
  "category": null
}
-->

# DockerForge LLM Documentation Guide

This guide is specifically designed for Language Learning Models (LLMs) that are tasked with maintaining, updating, or extending the DockerForge documentation. It explains the documentation structure, metadata format, and best practices for documentation maintenance.

## Documentation Structure

The DockerForge documentation is organized into the following structure:

```
docs/
├── index.md                           # Master index of all documentation
├── docs-metadata.json                 # Machine-readable metadata for all docs
├── llm_documentation_guide.md         # This guide for LLMs
├── api/                               # API documentation
│   ├── index.md                       # API documentation index
│   ├── api_reference.md               # General API reference
│   └── update_system.md               # Update system API reference
├── developer_guide/                   # Developer-focused documentation
│   ├── index.md                       # Developer guide index
│   └── update_system.md               # Update system developer guide
├── general/                           # General project documentation
│   ├── index.md                       # General documentation index
│   ├── contributing.md                # Contributing guidelines
│   └── code_of_conduct.md             # Code of conduct
├── project_plans/                     # Project planning documentation
│   ├── index.md                       # Project plans index
│   ├── alpha_plan.md                  # Alpha plan for WebUI fix
│   ├── security_upgrade_project_plan.md # Security upgrade project plan
│   └── future_projects/               # Templates for future projects
│       └── template.md                # Project plan template
└── user_guide/                        # User-focused documentation
    ├── index.md                       # User guide index
    ├── installation_guide.md          # Installation instructions
    ├── user_manual.md                 # User manual
    ├── troubleshooting_guide.md       # Troubleshooting guide
    ├── chat_agent_guide.md            # Guide for the chat agent
    └── update_system.md               # Update system user guide
```

## Document Metadata

Each document in the DockerForge documentation system includes metadata in a standardized format at the beginning of the file. This metadata helps organize and maintain the documentation.

```markdown
<!--
@doc-meta {
  "id": "unique-document-id",
  "version": "1.0",
  "last_updated": "YYYY-MM-DD",
  "update_frequency": "with-changes|weekly|monthly|quarterly|as-needed",
  "maintainer": "system|team-name",
  "status": "current|draft|deprecated",
  "category": "user_guide|api|developer_guide|project_plan|general"
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
  "last_updated": "2025-03-18",
  "document_count": 15,
  "categories": [
    {
      "name": "user_guide",
      "title": "User Guides",
      "description": "Documentation for end users",
      "index_path": "docs/user_guide/index.md"
    },
    // Additional categories...
  ],
  "documents": [
    {
      "path": "docs/index.md",
      "title": "DockerForge Documentation",
      "category": null,
      "status": "current",
      "last_updated": "2025-03-18",
      "update_frequency": "with-changes",
      "related_docs": []
    },
    // Additional documents...
  ]
}
```

## LLM Instructions

Many documents contain specific instructions for LLMs about how to maintain that particular document. These instructions are enclosed in HTML comments:

```markdown
<!-- 
@llm-instructions
This document follows the DockerForge documentation standard.
- Do not modify the @doc-meta section except to update version and last_updated
- Maintain the existing structure and headers
- Add new sections as needed following the established pattern
- Update the table of contents if present
- When updating status information, reflect changes in index files
-->
```

## Section-Specific Update Markers

Some documents contain markers for sections that require special handling:

```markdown
<!-- @llm-update-section
Instructions for updating this specific section
Can include rules, examples, or update frequency
-->

## Section Title

Content that should be updated according to the above rules.
```

## Document Relationships

Documents may reference related documents that should be updated when the primary document changes:

```markdown
<!-- 
@llm-related-docs
- docs/api/related_file.md: Update this if API endpoints change
- docs/user_guide/another_file.md: Update tutorial if this feature changes
-->
```

## Documentation Update Process

When updating documentation, follow these steps:

1. **Check docs-metadata.json**: Start by examining the metadata file to understand the document structure and relationships
2. **Identify documents to update**: Based on the change, identify all documents that need updating
3. **Check document metadata**: Review the metadata of each document to understand its purpose and update frequency
4. **Check document instructions**: Look for LLM instructions comments in the document
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

## Adding New Documentation

When adding new documentation:

1. Determine the appropriate category for the new document
2. Create the document using the appropriate template from an existing document
3. Add metadata to the document
4. Add the document to the relevant index file
5. Add the document to docs-metadata.json
6. Update any related documents to reference the new document

## Removing Documentation

When removing documentation:

1. Mark the document as deprecated in its metadata
2. Update any indexes or documents that reference the deprecated document
3. Update docs-metadata.json to reflect the deprecated status

## Maintenance Example: Updating a Document

Here's an example of updating a document:

1. Check docs-metadata.json to understand the document's metadata and relationships
2. Read the document's LLM instructions
3. Make the necessary changes following the instructions
4. Update the `last_updated` field in the document's metadata
5. Check for any related documents that need updates
6. If the document is referenced in an index, check if the index needs updating
7. Update docs-metadata.json with the new `last_updated` value

## Special Considerations for Project Plans

Project plans in the `project_plans` directory have special requirements:

1. Keep implementation prompts exactly as written for compatibility with automation
2. Update project status in the relevant index as the project progresses
3. Move projects between active/planned/completed sections based on status
4. Use the template in `future_projects/template.md` for new project plans

## Conclusion

By following this guide, you'll help maintain the consistency, accuracy, and usability of the DockerForge documentation. If you encounter any ambiguities or special cases not covered by this guide, apply best judgment based on the existing documentation patterns.

<!-- 
@llm-instructions
This is the master guide for LLMs maintaining DockerForge documentation.
- Keep this document up-to-date with any changes to documentation structure
- Update the file tree if directories or key files change
- Keep the metadata description current with any metadata format changes
- Add examples and clarifications if common LLM maintenance issues are identified
-->
