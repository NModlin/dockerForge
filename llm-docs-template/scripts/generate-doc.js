#!/usr/bin/env node

/**
 * Documentation Generator Script
 * 
 * This script generates new documentation files from templates:
 * - Creates new files with appropriate metadata
 * - Updates the metadata registry
 * - Provides a consistent structure for new documents
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Configuration
const DOCS_DIR = path.resolve(__dirname, '../docs');
const TEMPLATES_DIR = path.resolve(__dirname, '../_templates');
const METADATA_FILE = path.resolve(DOCS_DIR, 'docs-metadata.json');

// Define supported document types and their templates
const DOC_TYPES = {
  'standard': 'standard-doc-template.md',
  'api': 'api-reference-template.md',
  'user-guide': 'user-guide-template.md',
  'project-plan': 'project-plan-template.md'
};

// Parse command line arguments
const argv = yargs(hideBin(process.argv))
  .usage('Usage: $0 -t [type] -n [name] -p [path] -c [category]')
  .option('type', {
    alias: 't',
    describe: 'Document type',
    choices: Object.keys(DOC_TYPES),
    demandOption: true,
    type: 'string'
  })
  .option('name', {
    alias: 'n',
    describe: 'Document name (will be used for ID and title)',
    demandOption: true,
    type: 'string'
  })
  .option('path', {
    alias: 'p',
    describe: 'Path where to create the document (relative to docs directory)',
    demandOption: true,
    type: 'string'
  })
  .option('category', {
    alias: 'c',
    describe: 'Document category',
    choices: ['api', 'user-guide', 'developer-guide', 'project-plan', 'general', 'null'],
    default: 'null',
    type: 'string'
  })
  .help()
  .argv;

console.log(chalk.blue('Documentation Generator'));
console.log(chalk.blue('======================='));

// Generate an ID from name (kebab-case)
function generateId(name) {
  return name.toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

// Get today's date in YYYY-MM-DD format
function getTodayDate() {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

// Create directory if it doesn't exist
function ensureDirectoryExists(directoryPath) {
  if (!fs.existsSync(directoryPath)) {
    fs.mkdirSync(directoryPath, { recursive: true });
    console.log(chalk.green(`✓ Created directory: ${directoryPath}`));
  }
}

// Main function
async function generateDocument() {
  // Get template file
  const templateFile = DOC_TYPES[argv.type];
  const templatePath = path.resolve(TEMPLATES_DIR, templateFile);
  
  // Check if template exists
  if (!fs.existsSync(templatePath)) {
    console.error(chalk.red(`Error: Template file not found: ${templateFile}`));
    console.log(chalk.yellow('Note: If you haven\'t created template files yet, please create them in the _templates directory first.'));
    process.exit(1);
  }
  
  // Generate document metadata
  const docId = generateId(argv.name);
  const docTitle = argv.name;
  const docCategory = argv.category === 'null' ? null : argv.category;
  const today = getTodayDate();
  
  // Determine output path
  const docPath = path.resolve(DOCS_DIR, argv.path);
  const outputFilePath = path.extname(docPath) ? docPath : path.join(docPath, `${docId}.md`);
  const outputDir = path.dirname(outputFilePath);
  
  // Create directory if it doesn't exist
  ensureDirectoryExists(outputDir);
  
  // Check if file already exists
  if (fs.existsSync(outputFilePath)) {
    console.error(chalk.red(`Error: File already exists at ${outputFilePath}`));
    process.exit(1);
  }
  
  // Read template content
  let templateContent = fs.readFileSync(templatePath, 'utf8');
  
  // Replace template variables
  templateContent = templateContent
    .replace(/\[DOCUMENT_ID\]/g, docId)
    .replace(/\[DOCUMENT_TITLE\]/g, docTitle)
    .replace(/\[DOCUMENT_CATEGORY\]/g, docCategory === null ? 'null' : `"${docCategory}"`)
    .replace(/\[CURRENT_DATE\]/g, today)
    .replace(/\[DOCUMENT_PATH\]/g, path.relative(DOCS_DIR, outputFilePath).replace(/\\/g, '/'));
  
  // Write to file
  fs.writeFileSync(outputFilePath, templateContent);
  console.log(chalk.green(`✓ Created document: ${outputFilePath}`));
  
  // Update metadata registry if it exists
  if (fs.existsSync(METADATA_FILE)) {
    try {
      const metadataRegistry = JSON.parse(fs.readFileSync(METADATA_FILE, 'utf8'));
      
      // Add new document to registry
      metadataRegistry.documents.push({
        path: path.relative(DOCS_DIR, outputFilePath).replace(/\\/g, '/'),
        title: docTitle,
        category: docCategory,
        status: 'current',
        last_updated: today,
        update_frequency: 'as-needed',
        related_docs: []
      });
      
      // Update document count
      metadataRegistry.document_count = metadataRegistry.documents.length;
      metadataRegistry.last_updated = today;
      
      // Write updated registry
      fs.writeFileSync(METADATA_FILE, JSON.stringify(metadataRegistry, null, 2));
      console.log(chalk.green(`✓ Updated metadata registry: ${METADATA_FILE}`));
      
    } catch (error) {
      console.error(chalk.red(`Error updating metadata registry: ${error.message}`));
      console.log(chalk.yellow('Please update the metadata registry manually.'));
    }
  } else {
    console.log(chalk.yellow('Warning: Metadata registry file not found. Please update it manually.'));
  }
  
  console.log(chalk.green('\n✓ Document generation complete!'));
  console.log(chalk.blue('\nNext steps:'));
  console.log('1. Review and customize the generated document');
  console.log('2. Update related document links if necessary');
  console.log('3. If applicable, add the document to appropriate index files');
}

// Execute the main function
generateDocument().catch(error => {
  console.error(chalk.red(`Error: ${error.message}`));
  process.exit(1);
});
