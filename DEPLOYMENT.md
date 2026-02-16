# 🚀 Openclaw Deployment Guide

## Quick Start - Local Deployment

### Prerequisites
- Docker Desktop installed and running
- Port 3000 (Frontend), 8000 (Backend), 5432 (Database), 6379 (Redis) available

### Step 1: Start Docker Desktop
1. Open Docker Desktop application
2. Wait for it to fully initialize (~30-60 seconds)
3. Verify status in system tray

### Step 2: Deploy Services
```bash
cd C:\workspace
docker-compose up --build
```

This will:
- Build all 3 Docker images
- Start PostgreSQL database
- Start Redis cache
- Start FastAPI backend (http://localhost:8000)
- Start Next.js frontend (http://localhost:3000)
- Start Nginx reverse proxy

### Step 3: Access Services
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### Step 4: Test Registration
1. Visit http://localhost:3000
2. Click "Get Started Free" or "Create Account"
3. Fill in:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123
4. You get an instant 24-hour trial
5. Click "Launch Environment" to provision your isolated container

---

## Services & Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Next.js web app |
| Backend API | 8000 | FastAPI provisioning engine |
| Database | 5432 | PostgreSQL |
| Cache | 6379 | Redis |
| Reverse Proxy | 80/443 | Nginx |

---

## Useful Docker Commands

### View running services
```bash
docker-compose ps
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop services
```bash
docker-compose down
```

### Reset everything (including data)
```bash
docker-compose down -v
docker-compose up --build
```

---

## AWS Deployment with Terraform

### Prerequisites
- AWS Account
- AWS CLI configured with credentials
- Terraform installed

### Deploy Infrastructure
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review changes
terraform plan

# Apply to AWS
terraform apply
```

This deploys:
- VPC with public/private subnets
- ECS cluster for container orchestration
- Application Load Balancer
- CloudWatch logging
- Security groups
- RDS PostgreSQL database
- ElastiCache Redis

### Get Load Balancer URL
```bash
terraform output alb_hostname
```

---

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_URL`: Auth service endpoint
- `STRIPE_SECRET_KEY`: Stripe API key
- `SECRET_KEY`: JWT signing key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Stripe public key

---

## Troubleshooting

### Docker connection error
**Error**: `The system cannot find the file specified`
**Solution**: Ensure Docker Desktop is running

### Port already in use
**Error**: `Address already in use`
**Solution**: 
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Database connection timeout
**Solution**:
```bash
# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Frontend can't reach API
**Fix**: Update `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to `http://localhost:8000`

---

## Monitoring & Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f db
```

---

## Next Steps

1. ✅ Deploy locally with Docker Compose
2. Test user registration and environment provisioning
3. Configure Stripe API keys for billing
4. Set up Supabase for authentication
5. Deploy to AWS using Terraform
6. Configure custom domain
7. Set up SSL certificates
8. Configure monitoring and alerts

---

## Production Checklist

- [ ] Update `SECRET_KEY` to secure random value
- [ ] Change database password from default
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable audit logging
- [ ] Set up CloudWatch monitoring
- [ ] Configure email notifications
- [ ] Test disaster recovery
- [ ] Load testing
- [ ] Security audit

---

## Support

Check these files for more information:
- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [API.md](API.md) - API endpoint documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture

---

**Created**: February 16, 2026  
**Status**: Ready for deployment
