#!/bin/bash
set -e

echo "Stopping all containers..."
docker compose -f docker/docker-compose.yml down --rmi all --volumes --remove-orphans || true

echo "Pruning system..."
docker system prune -f

echo "Rebuilding..."
docker compose -f docker/docker-compose.yml build --no-cache

echo "Launching..."
docker compose -f docker/docker-compose.yml up -d

echo "Done!"
