#!/bin/bash
# Script to build and deploy the DockerForge Web UI frontend

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

echo -e "${BLUE}DockerForge Frontend Build Tool${NC}"
echo "=============================="
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js and npm.${NC}"
    exit 1
fi

# Parse command line arguments
MODE="dev"
CLEAN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--production)
      MODE="prod"
      shift
      ;;
    -c|--clean)
      CLEAN=true
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  -p, --production    Build for production"
      echo "  -c, --clean         Clean node_modules and perform fresh install"
      echo "  -h, --help          Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Clean if requested
if [ "$CLEAN" = true ]; then
    echo -e "${YELLOW}Cleaning node_modules...${NC}"
    rm -rf node_modules
    rm -rf dist
    echo -e "${GREEN}Clean completed.${NC}"
fi

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
npm install
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Build for the appropriate mode
if [ "$MODE" = "prod" ]; then
    echo -e "${BLUE}Building for production...${NC}"
    npm run build
    echo -e "${GREEN}Production build completed successfully.${NC}"
    echo -e "${YELLOW}Static files have been output to: $(cd ../../static && pwd)${NC}"
else
    echo -e "${BLUE}Starting development server...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    npm run serve
fi

echo ""
echo -e "${GREEN}Build process completed.${NC}"
