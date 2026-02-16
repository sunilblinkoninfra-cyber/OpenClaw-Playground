# Openclaw Deployment Script for Windows PowerShell
# Automates local deployment with Docker Compose

Write-Host "🚀 Openclaw Platform Deployment" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "✓ Checking Docker installation..." -ForegroundColor Green
try {
    $dockerVersion = docker --version
    Write-Host "  $dockerVersion"
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "✓ Checking Docker Compose..." -ForegroundColor Green
try {
    $composeVersion = docker-compose --version
    Write-Host "  $composeVersion"
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Setting up environment files..." -ForegroundColor Green

# Create .env files if they don't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  Created .env"
}

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "  Created backend\.env"
}

if (-not (Test-Path "frontend\.env.local")) {
    Copy-Item "frontend\.env.example" "frontend\.env.local"
    Write-Host "  Created frontend\.env.local"
}

Write-Host ""
Write-Host "✓ Building Docker images..." -ForegroundColor Green
docker-compose build

Write-Host ""
Write-Host "✓ Starting services..." -ForegroundColor Green
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if services are healthy
Write-Host ""
Write-Host "✓ Verifying services..." -ForegroundColor Green

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend: http://localhost:3000" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Frontend: Still starting..." -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Backend API: http://localhost:8000" -ForegroundColor Green
        Write-Host "    API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  ⚠ Backend: Still starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Visit http://localhost:3000 in your browser"
Write-Host "2. Create an account to get a 24-hour trial"
Write-Host "3. Launch your first environment"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  docker-compose logs -f"
Write-Host ""
Write-Host "To stop services:"
Write-Host "  docker-compose down"
Write-Host ""
Write-Host "For more info, see DEPLOYMENT.md"
