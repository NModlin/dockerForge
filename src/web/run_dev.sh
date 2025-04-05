#!/bin/bash
# Script to run the DockerForge Web UI in development mode

set -e

# Directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}DockerForge Web UI Development Runner${NC}"
echo "===================================="
echo ""

# Check if required commands are installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed.${NC}"
    exit 1
fi

# Trap Ctrl+C to kill all background processes
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Start the backend server
echo -e "${BLUE}Starting FastAPI backend server...${NC}"
cd "$SCRIPT_DIR/api"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r ../../requirements.txt >/dev/null 2>&1
python3 main.py &
BACKEND_PID=$!
echo -e "${GREEN}Backend server started. PID: $BACKEND_PID${NC}"

# Wait for backend to initialize
echo -e "${YELLOW}Waiting for backend to initialize...${NC}"
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Backend failed to start.${NC}"
    exit 1
fi

# Start the frontend development server
echo -e "${BLUE}Starting Vue.js frontend development server...${NC}"
cd "$SCRIPT_DIR/frontend"
npm install >/dev/null 2>&1
npm run serve &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend development server started. PID: $FRONTEND_PID${NC}"

echo ""
echo -e "${BLUE}Development environment is now running.${NC}"
echo -e "${YELLOW}Backend: http://localhost:54321${NC}"
echo -e "${YELLOW}Frontend: http://localhost:8080${NC}"
echo -e "${YELLOW}API Docs: http://localhost:54321/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
