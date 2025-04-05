# LLM-Friendly Documentation Template

A comprehensive GitHub template for creating documentation that is optimized for both human readers and Large Language Models (LLMs).

## Overview

This template provides a structured approach to creating and maintaining technical documentation that can be efficiently processed and updated by LLMs while remaining accessible and useful for human readers. It includes:

- Standardized directory structure
- Metadata and relationship tracking
- LLM-specific instruction formats
- Document templates for various content types
- Scripts for validation and maintenance
- GitHub integration for workflow automation

## Features

### 📋 Structured Documentation

- Consistent organization across document types
- Clear categorization (API, User Guides, Developer Guides, etc.)
- Standardized formatting and section structure

### 🤖 LLM-Optimized Instructions

- Machine-readable metadata
- Context-aware update instructions
- Section-specific guidance
- Relationship mapping between documents

### 🔄 Documentation Lifecycle Management

- Status tracking (draft, current, deprecated)
- Version history
- Update frequency indicators
- Relationship-based update triggers

### 🧰 Tools and Scripts

- Document validation
- Metadata consistency checking
- Link validation
- New document generation

### 🔗 GitHub Integration

- Issue templates for documentation-related tasks
- PR templates for documentation changes
- GitHub Actions for automated validation

## Getting Started

1. Click "Use this template" to create a new repository based on this template
2. Clone your new repository
3. Customize the documentation to fit your project needs:
   - Edit the index.md files in each directory
   - Update the docs-metadata.json file
   - Adjust the document templates in _templates/
   - Configure GitHub workflows as needed

## Directory Structure

```
llm-docs-template/
├── .github/                         # GitHub-specific files
│   ├── ISSUE_TEMPLATE/              # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md     # PR template
│   └── workflows/                   # GitHub Actions workflows
├── docs/                            # Main documentation directory
│   ├── index.md                     # Master index
│   ├── docs-metadata.json           # Machine-readable metadata registry
│   ├── llm-guide.md                 # Guide for LLMs maintaining docs
│   ├── api/                         # API documentation
│   ├── user-guide/                  # User-facing documentation
│   ├── developer-guide/             # Developer documentation
│   ├── project-plans/               # Project planning documentation
│   └── general/                     # General documentation
├── _templates/                      # Template files for new documentation
├── scripts/                         # Utility scripts
└── LICENSE                          # Repository license
```

## Documentation Types

### API Documentation

Reference material for application programming interfaces:
- Endpoint specifications
- Parameter details
- Request/response examples
- Error handling information

### User Guides

End-user focused documentation:
- Installation instructions
- Feature guides
- Walkthroughs and tutorials
- Troubleshooting information

### Developer Guides

Documentation for developers working on the project:
- Architecture overviews
- Design patterns
- Implementation guides
- Extension points

### Project Plans

Planning and roadmap documentation:
- Project proposals
- Implementation plans
- Release schedules
- Feature roadmaps

### General Documentation

Community and project-level documentation:
- Contributing guidelines
- Code of conduct
- License information
- Community resources

## LLM Maintenance Instructions

This template includes special instructions for LLMs in the form of HTML comments. These instructions help guide LLMs when updating or modifying the documentation. Key instruction types include:

- Document-level instructions
- Section-specific instructions
- Content pattern templates
- Relationship markers

For more details, see the [LLM Guide](docs/llm-guide.md).

## License

This template is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
