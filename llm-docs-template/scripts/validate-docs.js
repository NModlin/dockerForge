#!/usr/bin/env node

/**
 * Documentation Metadata Validation Script
 * 
 * This script validates the documentation metadata for all Markdown files in the docs directory.
 * It checks:
 * - Each file has a proper @doc-meta section
 * - Metadata follows the expected schema
 * - Consistency between metadata and file location
 * - Metadata registry (docs-metadata.json) is accurate
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const chalk = require('chalk');

// Configuration
const DOCS_DIR = path.resolve(__dirname, '../docs');
const METADATA_FILE = path.resolve(DOCS_DIR, 'docs-metadata.json');

// Error counter
let errorCount = 0;

console.log(chalk.blue('Documentation Metadata Validation'));
console.log(chalk.blue('================================='));

// Validate that the metadata registry exists
if (!fs.existsSync(METADATA_FILE)) {
  console.error(chalk.red(`Error: Metadata registry file not found at ${METADATA_FILE}`));
  process.exit(1);
}

// Load the metadata registry
const metadataRegistry = JSON.parse(fs.readFileSync(METADATA_FILE, 'utf8'));
console.log(chalk.green(`✓ Loaded metadata registry with ${metadataRegistry.documents.length} documents`));

// Get all Markdown files in the docs directory
const markdownFiles = glob.sync(`${DOCS_DIR}/**/*.md`);
console.log(chalk.green(`✓ Found ${markdownFiles.length} Markdown files to validate`));

// Map to store documents found in the filesystem
const filesystemDocs = new Map();

// Validate each Markdown file
markdownFiles.forEach(filePath => {
  const relativePath = path.relative(path.dirname(DOCS_DIR), filePath);
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Extract metadata
  const metadataMatch = content.match(/<!--\s*@doc-meta\s*({[\s\S]*?})\s*-->/);
  
  if (!metadataMatch) {
    console.error(chalk.red(`Error: Missing @doc-meta section in ${relativePath}`));
    errorCount++;
    return;
  }
  
  try {
    const metadata = JSON.parse(metadataMatch[1]);
    
    // Validate required fields
    const requiredFields = ['id', 'version', 'last_updated', 'update_frequency', 'maintainer', 'status'];
    for (const field of requiredFields) {
      if (!metadata[field]) {
        console.error(chalk.red(`Error: Missing required field '${field}' in metadata for ${relativePath}`));
        errorCount++;
      }
    }
    
    // Validate date format (YYYY-MM-DD)
    if (metadata.last_updated) {
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(metadata.last_updated)) {
        console.error(chalk.red(`Error: Invalid date format for 'last_updated' in ${relativePath}. Should be YYYY-MM-DD.`));
        errorCount++;
      }
    }
    
    // Validate status is one of the allowed values
    if (metadata.status && !['current', 'draft', 'deprecated'].includes(metadata.status)) {
      console.error(chalk.red(`Error: Invalid status '${metadata.status}' in ${relativePath}. Should be one of: current, draft, deprecated.`));
      errorCount++;
    }
    
    // Store valid document
    filesystemDocs.set(relativePath, metadata);
    
  } catch (error) {
    console.error(chalk.red(`Error parsing metadata in ${relativePath}: ${error.message}`));
    errorCount++;
  }
});

console.log(chalk.green(`✓ Validated metadata in ${filesystemDocs.size} files`));

// Check consistency between filesystem and metadata registry
const registryPaths = new Set(metadataRegistry.documents.map(doc => doc.path));
const filesystemPaths = new Set(filesystemDocs.keys());

// Files in filesystem but not in registry
for (const filePath of filesystemPaths) {
  if (!registryPaths.has(filePath)) {
    console.warn(chalk.yellow(`Warning: File ${filePath} exists but is not in the metadata registry`));
  }
}

// Files in registry but not in filesystem
for (const filePath of registryPaths) {
  if (!filesystemPaths.has(filePath)) {
    console.error(chalk.red(`Error: File ${filePath} is in the metadata registry but doesn't exist in the filesystem`));
    errorCount++;
  }
}

// Validate category references
for (const [filePath, metadata] of filesystemDocs.entries()) {
  if (metadata.category) {
    const category = metadataRegistry.categories.find(cat => cat.name === metadata.category);
    if (!category) {
      console.error(chalk.red(`Error: File ${filePath} references non-existent category '${metadata.category}'`));
      errorCount++;
    }
  }
}

// Validate document relationships
metadataRegistry.documents.forEach(doc => {
  if (doc.related_docs && Array.isArray(doc.related_docs)) {
    for (const relatedPath of doc.related_docs) {
      if (!registryPaths.has(relatedPath)) {
        console.error(chalk.red(`Error: Document ${doc.path} references non-existent related document '${relatedPath}'`));
        errorCount++;
      }
    }
  }
});

// Summary
if (errorCount > 0) {
  console.error(chalk.red(`\n✗ Validation failed with ${errorCount} errors`));
  process.exit(1);
} else {
  console.log(chalk.green('\n✓ All documentation metadata is valid!'));
  process.exit(0);
}
