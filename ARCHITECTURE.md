# Project Structure Reference

```
workspace/
│
├── backend/                        # FastAPI provisioning engine
│   ├── app/
│   │   ├── main.py                 # FastAPI app & routes
│   │   ├── config.py               # Configuration settings
│   │   ├── schemas.py              # Request/response models
│   │   ├── database.py             # SQLAlchemy models & session
│   │   ├── auth.py                 # Authentication logic
│   │   ├── provisioning.py         # Container orchestration
│   │   ├── billing.py              # Stripe integration
│   │   └── __init__.py
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment template
│
├── frontend/                       # Next.js web application
│   ├── app/
│   │   ├── page.tsx                # Landing page
│   │   ├── layout.tsx              # Root layout
│   │   ├── globals.css             # Global styles
│   │   ├── login/page.tsx          # Login page
│   │   ├── signup/page.tsx         # Signup page
│   │   └── dashboard/page.tsx      # User dashboard
│   ├── components/
│   │   └── ui.tsx                  # Reusable UI components
│   ├── lib/
│   │   ├── api.ts                  # API client
│   │   └── store.ts                # Zustand state management
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── infrastructure/
│   ├── docker/
│   │   ├── backend.Dockerfile      # Backend container image
│   │   ├── frontend.Dockerfile     # Frontend container image
│   │   ├── openclaw.Dockerfile     # User environment template
│   │   └── nginx.conf              # Nginx reverse proxy config
│   │
│   └── terraform/
│       ├── main.tf                 # AWS infrastructure definition
│       ├── variables.tf            # Variable definitions
│       └── outputs.tf              # Output values
│
├── shared/
│   └── types.ts                    # Shared TypeScript types
│
├── .github/
│   └── copilot-instructions.md     # Development instructions
│
├── .env.example                    # Global environment template
├── .gitignore                      # Git ignore rules
├── docker-compose.yml              # Local development setup
├── README.md                       # Project overview
├── SETUP_GUIDE.md                  # Detailed setup instructions
├── API.md                          # API documentation
└── ARCHITECTURE.md                 # This file
```

## Core Components

### 1. Authentication Service
- **File**: `backend/app/auth.py`
- **Purpose**: User registration, login, JWT token generation
- **Key Functions**:
  - `hash_password()` — Secure password hashing
  - `create_jwt_token()` — Generate JWT tokens
  - `start_user_trial()` — Initialize 24-hour trial
  - `create_token_response()` — Return user + token

### 2. Provisioning Engine
- **File**: `backend/app/provisioning.py`
- **Purpose**: Docker container management and lifecycle
- **Key Components**:
  - `DockerOrchestrator` — Manages Docker API
  - `provision_user_environment()` — Async provisioning workflow
  - `stop_user_environment()` — Container cleanup
- **Features**:
  - Automatic subdomain assignment
  - Resource limiting (CPU/memory)
  - Error handling and failed state tracking

### 3. Billing Integration
- **File**: `backend/app/billing.py`
- **Purpose**: Stripe subscription management
- **Key Functions**:
  - `create_subscription()` — Create new subscription
  - `handle_webhook_event()` — Process Stripe webhooks
  - `get_available_plans()` — List pricing plans
- **Webhook Events Handled**:
  - Subscription updates
  - Subscription cancellation
  - Payment success

### 4. Database Layer
- **File**: `backend/app/database.py`
- **Purpose**: SQLAlchemy ORM models and session management
- **Models**:
  - `User` — User accounts with trial tracking
  - `Container` — Provisioned environments
  - `Subscription` — Active subscriptions
  - `Plan` — Pricing tiers

### 5. Frontend API Client
- **File**: `frontend/lib/api.ts`
- **Purpose**: Type-safe API communication
- **Methods**: Auth, provisioning, billing
- **Features**:
  - Automatic token management
  - Error handling
  - LocalStorage persistence

### 6. State Management
- **File**: `frontend/lib/store.ts`
- **Purpose**: Zustand stores for auth and provisioning state
- **Stores**:
  - `useAuthStore` — User auth state
  - `useProvisioningStore` — Environment status

## Data Flow

### User Registration Flow
```
1. User fills signup form
2. Frontend calls POST /api/auth/signup
3. Backend creates User in database
4. Trial start/end dates set (24 hours)
5. JWT token generated and returned
6. Frontend stores token in localStorage
7. User redirected to dashboard
```

### Environment Provisioning Flow
```
1. User clicks "Launch Environment"
2. Frontend calls POST /api/provision/start
3. Backend checks trial/subscription status
4. DockerOrchestrator creates container
5. Assigns subdomain and persistent volume
6. Container starts and exposed via Nginx
7. Response sent with URL and status
8. Frontend polls status endpoint for updates
```

### Subscription Flow
```
1. User selects plan and enters card details
2. Frontend calls POST /api/billing/subscribe
3. Backend creates Stripe customer
4. Stripe subscription created
5. Subscription saved to database
6. Trial end date extended by subscription duration
7. User gains access to paid resources
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP,
  trial_start TIMESTAMP,
  trial_end TIMESTAMP,
  is_active BOOLEAN
);
```

### Containers Table
```sql
CREATE TABLE containers (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR FOREIGN KEY,
  container_id VARCHAR UNIQUE,
  status VARCHAR,
  subdomain VARCHAR UNIQUE,
  url VARCHAR,
  environment_type VARCHAR,
  custom_env JSON,
  created_at TIMESTAMP,
  started_at TIMESTAMP,
  stopped_at TIMESTAMP,
  error_message VARCHAR
);
```

### Subscriptions Table
```sql
CREATE TABLE subscriptions (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR UNIQUE FOREIGN KEY,
  plan_id VARCHAR,
  stripe_subscription_id VARCHAR UNIQUE,
  status VARCHAR,
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

## API Architecture

### Request Flow
```
User Browser
    ↓
Next.js Frontend (3000)
    ↓ (HTTP requests)
Nginx Reverse Proxy (80/443)
    ↓
FastAPI Backend (8000)
    ↓
    ├→ PostgreSQL (5432)
    ├→ Redis (6379)
    ├→ Docker Daemon
    └→ Stripe API
```

### Authentication
- JWT tokens in `Authorization: Bearer <token>` header
- Token expiry: 24 hours (configurable)
- Refresh by logging in again
- Stored in browser localStorage

### Rate Limiting
- API routes: 10 req/sec
- General routes: 100 req/min
- Per IP address
- Enforced by Nginx

### CORS
- Configured in FastAPI middleware
- Update `allow_origins` for production

## Infrastructure (AWS)

### Compute
- **ECS Cluster**: Container orchestration (Fargate)
- **EC2 Instances**: (Option B - more expensive)
- **Load Balancer**: Application Load Balancer (ALB)

### Networking
- **VPC**: Isolated network (10.0.0.0/16)
- **Subnets**: 2 public, 2 private (multi-AZ)
- **Security Groups**: Firewall rules per service
- **Route Tables**: Public and private routing

### Data
- **RDS**: PostgreSQL database (managed)
- **ElastiCache**: Redis for caching
- **S3**: Persistent volumes and backups

### Monitoring
- **CloudWatch**: Logs and metrics
- **CloudWatch Alarms**: Alert on thresholds
- **VPC Flow Logs**: Network traffic analysis

## Security Layers

1. **Container Isolation**
   - Non-root user execution
   - CPU and memory limits
   - Network policies

2. **API Security**
   - JWT authentication
   - Rate limiting
   - Input validation (Pydantic)
   - HTTPS/TLS

3. **Data Protection**
   - Password hashing (bcrypt)
   - Encrypted in transit (HTTPS)
   - Secure cookie settings

4. **Access Control**
   - Trial status enforcement
   - Subscription verification
   - User isolation

## Scaling Strategy

### Phase 1 (MVP: 0-500 users)
- Single EC2 instance with Docker containers
- Manual scaling
- Shared database
- Local image registry

### Phase 2 (Growth: 500-5000 users)
- Kubernetes cluster (EKS)
- Auto-scaling groups
- Redis queue for async tasks
- Private image registry (ECR)
- Multi-AZ deployment

### Phase 3 (Enterprise)
- Multi-region deployment
- Dedicated clusters per region
- Custom SLAs and support
- Advanced monitoring and logging
- DDoS protection

## Cost Estimation

### Infrastructure Per User/Month
- Compute (1 vCPU): $10-15
- Memory (2GB): $8
- Storage: $2
- **Total**: $20-25/month

### Recommended Pricing
- Starter: $39/month (profit margin ~40%)
- Professional: $59/month
- Enterprise: Custom

## Performance Considerations

### Frontend
- Next.js static optimization
- Code splitting
- Image optimization
- Caching headers

### Backend
- Connection pooling
- Database query optimization
- Redis caching for frequently accessed data
- Async I/O for Docker operations

### Database
- Indexes on foreign keys and frequently queried columns
- Query result caching
- Connection pooling
- Read replicas for scaling (Phase 3)

---

**For detailed information, see:**
- [README.md](README.md) — Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) — Getting started
- [API.md](API.md) — Endpoint documentation
