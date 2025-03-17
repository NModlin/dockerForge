#!/bin/bash
#
# Unified Docker Management Utility
# A comprehensive script for monitoring, troubleshooting, maintaining,
# and setting up Docker environments
# Author: Claude
# Date: March 15, 2025
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
LOG_DIR="./logs"
CONFIG_DIR="./config"
SCRIPT_VERSION="2.0.0"

# Default environment variables
DOMAIN="example.com"
DATA_DIR="$HOME/docker"
BACKUP_DIR="$HOME/docker-backup-$(date +%Y%m%d)"

# Function to create a timestamp
get_timestamp() {
  date +"%Y%m%d_%H%M%S"
}

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

# Function to ask yes/no questions
ask_yes_no() {
  local prompt="$1"
  local response

  while true; do
    read -p "$prompt (y/n): " response
    case "${response,,}" in
      y|yes) return 0 ;;
      n|no) return 1 ;;
      *) echo "Please answer y or n" ;;
    esac
  done
}

# Check for Docker and Docker Compose
check_docker_installed() {
  print_section "CHECKING DOCKER INSTALLATION"

  if ! command_exists docker; then
    error "Docker is not installed or not in PATH"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    return 1
  else
    success "Docker is installed"
    docker --version
  fi

  if command_exists docker-compose; then
    success "Docker Compose is installed"
    docker-compose --version
  elif command_exists "docker" && docker compose version &>/dev/null; then
    success "Docker Compose plugin is installed"
    docker compose version
  else
    warning "Docker Compose not found"
    echo "Some functions may be limited. Consider installing Docker Compose:"
    echo "https://docs.docker.com/compose/install/"
  fi

  # Check if docker daemon is running
  if ! docker info &>/dev/null; then
    error "Docker daemon is not running"
    echo "Start the Docker service with:"
    echo "  sudo systemctl start docker"
    return 1
  else
    success "Docker daemon is running"
  fi

  return 0
}

# Function to fix common Docker networking issues
fix_docker_networking() {
  print_section "DOCKER NETWORK FIXES"

  echo -e "${YELLOW}WARNING: This will attempt to fix Docker networking issues${NC}"
  echo "It may temporarily disrupt container connectivity"

  if ! ask_yes_no "Do you want to proceed?"; then
    echo "Network fix canceled"
    return 0
  fi

  # Check if running as root
  if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Some network fixes require root privileges${NC}"
    if ! ask_yes_no "Continue with available fixes?"; then
      echo "Operation canceled"
      return 1
    fi
  fi

  echo "Checking Docker service status..."
  if command_exists systemctl; then
    if ! systemctl is-active --quiet docker; then
      echo -e "${RED}Docker service is not running${NC}"
      echo "Starting Docker service..."
      if [ "$EUID" -eq 0 ]; then
        systemctl start docker
      else
        sudo systemctl start docker
      fi
    else
      echo -e "${GREEN}Docker service is running${NC}"
    fi
  else
    # For systems without systemd
    if ! docker info &>/dev/null; then
      error "Docker is not running"
      echo "Please start Docker using your system's service manager"
    else
      success "Docker is running"
    fi
  fi

  echo "Creating required networks if they don't exist..."

  # Create common networks that might be needed
  for network in proxy shared bridge; do
    if ! docker network ls --format '{{.Name}}' | grep -q "^$network$"; then
      echo "Creating network '$network'..."
      docker network create "$network" || echo -e "${RED}Failed to create network '$network'${NC}"
    else
      echo -e "${GREEN}Network '$network' already exists${NC}"
    fi
  done

  echo "Checking IP forwarding..."
  local ip_forward=$(sysctl -n net.ipv4.ip_forward 2>/dev/null || echo "unknown")
  if [ "$ip_forward" = "0" ]; then
    echo -e "${YELLOW}IP forwarding is disabled. Enabling...${NC}"
    if [ "$EUID" -eq 0 ]; then
      sysctl -w net.ipv4.ip_forward=1
      echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    else
      sudo sysctl -w net.ipv4.ip_forward=1
      echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
    fi
  else
    echo -e "${GREEN}IP forwarding is enabled${NC}"
  fi

  echo "Restarting Docker service..."
  if command_exists systemctl; then
    if [ "$EUID" -eq 0 ]; then
      systemctl restart docker
    else
      sudo systemctl restart docker
    fi
  else
    # For systems without systemd
    if [ "$EUID" -eq 0 ]; then
      service docker restart 2>/dev/null ||
      /etc/init.d/docker restart 2>/dev/null ||
      error "Couldn't restart Docker. Please restart manually based on your system."
    else
      sudo service docker restart 2>/dev/null ||
      sudo /etc/init.d/docker restart 2>/dev/null ||
      error "Couldn't restart Docker. Please restart manually based on your system."
    fi
  fi

  echo -e "${GREEN}Network fixes applied${NC}"

  # Ask if user wants to restart containers
  if ask_yes_no "Do you want to restart all containers?"; then
    restart_containers
  fi
}

print_banner "DockerForge"

# Function to clean up Docker resources
clean_docker_resources() {
  print_section "DOCKER CLEANUP"

  echo -e "${YELLOW}WARNING: This will remove unused Docker resources${NC}"
  if ! ask_yes_no "Do you want to proceed?"; then
    echo "Cleanup canceled"
    return 0
  fi

  # Create backup of container configurations
  local backup_dir="${BACKUP_DIR}/container_backup_$(get_timestamp)"
  if ask_yes_no "Would you like to back up container configurations before cleanup?"; then
    mkdir -p "$backup_dir"

    echo "Creating a backup of container configurations..."
    docker ps -a --format "{{.Image}} # {{.Names}} # {{.Command}} # {{.Ports}}" > "$backup_dir/containers.txt"
    echo "Container info backed up to $backup_dir/containers.txt"

    echo "Creating a backup of volumes..."
    docker volume ls > "$backup_dir/volumes.txt"
    echo "Volume info backed up to $backup_dir/volumes.txt"

    echo "Creating a backup of networks..."
    docker network ls > "$backup_dir/networks.txt"
    echo "Network info backed up to $backup_dir/networks.txt"

    success "Configurations backed up to $backup_dir"
  fi

  # Step 1: Remove dangling images
  echo "Step 1: Removing dangling images..."
  docker image prune -f
  echo

  # Step 2: Identify unused volumes
  echo "Step 2: Identifying unused volumes..."
  # List all volumes that aren't attached to containers
  docker volume ls -qf dangling=true

  echo
  echo "To remove these volumes, run:"
  echo "docker volume prune -f"
  echo "WARNING: This will permanently delete data in these volumes!"
  echo

  # Step 3: Remove unused networks
  echo "Step 3: Removing unused networks..."
  docker network prune -f
  echo

  # Step 4: Clean build cache
  echo "Step 4: Cleaning build cache..."
  docker builder prune -f
  echo

  # Step 5: List large images for review
  echo "Step 5: Largest images (consider removing if unused):"
  docker image ls --format "{{.Size}}\t{{.Repository}}:{{.Tag}}" | sort -hr | head -10
  echo

  # Step 6: Remove unused containers
  echo "Step 6: Removing unused containers..."
  docker container prune -f
  echo

  # Step 7: Ask about volume removal
  if ask_yes_no "Do you want to remove unused volumes? (this will DELETE DATA)"; then
    echo "Removing unused volumes..."
    docker volume prune -f
  fi

  echo -e "${GREEN}Docker cleanup completed${NC}"

  # Show docker disk usage after cleanup
  echo "Current Docker disk usage:"
  docker system df

  echo
  echo "For more aggressive cleanup, consider running:"
  echo "docker system prune -a --volumes"
  echo "WARNING: This will remove ALL unused containers, networks, images, and volumes!"
}

# Function to show container details
show_container_details() {
  local container=$1

  if [ -z "$container" ]; then
    print_section "AVAILABLE CONTAINERS"
    local containers=$(get_all_containers)

    if [ -z "$containers" ]; then
      echo -e "${YELLOW}No containers found${NC}"
      return 1
    fi

    echo "Choose a container to inspect:"
    local i=1
    local container_array=()

    while read -r container_name; do
      echo "  $i) $container_name"
      container_array[$i]="$container_name"
      i=$((i+1))
    done <<< "$containers"

    echo "  q) Quit"

    local selection
    read -p "Enter selection (1-$((i-1))): " selection

    if [[ "$selection" == "q" ]]; then
      return 0
    elif [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
      container="${container_array[$selection]}"
    else
      echo -e "${RED}Invalid selection${NC}"
      return 1
    fi
  fi

  print_section "CONTAINER DETAILS: $container"

  # Check if container exists
  if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "${RED}Container '$container' does not exist${NC}"
    return 1
  fi

  echo "Basic Information:"
  docker ps -a --filter "name=$container" --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

  echo -e "\nContainer Configuration:"
  docker inspect --format='ID: {{.Id}}
Name: {{.Name}}
Created: {{.Created}}
Image: {{.Config.Image}}
Command: {{.Config.Cmd}}
Entrypoint: {{.Config.Entrypoint}}
Working Dir: {{.Config.WorkingDir}}
User: {{.Config.User}}
Hostname: {{.Config.Hostname}}
Env: {{range .Config.Env}}
  - {{.}}{{end}}' "$container"

  echo -e "\nNetwork Settings:"
  docker inspect --format='{{range $net, $conf := .NetworkSettings.Networks}}
Network: {{$net}}
  IP Address: {{$conf.IPAddress}}
  Gateway: {{$conf.Gateway}}
  MAC Address: {{$conf.MacAddress}}
{{end}}' "$container"

  echo -e "\nVolumes:"
  docker inspect --format='{{range $mount := .Mounts}}
Source: {{$mount.Source}}
Destination: {{$mount.Destination}}
Mode: {{$mount.Mode}}
RW: {{$mount.RW}}
Type: {{$mount.Type}}
{{end}}' "$container"

  echo -e "\nState:"
  docker inspect --format='Status: {{.State.Status}}
Running: {{.State.Running}}
Paused: {{.State.Paused}}
Restarting: {{.State.Restarting}}
OOMKilled: {{.State.OOMKilled}}
Dead: {{.State.Dead}}
Pid: {{.State.Pid}}
ExitCode: {{.State.ExitCode}}
Error: {{.State.Error}}
StartedAt: {{.State.StartedAt}}
FinishedAt: {{.State.FinishedAt}}' "$container"

  echo -e "\nHealth Check:"
  docker inspect --format='{{if .Config.Healthcheck}}
Test: {{.Config.Healthcheck.Test}}
Interval: {{.Config.Healthcheck.Interval}}
Timeout: {{.Config.Healthcheck.Timeout}}
Retries: {{.Config.Healthcheck.Retries}}
Status: {{.State.Health.Status}}
{{else}}No health check configured{{end}}' "$container"
}

# Function to run a command inside a container
exec_in_container() {
  local container=$1
  local command=$2

  if [ -z "$container" ]; then
    print_section "AVAILABLE CONTAINERS"
    local containers=$(get_running_containers)

    if [ -z "$containers" ]; then
      echo -e "${YELLOW}No running containers found${NC}"
      return 1
    fi

    echo "Choose a container to execute command in:"
    local i=1
    local container_array=()

    while read -r container_name; do
      echo "  $i) $container_name"
      container_array[$i]="$container_name"
      i=$((i+1))
    done <<< "$containers"

    echo "  q) Quit"

    local selection
    read -p "Enter selection (1-$((i-1))): " selection

    if [[ "$selection" == "q" ]]; then
      return 0
    elif [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
      container="${container_array[$selection]}"
    else
      echo -e "${RED}Invalid selection${NC}"
      return 1
    fi
  fi

  # Check if container exists and is running
  if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "${RED}Container '$container' is not running${NC}"
    return 1
  fi

  if [ -z "$command" ]; then
    echo -e "${YELLOW}No command specified. Starting shell if available...${NC}"
    # Try to use bash, if not available try sh
    if docker exec -it "$container" bash -c "echo Bash available" &>/dev/null; then
      docker exec -it "$container" bash
    elif docker exec -it "$container" sh -c "echo Shell available" &>/dev/null; then
      docker exec -it "$container" sh
    else
      echo -e "${RED}No shell available in the container${NC}"

      # List available binaries as a fallback
      echo "Available binaries in the container (partial list):"
      docker exec "$container" ls -la /bin /usr/bin | grep -v "^d" | awk '{print $9}' | grep -v "^$" | sort | head -20

      # Prompt for a command
      read -p "Enter a command to execute: " command
      docker exec -it "$container" $command
    fi
  else
    print_section "EXECUTING IN CONTAINER: $container"
    echo "Command: $command"
    echo "Output:"
    docker exec -it "$container" $command
  fi
}

# Function to ensure log directory exists
ensure_log_directory() {
  if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo -e "${GREEN}Created log directory: $LOG_DIR${NC}"
  fi
}

# Function to ensure config directory exists
ensure_config_directory() {
  if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}Created configuration directory: $CONFIG_DIR${NC}"
  fi
}

# Function to display loading animation
show_spinner() {
  local pid=$1
  local delay=0.1
  local spinstr='|/-\'

  while kill -0 $pid 2>/dev/null; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    local spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\b\b\b\b\b\b"
  done
  printf "    \b\b\b\b"
}

# Check docker compose version and use appropriate command
get_compose_command() {
  if command_exists docker-compose; then
    echo "docker-compose"
  else
    echo "docker compose"
  fi
}

# Get all container names
get_all_containers() {
  docker ps -a --format '{{.Names}}' | sort
}

# Get running container names
get_running_containers() {
  docker ps --format '{{.Names}}' | sort
}

# Get all networks
get_all_networks() {
  docker network ls --format '{{.Name}}' | sort
}

# Function to check container health
check_container_health() {
  local container=$1

  echo -e "Checking ${YELLOW}$container${NC}..."

  # Check if container exists
  if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "  ${RED}✗ CONTAINER NOT FOUND${NC}"
    return 1
  fi

  # Check if container is running
  if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "  ${RED}✗ NOT RUNNING${NC}"

    # Get container status and exit code
    local status=$(docker ps -a --filter "name=$container" --format '{{.Status}}')
    local exit_code=$(docker inspect --format='{{.State.ExitCode}}' "$container" 2>/dev/null || echo "unknown")

    echo -e "  Status: $status, Exit Code: $exit_code"

    # Get recent logs
    echo -e "  Recent logs:"
    docker logs --tail 5 "$container" 2>&1 | sed 's/^/    /'

    return 1
  fi

  # Container is running, check health if available
  local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}N/A{{end}}' "$container" 2>/dev/null)
  local status=$(docker ps --filter "name=$container" --format '{{.Status}}')

  case "$health" in
    "healthy")
      echo -e "  ${GREEN}✓ RUNNING (HEALTHY)${NC}"
      echo -e "  Uptime: $status"
      ;;
    "unhealthy")
      echo -e "  ${RED}✗ RUNNING (UNHEALTHY)${NC}"
      echo -e "  Recent logs:"
      docker logs --tail 5 "$container" 2>&1 | sed 's/^/    /'
      ;;
    "starting")
      echo -e "  ${YELLOW}⚠ RUNNING (STARTING)${NC}"
      echo -e "  Container is still initializing"
      ;;
    *)
      echo -e "  ${GREEN}✓ RUNNING${NC}"
      echo -e "  Uptime: $status"
      ;;
  esac

  # Get container resource usage
  local cpu=$(docker stats "$container" --no-stream --format "{{.CPUPerc}}")
  local mem=$(docker stats "$container" --no-stream --format "{{.MemUsage}}")
  local net=$(docker stats "$container" --no-stream --format "{{.NetIO}}")

  echo -e "  Resource usage:"
  echo -e "    CPU: $cpu"
  echo -e "    Memory: $mem"
  echo -e "    Network I/O: $net"

  return 0
}

# Function to check health of all containers
check_all_containers_health() {
  local timestamp=$(get_timestamp)
  local export_to_file=$1
  local log_file=""

  print_section "CONTAINER HEALTH CHECK"

  if [ "$export_to_file" = true ]; then
    ensure_log_directory
    log_file="${LOG_DIR}/container_health_${timestamp}.log"
    echo -e "${YELLOW}Results will be saved to: $log_file${NC}"
    exec > >(tee -a "$log_file") 2>&1
  fi

  echo "Checking Docker service status..."
  if command_exists systemctl && systemctl --version &>/dev/null; then
    if ! systemctl is-active --quiet docker; then
      echo -e "${RED}✗ Docker service is not running${NC}"
      echo "Try: sudo systemctl start docker"
      return 1
    else
      echo -e "${GREEN}✓ Docker service is running${NC}"
    fi
  else
    # For systems without systemd
    if ! docker info &>/dev/null; then
      error "Docker is not running"
      echo "Please start Docker using your system's service manager"
      return 1
    else
      success "Docker is running"
    fi
  fi

  echo "Checking Docker networks..."
  local networks=$(get_all_networks)
  if [ -z "$networks" ]; then
    echo -e "${YELLOW}⚠ No Docker networks found${NC}"
  else
    echo -e "${GREEN}Found $(echo "$networks" | wc -l) networks:${NC}"
    echo "$networks" | sed 's/^/  - /'
  fi

  # Get list of containers
  local all_containers=$(get_all_containers)
  local running_containers=$(get_running_containers)

  echo -e "\nFound $(echo "$all_containers" | wc -l) containers, $(echo "$running_containers" | wc -l) running"

  # Check each container
  local total=0
  local running=0
  local issues=0
  local not_running=0

  for container in $all_containers; do
    total=$((total+1))

    echo -e "\n-------------------------------------------"
    if check_container_health "$container"; then
      if docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}unknown{{end}}' "$container" | grep -q "unhealthy"; then
        issues=$((issues+1))
      else
        running=$((running+1))
      fi
    elif docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      issues=$((issues+1))
    else
      not_running=$((not_running+1))
    fi
  done

  print_section "HEALTH CHECK SUMMARY"
  echo -e "Total containers: $total"
  echo -e "Running normally: ${GREEN}$running${NC}"
  echo -e "Running with issues: ${YELLOW}$issues${NC}"
  echo -e "Not running: ${RED}$not_running${NC}"

  # Network connectivity test
  if [ "$total" -gt 1 ] && [ "$running" -gt 0 ]; then
    print_section "TESTING INTER-CONTAINER CONNECTIVITY"

    # Select a reference container (preferrably a web server or proxy)
    local ref_container
    for preferred in caddy nginx traefik proxy haproxy; do
      if docker ps --format '{{.Names}}' | grep -q "^$preferred$"; then
        ref_container=$preferred
        break
      fi
    done

    # If no preferred container found, use the first running container
    if [ -z "$ref_container" ]; then
      ref_container=$(get_running_containers | head -1)
    fi

    echo "Using container '$ref_container' as reference for connectivity tests"

    for container in $running_containers; do
      if [ "$container" != "$ref_container" ]; then
        echo -n "Testing if $ref_container can reach $container... "

        # Try ping first (might not work in minimal containers without ping)
        if docker exec "$ref_container" ping -c 1 -W 1 "$container" &>/dev/null; then
          echo -e "${GREEN}✓ SUCCESS${NC}"
        else
          # Try using wget or curl as fallback
          if docker exec "$ref_container" wget -q --spider --timeout=1 "http://$container" &>/dev/null || \
             docker exec "$ref_container" curl -s --connect-timeout 1 "http://$container" &>/dev/null; then
            echo -e "${GREEN}✓ SUCCESS (HTTP)${NC}"
          else
            echo -e "${RED}✗ FAILED${NC}"
          fi
        fi
      fi
    done
  fi

  # Provide recommendations based on results
  if [ $not_running -gt 0 ] || [ $issues -gt 0 ]; then
    print_section "RECOMMENDATIONS"

    if [ $not_running -gt 0 ]; then
      echo "1. Start containers that aren't running:"
      echo "   $0 start [container-name]"
      echo
    fi

    if [ $issues -gt 0 ]; then
      echo "2. Check logs for containers with issues:"
      echo "   $0 logs [container-name]"
      echo
      echo "3. Restart containers with issues:"
      echo "   $0 restart [container-name]"
      echo
    fi

    echo "4. Check Docker resource usage:"
    echo "   $0 resources"
    echo
  fi

  if [ "$export_to_file" = true ]; then
    echo -e "\n${GREEN}Health check report saved to: $log_file${NC}"
    exec &>/dev/tty
  fi
}

# Function to export all information as an AI prompt
export_ai_prompt() {
  local timestamp=$(get_timestamp)
  local log_file="${LOG_DIR}/docker_ai_prompt_${timestamp}.txt"

  print_section "EXPORTING AI PROMPT"
  ensure_log_directory

  echo -e "${YELLOW}Collecting system and Docker information...${NC}"

  # Create a temporary file to collect all information
  local temp_file=$(mktemp)

  # Start building the AI prompt
  cat > "$temp_file" << EOF
# Docker Troubleshooting Report

I need help analyzing my Docker environment. Here's all the information about my system and Docker containers:

## System Information

\`\`\`
EOF

  # Add system information
  echo "OS Information:" >> "$temp_file"
  if command_exists hostnamectl; then
    hostnamectl >> "$temp_file"
  else
    echo "Kernel: $(uname -r)" >> "$temp_file"
    echo "Architecture: $(uname -m)" >> "$temp_file"
  fi

  echo -e "\nCPU Information:" >> "$temp_file"
  if command_exists lscpu; then
    lscpu >> "$temp_file"
  else
    grep "model name" /proc/cpuinfo | head -1 >> "$temp_file"
    echo "CPU(s): $(grep -c processor /proc/cpuinfo)" >> "$temp_file"
  fi

  echo -e "\nMemory Information:" >> "$temp_file"
  if command_exists free; then
    free -h >> "$temp_file"
  else
    grep -E "MemTotal|MemFree|MemAvailable" /proc/meminfo >> "$temp_file"
  fi

  echo -e "\nDisk Usage:" >> "$temp_file"
  df -h >> "$temp_file"

  # Add Docker information
  echo -e "\nDocker Version:" >> "$temp_file"
  docker version >> "$temp_file"

  echo -e "\nDocker Info:" >> "$temp_file"
  docker info >> "$temp_file"

  echo -e "\nDocker Disk Usage:" >> "$temp_file"
  docker system df -v >> "$temp_file"

  # Close the code block and start a new section
  cat >> "$temp_file" << EOF
\`\`\`

## Docker Containers

\`\`\`
EOF

  # Add container information
  echo "All Containers:" >> "$temp_file"
  docker ps -a >> "$temp_file"

  echo -e "\nRunning Containers:" >> "$temp_file"
  docker ps >> "$temp_file"

  # Close the code block and start a new section
  cat >> "$temp_file" << EOF
\`\`\`

## Container Health Check

\`\`\`
EOF

  # Add container health information
  local all_containers=$(get_all_containers)
  local running_containers=$(get_running_containers)

  echo "Found $(echo "$all_containers" | wc -l) containers, $(echo "$running_containers" | wc -l) running" >> "$temp_file"

  # Check each container
  local total=0
  local running=0
  local issues=0
  local not_running=0
  local containers_with_issues=""

  for container in $all_containers; do
    total=$((total+1))

    echo -e "\n--- Container: $container ---" >> "$temp_file"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo "CONTAINER NOT FOUND" >> "$temp_file"
      continue
    fi

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo "NOT RUNNING" >> "$temp_file"

      # Get container status and exit code
      local status=$(docker ps -a --filter "name=$container" --format '{{.Status}}')
      local exit_code=$(docker inspect --format='{{.State.ExitCode}}' "$container" 2>/dev/null || echo "unknown")

      echo "Status: $status, Exit Code: $exit_code" >> "$temp_file"

      # Get recent logs
      echo "Recent logs:" >> "$temp_file"
      docker logs --tail 5 "$container" 2>&1 >> "$temp_file"

      not_running=$((not_running+1))
      containers_with_issues="$containers_with_issues\n- $container (not running, exit code: $exit_code)"
    else
      # Container is running, check health if available
      local health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}N/A{{end}}' "$container" 2>/dev/null)
      local status=$(docker ps --filter "name=$container" --format '{{.Status}}')

      case "$health" in
        "healthy")
          echo "RUNNING (HEALTHY)" >> "$temp_file"
          echo "Uptime: $status" >> "$temp_file"
          running=$((running+1))
          ;;
        "unhealthy")
          echo "RUNNING (UNHEALTHY)" >> "$temp_file"
          echo "Recent logs:" >> "$temp_file"
          docker logs --tail 5 "$container" 2>&1 >> "$temp_file"
          issues=$((issues+1))
          containers_with_issues="$containers_with_issues\n- $container (unhealthy)"
          ;;
        "starting")
          echo "RUNNING (STARTING)" >> "$temp_file"
          echo "Container is still initializing" >> "$temp_file"
          issues=$((issues+1))
          containers_with_issues="$containers_with_issues\n- $container (starting)"
          ;;
        *)
          echo "RUNNING" >> "$temp_file"
          echo "Uptime: $status" >> "$temp_file"
          running=$((running+1))
          ;;
      esac

      # Get container resource usage
      local cpu=$(docker stats "$container" --no-stream --format "{{.CPUPerc}}")
      local mem=$(docker stats "$container" --no-stream --format "{{.MemUsage}}")
      local net=$(docker stats "$container" --no-stream --format "{{.NetIO}}")

      echo "Resource usage:" >> "$temp_file"
      echo "  CPU: $cpu" >> "$temp_file"
      echo "  Memory: $mem" >> "$temp_file"
      echo "  Network I/O: $net" >> "$temp_file"
    fi
  done

  # Add summary
  echo -e "\nSUMMARY:" >> "$temp_file"
  echo "Total containers: $total" >> "$temp_file"
  echo "Running normally: $running" >> "$temp_file"
  echo "Running with issues: $issues" >> "$temp_file"
  echo "Not running: $not_running" >> "$temp_file"

  # Close the code block and start a new section
  cat >> "$temp_file" << EOF
\`\`\`

## Docker Networks

\`\`\`
EOF

  # Add network information
  echo "Docker networks:" >> "$temp_file"
  docker network ls >> "$temp_file"

  echo -e "\nDetailed network information:" >> "$temp_file"
  for network in $(get_all_networks); do
    echo -e "\nNetwork: $network" >> "$temp_file"
    docker network inspect "$network" | grep -E 'Name|Driver|Subnet|Gateway|"Containers"' >> "$temp_file"
  done

  # Close the code block and start a new section
  cat >> "$temp_file" << EOF
\`\`\`

## Issues Detected

EOF

  # Add issues section
  if [ $not_running -gt 0 ] || [ $issues -gt 0 ]; then
    echo "The following containers have issues:" >> "$temp_file"
    echo -e "$containers_with_issues" >> "$temp_file"

    # Add logs for containers with issues
    echo -e "\n### Logs for Containers with Issues\n" >> "$temp_file"

    IFS=
    for container_info in $(echo -e "$containers_with_issues"); do
      if [[ "$container_info" =~ -\ ([^\ ]+) ]]; then
        local container="${BASH_REMATCH[1]}"
        echo -e "\n#### Logs for $container\n" >> "$temp_file"
        echo '```' >> "$temp_file"
        docker logs --tail 50 "$container" 2>&1 >> "$temp_file" || echo "Could not retrieve logs" >> "$temp_file"
        echo '```' >> "$temp_file"
      fi
    done
    unset IFS
  else
    echo "No issues detected with Docker containers." >> "$temp_file"
  fi
}


# Function to export all logs
export_all_logs() {
  local lines=$1
  local timestamp=$(get_timestamp)

  if [ -z "$lines" ]; then
    lines=100
  fi

  print_section "EXPORTING LOGS FOR ALL CONTAINERS"
  ensure_log_directory

  local log_dir="${LOG_DIR}/all_logs_${timestamp}"
  mkdir -p "$log_dir"

  echo -e "${YELLOW}Logs will be saved to: $log_dir/${NC}"

  local containers=$(get_all_containers)
  if [ -z "$containers" ]; then
    echo -e "${YELLOW}No containers found${NC}"
    return 1
  fi

  for container in $containers; do
    echo "Exporting logs for $container..."
    docker logs --tail "$lines" "$container" > "$log_dir/${container}.log" 2>&1
  done

  echo -e "${GREEN}Logs for all containers exported to: $log_dir/${NC}"
}

# Function to start containers
start_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "STARTING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to start all services..."
      $compose_cmd up -d
    else
      echo "Starting all stopped containers..."
      docker start $(docker ps -a -f "status=exited" --format "{{.Names}}")
    fi
  else
    print_section "STARTING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    # Check if container is already running
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${YELLOW}Container '$container' is already running${NC}"
      return 0
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to start service..."
      $compose_cmd up -d "$container"
    else
      echo "Starting container..."
      docker start "$container"
    fi

    # Verify container started
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' started successfully${NC}"
    else
      echo -e "${RED}Failed to start container '$container'${NC}"
      echo "Check logs for details:"
      docker logs --tail 10 "$container"
      return 1
    fi
  fi
}

# Function to stop containers
stop_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "STOPPING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to stop all services..."
      $compose_cmd down
    else
      echo "Stopping all running containers..."
      docker stop $(docker ps -q)
    fi
  else
    print_section "STOPPING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    # Check if container is already stopped
    if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${YELLOW}Container '$container' is already stopped${NC}"
      return 0
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to stop service..."
      $compose_cmd stop "$container"
    else
      echo "Stopping container..."
      docker stop "$container"
    fi

    # Verify container stopped
    if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' stopped successfully${NC}"
    else
      echo -e "${RED}Failed to stop container '$container'${NC}"
      return 1
    fi
  fi
}

# Function to restart containers
restart_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "RESTARTING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to restart all services..."
      $compose_cmd restart
    else
      echo "Restarting all running containers..."
      docker restart $(docker ps -q)
    fi
  else
    print_section "RESTARTING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to restart service..."
      $compose_cmd restart "$container"
    else
      echo "Restarting container..."
      docker restart "$container"
    fi

    # Verify container restarted
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' restarted successfully${NC}"
    else
      echo -e "${RED}Failed to restart container '$container'${NC}"
      return 1
    fi
  fi
}

# Function to check Docker network setup
check_docker_networks() {
  local timestamp=$(get_timestamp)
  local export_to_file=$1
  local log_file=""

  print_section "DOCKER NETWORK INSPECTION"

  if [ "$export_to_file" = true ]; then
    ensure_log_directory
    log_file="${LOG_DIR}/network_inspection_${timestamp}.log"
    echo -e "${YELLOW}Results will be saved to: $log_file${NC}"
    exec > >(tee -a "$log_file") 2>&1
  fi

  echo "Docker networks:"
  docker network ls

  echo -e "\nDetailed network information:"
  for network in $(get_all_networks); do
    echo -e "\n${YELLOW}Network: $network${NC}"
    docker network inspect "$network" | grep -E 'Name|Driver|Subnet|Gateway|"Containers"' | sed 's/,//g' | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/^[ \t]*//'
  done

  echo -e "\nContainer network connections:"
  for container in $(get_running_containers); do
    echo -e "\n${YELLOW}Container: $container${NC}"
    docker inspect --format='Networks: {{range $net, $conf := .NetworkSettings.Networks}}{{$net}} {{end}}' "$container"
    docker inspect --format='IP Addresses: {{range $net, $conf := .NetworkSettings.Networks}}{{$conf.IPAddress}} {{end}}' "$container"
  done

  echo -e "\nTesting network connectivity:"

  # Test container to internet connectivity
  local test_container=$(get_running_containers | head -1)
  if [ -n "$test_container" ]; then
    echo "Testing internet connectivity from container $test_container"
    if docker exec "$test_container" ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
      echo -e "${GREEN}✓ Container can ping internet \(8.8.8.8\)${NC}"
    else
      echo -e "${RED}✗ Container cannot ping internet \(8.8.8.8\)${NC}"
    fi

    # Try DNS resolution test
    if docker exec "$test_container" nslookup google.com &>/dev/null; then
      echo -e "${GREEN}✓ DNS resolution works \(google.com\)${NC}"
    else
      echo -e "${RED}✗ DNS resolution failed \(google.com\)${NC}"

      # Show the container's DNS config
      echo "Container DNS configuration:"
      docker exec "$test_container" cat /etc/resolv.conf 2>/dev/null || echo "Could not read DNS configuration"
    fi
  else
    echo -e "${YELLOW}⚠ No running containers available to test network connectivity${NC}"
  fi

  # Check for common network issues
  echo -e "\nChecking for common network issues:"

  # IP forwarding check
  echo -n "IP forwarding enabled: "
  local ip_forward=$(sysctl -n net.ipv4.ip_forward 2>/dev/null || echo "unknown")
  if [ "$ip_forward" = "1" ]; then
    echo -e "${GREEN}Yes${NC}"
  elif [ "$ip_forward" = "0" ]; then
    echo -e "${RED}No \(Docker networking may be affected\)${NC}"
    echo "  Fix: sudo sysctl -w net.ipv4.ip_forward=1"
  else
    echo -e "${YELLOW}Unknown${NC}"
  fi

  # Overlapping subnets check
  echo -n "Overlapping network subnets: "
  local subnets=$(docker network ls --format '{{.Name}}' | xargs -I{} docker network inspect {} --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' 2>/dev/null)
  local duplicate_subnets=$(echo "$subnets" | sort | uniq -d)
  if [ -n "$duplicate_subnets" ]; then
    echo -e "${RED}Yes${NC}"
    echo "  Overlapping subnets found:"
    echo "$duplicate_subnets" | sed 's/^/  - /'
  else
    echo -e "${GREEN}None detected${NC}"
  fi

  if [ "$export_to_file" = true ]; then
    echo -e "\n${GREEN}Network inspection report saved to: $log_file${NC}"
    exec &>/dev/tty
    local IFS=$'\n'
    for container_info in $(echo -e "$containers_with_issues"); do
      if [[ "$container_info" =~ -\ ([^\ ]+) ]]; then
        local container="${BASH_REMATCH[1]}"
        echo -e "\n#### Logs for $container\n" >> "$temp_file"
        echo '```' >> "$temp_file"
        docker logs --tail 50 "$container" 2>&1 >> "$temp_file" || echo "Could not retrieve logs" >> "$temp_file"
        echo '```' >> "$temp_file"
      fi
    done
    unset IFS
  else
    echo "No issues detected with Docker containers." >> "$temp_file"
  fi

  # Add prompt for AI
  cat >> "$temp_file" << EOF

## Questions

1. What issues can you identify in my Docker environment?
2. What are the potential causes of these issues?
3. What steps should I take to resolve these issues?
4. Are there any best practices I should implement to prevent these issues in the future?
EOF

  # Move the temp file to the final location
  mv "$temp_file" "$log_file"

  echo -e "${GREEN}AI prompt exported to: $log_file${NC}"
  echo "You can use this file to get help from an AI assistant."

  # Ask if user wants to view the file
  if ask_yes_no "Do you want to view the exported AI prompt?"; then
    if command_exists less; then
      less "$log_file"
    else
      cat "$log_file"
    fi
  fi
}

# Function to check system resources
check_system_resources() {
  local timestamp=$(get_timestamp)
  local export_to_file=$1
  local log_file=""

  print_section "SYSTEM RESOURCES"

  if [ "$export_to_file" = true ]; then
    ensure_log_directory
    log_file="${LOG_DIR}/system_resources_${timestamp}.log"
    echo -e "${YELLOW}Results will be saved to: $log_file${NC}"
    exec > >(tee -a "$log_file") 2>&1
  fi

  echo "System information:"
  if command_exists hostnamectl; then
    hostnamectl | grep -E "Operating System|Kernel|Architecture"
  else
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
  fi

  echo -e "\nCPU information:"
  if command_exists lscpu; then
    lscpu | grep -E "^CPU\(s\):|^Model name:|^CPU MHz:"
  else
    grep "model name" /proc/cpuinfo | head -1
    echo "CPU(s): $(grep -c processor /proc/cpuinfo)"
  fi

  echo -e "\nMemory information:"
  if command_exists free; then
    free -h
  else
    grep -E "MemTotal|MemFree|MemAvailable" /proc/meminfo
  fi

  echo -e "\nDisk usage:"
  df -h / /var/lib/docker 2>/dev/null || df -h /

  echo -e "\nDocker disk usage:"
  docker system df

  echo -e "\nRunning container resource usage:"
  docker stats --no-stream

  if [ "$export_to_file" = true ]; then
    echo -e "\n${GREEN}Resource report saved to: $log_file${NC}"
    exec &>/dev/tty
  fi
}

# Function to check Docker logs
check_docker_logs() {
  local container=$1
  local lines=$2
  local timestamp=$(get_timestamp)
  local export_to_file=$3
  local log_file=""

  if [ -z "$lines" ]; then
    lines=100
  fi

  if [ -z "$container" ]; then
    print_section "AVAILABLE CONTAINERS"
    local containers=$(get_all_containers)

    if [ -z "$containers" ]; then
      echo -e "${YELLOW}No containers found${NC}"
      return 1
    fi

    echo "Choose a container to view logs:"
    local i=1
    local container_array=()

    while read -r container_name; do
      echo "  $i) $container_name"
      container_array[$i]="$container_name"
      i=$((i+1))
    done <<< "$containers"

    echo "  q) Quit"

    local selection
    read -p "Enter selection (1-$((i-1))): " selection

    if [[ "$selection" == "q" ]]; then
      return 0
    elif [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
      container="${container_array[$selection]}"
    else
      echo -e "${RED}Invalid selection${NC}"
      return 1
    fi
  fi

  print_section "LOGS FOR CONTAINER: $container"

  # Check if container exists
  if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
    echo -e "${RED}Container '$container' does not exist${NC}"
    return 1
  fi

  if [ "$export_to_file" = true ]; then
    ensure_log_directory
    log_file="${LOG_DIR}/${container}_logs_${timestamp}.log"
    echo -e "${YELLOW}Logs will be saved to: $log_file${NC}"

    # Check if container is running
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      local container_info=$(docker inspect --format='{{.State.StartedAt}} \(Running for {{.State.Health.Status}}\)' "$container")
      echo "Container started at: $container_info"

      docker logs --tail "$lines" "$container" > "$log_file"
      echo -e "${GREEN}Last $lines lines of logs saved to: $log_file${NC}"

      # Ask if user wants to follow logs
      if ask_yes_no "Do you want to follow logs in real-time?"; then
        docker logs --tail 10 -f "$container"
      else
        # Show just a preview
        echo -e "\n${YELLOW}Log preview (last 10 lines):${NC}"
        docker logs --tail 10 "$container"
      fi
    else
      echo -e "${YELLOW}Container is not running. Showing logs from last run.${NC}"
      docker logs --tail "$lines" "$container" > "$log_file"
      echo -e "${GREEN}Last $lines lines of logs saved to: $log_file${NC}"

      # Show just a preview
      echo -e "\n${YELLOW}Log preview (last 10 lines):${NC}"
      docker logs --tail 10 "$container"
    fi
  else
    # Interactive logs
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      local container_info=$(docker inspect --format='{{.State.StartedAt}} \(Running for {{.State.Health.Status}}\)' "$container")
      echo "Container started at: $container_info"

      # Show logs with follow option
      echo -e "${YELLOW}Showing last $lines lines of logs (press Ctrl+C to exit)${NC}"
      docker logs --tail "$lines" -f "$container"
    else
      echo -e "${YELLOW}Container is not running. Showing logs from last run.${NC}"
      docker logs --tail "$lines" "$container"
    fi
  fi
}

# Function to export all logs
export_all_logs() {
  local lines=$1
  local timestamp=$(get_timestamp)

  if [ -z "$lines" ]; then
    lines=100
  fi

  print_section "EXPORTING LOGS FOR ALL CONTAINERS"
  ensure_log_directory

  local log_dir="${LOG_DIR}/all_logs_${timestamp}"
  mkdir -p "$log_dir"

  echo -e "${YELLOW}Logs will be saved to: $log_dir/${NC}"

  local containers=$(get_all_containers)
  if [ -z "$containers" ]; then
    echo -e "${YELLOW}No containers found${NC}"
    return 1
  fi

  for container in $containers; do
    echo "Exporting logs for $container..."
    docker logs --tail "$lines" "$container" > "$log_dir/${container}.log" 2>&1
  done

  echo -e "${GREEN}Logs for all containers exported to: $log_dir/${NC}"
}

# Function to start containers
start_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "STARTING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to start all services..."
      $compose_cmd up -d
    else
      echo "Starting all stopped containers..."
      docker start $(docker ps -a -f "status=exited" --format "{{.Names}}")
    fi
  else
    print_section "STARTING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    # Check if container is already running
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${YELLOW}Container '$container' is already running${NC}"
      return 0
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to start service..."
      $compose_cmd up -d "$container"
    else
      echo "Starting container..."
      docker start "$container"
    fi

    # Verify container started
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' started successfully${NC}"
    else
      echo -e "${RED}Failed to start container '$container'${NC}"
      echo "Check logs for details:"
      docker logs --tail 10 "$container"
      return 1
    fi
  fi
}

# Function to stop containers
stop_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "STOPPING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to stop all services..."
      $compose_cmd down
    else
      echo "Stopping all running containers..."
      docker stop $(docker ps -q)
    fi
  else
    print_section "STOPPING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    # Check if container is already stopped
    if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${YELLOW}Container '$container' is already stopped${NC}"
      return 0
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to stop service..."
      $compose_cmd stop "$container"
    else
      echo "Stopping container..."
      docker stop "$container"
    fi

    # Verify container stopped
    if ! docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' stopped successfully${NC}"
    else
      echo -e "${RED}Failed to stop container '$container'${NC}"
      return 1
    fi
  fi
}

# Function to restart containers
restart_containers() {
  local container=$1

  # Check for docker-compose
  local compose_cmd=$(get_compose_command)
  local using_compose=false

  if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
    using_compose=true
  fi

  if [ -z "$container" ]; then
    print_section "RESTARTING ALL CONTAINERS"

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to restart all services..."
      $compose_cmd restart
    else
      echo "Restarting all running containers..."
      docker restart $(docker ps -q)
    fi
  else
    print_section "RESTARTING CONTAINER: $container"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${RED}Container '$container' does not exist${NC}"
      return 1
    fi

    if [ "$using_compose" = true ]; then
      echo "Using $compose_cmd to restart service..."
      $compose_cmd restart "$container"
    else
      echo "Restarting container..."
      docker restart "$container"
    fi

    # Verify container restarted
    if docker ps --format '{{.Names}}' | grep -q "^$container$"; then
      echo -e "${GREEN}Container '$container' restarted successfully${NC}"
    else
      echo -e "${RED}Failed to restart container '$container'${NC}"
      return 1
    fi
  fi
}

# Function to check Docker network setup
check_docker_networks() {
  local timestamp=$(get_timestamp)
  local export_to_file=$1
  local log_file=""

  print_section "DOCKER NETWORK INSPECTION"

  if [ "$export_to_file" = true ]; then
    ensure_log_directory
    log_file="${LOG_DIR}/network_inspection_${timestamp}.log"
    echo -e "${YELLOW}Results will be saved to: $log_file${NC}"
    exec > >(tee -a "$log_file") 2>&1
  fi

  echo "Docker networks:"
  docker network ls

  echo -e "\nDetailed network information:"
  for network in $(get_all_networks); do
    echo -e "\n${YELLOW}Network: $network${NC}"
    docker network inspect "$network" | grep -E 'Name|Driver|Subnet|Gateway|"Containers"' | sed 's/,//g' | sed 's/"//g' | sed 's/{//g' | sed 's/}//g' | sed 's/^[ \t]*//'
  done

  echo -e "\nContainer network connections:"
  for container in $(get_running_containers); do
    echo -e "\n${YELLOW}Container: $container${NC}"
    docker inspect --format='Networks: {{range $net, $conf := .NetworkSettings.Networks}}{{$net}} {{end}}' "$container"
    docker inspect --format='IP Addresses: {{range $net, $conf := .NetworkSettings.Networks}}{{$conf.IPAddress}} {{end}}' "$container"
  done

  echo -e "\nTesting network connectivity:"

  # Test container to internet connectivity
  local test_container=$(get_running_containers | head -1)
  if [ -n "$test_container" ]; then
    echo "Testing internet connectivity from container $test_container"
    if docker exec "$test_container" ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
      echo -e "${GREEN}✓ Container can ping internet \(8.8.8.8\)${NC}"
    else
      echo -e "${RED}✗ Container cannot ping internet \(8.8.8.8\)${NC}"
    fi

    # Try DNS resolution test
    if docker exec "$test_container" nslookup google.com &>/dev/null; then
      echo -e "${GREEN}✓ DNS resolution works \(google.com\)${NC}"
    else
      echo -e "${RED}✗ DNS resolution failed \(google.com\)${NC}"

      # Show the container's DNS config
      echo "Container DNS configuration:"
      docker exec "$test_container" cat /etc/resolv.conf 2>/dev/null || echo "Could not read DNS configuration"
    fi
  else
    echo -e "${YELLOW}⚠ No running containers available to test network connectivity${NC}"
  fi

  # Check for common network issues
  echo -e "\nChecking for common network issues:"

  # IP forwarding check
  echo -n "IP forwarding enabled: "
  local ip_forward=$(sysctl -n net.ipv4.ip_forward 2>/dev/null || echo "unknown")
  if [ "$ip_forward" = "1" ]; then
    echo -e "${GREEN}Yes${NC}"
  elif [ "$ip_forward" = "0" ]; then
    echo -e "${RED}No \(Docker networking may be affected\)${NC}"
    echo "  Fix: sudo sysctl -w net.ipv4.ip_forward=1"
  else
    echo -e "${YELLOW}Unknown${NC}"
  fi

  # Overlapping subnets check
  echo -n "Overlapping network subnets: "
  local subnets=$(docker network ls --format '{{.Name}}' | xargs -I{} docker network inspect {} --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' 2>/dev/null)
  local duplicate_subnets=$(echo "$subnets" | sort | uniq -d)
  if [ -n "$duplicate_subnets" ]; then
    echo -e "${RED}Yes${NC}"
    echo "  Overlapping subnets found:"
    echo "$duplicate_subnets" | sed 's/^/  - /'
  else
    echo -e "${GREEN}None detected${NC}"
  fi

  if [ "$export_to_file" = true ]; then
    echo -e "\n${GREEN}Network inspection report saved to: $log_file${NC}"
    exec &>/dev/tty
  fi
}

# Function to display the main menu
show_main_menu() {
  clear
  print_banner "DockerForge v${SCRIPT_VERSION}"
  echo -e "${CYAN}A comprehensive Docker management utility${NC}"
  echo

  echo -e "${YELLOW}MAIN MENU${NC}"
  echo "1) Container Management"
  echo "2) Docker Health Check"
  echo "3) Docker Logs"
  echo "4) Docker Networks"
  echo "5) System Resources"
  echo "6) Docker Cleanup"
  echo "7) Docker Troubleshooting"
  echo "8) Exit"
  echo
  read -p "Enter your choice (1-8): " main_choice

  case $main_choice in
    1) show_container_menu ;;
    2) show_health_menu ;;
    3) show_logs_menu ;;
    4) show_network_menu ;;
    5) check_system_resources ;;
    6) clean_docker_resources ;;
    7) show_troubleshooting_menu ;;
    8) echo "Exiting..."; exit 0 ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_main_menu ;;
  esac
}

# Function to display container management menu
show_container_menu() {
  clear
  print_section "CONTAINER MANAGEMENT"
  echo "1) List Containers"
  echo "2) Start Container(s)"
  echo "3) Stop Container(s)"
  echo "4) Restart Container(s)"
  echo "5) Container Details"
  echo "6) Execute Command in Container"
  echo "7) Back to Main Menu"
  echo
  read -p "Enter your choice (1-7): " container_choice

  case $container_choice in
    1)
      echo "All Containers:"
      docker ps -a
      echo
      echo "Running Containers:"
      docker ps
      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    2)
      echo "Available containers:"
      local i=1
      local container_array=()

      for container in $(get_all_containers); do
        echo "  $i) $container"
        container_array[$i]="$container"
        i=$((i+1))
      done

      echo "  a) All containers"
      echo "  b) Back to Container Menu"

      read -p "Enter your choice: " start_choice

      if [[ "$start_choice" == "a" ]]; then
        start_containers
      elif [[ "$start_choice" == "b" ]]; then
        show_container_menu
      elif [[ "$start_choice" =~ ^[0-9]+$ ]] && [ "$start_choice" -ge 1 ] && [ "$start_choice" -lt "$i" ]; then
        start_containers "${container_array[$start_choice]}"
      else
        echo -e "${RED}Invalid selection${NC}"
      fi

      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    3)
      echo "Running containers:"
      local i=1
      local container_array=()

      for container in $(get_running_containers); do
        echo "  $i) $container"
        container_array[$i]="$container"
        i=$((i+1))
      done

      echo "  a) All containers"
      echo "  b) Back to Container Menu"

      read -p "Enter your choice: " stop_choice

      if [[ "$stop_choice" == "a" ]]; then
        stop_containers
      elif [[ "$stop_choice" == "b" ]]; then
        show_container_menu
      elif [[ "$stop_choice" =~ ^[0-9]+$ ]] && [ "$stop_choice" -ge 1 ] && [ "$stop_choice" -lt "$i" ]; then
        stop_containers "${container_array[$stop_choice]}"
      else
        echo -e "${RED}Invalid selection${NC}"
      fi

      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    4)
      echo "Available containers:"
      local i=1
      local container_array=()

      for container in $(get_all_containers); do
        echo "  $i) $container"
        container_array[$i]="$container"
        i=$((i+1))
      done

      echo "  a) All containers"
      echo "  b) Back to Container Menu"

      read -p "Enter your choice: " restart_choice

      if [[ "$restart_choice" == "a" ]]; then
        restart_containers
      elif [[ "$restart_choice" == "b" ]]; then
        show_container_menu
      elif [[ "$restart_choice" =~ ^[0-9]+$ ]] && [ "$restart_choice" -ge 1 ] && [ "$restart_choice" -lt "$i" ]; then
        restart_containers "${container_array[$restart_choice]}"
      else
        echo -e "${RED}Invalid selection${NC}"
      fi

      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    5)
      show_container_details
      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    6)
      exec_in_container
      read -p "Press Enter to continue..."
      show_container_menu
      ;;
    7) show_main_menu ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_container_menu ;;
  esac
}

# Function to display health check menu
show_health_menu() {
  clear
  print_section "DOCKER HEALTH CHECK"
  echo "1) Check All Containers Health"
  echo "2) Check Specific Container Health"
  echo "3) Export Health Report"
  echo "4) Back to Main Menu"
  echo
  read -p "Enter your choice (1-4): " health_choice

  case $health_choice in
    1)
      check_all_containers_health
      read -p "Press Enter to continue..."
      show_health_menu
      ;;
    2)
      echo "Available containers:"
      local i=1
      local container_array=()

      for container in $(get_all_containers); do
        echo "  $i) $container"
        container_array[$i]="$container"
        i=$((i+1))
      done

      echo "  b) Back to Health Menu"

      read -p "Enter your choice: " container_choice

      if [[ "$container_choice" == "b" ]]; then
        show_health_menu
      elif [[ "$container_choice" =~ ^[0-9]+$ ]] && [ "$container_choice" -ge 1 ] && [ "$container_choice" -lt "$i" ]; then
        check_container_health "${container_array[$container_choice]}"
      else
        echo -e "${RED}Invalid selection${NC}"
      fi

      read -p "Press Enter to continue..."
      show_health_menu
      ;;
    3)
      check_all_containers_health true
      read -p "Press Enter to continue..."
      show_health_menu
      ;;
    4) show_main_menu ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_health_menu ;;
  esac
}

# Function to display logs menu
show_logs_menu() {
  clear
  print_section "DOCKER LOGS"
  echo "1) View Container Logs"
  echo "2) Export Container Logs"
  echo "3) Export All Logs"
  echo "4) Back to Main Menu"
  echo
  read -p "Enter your choice (1-4): " logs_choice

  case $logs_choice in
    1)
      check_docker_logs
      read -p "Press Enter to continue..."
      show_logs_menu
      ;;
    2)
      echo "Available containers:"
      local i=1
      local container_array=()

      for container in $(get_all_containers); do
        echo "  $i) $container"
        container_array[$i]="$container"
        i=$((i+1))
      done

      echo "  b) Back to Logs Menu"

      read -p "Enter your choice: " container_choice

      if [[ "$container_choice" == "b" ]]; then
        show_logs_menu
      elif [[ "$container_choice" =~ ^[0-9]+$ ]] && [ "$container_choice" -ge 1 ] && [ "$container_choice" -lt "$i" ]; then
        read -p "How many lines of logs to export? [100]: " lines
        lines=${lines:-100}
        check_docker_logs "${container_array[$container_choice]}" "$lines" true
      else
        echo -e "${RED}Invalid selection${NC}"
      fi

      read -p "Press Enter to continue..."
      show_logs_menu
      ;;
    3)
      read -p "How many lines of logs to export? [100]: " lines
      lines=${lines:-100}
      export_all_logs "$lines"
      read -p "Press Enter to continue..."
      show_logs_menu
      ;;
    4) show_main_menu ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_logs_menu ;;
  esac
}

# Function to display network menu
show_network_menu() {
  clear
  print_section "DOCKER NETWORKS"
  echo "1) List Networks"
  echo "2) Inspect Networks"
  echo "3) Fix Network Issues"
  echo "4) Export Network Report"
  echo "5) Back to Main Menu"
  echo
  read -p "Enter your choice (1-5): " network_choice

  case $network_choice in
    1)
      echo "Docker networks:"
      docker network ls
      read -p "Press Enter to continue..."
      show_network_menu
      ;;
    2)
      check_docker_networks
      read -p "Press Enter to continue..."
      show_network_menu
      ;;
    3)
      fix_docker_networking
      read -p "Press Enter to continue..."
      show_network_menu
      ;;
    4)
      check_docker_networks true
      read -p "Press Enter to continue..."
      show_network_menu
      ;;
    5) show_main_menu ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_network_menu ;;
  esac
}

# Function to display troubleshooting menu
show_troubleshooting_menu() {
  clear
  print_section "DOCKER TROUBLESHOOTING"
  echo "1) Check Docker Installation"
  echo "2) Export AI Troubleshooting Prompt"
  echo "3) Fix Common Issues"
  echo "4) Back to Main Menu"
  echo
  read -p "Enter your choice (1-4): " trouble_choice

  case $trouble_choice in
    1)
      check_docker_installed
      read -p "Press Enter to continue..."
      show_troubleshooting_menu
      ;;
    2)
      export_ai_prompt
      read -p "Press Enter to continue..."
      show_troubleshooting_menu
      ;;
    3)
      fix_docker_networking
      read -p "Press Enter to continue..."
      show_troubleshooting_menu
      ;;
    4) show_main_menu ;;
    *) echo -e "${RED}Invalid option${NC}"; sleep 2; show_troubleshooting_menu ;;
  esac
}

# Main script execution
main() {
  # Create necessary directories
  ensure_log_directory
  ensure_config_directory

  # Process command line arguments
  if [ $# -eq 0 ]; then
    # No arguments, show the main menu
    show_main_menu
  else
    # Process arguments
    case "$1" in
      "health")
        if [ -n "$2" ]; then
          check_container_health "$2"
        else
          check_all_containers_health
        fi
        ;;
      "logs")
        if [ -n "$2" ]; then
          check_docker_logs "$2" "${3:-100}"
        else
          check_docker_logs
        fi
        ;;
      "start")
        if [ -n "$2" ]; then
          start_containers "$2"
        else
          start_containers
        fi
        ;;
      "stop")
        if [ -n "$2" ]; then
          stop_containers "$2"
        else
          stop_containers
        fi
        ;;
      "restart")
        if [ -n "$2" ]; then
          restart_containers "$2"
        else
          restart_containers
        fi
        ;;
      "inspect")
        if [ -n "$2" ]; then
          show_container_details "$2"
        else
          show_container_details
        fi
        ;;
      "exec")
        if [ -n "$2" ]; then
          exec_in_container "$2" "$3"
        else
          exec_in_container
        fi
        ;;
      "networks")
        check_docker_networks
        ;;
      "fix-network")
        fix_docker_networking
        ;;
      "resources")
        check_system_resources
        ;;
      "cleanup")
        clean_docker_resources
        ;;
      "help"|"-h"|"--help")
        echo "DockerForge v${SCRIPT_VERSION} - Docker Management Utility"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  health [container]     Check health of all or specific container"
        echo "  logs [container] [lines] View logs of a container"
        echo "  start [container]      Start all or specific container"
        echo "  stop [container]       Stop all or specific container"
        echo "  restart [container]    Restart all or specific container"
        echo "  inspect [container]    Show details of a container"
        echo "  exec [container] [cmd] Execute command in container"
        echo "  networks               Check Docker networks"
        echo "  fix-network            Fix common Docker networking issues"
        echo "  resources              Check system resources"
        echo "  cleanup                Clean up Docker resources"
        echo "  help                   Show this help message"
        echo
        echo "Run without arguments to use the interactive menu"
        ;;
      *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
    esac
  fi
}

# Run the main function with all arguments
main "$@"
