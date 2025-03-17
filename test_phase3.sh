#!/bin/bash
# Test script for DockerForge Phase 3 functionality

# Set up environment
echo "Setting up environment..."
export PYTHONPATH=$(pwd)

# Install required dependencies if needed
if ! pip show docker > /dev/null 2>&1; then
    echo "Installing docker package..."
    pip install docker
fi

# Make sure the monitoring directory is initialized
mkdir -p ~/.dockerforge/patterns
mkdir -p ~/.dockerforge/templates
mkdir -p ~/.dockerforge/issues
mkdir -p ~/.dockerforge/recommendations
mkdir -p ~/.dockerforge/recommendation_templates

# Copy example patterns and templates if they don't exist
if [ ! -f ~/.dockerforge/patterns/docker_error_patterns.json ]; then
    echo "Copying example patterns..."
    cp -f examples/patterns/docker_error_patterns.json ~/.dockerforge/patterns/
fi

if [ ! -f ~/.dockerforge/templates/log_analysis.json ]; then
    echo "Copying example templates..."
    cp -f examples/templates/log_analysis.json ~/.dockerforge/templates/
fi

if [ ! -f ~/.dockerforge/recommendation_templates/recommendation_template.json ]; then
    echo "Copying example recommendation templates..."
    cp -f examples/templates/recommendation_template.json ~/.dockerforge/recommendation_templates/
fi

# Run the test script
echo "Running Phase 3 test script..."
python examples/test_phase3.py

# Print instructions for using the CLI
echo ""
echo "To test the CLI commands, try the following:"
echo "  python -m src.cli monitor logs dockerforge-test"
echo "  python -m src.cli monitor stats dockerforge-test"
echo "  python -m src.cli monitor analyze dockerforge-test"
echo "  python -m src.cli monitor issues"
echo "  python -m src.cli monitor recommendations"
echo ""
echo "To clean up the test container:"
echo "  docker rm -f dockerforge-test"
