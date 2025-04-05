#!/usr/bin/env node

/**
 * LLM Instruction Validation Script
 * 
 * This script validates the LLM instruction comments in documentation files:
 * - Checks that each file has appropriate @llm-instructions
 * - Validates the format of various instruction types
 * - Ensures section-specific markers are used correctly
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const chalk = require('chalk');

// Configuration
const DOCS_DIR = path.resolve(__dirname, '../docs');
const REQUIRED_CATEGORIES = ['api', 'user-guide', 'developer-guide', 'project-plan', 'general'];

// Instruction types to check for
const INSTRUCTION_TYPES = [
  '@llm-instructions',
  '@llm-update-section',
  '@llm-reference-section',
  '@llm-procedural-section',
  '@llm-related-docs',
  '@llm-conditional-instructions',
  '@llm-reasoning-guide',
  '@llm-template'
];

// Error counter
let errorCount = 0;
let warningCount = 0;

console.log(chalk.blue('LLM Instruction Validation'));
console.log(chalk.blue('=========================='));

// Get all Markdown files in the docs directory
const markdownFiles = glob.sync(`${DOCS_DIR}/**/*.md`);
console.log(chalk.green(`✓ Found ${markdownFiles.length} Markdown files to validate`));

// Get file category based on path
function getFileCategory(filePath) {
  const relativePath = path.relative(DOCS_DIR, filePath);
  
  for (const category of REQUIRED_CATEGORIES) {
    if (relativePath.startsWith(category + '/') || relativePath.includes('/' + category + '/')) {
      return category;
    }
  }
  
  return null;
}

// Check if a file has the required instruction type
function hasInstructionType(content, type) {
  const regex = new RegExp(`<!--\\s*${type}\\s+[\\s\\S]*?-->`, 'i');
  return regex.test(content);
}

// Validate document-level instructions
function validateDocumentInstructions(content, filePath) {
  const relativePath = path.relative(DOCS_DIR, filePath);
  
  // Check for @llm-instructions
  if (!hasInstructionType(content, '@llm-instructions')) {
    console.warn(chalk.yellow(`Warning: Missing @llm-instructions in ${relativePath}`));
    warningCount++;
  }
  
  // Extract @llm-instructions content
  const instructionsMatch = content.match(/<!--\s*@llm-instructions\s+([\s\S]*?)-->/);
  if (instructionsMatch) {
    const instructions = instructionsMatch[1].trim();
    
    // Check for document purpose
    if (!instructions.includes('DOCUMENT PURPOSE:')) {
      console.warn(chalk.yellow(`Warning: @llm-instructions missing DOCUMENT PURPOSE in ${relativePath}`));
      warningCount++;
    }
    
    // Check for primary audience
    if (!instructions.includes('PRIMARY AUDIENCE:')) {
      console.warn(chalk.yellow(`Warning: @llm-instructions missing PRIMARY AUDIENCE in ${relativePath}`));
      warningCount++;
    }
    
    // Check for maintenance guidelines
    if (!instructions.includes('MAINTENANCE GUIDELINES:')) {
      console.warn(chalk.yellow(`Warning: @llm-instructions missing MAINTENANCE GUIDELINES in ${relativePath}`));
      warningCount++;
    }
  }
}

// Validate section-specific markers
function validateSectionMarkers(content, filePath) {
  const relativePath = path.relative(DOCS_DIR, filePath);
  
  // Check for proper format of @llm-update-section
  const updateSectionMatches = content.match(/<!--\s*@llm-update-section\s+([\s\S]*?)-->/g);
  if (updateSectionMatches) {
    updateSectionMatches.forEach(match => {
      if (!match.includes('-') && !match.includes('*')) {
        console.warn(chalk.yellow(`Warning: @llm-update-section should contain bullet points in ${relativePath}`));
        warningCount++;
      }
    });
  }
  
  // Check for proper format of @llm-related-docs
  const relatedDocsMatch = content.match(/<!--\s*@llm-related-docs\s+([\s\S]*?)-->/);
  if (relatedDocsMatch) {
    const relatedDocs = relatedDocsMatch[1].trim();
    
    if (!relatedDocs.includes('-') || !relatedDocs.includes(':')) {
      console.warn(chalk.yellow(`Warning: @llm-related-docs should list documents with explanations in ${relativePath}`));
      warningCount++;
    }
  }
}

// Validate category-specific requirements
function validateCategoryRequirements(content, category, filePath) {
  const relativePath = path.relative(DOCS_DIR, filePath);
  
  if (category === 'api') {
    // API documentation should have endpoints properly documented
    if (!content.includes('**Method:') || !content.includes('**Path:')) {
      console.warn(chalk.yellow(`Warning: API documentation missing Method/Path in ${relativePath}`));
      warningCount++;
    }
    
    // API documentation should have @llm-reference-section
    if (!hasInstructionType(content, '@llm-reference-section')) {
      console.warn(chalk.yellow(`Warning: API documentation missing @llm-reference-section in ${relativePath}`));
      warningCount++;
    }
  }
  
  if (category === 'project-plan') {
    // Project plans should have status information
    if (!content.includes('**Status:')) {
      console.warn(chalk.yellow(`Warning: Project plan missing Status field in ${relativePath}`));
      warningCount++;
    }
    
    // Project plans should have @llm-reasoning-guide
    if (!hasInstructionType(content, '@llm-reasoning-guide')) {
      console.warn(chalk.yellow(`Warning: Project plan missing @llm-reasoning-guide in ${relativePath}`));
      warningCount++;
    }
  }
}

// Process each file
markdownFiles.forEach(filePath => {
  const content = fs.readFileSync(filePath, 'utf8');
  const relativePath = path.relative(DOCS_DIR, filePath);
  const category = getFileCategory(filePath);
  
  // Skip the main LLM guide itself
  if (relativePath === 'llm-guide.md') {
    return;
  }
  
  // Check metadata
  const metadataMatch = content.match(/<!--\s*@doc-meta\s*({[\s\S]*?})\s*-->/);
  if (!metadataMatch) {
    console.error(chalk.red(`Error: Missing @doc-meta section in ${relativePath}`));
    errorCount++;
  }
  
  // Validate document-level instructions
  validateDocumentInstructions(content, filePath);
  
  // Validate section markers
  validateSectionMarkers(content, filePath);
  
  // Validate category-specific requirements
  if (category) {
    validateCategoryRequirements(content, category, filePath);
  }
  
  // Count instruction types
  let instructionCount = 0;
  INSTRUCTION_TYPES.forEach(type => {
    if (hasInstructionType(content, type)) {
      instructionCount++;
    }
  });
  
  // Every file should have at least some instructions
  if (instructionCount === 0) {
    console.error(chalk.red(`Error: No LLM instructions found in ${relativePath}`));
    errorCount++;
  }
});

// Summary
if (errorCount > 0 || warningCount > 0) {
  console.log(chalk.yellow(`\nFound ${warningCount} warnings and ${errorCount} errors.`));
  
  if (errorCount > 0) {
    console.error(chalk.red(`✗ LLM instruction validation failed with ${errorCount} errors`));
    process.exit(1);
  } else {
    console.log(chalk.yellow(`⚠ LLM instruction validation passed with warnings`));
    process.exit(0);
  }
} else {
  console.log(chalk.green('\n✓ All LLM instructions are valid!'));
  process.exit(0);
}
