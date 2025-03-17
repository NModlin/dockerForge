#!/bin/bash

# DockerForge Phase 5 Test Script
# This script tests the Docker Compose management functionality

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}==== $1 ====${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info messages
print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# Check if DockerForge is installed
check_installation() {
    print_header "Checking DockerForge Installation"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! pip list | grep -q dockerforge; then
        print_info "DockerForge not installed as a package, running from source"
    else
        print_success "DockerForge is installed"
    fi
}

# Create a test Docker Compose file
create_test_compose_file() {
    print_header "Creating Test Docker Compose File"
    
    mkdir -p test_compose
    
    cat > test_compose/docker-compose.yml << EOF
version: '3'

services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
    environment:
      - NGINX_HOST=localhost
      - NGINX_PORT=80
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=testdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

    mkdir -p test_compose/html
    echo "<html><body><h1>DockerForge Test</h1></body></html>" > test_compose/html/index.html
    
    print_success "Created test Docker Compose file at test_compose/docker-compose.yml"
}

# Test Docker Compose discovery
test_compose_discovery() {
    print_header "Testing Docker Compose Discovery"
    
    # Run the discovery command
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'list', '--path', 'test_compose']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose discovery successful"
    else
        print_error "Docker Compose discovery failed"
        exit 1
    fi
}

# Test Docker Compose validation
test_compose_validation() {
    print_header "Testing Docker Compose Validation"
    
    # Run the validation command
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'validate', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose validation successful"
    else
        print_error "Docker Compose validation failed"
        exit 1
    fi
}

# Test Docker Compose visualization
test_compose_visualization() {
    print_header "Testing Docker Compose Visualization"
    
    # Run the visualization command
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'visualize', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose visualization successful"
    else
        print_error "Docker Compose visualization failed"
        exit 1
    fi
}

# Test Docker Compose backup and history
test_compose_backup() {
    print_header "Testing Docker Compose Backup and History"
    
    # Create a backup
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'backup', 'test_compose/docker-compose.yml', '-d', 'Test backup']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose backup successful"
    else
        print_error "Docker Compose backup failed"
        exit 1
    fi
    
    # Show history
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'history', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose history successful"
    else
        print_error "Docker Compose history failed"
        exit 1
    fi
}

# Test Docker Compose template management
test_compose_templates() {
    print_header "Testing Docker Compose Template Management"
    
    # Create a template from the web service
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'create-template', 'test_compose/docker-compose.yml', 'web', 'web-template']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose template creation successful"
    else
        print_error "Docker Compose template creation failed"
        exit 1
    fi
    
    # List templates
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'templates']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose template listing successful"
    else
        print_error "Docker Compose template listing failed"
        exit 1
    fi
    
    # Apply template to create a new Docker Compose file
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'apply-template', 'web-template', 'test_compose/new-compose.yml', '-v', 'NGINX_PORT=8080']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose template application successful"
    else
        print_error "Docker Compose template application failed"
        exit 1
    fi
}

# Test Docker Compose operations (if Docker is available)
test_compose_operations() {
    print_header "Testing Docker Compose Operations"
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        print_info "Docker is not running, skipping operations tests"
        return
    fi
    
    # Run Docker Compose up in detached mode
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'up', 'test_compose/docker-compose.yml', '-d']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose up successful"
    else
        print_error "Docker Compose up failed"
        exit 1
    fi
    
    # List running containers
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'ps', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose ps successful"
    else
        print_error "Docker Compose ps failed"
        exit 1
    fi
    
    # Check health status
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'health', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose health check successful"
    else
        print_error "Docker Compose health check failed"
        exit 1
    fi
    
    # Stop Docker Compose services
    python -c "import sys; sys.path.insert(0, '.'); from src.cli import cli; from click.testing import CliRunner; runner = CliRunner(); result = runner.invoke(cli, ['compose', 'down', 'test_compose/docker-compose.yml']); print(result.output); sys.exit(0 if result.exit_code == 0 else 1)"
    
    if [ $? -eq 0 ]; then
        print_success "Docker Compose down successful"
    else
        print_error "Docker Compose down failed"
        exit 1
    fi
}

# Clean up test files
cleanup() {
    print_header "Cleaning Up"
    
    rm -rf test_compose
    
    print_success "Cleaned up test files"
}

# Run all tests
run_all_tests() {
    check_installation
    create_test_compose_file
    test_compose_discovery
    test_compose_validation
    test_compose_visualization
    test_compose_backup
    test_compose_templates
    test_compose_operations
    cleanup
    
    print_header "All Tests Completed Successfully"
}

# Run the tests
run_all_tests
