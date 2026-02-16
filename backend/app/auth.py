from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import User
from app.schemas import UserResponse, TokenResponse

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.InvalidTokenError:
        return None


def start_user_trial(user: User, db: Session) -> User:
    """Initialize a 24-hour trial for a new user."""
    user.trial_start = datetime.utcnow()
    user.trial_end = datetime.utcnow() + timedelta(hours=settings.TRIAL_DURATION_HOURS)
    db.commit()
    db.refresh(user)
    return user


def user_to_response(user: User) -> UserResponse:
    """Convert User ORM object to response schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at,
        trial_start=user.trial_start,
        trial_end=user.trial_end,
        has_active_subscription=user.has_paid_access()
    )


def create_token_response(user: User) -> TokenResponse:
    """Create a complete token response with user info."""
    token = create_jwt_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token,
        user=user_to_response(user)
    )
