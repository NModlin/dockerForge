# Contributing to DockerForge

Thank you for your interest in contributing to DockerForge! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Community](#community)

## Code of Conduct

DockerForge has adopted a Code of Conduct that we expect project participants to adhere to. Please read the [full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker installed and running
- Git

### Fork and Clone the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/dockerforge.git
   cd dockerforge
   ```

3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/dockerforge/dockerforge.git
   ```

4. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

### Setting Up the Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running the Application

To run the CLI in development mode:
```bash
python -m src.cli
```

To run the web interface in development mode:
```bash
python -m src.web.api.main
```

## Project Structure

The DockerForge project is organized as follows:

```
dockerforge/
├── config/                 # Configuration files
├── data/                   # Data storage
├── docs/                   # Documentation
├── examples/               # Example files and usage
├── src/                    # Source code
│   ├── backup/             # Backup and restore functionality
│   ├── compose/            # Docker Compose management
│   ├── config/             # Configuration management
│   ├── core/               # Core functionality
│   │   └── agents/         # AI agents
│   ├── docker/             # Docker integration
│   ├── monitoring/         # Monitoring functionality
│   ├── notifications/      # Notification system
│   ├── platforms/          # Platform-specific code
│   ├── resource_monitoring/# Resource monitoring
│   ├── security/           # Security scanning and auditing
│   ├── update/             # Update system
│   ├── utils/              # Utility functions
│   ├── web/                # Web interface
│   │   ├── api/            # Backend API
│   │   │   ├── models/     # Database models
│   │   │   ├── routers/    # API routes
│   │   │   ├── schemas/    # Pydantic schemas
│   │   │   └── services/   # Business logic
│   │   └── frontend/       # Frontend code (Vue.js)
│   ├── cli.py              # CLI entry point
│   └── __init__.py         # Package initialization
├── tests/                  # Test suite
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
├── .gitignore              # Git ignore file
├── LICENSE                 # License file
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # Project readme
└── setup.py                # Setup script
```

## Coding Standards

DockerForge follows these coding standards:

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use [mypy](https://mypy.readthedocs.io/) for type checking
- Use docstrings for all public functions, classes, and methods
- Use type hints for function parameters and return values

### JavaScript/Vue.js

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use ESLint for linting
- Use Prettier for code formatting
- Follow Vue.js style guide for Vue components

### General

- Write clear, descriptive variable and function names
- Keep functions small and focused on a single task
- Write comprehensive tests for new functionality
- Document complex logic with comments
- Update documentation when changing functionality

## Commit Guidelines

DockerForge follows the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect the meaning of the code (formatting, etc.)
- `refactor`: Code changes that neither fix a bug nor add a feature
- `perf`: Performance improvements
- `test`: Adding or correcting tests
- `chore`: Changes to the build process or auxiliary tools

Examples:
```
feat(backup): add incremental backup support
fix(monitoring): correct CPU usage calculation
docs: update installation instructions
```

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update documentation if necessary
3. Add tests for new functionality
4. Run the test suite to ensure all tests pass
5. Submit a pull request to the `main` branch
6. Wait for code review and address any feedback
7. Once approved, your pull request will be merged

### Pull Request Template

When creating a pull request, please use the provided template and fill in all relevant sections.

## Testing

DockerForge uses pytest for testing. To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=src
```

### Writing Tests

- Write unit tests for all new functionality
- Write integration tests for complex interactions
- Mock external dependencies when appropriate
- Aim for high test coverage, especially for critical functionality
- Use descriptive test names that explain what is being tested

## Documentation

DockerForge uses Markdown for documentation. When contributing:

- Update documentation for any changed functionality
- Add documentation for new features
- Use clear, concise language
- Include examples where appropriate
- Check for spelling and grammar errors

## Issue Reporting

When reporting issues, please use the provided issue template and include:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (OS, Docker version, DockerForge version)
- Screenshots or logs if applicable

## Feature Requests

When requesting features, please use the provided feature request template and include:

- A clear, descriptive title
- A detailed description of the feature
- The problem the feature would solve
- Potential implementation ideas (optional)
- Any relevant examples or references

## Community

Join the DockerForge community:

- [Discord Server](https://discord.gg/dockerforge)
- [GitHub Discussions](https://github.com/dockerforge/dockerforge/discussions)
- [Twitter](https://twitter.com/dockerforge)

## License

By contributing to DockerForge, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Acknowledgements

Thank you to all the contributors who have helped make DockerForge better!
