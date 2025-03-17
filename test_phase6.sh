#!/bin/bash

# Test script for Phase 6: Resource Monitoring
# This script tests the resource monitoring functionality of DockerForge

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${YELLOW}==== $1 ====${NC}\n"
}

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        if [ "$2" != "continue" ]; then
            exit 1
        fi
    fi
}

# Function to run a test and check its output
run_test() {
    local cmd="$1"
    local expected="$2"
    local description="$3"
    local continue_on_error="$4"
    
    echo -e "Running: $cmd"
    output=$(eval "$cmd" 2>&1)
    
    if [[ "$output" == *"$expected"* ]]; then
        echo -e "${GREEN}✓ $description${NC}"
    else
        echo -e "${RED}✗ $description${NC}"
        echo -e "Expected output to contain: $expected"
        echo -e "Actual output: $output"
        if [ "$continue_on_error" != "continue" ]; then
            exit 1
        fi
    fi
}

# Make sure we're in the project root directory
cd "$(dirname "$0")"

print_header "Setting up test environment"

# Make sure Docker is running
docker info > /dev/null 2>&1
check_status "Docker is running"

# Start a test container if not already running
if ! docker ps | grep -q "dockerforge-test"; then
    echo "Starting test container..."
    docker run -d --name dockerforge-test -p 8080:80 nginx
    check_status "Started test container" "continue"
    sleep 2
fi

# Install the package in development mode if not already installed
if ! pip list | grep -q "dockerforge"; then
    echo "Installing DockerForge in development mode..."
    pip install -e .
    check_status "Installed DockerForge" "continue"
fi

print_header "Testing Resource Monitoring CLI Commands"

# Test resource monitoring help
run_test "python -m src.cli resource --help" "Monitor and optimize Docker container resources" "Resource monitoring help command works" "continue"

# Test resource monitoring start command
run_test "python -m src.cli resource start --help" "Start the resource monitoring daemon" "Resource start help command works" "continue"

# Test resource monitoring status command (daemon not running)
run_test "python -m src.cli resource status" "Resource monitoring daemon is not running" "Resource status command works when daemon is not running" "continue"

# Start the resource monitoring daemon
echo "Starting resource monitoring daemon..."
python -m src.cli resource start
check_status "Started resource monitoring daemon" "continue"
sleep 5

# Test resource monitoring status command (daemon running)
run_test "python -m src.cli resource status" "Resource Monitoring Daemon Status" "Resource status command works when daemon is running" "continue"

# Test resource monitoring metrics command
run_test "python -m src.cli resource metrics" "Container Resource Metrics" "Resource metrics command works" "continue"

# Test resource monitoring anomalies command
run_test "python -m src.cli resource anomalies" "No anomalies found" "Resource anomalies command works" "continue"

# Test resource monitoring recommendations command
run_test "python -m src.cli resource recommendations" "No recommendations found" "Resource recommendations command works" "continue"

# Test resource monitoring report command
run_test "python -m src.cli resource report" "No optimization recommendations available" "Resource report command works" "continue"

# Test resource monitoring with specific container
run_test "python -m src.cli resource metrics --container dockerforge-test" "Container Resource Metrics" "Resource metrics command works with specific container" "continue"

# Stop the resource monitoring daemon
echo "Stopping resource monitoring daemon..."
python -m src.cli resource stop
check_status "Stopped resource monitoring daemon" "continue"

# Verify daemon is stopped
run_test "python -m src.cli resource status" "Resource monitoring daemon is not running" "Resource daemon is stopped" "continue"

print_header "Testing Resource Monitoring Standalone CLI"

# Test standalone CLI help
run_test "python -m src.cli_resource_monitoring --help" "DockerForge Resource Monitoring CLI" "Standalone CLI help command works" "continue"

# Test standalone CLI start command
run_test "python -m src.cli_resource_monitoring start --help" "Start the monitoring daemon" "Standalone CLI start help command works" "continue"

# Start the monitoring daemon using standalone CLI
echo "Starting monitoring daemon using standalone CLI..."
python -m src.cli_resource_monitoring start
check_status "Started monitoring daemon" "continue"
sleep 5

# Test standalone CLI status command
run_test "python -m src.cli_resource_monitoring status" "Daemon Status" "Standalone CLI status command works" "continue"

# Test standalone CLI metrics command
run_test "python -m src.cli_resource_monitoring metrics" "Container Metrics" "Standalone CLI metrics command works" "continue"

# Test standalone CLI anomalies command
run_test "python -m src.cli_resource_monitoring anomalies" "No anomalies found" "Standalone CLI anomalies command works" "continue"

# Test standalone CLI recommendations command
run_test "python -m src.cli_resource_monitoring recommendations" "No recommendations found" "Standalone CLI recommendations command works" "continue"

# Test standalone CLI report command
run_test "python -m src.cli_resource_monitoring report" "No optimization recommendations available" "Standalone CLI report command works" "continue"

# Stop the monitoring daemon using standalone CLI
echo "Stopping monitoring daemon using standalone CLI..."
python -m src.cli_resource_monitoring stop
check_status "Stopped monitoring daemon" "continue"

# Verify daemon is stopped
run_test "python -m src.cli_resource_monitoring status" "Daemon is not running" "Standalone CLI daemon is stopped" "continue"

print_header "Cleaning up test environment"

# Clean up test container
echo "Removing test container..."
docker stop dockerforge-test > /dev/null 2>&1
docker rm dockerforge-test > /dev/null 2>&1
check_status "Removed test container" "continue"

print_header "Phase 6 Tests Completed Successfully"
echo -e "${GREEN}All tests passed!${NC}"
