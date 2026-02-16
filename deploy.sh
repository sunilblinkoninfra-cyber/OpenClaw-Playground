#!/bin/bash

# Openclaw Deployment Script
# Automates local deployment with Docker Compose

set -e

echo "🚀 Openclaw Platform Deployment"
echo "================================="
echo ""

# Check Docker
echo "✓ Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi
docker --version

echo "✓ Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi
docker-compose --version

echo ""
echo "✓ Setting up environment files..."

# Create .env files if they don't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "  Created backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "  Created frontend/.env.local"
fi

echo ""
echo "✓ Pulling latest images..."
docker-compose pull

echo ""
echo "✓ Building Docker images..."
docker-compose build

echo ""
echo "✓ Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo ""
echo "✓ Verifying services..."

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "  ✓ Frontend: http://localhost:3000"
else
    echo "  ⚠ Frontend: Still starting..."
fi

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "  ✓ Backend API: http://localhost:8000"
    echo "    API Docs: http://localhost:8000/docs"
else
    echo "  ⚠ Backend: Still starting..."
fi

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Next steps:"
echo "1. Visit http://localhost:3000 in your browser"
echo "2. Create an account to get a 24-hour trial"
echo "3. Launch your first environment"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "For more info, see DEPLOYMENT.md"
