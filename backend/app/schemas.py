from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ============================================================================
# Auth Models
# ============================================================================

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    has_active_subscription: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Provisioning Models
# ============================================================================

class ProvisioningRequest(BaseModel):
    user_id: str
    environment_type: str = "openclaw"
    custom_env: Optional[dict] = None


class ContainerStatus(BaseModel):
    status: str  # "provisioning", "running", "stopped", "error"
    container_id: Optional[str]
    subdomain: Optional[str]
    url: Optional[str]
    created_at: Optional[datetime]
    error_message: Optional[str]


class ProvisioningResponse(BaseModel):
    user_id: str
    status: ContainerStatus
    trial_end: Optional[datetime]


# ============================================================================
# Billing Models
# ============================================================================

class PlanResponse(BaseModel):
    id: str
    name: str
    price: float
    currency: str
    interval: str  # "month", "year"
    features: list[str]
    stripe_price_id: str


class SubscriptionRequest(BaseModel):
    plan_id: str
    payment_method_id: str


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: str  # "active", "past_due", "canceled"
    current_period_end: datetime
    stripe_subscription_id: str


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
