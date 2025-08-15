#!/bin/bash

echo "🧹 Cleaning up Docker resources..."

# Stop all running containers
echo "Stopping containers..."
docker stop $(docker ps -a -q) 2>/dev/null || echo "No containers to stop"

# Remove all containers
echo "Removing containers..."
docker rm $(docker ps -a -q) 2>/dev/null || echo "No containers to remove"

# Remove all images
echo "Removing images..."
docker rmi $(docker images -q) 2>/dev/null || echo "No images to remove"

# Clean up volumes
echo "Cleaning volumes..."
docker volume prune -f

# Clean up networks
echo "Cleaning networks..."
docker network prune -f

# Clean up everything
echo "Full cleanup..."
docker system prune -a -f

echo "✅ Docker cleanup complete!"

echo ""
echo "🔨 Building new image..."
docker build -t text-embeddings-app .

echo ""
echo "🚀 Running container..."
docker run -p 8501:8501 text-embeddings-app

echo ""
echo "📱 App should be available at: http://localhost:8501"
