# LLM-Friendly Documentation Template

A comprehensive documentation template system optimized for Large Language Model (LLM) maintenance. This package contains everything you need to set up and manage documentation that can be efficiently maintained by both humans and LLMs.

## Package Structure

This package contains two main components:

1. **`template/`**: The core documentation template
   - Complete documentation structure with categories
   - LLM instruction markers for easy maintenance
   - Validation scripts and GitHub integrations
   - Document templates for different content types

2. **`guides/`**: Implementation and usage guides
   - Getting started instructions
   - GitHub integration guidelines
   - LLM maintenance best practices
   - Implementation checklist

## Key Features

- **LLM-Friendly Instructions**: Special markers in HTML comments guide LLMs on how to maintain documentation
- **Structured Metadata**: Consistent metadata format allows tracking documentation relationships
- **Category-Based Organization**: Logical separation of API, user guides, developer guides, and project plans
- **Validation Tooling**: Scripts to ensure documentation quality and consistency
- **GitHub Integration**: Ready-to-use GitHub issue templates and workflows

## Getting Started

1. Copy this entire directory to your project or create a dedicated documentation repository
2. Follow the implementation instructions in the guides directory
3. Customize the template for your specific needs
4. Start creating your documentation using the provided structure and templates

## Documentation Categories

The template includes these documentation categories:

- **API Documentation**: Reference material for APIs and technical interfaces
- **User Guides**: End-user focused documentation for using your product
- **Developer Guides**: Information for developers extending your project
- **Project Plans**: Documentation for ongoing and planned development work
- **General Documentation**: Community guidelines and project information

## Using with LLMs

This template is specifically designed to work well with LLMs for maintenance. The special instruction markers throughout the documentation provide clear guidance on:

- What parts of documents to update and when
- How different documents relate to each other
- What information needs to be preserved
- Specific formatting and structure requirements

For more details on how LLMs can maintain your documentation, see the LLM maintenance guide in the guides directory.

## License

This template is released under the MIT License - see the LICENSE file for details.
