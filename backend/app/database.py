from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

from app.config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# Models
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    containers = relationship("Container", back_populates="user")
    subscription = relationship("Subscription", uselist=False, back_populates="user")
    
    def is_trial_active(self) -> bool:
        if not self.trial_end:
            return False
        return datetime.utcnow() < self.trial_end
    
    def has_paid_access(self) -> bool:
        if not self.subscription:
            return False
        return self.subscription.is_active()


class Container(Base):
    __tablename__ = "containers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    container_id = Column(String, nullable=True, unique=True)
    status = Column(String, default="pending")  # pending, running, stopped, error
    subdomain = Column(String, unique=True, nullable=True)
    url = Column(String, nullable=True)
    environment_type = Column(String, default="openclaw")
    custom_env = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="containers")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    plan_id = Column(String, nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=False)
    status = Column(String, default="active")  # active, past_due, canceled
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    
    def is_active(self) -> bool:
        return self.status == "active" and datetime.utcnow() < self.current_period_end


class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # in cents
    currency = Column(String, default="usd")
    interval = Column(String, default="month")  # month, year
    features = Column(JSON, nullable=False)
    stripe_price_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
