# Openclaw Platform

![CI](https://github.com/sunilblinkoninfra-cyber/OpenClaw-Playground/actions/workflows/ci.yml/badge.svg)

**Zero Installation Friction Cloud IDE with AI Agent Integration**

A SaaS platform providing instant, isolated, cloud-based development environments with integrated AI capabilities. Users get a fully configured environment in seconds—no setup required.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Local Development

```bash
# Clone and navigate
cd workspace

# Start all services
docker-compose up

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Database: localhost:5432
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📋 Features

### MVP (Month 1-3)
- ✅ User authentication (Supabase/Firebase)
- ✅ 24-hour trial enforcement
- ✅ Per-user Docker container provisioning
- ✅ Automatic subdomain assignment
- ✅ Stripe billing integration
- ✅ Trial expiry cleanup
- ✅ Basic web dashboard
- ✅ Mobile wrapper (WebView)

### Future Enhancements
- Team collaboration
- Workspace templates
- Snapshot & resume
- API access tier
- White-label enterprise
- Multi-region deployment

## 🏗️ Architecture

### Core Components

**1. Auth Service**
- JWT-based authentication
- Supabase integration
- OAuth support (optional)
- User trial metadata storage

**2. Provisioning Engine** (FastAPI)
- Receives provisioning requests
- Manages Docker containers (ECS/EKS)
- Assigns subdomains
- Attaches persistent volumes
- Schedules cleanup jobs

**3. Container Template**
- Ubuntu 22.04 base
- Openclaw pre-installed
- Dependencies pre-configured
- Exposed on port 8080

**4. Domain Routing** (Nginx/Traefik)
- Each user gets `[username].yourapp.ai`
- Wildcard SSL via Let's Encrypt
- Reverse proxy to container

**5. Trial Management**
- 24-hour window per user
- Automatic container suspension
- Cron job cleanup
- User notification on expiry

**6. Billing** (Stripe)
- Subscription plan management
- Webhook-based activation
- Multi-tier pricing
- Invoice generation

## 💰 Pricing & Cost Model

### Infrastructure Costs (per user/month)
- 1 vCPU: ~$10–15
- 2GB RAM: ~$8
- Storage: ~$2
- **Total base**: ~$20–25/month

### Recommended Pricing
- Starter: $39/month
- Professional: $59/month
- Enterprise: Custom

## 🔒 Security

- Container isolation (non-root users)
- CPU & memory limits
- Network isolation
- Rate limiting per user
- No public port exposure
- Outbound request controls
- Firewall rules
- Anomaly detection logging
- Phone verification for trials
- Credit card required for trials

## 📊 Scaling Strategy

### Phase 1 (0–500 users)
- Single EC2 instance
- Docker containers
- Manual scaling

### Phase 2 (500–5000 users)
- Kubernetes (EKS)
- Auto-scaling groups
- Redis queue

### Phase 3 (Enterprise)
- Dedicated clusters
- Multi-region
- Custom SLAs

## 📁 Project Structure

```
workspace/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Configuration
│   │   ├── auth/                # Auth service
│   │   ├── provisioning/        # Container orchestration
│   │   ├── billing/             # Stripe integration
│   │   └── models/              # Database models
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home page
│   │   ├── login/               # Auth pages
│   │   ├── dashboard/           # User dashboard
│   │   └── api/                 # API client
│   ├── components/              # Reusable components
│   ├── package.json
│   └── .env.example
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf              # AWS resources
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── docker/
│       ├── backend.Dockerfile
│       ├── frontend.Dockerfile
│       ├── openclaw.Dockerfile  # User env template
│       └── nginx.conf
│
├── shared/
│   └── types.ts                 # Shared TypeScript types
│
├── docker-compose.yml           # Local development
└── README.md
```

## 🔄 Development Workflow

### Creating a Feature
1. Create feature branch: `git checkout -b feature/description`
2. Make changes in respective backend/frontend directories
3. Test locally with Docker Compose
4. Commit and push
5. Open PR with description

### Testing
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 📚 API Documentation

Detailed API docs available at: `http://localhost:8000/docs` (Swagger UI)

### Key Endpoints

**Authentication**
- `POST /api/auth/signup` - Create account & start trial
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Current user info

**Provisioning**
- `POST /api/provision/start` - Launch user environment
- `GET /api/provision/status/{user_id}` - Check environment status
- `POST /api/provision/stop` - Stop environment

**Billing**
- `POST /api/billing/subscribe` - Upgrade to paid plan
- `GET /api/billing/plans` - Available plans
- `POST /api/billing/webhook` - Stripe events

## ⚙️ Environment Setup

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_WEBHOOK_SECRET=your_webhook_secret
DOCKER_REGISTRY=your_registry_url
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_pub_key
```

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Linux/macOS
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Docker issues:**
```bash
docker system prune
docker volume prune
```

**Database reset:**
```bash
docker-compose down -v
docker-compose up
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Ensure Docker Compose passes
5. Open pull request

## 📄 License

Proprietary - All rights reserved

---

**Last Updated:** February 16, 2026  
**Status:** MVP Development  
**Team:** Openclaw Platform
