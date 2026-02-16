from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.config import settings
from app.database import init_db, get_db, User
from app.schemas import (
    UserSignupRequest, UserLoginRequest, TokenResponse, UserResponse,
    ProvisioningRequest, ProvisioningResponse,
    PlanResponse, SubscriptionRequest, SubscriptionResponse,
    HealthResponse
)
from app.auth import (
    hash_password, verify_password, create_token_response, 
    start_user_trial, user_to_response, decode_jwt_token
)
from app.provisioning import provision_user_environment, stop_user_environment
from app.billing import get_available_plans, create_subscription, handle_webhook_event

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.utcnow()
    )


# ============================================================================
# Auth Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/auth/signup", response_model=TokenResponse)
async def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """Register a new user and start their 24-hour trial."""
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    try:
        # Create user
        user = User(
            email=request.email,
            name=request.name,
            password_hash=hash_password(request.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Start trial
        user = start_user_trial(user, db)
        
        logger.info(f"New user registered: {user.email}")
        
        return create_token_response(user)
    
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post(f"{settings.API_PREFIX}/auth/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return create_token_response(user)


@app.get(f"{settings.API_PREFIX}/auth/me", response_model=UserResponse)
async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_to_response(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# Provisioning Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/provision/start", response_model=ProvisioningResponse)
async def start_provisioning(
    request: ProvisioningRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Start a new environment for the user."""
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_jwt_token(token)
        
        if not payload or payload.get("sub") != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        user = db.query(User).filter(User.id == request.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check trial/subscription
        if not (user.is_trial_active() or user.has_paid_access()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trial expired. Please upgrade to continue."
            )
        
        return await provision_user_environment(request.user_id, db)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provisioning error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Provisioning failed"
        )


@app.get(f"{settings.API_PREFIX}/provision/status/{{user_id}}", response_model=ProvisioningResponse)
async def get_provisioning_status(
    user_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get the status of a user's environment."""
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_jwt_token(token)
        
        if not payload or payload.get("sub") != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        return await provision_user_environment(user_id, db)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status check failed"
        )


@app.post(f"{settings.API_PREFIX}/provision/stop")
async def stop_provisioning(
    request: ProvisioningRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Stop a user's environment."""
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_jwt_token(token)
        
        if not payload or payload.get("sub") != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        success = await stop_user_environment(request.user_id, db)
        
        return {"success": success}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop environment"
        )


# ============================================================================
# Billing Endpoints
# ============================================================================

@app.get(f"{settings.API_PREFIX}/billing/plans", response_model=list[dict])
async def list_plans(db: Session = Depends(get_db)):
    """Get available pricing plans."""
    return await get_available_plans(db)


@app.post(f"{settings.API_PREFIX}/billing/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    request: SubscriptionRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Create a subscription for the user."""
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription = await create_subscription(
            user, 
            request.plan_id, 
            request.payment_method_id, 
            db
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription"
            )
        
        return SubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            current_period_end=subscription.current_period_end,
            stripe_subscription_id=subscription.stripe_subscription_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription creation failed"
        )


@app.post(f"{settings.API_PREFIX}/billing/webhook")
async def stripe_webhook(
    request: dict,
    x_stripe_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events."""
    
    try:
        # In production, verify the signature
        # signature = request.headers.get('x-stripe-signature')
        # stripe.Webhook.construct_event(
        #     body, signature, settings.STRIPE_WEBHOOK_SECRET
        # )
        
        success = await handle_webhook_event(request, db)
        return {"received": success}
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
