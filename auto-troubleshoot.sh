#!/bin/bash
#
# DockerForge Auto-Troubleshooting Demo
# This script demonstrates how to use DockerForge with Ollama for auto-troubleshooting
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

# Function to check if Docker is running
check_docker() {
  if command_exists docker; then
    if docker info >/dev/null 2>&1; then
      success "Docker is running"
      return 0
    else
      error "Docker is installed but not running"
      return 1
    fi
  else
    error "Docker is not installed"
    return 1
  fi
}

# Function to check if Ollama is running
check_ollama() {
  if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    success "Ollama is running"
    return 0
  else
    error "Ollama is not running"
    return 1
  fi
}

# Function to check if Ollama has the required model
check_ollama_model() {
  local model="$1"
  local tags=$(curl -s http://localhost:11434/api/tags)
  
  if echo "$tags" | grep -q "\"name\":\"$model\""; then
    success "Ollama has the $model model"
    return 0
  else
    warning "Ollama does not have the $model model"
    echo -e "${CYAN}Pulling the $model model...${NC}"
    
    # Pull the model
    curl -s http://localhost:11434/api/pull -d "{\"name\":\"$model\"}"
    
    # Check if the model was pulled successfully
    tags=$(curl -s http://localhost:11434/api/tags)
    if echo "$tags" | grep -q "\"name\":\"$model\""; then
      success "Pulled the $model model"
      return 0
    else
      error "Failed to pull the $model model"
      return 1
    fi
  fi
}

# Function to run DockerForge
run_dockerforge() {
  local command="$1"
  shift
  
  echo -e "${CYAN}Running: dockerforge $command $*${NC}"
  "$SCRIPT_DIR/dockerforge.sh" "$command" "$@"
}

# Main function
main() {
  print_banner "DockerForge Auto-Troubleshooting Demo"
  
  print_section "CHECKING PREREQUISITES"
  
  # Check if Docker is running
  if ! check_docker; then
    error "Docker must be running to continue"
    exit 1
  fi
  
  # Check if Ollama is running
  if ! check_ollama; then
    echo -e "${CYAN}Starting Ollama with Docker...${NC}"
    
    # Start Ollama with Docker
    docker run -d --name ollama -p 11434:11434 ollama/ollama
    
    # Wait for Ollama to start
    echo -e "${CYAN}Waiting for Ollama to start...${NC}"
    for i in {1..30}; do
      if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        success "Ollama started successfully"
        break
      fi
      
      if [ $i -eq 30 ]; then
        error "Ollama failed to start"
        exit 1
      fi
      
      echo -n "."
      sleep 1
    done
    echo
  fi
  
  # Check if Ollama has the required model
  check_ollama_model "llama3"
  
  print_section "DEMO SCENARIOS"
  
  echo -e "${CYAN}Available demo scenarios:${NC}"
  echo "1. Analyze a running container"
  echo "2. Analyze Docker logs"
  echo "3. Analyze a Docker Compose file"
  echo "4. Analyze a Dockerfile"
  echo "5. Troubleshoot Docker connection issues"
  echo "6. Exit"
  
  read -p "Select a scenario (1-6): " scenario
  
  case $scenario in
    1)
      print_section "ANALYZING A RUNNING CONTAINER"
      
      # List running containers
      echo -e "${CYAN}Running containers:${NC}"
      docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"
      
      # Prompt for container ID or name
      read -p "Enter container ID or name: " container
      
      # Analyze container
      run_dockerforge troubleshoot container "$container"
      ;;
    
    2)
      print_section "ANALYZING DOCKER LOGS"
      
      # Prompt for log file
      read -p "Enter path to Docker log file: " log_file
      
      # Check if file exists
      if [ ! -f "$log_file" ]; then
        error "Log file does not exist: $log_file"
        exit 1
      fi
      
      # Analyze logs
      run_dockerforge troubleshoot logs "$log_file"
      ;;
    
    3)
      print_section "ANALYZING A DOCKER COMPOSE FILE"
      
      # Prompt for Docker Compose file
      read -p "Enter path to Docker Compose file: " compose_file
      
      # Check if file exists
      if [ ! -f "$compose_file" ]; then
        error "Docker Compose file does not exist: $compose_file"
        exit 1
      fi
      
      # Analyze Docker Compose file
      run_dockerforge troubleshoot compose "$compose_file"
      ;;
    
    4)
      print_section "ANALYZING A DOCKERFILE"
      
      # Prompt for Dockerfile
      read -p "Enter path to Dockerfile: " dockerfile
      
      # Check if file exists
      if [ ! -f "$dockerfile" ]; then
        error "Dockerfile does not exist: $dockerfile"
        exit 1
      fi
      
      # Analyze Dockerfile
      run_dockerforge troubleshoot dockerfile "$dockerfile"
      ;;
    
    5)
      print_section "TROUBLESHOOTING DOCKER CONNECTION ISSUES"
      
      # Troubleshoot Docker connection issues
      run_dockerforge troubleshoot connection
      ;;
    
    6)
      print_section "EXITING"
      exit 0
      ;;
    
    *)
      error "Invalid scenario: $scenario"
      exit 1
      ;;
  esac
}

# Run the main function
main "$@"
