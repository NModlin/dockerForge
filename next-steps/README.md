# Next Steps Guide

This guide walks through how to use the LLM-friendly documentation template.

## 1. Create a GitHub Repository

To use this template for your own project:

1. Create a new GitHub repository
2. Upload the contents of the `llm-docs-template` directory to your repository
3. Configure the repository settings:
   - Enable GitHub Pages if you want to publish the documentation
   - Set up branch protection rules for the main branch
   - Configure GitHub Actions permissions

## 2. Customize the Template

Customize the template for your specific project:

1. **Update Basic Information**:
   - Edit the main `README.md` with your project name and description
   - Update the LICENSE file with your copyright information
   - Edit `docs/index.md` to reflect your project's structure

2. **Configure Metadata**:
   - Modify `docs/docs-metadata.json` to match your project's categories and documents
   - Update category names and descriptions as needed

3. **Adjust Documentation Structure**:
   - Keep or remove categories based on your needs (API, user guides, etc.)
   - Reorganize the directory structure if necessary

## 3. Set Up Development Environment

To work with the validation scripts:

1. Install Node.js dependencies:
   ```bash
   cd llm-docs-template/scripts
   npm install
   ```

2. Make scripts executable:
   ```bash
   chmod +x scripts/*.js
   ```

## 4. Creating New Documentation

There are two ways to create new documentation:

### Method 1: Using the Generator Script

The template includes a document generator script to create new documents from templates:

```bash
cd scripts
node generate-doc.js -t standard -n "Your Document Title" -p "path/to/save/document" -c "category"
```

For example, to create a new API documentation:

```bash
node generate-doc.js -t api -n "User Authentication API" -p "api/auth.md" -c "api"
```

### Method 2: Manual Creation

1. Copy the appropriate template from `_templates/` directory
2. Create the new file in the correct location
3. Replace the placeholder values:
   - Replace `[DOCUMENT_ID]` with a unique ID (kebab-case)
   - Replace `[DOCUMENT_TITLE]` with your document title
   - Replace `[CURRENT_DATE]` with today's date (YYYY-MM-DD)
   - Replace `[DOCUMENT_CATEGORY]` with the appropriate category
4. Update the content with your specific information
5. Add the document to `docs-metadata.json`

## 5. Validating Documentation

Use the validation scripts to ensure documentation quality:

1. **Validate Metadata**:
   ```bash
   cd scripts
   node validate-docs.js
   ```

2. **Check Links**:
   ```bash
   node check-links.js
   ```

3. **Validate LLM Instructions**:
   ```bash
   node validate-llm-instructions.js
   ```

4. **GitHub Actions Integration**:
   These validations will also run automatically through GitHub Actions when changes are pushed.

## 6. LLM Maintenance Guidelines

To ensure LLMs can effectively maintain your documentation:

1. **Always Include Metadata**:
   - Every document should have a `@doc-meta` section
   - Keep IDs consistent and uniquely identifiable

2. **Use Appropriate Instructions**:
   - Include `@llm-instructions` in every document
   - Specify clear DOCUMENT PURPOSE and PRIMARY AUDIENCE
   - Include MAINTENANCE GUIDELINES with specific rules

3. **Section-Specific Markers**:
   - Use `@llm-update-section` for content that changes frequently
   - Use `@llm-reference-section` for technical reference content
   - Use `@llm-procedural-section` for step-by-step procedures

4. **Document Relationships**:
   - Use `@llm-related-docs` to specify which documents should be updated together
   - Include reasons for relationships

5. **Conditional Instructions**:
   - Use `@llm-conditional-instructions` for context-specific guidance
   - Specify different requirements based on document status or type

## 7. Real-World Usage Example

Let's walk through a common scenario:

### Adding API Documentation for a New Endpoint

1. Generate the document:
   ```bash
   cd scripts
   node generate-doc.js -t api -n "User Registration API" -p "api/register.md" -c "api"
   ```

2. Edit the document:
   - Add the endpoint details
   - Include request/response examples
   - Specify error responses
   - Add related documents

3. Update the API index:
   - Add the new endpoint to `docs/api/index.md`

4. Validate the documentation:
   ```bash
   node validate-docs.js
   node check-links.js
   ```

5. Commit and push the changes:
   ```bash
   git add docs/api/register.md docs/api/index.md docs/docs-metadata.json
   git commit -m "Add User Registration API documentation"
   git push
   ```

## 8. Recommended Documentation Workflows

### For Solo Developers

1. Create documentation alongside code changes
2. Run validation scripts locally before committing
3. Use document templates for consistency

### For Teams

1. Create documentation PR alongside code PRs
2. Use GitHub Actions for validation in CI pipeline
3. Have documentation changes reviewed by both technical and non-technical team members
4. Designate documentation maintainers

## Next Steps

Now that you have set up your documentation repository:

1. Start creating your project's essential documentation
2. Customize templates further as needed
3. Consider setting up automated publishing (GitHub Pages, ReadTheDocs, etc.)
4. Develop project-specific LLM instruction markers if needed
