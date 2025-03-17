#!/bin/bash
# Docker Environment Cleanup Script

echo "===== Docker Environment Cleanup ====="
echo "This script will help clean up unused Docker resources"
echo

# Step 1: Remove dangling images
echo "Step 1: Removing dangling images..."
docker image prune -f
echo

# Step 2: Remove unused volumes
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

echo "===== Cleanup Complete ====="
echo "For more aggressive cleanup, consider running:"
echo "docker system prune -a --volumes"
echo "WARNING: This will remove ALL unused containers, networks, images, and volumes!"
