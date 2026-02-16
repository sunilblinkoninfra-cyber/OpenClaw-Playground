# Openclaw Platform - Development Guide

## Project Overview
Full-stack cloud IDE platform with FastAPI backend, Next.js frontend, and Docker/Terraform infrastructure automation.

### Tech Stack
- **Backend**: FastAPI, Python 3.11
- **Frontend**: Next.js 14, React, TypeScript
- **Containerization**: Docker, Docker Compose
- **Infrastructure**: Terraform, AWS (ECS/EKS)
- **Database**: PostgreSQL (via Supabase)
- **Auth**: JWT + Supabase
- **Payments**: Stripe
- **Reverse Proxy**: Nginx/Traefik

## Project Structure
```
workspace/
├── backend/              # FastAPI provisioning engine
├── frontend/            # Next.js web application
├── infrastructure/      # Terraform + Docker configs
├── shared/              # Shared types and utilities
├── docker-compose.yml   # Local development setup
└── README.md
```

## Development Workflow

### Backend Setup
1. Navigate to `backend/` directory
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend Setup
1. Navigate to `frontend/` directory
2. Install dependencies: `npm install`
3. Run development server: `npm run dev`
4. Open http://localhost:3000

### Docker Compose (All Services)
```bash
docker-compose up
```

## Key Services

### Auth Service
- JWT token generation
- Supabase integration
- OAuth support (optional)

### Provisioning Engine
- Docker container orchestration
- Automatic domain assignment
- Trial enforcement
- Cleanup on expiry

### Trial Logic
- 24-hour trial creation at signup
- Automatic expiry and cleanup
- Subscription renewal flow

### Billing Integration
- Stripe webhook handling
- Plan management
- Subscription validation

## Environment Variables
Create `.env` files in backend and frontend directories:

**Backend (.env)**
```
SUPABASE_URL=
SUPABASE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
DOCKER_REGISTRY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
REDIS_URL=redis://localhost:6379
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

## API Endpoints

### Auth
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Provisioning
- `POST /api/provision/start` - Start environment
- `GET /api/provision/status/{user_id}` - Check status
- `POST /api/provision/stop` - Stop environment

### Billing
- `POST /api/billing/subscribe` - Create subscription
- `GET /api/billing/plans` - List plans
- `POST /api/billing/webhook` - Stripe webhook

## Deployment

### Docker Build
```bash
docker build -f infrastructure/docker/backend.Dockerfile -t openclaw-backend:latest .
docker build -f infrastructure/docker/frontend.Dockerfile -t openclaw-frontend:latest .
```

### Terraform Deploy
```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

## Quick Troubleshooting
- Port 8000 in use: `lsof -i :8000` (macOS/Linux)
- Clear Docker: `docker system prune`
- Reset database: Delete local Supabase data

## Contributing
- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- All PRs require passing tests

---
Last Updated: Feb 16, 2026
