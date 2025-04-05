# GitHub Integration Guide

This guide explains how to fully integrate the LLM-friendly documentation template with GitHub's features for maximum benefit.

## Setting Up as a GitHub Template Repository

To make your repository a GitHub template:

1. Go to your repository on GitHub
2. Click on "Settings" in the top navigation bar
3. Scroll down to the "Template repository" section
4. Check the box "Template repository"
5. Save changes

Now others can create new repositories based on your template:
- The "Use this template" button will appear on your repository
- Users can create new repositories with the same directory structure and files

## GitHub Actions Setup

The template includes GitHub Actions workflows in `.github/workflows/`. Here's how to use them effectively:

### Documentation Validation Workflow

The `doc-validation.yml` workflow automatically validates documentation when changes are pushed:

1. Ensure GitHub Actions is enabled for your repository
2. The workflow will run automatically on:
   - Pushes to main/master that modify docs
   - Pull requests to main/master that modify docs
   - Manual triggers via the "Actions" tab

### Customizing the Workflow

You may want to customize the workflow based on your project's needs:

```yaml
name: Documentation Validation

on:
  push:
    branches: [ main, develop ]  # Add your branches
    paths:
      - 'docs/**'
      - 'other-docs-folder/**'   # Add other doc paths
  pull_request:
    branches: [ main, develop ]  # Add your branches
    paths:
      - 'docs/**'
      - 'other-docs-folder/**'   # Add other doc paths
  workflow_dispatch:

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      # Existing steps...
      
      # Add custom steps here
      - name: Custom validation
        run: node your-custom-script.js
```

## GitHub Pages Integration

You can use GitHub Pages to publish your documentation:

1. Go to repository Settings
2. Navigate to "Pages" in the sidebar
3. Set "Source" to your preferred branch (main/master)
4. Set the folder to `/docs` or `/` based on your structure
5. Click "Save"

Your documentation will be published at `https://username.github.io/repository-name/`.

### Enhancing GitHub Pages

For better documentation with GitHub Pages:

1. Consider adding a theme by creating a `_config.yml` file:
   ```yaml
   remote_theme: pages-themes/minimal@v0.2.0
   plugins:
   - jekyll-remote-theme
   ```

2. Add a `.nojekyll` file if you're using custom HTML/CSS or want to keep underscore-prefixed files

## Issue Templates

The template includes issue templates in `.github/ISSUE_TEMPLATE/`:

- `bug_report.md`: For reporting documentation bugs
- `feature_request.md`: For requesting new documentation features
- `documentation_update.md`: For requesting documentation updates

### Customizing Issue Templates

To customize issue templates for your project:

1. Edit the existing templates in `.github/ISSUE_TEMPLATE/`
2. Add project-specific fields and questions
3. Consider creating a `config.yml` file in the same directory to define issue template chooser settings:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Project Community Forum
    url: https://example.com/forum
    about: Please ask general questions here.
```

## Pull Request Template

The template includes a PR template in `.github/PULL_REQUEST_TEMPLATE.md`:

1. Edit this template to include project-specific requirements
2. Add any required checklists specific to your documentation style
3. Consider adding links to your documentation guidelines

## GitHub Projects Integration

For larger documentation efforts, you can integrate with GitHub Projects:

1. Create a new Project in your GitHub repository
2. Set up columns for documentation status (e.g., "To Do", "In Progress", "Review", "Done")
3. Create documentation tasks as issues
4. Track documentation progress through the project board

## Branch Protection Rules

Implement branch protection for documentation quality:

1. Go to repository Settings > Branches
2. Add a rule for your main branch
3. Enable these settings:
   - Require pull request reviews
   - Require status checks to pass before merging
   - Require branches to be up to date
   - Include administrators

## Automated Review Assignments

Set up automatic reviewer assignment:

1. Create a CODEOWNERS file in the `.github` directory:
   ```
   # Documentation owners
   /docs/  @documentation-team
   
   # Specific documentation areas
   /docs/api/  @api-team
   /docs/user-guide/  @user-experience-team
   ```

2. GitHub will automatically request reviews from these teams/individuals when changes are made to these files

## GitHub Discussions

Enable GitHub Discussions for documentation feedback:

1. Go to repository Settings
2. Scroll down to "Features"
3. Check "Discussions"
4. Set up categories for different types of documentation discussions:
   - Questions
   - Ideas
   - Documentation Improvements
   - General

## GitHub Actions for Documentation Generation

You can extend the template with additional GitHub Actions for automatic documentation generation:

```yaml
name: Generate API Documentation

on:
  push:
    branches: [ main ]
    paths:
      - 'src/api/**'  # Path to your API code

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm ci
      - name: Generate API documentation
        run: node scripts/generate-api-docs.js
      - name: Commit and push if changed
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "<>"
          git add docs/api/
          git commit -m "Update API documentation" || exit 0
          git push
```

This creates a powerful documentation system that automatically stays up-to-date with your code changes.
