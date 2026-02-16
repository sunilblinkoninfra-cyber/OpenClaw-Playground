# Openclaw Platform - Setup Guide

This guide will help you get the Openclaw platform up and running locally and prepare for deployment.

## Prerequisites

- **Git** — For version control
- **Docker & Docker Compose** — For containerization
- **Python 3.11+** — Backend runtime
- **Node.js 18+** — Frontend runtime
- **PostgreSQL** — Database (included in Docker Compose)
- **Redis** — Caching & queues (included in Docker Compose)
- **AWS Account** — For production deployment (optional for dev)
- **Stripe Account** — For payment processing
- **Supabase Account** — For authentication (optional)

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
cd workspace
cp .env.example .env
# Edit .env with your secrets
```

### 2. Start with Docker Compose
```bash
docker-compose up
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:3000`
- PostgreSQL database
- Redis cache
- Nginx reverse proxy

### 3. Access Services
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api

## Manual Setup (Without Docker)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Initialize database (first time)
# This is done automatically on app startup

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
```

## Database Setup

### Using Docker Compose (Automatic)
Database is automatically created when you run `docker-compose up`.

### Manual PostgreSQL Setup
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE openclaw;
CREATE USER openclaw_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE openclaw TO openclaw_user;

# Exit
\q
```

### Running Migrations
The database tables are automatically created on first run of the backend using SQLAlchemy ORM.

If you need to reset:
```bash
# Backend will recreate tables on startup
# Or manually with Python:
python -c "from app.database import init_db; init_db()"
```

## Environment Configuration

### Backend (.env)
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/openclaw
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
ENVIRONMENT=development
SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_pub_key
```

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --watch
```

## Building for Production

### Backend Docker Image
```bash
docker build -f infrastructure/docker/backend.Dockerfile -t openclaw-backend:latest .
docker tag openclaw-backend:latest your-registry/openclaw-backend:latest
docker push your-registry/openclaw-backend:latest
```

### Frontend Docker Image
```bash
docker build -f infrastructure/docker/frontend.Dockerfile -t openclaw-frontend:latest .
docker tag openclaw-frontend:latest your-registry/openclaw-frontend:latest
docker push your-registry/openclaw-frontend:latest
```

### User Environment Docker Image
```bash
docker build -f infrastructure/docker/openclaw.Dockerfile -t openclaw-env:latest .
docker tag openclaw-env:latest your-registry/openclaw-env:latest
docker push your-registry/openclaw-env:latest
```

## Deployment with Terraform

### Prerequisites
- AWS Account with credentials configured
- Terraform installed (v1.0+)

### Deploy Infrastructure
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply changes
terraform apply

# Get outputs
terraform output
```

### Update Terraform State Storage (Recommended)
Uncomment the backend configuration in `main.tf` and create S3 bucket for state storage:

```bash
aws s3 mb s3://openclaw-terraform-state --region us-east-1
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>

# Or on Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**2. Database Connection Error**
```bash
# Ensure PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs db

# Restart service
docker-compose restart db
```

**3. Redis Connection Error**
```bash
# Restart Redis
docker-compose restart redis

# Or test locally with redis-cli
redis-cli ping
```

**4. Frontend Can't Connect to API**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running on correct port
- Check CORS settings in backend

**5. Docker Image Build Fails**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Checking Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Backend logs
python -u app/main.py 2>&1 | tee logs.txt
```

## Development Workflow

### 1. Feature Branch
```bash
git checkout -b feature/my-feature
```

### 2. Make Changes
Edit relevant files in `backend/`, `frontend/`, or `infrastructure/`

### 3. Test Locally
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

### 4. Commit and Push
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/my-feature
```

### 5. Create Pull Request
Push to repository and create PR for review

## Security Checklist

Before production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Update database password from default
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set proper environment to `production`
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts
- [ ] Review and update rate limiting
- [ ] Configure CORS for specific domains
- [ ] Enable phone verification for trials
- [ ] Require credit card for trials
- [ ] Set up emergency access procedures

## Performance Optimization

### Frontend
```bash
# Build analysis
npm run build
# Check with: npm install --save-dev webpack-bundle-analyzer
```

### Backend
- Use `gunicorn` or `uvicorn` with multiple workers in production
- Enable caching with Redis
- Use connection pooling for database
- Enable gzip compression in Nginx

### Database
- Add indexes on frequently queried columns
- Implement query caching
- Set up read replicas for scaling

## Monitoring and Logging

### CloudWatch (AWS)
Logs automatically sent via Terraform setup

### Local Monitoring
```bash
# Check container health
docker-compose ps

# View resource usage
docker stats

# Check services
curl http://localhost:8000/health
```

## Useful Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Run one-off command
docker-compose exec backend python -c "from app.database import init_db; init_db()"

# Rebuild images
docker-compose build

# Clean up everything
docker-compose down -v
docker system prune -a
```

## Next Steps

1. **Configure Environment** — Update `.env` files with your API keys
2. **Setup Database** — Run initial migrations
3. **Test Locally** — Verify all services work
4. **Customize Branding** — Update colors and copy
5. **Deploy** — Use Terraform to deploy to AWS
6. **Setup Monitoring** — Configure CloudWatch and alerts
7. **Configure Domain** — Point your domain to the ALB
8. **Enable HTTPS** — Set up SSL certificates

## Support

- Check [README.md](README.md) for architecture overview
- Check [API.md](API.md) for API documentation
- Check `.github/copilot-instructions.md` for development instructions
- Review inline code comments for implementation details

---

**Created:** February 16, 2026  
**Status:** MVP Phase Ready
