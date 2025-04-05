# LLM Documentation Maintenance Guide

This guide explains how LLMs (Large Language Models) can effectively maintain documentation using the template, and how humans can structure their documentation to maximize LLM effectiveness.

## How LLMs Interact With This Documentation

LLMs have certain capabilities and limitations when working with documentation:

1. **Context Awareness**: LLMs can only "see" what's in their context window
2. **Instruction Following**: LLMs perform better with explicit, structured instructions
3. **Pattern Recognition**: LLMs excel at following consistent patterns
4. **Relationship Understanding**: LLMs need explicit hints about document relationships

This template is designed to account for these characteristics and provide optimal guidance to LLMs.

## Key Features for LLM Maintenance

### 1. Metadata Headers

The `@doc-meta` section provides essential context:

```markdown
<!--
@doc-meta {
  "id": "unique-document-id",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "with-changes",
  "maintainer": "system",
  "status": "current",
  "category": "user-guide"
}
-->
```

**Why it helps LLMs**: This structured format allows LLMs to quickly understand the document's purpose, status, and metadata without having to infer it from the content.

### 2. Document-Level Instructions

The `@llm-instructions` section provides high-level guidance:

```markdown
<!-- 
@llm-instructions
DOCUMENT PURPOSE: Define project scope, schedule, and implementation details
PRIMARY AUDIENCE: Project stakeholders, developers, and managers
MAINTENANCE PRIORITY: High (critical project planning document)

MAINTENANCE GUIDELINES:
- Update status information as the project progresses
- Keep timelines accurate and updated
- Maintain implementation details in sync with actual development
- Document all decisions and their rationales
- Track changes to requirements or scope
- Keep the risk assessment current
-->
```

**Why it helps LLMs**: This gives clear, explicit instruction about the document's purpose, audience, and maintenance requirements, helping the LLM make appropriate editorial decisions.

### 3. Section-Specific Markers

Various section markers provide contextual guidance:

```markdown
<!-- @llm-update-section
This section should be updated when [specific conditions].
- [List specific update guidelines for this section]
- [Include instructions on what should be modified and how]
-->
```

**Why it helps LLMs**: These markers provide granular guidance about how to handle specific sections, allowing for more nuanced maintenance.

### 4. Relationship Markers

The `@llm-related-docs` section shows document dependencies:

```markdown
<!-- @llm-related-docs
- docs/api/auth.md: Update this if authentication flow changes
- docs/user-guide/login.md: Update screenshots and process if UI changes
-->
```

**Why it helps LLMs**: This explicitly maps relationships between documents, helping LLMs understand what other documents might need updating.

### 5. Conditional Instructions

The `@llm-conditional-instructions` provides context-specific guidance:

```markdown
<!-- 
@llm-conditional-instructions
IF PROJECT IS IN PLANNING STATUS:
- Focus on completing all sections with as much detail as possible
- Identify any missing information that needs to be gathered

IF PROJECT IS ACTIVE:
- Keep implementation phases updated with current status
- Update risk assessment based on challenges encountered
-->
```

**Why it helps LLMs**: This provides branching logic that helps LLMs make appropriate decisions based on the current state.

## How to Interact with LLMs When Maintaining Documentation

### 1. Providing Clear Instructions to LLMs

When asking an LLM to update documentation, be specific about:

1. **What document(s) need updating**: "Update the User Authentication API documentation"
2. **What changed**: "The rate limiting policy changed from 100 to 200 requests per minute"
3. **What sections are affected**: "Update the Rate Limiting section and any examples that mention rate limits"
4. **Related documents to check**: "Also check if the API Overview document needs updating"

### 2. Effective Prompting Patterns

Use these patterns for better LLM documentation maintenance:

#### For document updates:

```
Please update the [document name] to reflect the following changes:
1. [Change 1]
2. [Change 2]

Pay special attention to:
- [Specific section or aspect]
- [Another section or aspect]

Follow the LLM instructions in the document and ensure that related documents are also checked for consistency.
```

#### For document creation:

```
Please create a new document for [purpose] using the [template type] template.
The document should:
1. [Requirement 1]
2. [Requirement 2]

Replace all placeholder values and ensure the document follows the structure in the template.
Also update the metadata registry to include this new document.
```

### 3. Review Process

After an LLM updates documentation:

1. **Check consistency**: Verify that all related documents are consistent
2. **Verify metadata**: Ensure metadata was properly updated
3. **Validate links**: Check that any links or references are correct
4. **Run validation scripts**: Use the provided validation scripts

## How LLMs Should Approach Documentation Updates

This section is meant for LLMs to follow when updating documentation. It provides a step-by-step methodology.

### Step 1: Understand the Change Request

1. Identify which specific documents need updating
2. Understand the nature of the changes (feature addition, correction, etc.)
3. Determine which sections will be affected
4. Note any dependencies or related documents

### Step 2: Analyze the Current Documentation

1. Review the `@doc-meta` section to understand the document's purpose and status
2. Read all `@llm-instructions` carefully to understand maintenance guidelines
3. Identify relevant section-specific markers (`@llm-update-section`, etc.)
4. Check for `@llm-related-docs` to understand document relationships
5. Look for `@llm-conditional-instructions` that might apply

### Step 3: Plan the Update

1. Determine which sections need modification
2. Plan changes that follow the existing structure and style
3. Check if metadata needs updating (version, last_updated)
4. Identify any related documents that might need consequential updates

### Step 4: Execute the Update

1. Update content according to the guidelines
2. Follow section-specific instructions carefully
3. Preserve existing structure, formatting, and language style
4. Update metadata (especially last_updated and version if significant changes)
5. Add an entry to change logs if present

### Step 5: Verify Consistency

1. Ensure all changes are consistent within the document
2. Check that all referenced information is consistent with related documents
3. Verify that the document still serves its stated purpose
4. Ensure any examples or code snippets remain accurate

## Common LLM Documentation Maintenance Scenarios

### Scenario 1: API Endpoint Change

When an API endpoint changes:

1. Update the specific API endpoint documentation
2. Check the API overview documentation
3. Update any user guides that reference the endpoint
4. Check for code examples in developer guides
5. Update version numbers and last_updated dates

### Scenario 2: User Interface Change

When a user interface changes:

1. Update the relevant user guide sections
2. Replace screenshots with updated ones (note this for human review)
3. Update step-by-step instructions to match the new flow
4. Check for references to the UI in other documents

### Scenario 3: Project Status Update

When a project status changes:

1. Update the project plan status field
2. Update the relevant phase status information
3. Update timelines and dates
4. Update the risk assessment based on current status
5. Update the project listing in the project plans index

### Scenario 4: New Documentation Creation

When creating new documentation:

1. Use the appropriate template
2. Replace all placeholder values
3. Fill in all required sections
4. Add the document to the metadata registry
5. Update relevant index documents to reference the new document

## Best Practices for LLM-Maintained Documentation

1. **Follow Instructions Precisely**: Always adhere to the instructions in `@llm-instructions` and other markers
2. **Maintain Consistency**: Keep style, formatting, and tone consistent
3. **Preserve Structure**: Maintain the existing document structure
4. **Update Metadata**: Always update metadata when changing documents
5. **Check Relationships**: Review and update related documents
6. **Respect Purpose**: Ensure changes align with the document's stated purpose
7. **Note Ambiguities**: If instructions are unclear, note this for human review

By following these guidelines, LLMs can effectively maintain documentation using this template structure, resulting in consistent, accurate, and up-to-date documentation.
