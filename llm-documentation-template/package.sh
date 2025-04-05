#!/bin/bash
# LLM-Friendly Documentation Template Packaging Script
#
# This script helps prepare the template for distribution or moving to a new repository.
# It creates a zip file containing the template and guides.

echo "========================================================"
echo "  LLM-Friendly Documentation Template Packaging Script  "
echo "========================================================"
echo 

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
PACKAGE_NAME="llm-doc-template-$TIMESTAMP.zip"
CURRENT_DIR=$(pwd)

echo "This script will create a packaged version of the LLM-Friendly Documentation Template."
echo "Current directory: $CURRENT_DIR"
echo

# Check if we're in the right directory
if [ ! -d "template" ] || [ ! -d "guides" ]; then
  echo "ERROR: This script should be run from the llm-documentation-template directory."
  echo "Please navigate to the llm-documentation-template directory and try again."
  exit 1
fi

echo "Creating package: $PACKAGE_NAME"
echo "This package will contain:"
echo "  - The LLM-friendly documentation template (template/)"
echo "  - Implementation guides (guides/)"
echo "  - The README file"
echo
echo "Creating zip package..."

# Create the zip archive
zip -r "$PACKAGE_NAME" README.md template/ guides/ package.sh

if [ $? -eq 0 ]; then
  echo "Package created successfully: $CURRENT_DIR/$PACKAGE_NAME"
  echo
  echo "To use this template in a different project:"
  echo "1. Unzip the package: unzip $PACKAGE_NAME"
  echo "2. Copy the template directory to your project"
  echo "3. Follow the instructions in guides/README.md to set up the template"
  echo
  echo "If you want to create a dedicated documentation repository:"
  echo "1. Create a new empty repository on GitHub"
  echo "2. Clone that repository locally"
  echo "3. Extract and copy the contents of this package into that repository"
  echo "4. Push the changes to GitHub"
  echo
else
  echo "ERROR: Failed to create package."
  exit 1
fi

echo "Done!"
