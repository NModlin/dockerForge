# Contributing to DockerForge

Thank you for your interest in contributing to DockerForge! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](code_of_conduct.md) to help us maintain a healthy and welcoming community.

## How to Contribute

There are many ways to contribute to DockerForge:

1. **Report bugs**: If you find a bug, please report it by creating an issue in the GitHub repository.
2. **Suggest features**: If you have an idea for a new feature, please suggest it by creating an issue in the GitHub repository.
3. **Improve documentation**: Help us improve the documentation by fixing typos, adding examples, or clarifying explanations.
4. **Write code**: Contribute code by fixing bugs, implementing features, or improving existing code.

## Development Workflow

### Setting Up the Development Environment

1. Fork the repository on GitHub.
2. Clone your fork to your local machine:

```bash
git clone https://github.com/your-username/dockerforge.git
cd dockerforge
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

The DockerForge project is organized as follows:

```
dockerforge/
├── config/                 # Configuration files
├── docs/                   # Documentation
│   ├── api/                # API reference
│   ├── developer_guide/    # Developer guide
│   └── user_guide/         # User guide
├── examples/               # Example files and usage examples
├── src/                    # Source code
│   ├── backup/             # Backup and restore functionality
│   ├── compose/            # Docker Compose management
│   ├── config/             # Configuration management
│   ├── core/               # Core functionality
│   ├── docker/             # Docker interaction
│   ├── fixes/              # Fix proposal and application
│   ├── monitoring/         # Monitoring functionality
│   ├── notifications/      # Notification system
│   ├── platforms/          # Platform-specific functionality
│   ├── resource_monitoring/ # Resource monitoring
│   ├── security/           # Security scanning and auditing
│   ├── update/             # Update system
│   └── utils/              # Utility functions
├── tests/                  # Test files
└── scripts/                # Utility scripts
```

## Coding Standards

DockerForge follows these coding standards:

1. **PEP 8**: Follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
2. **Type Hints**: Use type hints for function and method signatures.
3. **Docstrings**: Use docstrings to document classes, methods, and functions.
4. **Tests**: Write tests for new functionality and ensure existing tests pass.
5. **Error Handling**: Handle errors appropriately and provide meaningful error messages.
6. **Logging**: Use the logging module for logging messages.

## Documentation

DockerForge uses Markdown for documentation. When contributing to the documentation, please:

1. Use clear and concise language.
2. Provide examples where appropriate.
3. Use proper Markdown formatting.
4. Check for spelling and grammar errors.

## Testing

DockerForge uses pytest for testing. When contributing code, please:

1. Write tests for new functionality.
2. Ensure existing tests pass.
3. Use appropriate test fixtures and mocks.
4. Aim for high test coverage.

## Versioning

DockerForge follows [Semantic Versioning](https://semver.org/). When contributing changes that affect the version number, please:

1. Update the version number in the appropriate files.
2. Update the changelog with a description of the changes.
3. Tag the release with the appropriate version number.

## License

By contributing to DockerForge, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE).

## Questions

If you have any questions about contributing to DockerForge, please feel free to create an issue in the GitHub repository or contact the maintainers directly.

Thank you for your contributions!
