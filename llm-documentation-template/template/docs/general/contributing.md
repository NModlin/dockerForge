<!--
@doc-meta {
  "id": "contributing-guide",
  "version": "1.0",
  "last_updated": "2025-03-18",
  "update_frequency": "as-needed",
  "maintainer": "system",
  "status": "current",
  "category": "general"
}
-->

# Contributing to the Project

Thank you for your interest in contributing to the project! This document provides guidelines and instructions for contributing.

<!-- 
@llm-instructions
DOCUMENT PURPOSE: Provide guidelines for contributing to the project
PRIMARY AUDIENCE: Potential contributors
MAINTENANCE PRIORITY: Medium (community document)

MAINTENANCE GUIDELINES:
- Keep the development workflow instructions up-to-date with current best practices
- Update the project structure section if the file organization changes
- Ensure the license information is always current and accurate
- Do not modify the coding standards unless there is a project-wide decision to change them
-->

## Code of Conduct

Please read and follow our [Code of Conduct](code-of-conduct.md) to help us maintain a healthy and welcoming community.

## How to Contribute

There are many ways to contribute to the project:

1. **Report bugs**: If you find a bug, please report it by creating an issue in the GitHub repository.
2. **Suggest features**: If you have an idea for a new feature, please suggest it by creating an issue in the GitHub repository.
3. **Improve documentation**: Help us improve the documentation by fixing typos, adding examples, or clarifying explanations.
4. **Write code**: Contribute code by fixing bugs, implementing features, or improving existing code.

## Development Workflow

### Setting Up the Development Environment

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

```bash
git clone https://github.com/your-username/project-name.git
cd project-name
```

3. Create a virtual environment and install the development dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Making Changes

1. Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes to the code or documentation.
3. Run the tests to ensure your changes don't break existing functionality:

```bash
pytest
```

4. Run the linter to ensure your code follows the project's style guidelines:

```bash
flake8
```

5. Commit your changes with a descriptive commit message:

```bash
git commit -m "Add feature: your feature description"
```

6. Push your changes to your fork:

```bash
git push origin feature/your-feature-name
```

7. Create a pull request from your fork to the main repository.

### Pull Request Guidelines

When creating a pull request, please:

1. Provide a clear and descriptive title.
2. Include a detailed description of the changes you've made.
3. Reference any related issues using the GitHub issue number (e.g., "Fixes #123").
4. Ensure all tests pass and the code follows the project's style guidelines.
5. Update the documentation if necessary.

## Project Structure

<!-- @llm-update-section
This section describes the project structure and should be updated when the structure changes.
-->

The project is organized as follows:

```
project-name/
├── docs/                   # Documentation
│   ├── api/                # API reference
│   ├── developer-guide/    # Developer guide
│   ├── general/            # General documentation
│   ├── project-plans/      # Project plans
│   └── user-guide/         # User guide
├── src/                    # Source code
│   ├── core/               # Core functionality
│   └── utils/              # Utility functions
├── tests/                  # Test files
└── scripts/                # Utility scripts
```

## Coding Standards

The project follows these coding standards:

1. **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
2. **Type Hints**: Use type hints for function and method signatures.
3. **Docstrings**: Use docstrings to document classes, methods, and functions.
4. **Tests**: Write tests for new functionality and ensure existing tests pass.
5. **Error Handling**: Handle errors appropriately and provide meaningful error messages.
6. **Logging**: Use the logging module for logging messages.

## Documentation

The project uses Markdown for documentation. When contributing to the documentation, please:

1. Use clear and concise language.
2. Provide examples where appropriate.
3. Use proper Markdown formatting.
4. Check for spelling and grammar errors.

## Testing

The project uses pytest for testing. When contributing code, please:

1. Write tests for new functionality.
2. Ensure existing tests pass.
3. Use appropriate test fixtures and mocks.
4. Aim for high test coverage.

## License

By contributing to the project, you agree that your contributions will be licensed under the project's license.

## Questions

If you have any questions about contributing, please feel free to create an issue in the GitHub repository or contact the maintainers directly.

Thank you for your contributions!

<!-- @llm-related-docs
- docs/general/code-of-conduct.md: Update references if contribution process changes
- docs/developer-guide/development-workflow.md: Keep in sync with development workflow instructions here
-->
