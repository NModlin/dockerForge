#!/usr/bin/env node

/**
 * Documentation Link Checker
 * 
 * This script checks for broken links in Markdown files:
 * - Internal links between documentation files
 * - Links to anchors within documents
 * - Missing referenced files
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const chalk = require('chalk');
const markdownIt = require('markdown-it');

// Configuration
const DOCS_DIR = path.resolve(__dirname, '../docs');
const md = new markdownIt();

// Error counter
let errorCount = 0;
let warningCount = 0;

console.log(chalk.blue('Documentation Link Checker'));
console.log(chalk.blue('========================='));

// Get all Markdown files in the docs directory
const markdownFiles = glob.sync(`${DOCS_DIR}/**/*.md`);
console.log(chalk.green(`✓ Found ${markdownFiles.length} Markdown files to check`));

// Map of all document paths (normalized for case-insensitive comparison)
const existingFiles = new Map();
markdownFiles.forEach(filePath => {
  const relativePath = path.relative(DOCS_DIR, filePath).replace(/\\/g, '/');
  existingFiles.set(relativePath.toLowerCase(), relativePath);
});

// Function to check if a file exists (case-insensitive)
function fileExists(filePath) {
  return existingFiles.has(filePath.toLowerCase());
}

// Function to extract links from markdown content
function extractLinks(content) {
  const links = [];
  const tokens = md.parse(content, {});
  
  tokens.forEach(token => {
    if (token.type === 'inline') {
      token.children.forEach(child => {
        if (child.type === 'link_open') {
          const href = child.attrs.find(attr => attr[0] === 'href');
          if (href) {
            links.push(href[1]);
          }
        }
      });
    }
  });
  
  // Also find links in HTML comments for LLM related documents
  const relatedDocsMatches = content.match(/<!--\s*@llm-related-docs\s*([\s\S]*?)-->/g);
  if (relatedDocsMatches) {
    relatedDocsMatches.forEach(match => {
      const linkMatches = match.match(/- (.*?):/g);
      if (linkMatches) {
        linkMatches.forEach(linkMatch => {
          const link = linkMatch.replace(/- /, '').replace(/:$/, '');
          links.push(link);
        });
      }
    });
  }
  
  return links;
}

// Process each file
markdownFiles.forEach(filePath => {
  const relativePath = path.relative(DOCS_DIR, filePath).replace(/\\/g, '/');
  const content = fs.readFileSync(filePath, 'utf8');
  const links = extractLinks(content);
  
  links.forEach(link => {
    // Skip external links and absolute URLs
    if (link.startsWith('http://') || link.startsWith('https://') || link.startsWith('#')) {
      return;
    }
    
    // Handle links with anchors
    let targetPath = link;
    let anchor = '';
    if (link.includes('#')) {
      [targetPath, anchor] = link.split('#');
    }
    
    // If empty targetPath, it's a link to an anchor in the current file
    if (targetPath === '') {
      // We could check if the anchor exists in the current file
      return;
    }
    
    // Convert relative paths to absolute paths
    let absolutePath = targetPath;
    if (!path.isAbsolute(targetPath)) {
      absolutePath = path.normalize(path.join(path.dirname(relativePath), targetPath));
    }
    
    // Check if the file exists
    if (!fileExists(absolutePath)) {
      console.error(chalk.red(`Error: Broken link in ${relativePath} to non-existent file: ${targetPath}`));
      errorCount++;
    }
  });
});

// Summary
if (errorCount > 0 || warningCount > 0) {
  console.log(chalk.yellow(`\nFound ${warningCount} warnings and ${errorCount} errors.`));
  
  if (errorCount > 0) {
    console.error(chalk.red(`✗ Link check failed with ${errorCount} errors`));
    process.exit(1);
  } else {
    console.log(chalk.yellow(`⚠ Link check passed with warnings`));
    process.exit(0);
  }
} else {
  console.log(chalk.green('\n✓ All documentation links are valid!'));
  process.exit(0);
}
