#!/bin/bash
# Update + rebuild script for Docker container

echo ""
echo "📦 Pulling latest code from GitHub (or wherever)..."
git pull

echo ""
echo "🔄 Rebuilding Docker container..."
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up --build -d

echo ""
echo "✅ Update complete! Visit: http://localhost:5100"
echo ""
