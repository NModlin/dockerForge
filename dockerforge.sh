#!/bin/bash
#
# DockerForge - A comprehensive Docker management tool with AI-powered troubleshooting
# A unified script for monitoring, troubleshooting, maintaining,
# and setting up Docker environments
# Author: DockerForge Team
# Date: March 16, 2025
#

# Color definitions for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script configuration variables
SCRIPT_VERSION="0.1.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print banners
print_banner() {
  local text="$1"
  local width=$(tput cols)
  [ -z "$width" ] && width=80
  local padding=$(( (width - ${#text} - 4) / 2 ))
  [ "$padding" -lt 0 ] && padding=0

  printf "\n${BLUE}%${width}s${NC}\n" | tr " " "="
  printf "${BLUE}%*s %s %*s${NC}\n" $padding "" "$text" $padding ""
  printf "${BLUE}%${width}s${NC}\n\n" | tr " " "="
}

# Function to print section headers
print_section() {
  local text="$1"
  local width=$(tput cols)
  [ -z "$width" ] && width=80

  printf "\n${CYAN}=== %s ${NC}" "$text"
  local line_length=$((width - ${#text} - 5))
  printf "%${line_length}s\n" | tr " " "="
}

# Function to print warning messages
warning() {
  echo -e "${YELLOW}WARNING: $1${NC}"
}

# Function to print success messages
success() {
  echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Function to print error messages
error() {
  echo -e "${RED}ERROR: $1${NC}"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
  if command_exists python3; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    python_major=$(echo $python_version | cut -d. -f1)
    python_minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$python_major" -ge 3 ] && [ "$python_minor" -ge 8 ]; then
      success "Python $python_version is installed"
      return 0
    else
      error "Python 3.8 or higher is required, found $python_version"
      return 1
    fi
  else
    error "Python 3 is not installed or not in PATH"
    return 1
  fi
}

# Function to check if virtual environment exists
check_venv() {
  if [ -d "$SCRIPT_DIR/venv" ]; then
    return 0
  else
    return 1
  fi
}

# Function to create virtual environment
create_venv() {
  print_section "CREATING VIRTUAL ENVIRONMENT"
  
  if check_venv; then
    warning "Virtual environment already exists"
    return 0
  fi
  
  if ! check_python_version; then
    error "Cannot create virtual environment"
    return 1
  fi
  
  echo "Creating virtual environment..."
  python3 -m venv "$SCRIPT_DIR/venv"
  
  if [ $? -eq 0 ]; then
    success "Virtual environment created"
    return 0
  else
    error "Failed to create virtual environment"
    return 1
  fi
}

# Function to install dependencies
install_dependencies() {
  print_section "INSTALLING DEPENDENCIES"
  
  if ! check_venv; then
    if ! create_venv; then
      error "Cannot install dependencies"
      return 1
    fi
  fi
  
  echo "Installing dependencies..."
  source "$SCRIPT_DIR/venv/bin/activate"
  pip install --upgrade pip
  pip install -e "$SCRIPT_DIR"
  
  if [ $? -eq 0 ]; then
    success "Dependencies installed"
    return 0
  else
    error "Failed to install dependencies"
    return 1
  fi
}

# Function to run the application
run_app() {
  if ! check_venv; then
    if ! create_venv; then
      error "Cannot run application"
      return 1
    fi
    
    if ! install_dependencies; then
      error "Cannot run application"
      return 1
    fi
  fi
  
  source "$SCRIPT_DIR/venv/bin/activate"
  python -m src.cli "$@"
}

# Function to display help
show_help() {
  print_banner "DockerForge v${SCRIPT_VERSION}"
  
  echo -e "${CYAN}USAGE:${NC}"
  echo "  $0 [command] [options]"
  
  echo -e "\n${CYAN}COMMANDS:${NC}"
  echo "  check                Check Docker installation and connectivity"
  echo "  info                 Show Docker and system information"
  echo "  list                 List Docker containers"
  echo "  logs <container>     View logs for a container"
  echo "  start <container>    Start a container"
  echo "  stop <container>     Stop a container"
  echo "  restart <container>  Restart a container"
  echo "  inspect <container>  Inspect a container"
  echo "  exec <container>     Execute a command in a container"
  echo "  networks             List Docker networks"
  echo "  volumes              List Docker volumes"
  echo "  images               List Docker images"
  echo "  monitor              Monitor Docker containers and analyze logs"
  echo "  resource             Monitor and optimize Docker container resources"
  echo "  compose              Manage Docker Compose files"
  echo "  security             Manage Docker security scanning, auditing, and reporting"
  echo "  backup               Manage Docker container, image, and volume backups"
  echo "  troubleshoot         Troubleshoot Docker issues using AI"
  echo "  config               Manage DockerForge configuration"
  echo "  help                 Show this help message"
  
  echo -e "\n${CYAN}OPTIONS:${NC}"
  echo "  --verbose, -v        Enable verbose output"
  echo "  --config, -c         Path to configuration file"
  echo "  --env-file, -e       Path to .env file"
  
  echo -e "\n${CYAN}EXAMPLES:${NC}"
  echo "  $0 check                     # Check Docker installation"
  echo "  $0 list -a                   # List all containers"
  echo "  $0 logs nginx -f             # Follow logs for nginx container"
  echo "  $0 exec nginx bash           # Run bash in nginx container"
  echo "  $0 config get docker.host    # Get configuration value"
  echo "  $0 security scan --image nginx:latest  # Scan image for vulnerabilities"
  echo "  $0 backup container my-container       # Backup a container"
  echo "  $0 resource start            # Start resource monitoring daemon"
}

# Main function
main() {
  # Check if help is requested
  if [ "$1" = "help" ] || [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
    return 0
  fi
  
  # Run the application
  run_app "$@"
}

# Run the main function with all arguments
main "$@"
