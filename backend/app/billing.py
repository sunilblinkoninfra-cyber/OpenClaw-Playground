import stripe
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.database import Subscription, Plan, User

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


async def get_available_plans(db: Session) -> list[dict]:
    """Retrieve available pricing plans."""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return [
        {
            "id": plan.id,
            "name": plan.name,
            "price": plan.price / 100,  # Convert from cents
            "currency": plan.currency,
            "interval": plan.interval,
            "features": plan.features,
            "stripe_price_id": plan.stripe_price_id
        }
        for plan in plans
    ]


async def create_subscription(
    user: User,
    plan_id: str,
    payment_method_id: str,
    db: Session
) -> Optional[Subscription]:
    """
    Create a new subscription for a user.
    """
    try:
        # Get plan details
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            logger.error(f"Plan not found: {plan_id}")
            return None
        
        # Create Stripe customer (if not exists)
        stripe_customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            payment_method=payment_method_id,
            invoice_settings={"default_payment_method": payment_method_id}
        )
        
        # Create Stripe subscription
        stripe_subscription = stripe.Subscription.create(
            customer=stripe_customer.id,
            items=[{"price": plan.stripe_price_id}],
            payment_settings={
                "payment_method_types": ["card"],
                "save_default_payment_method": "on_subscription"
            }
        )
        
        # Create database subscription record
        subscription = Subscription(
            user_id=user.id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_subscription.id,
            status="active",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(
                days=30 if plan.interval == "month" else 365
            )
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Subscription created: {subscription.id}")
        return subscription
        
    except stripe.error.CardError as e:
        logger.error(f"Card error: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        return None


async def handle_webhook_event(event: dict, db: Session) -> bool:
    """
    Handle Stripe webhook events.
    """
    event_type = event.get("type")
    
    if event_type == "customer.subscription.updated":
        subscription_data = event.get("data", {}).get("object", {})
        return await _handle_subscription_updated(subscription_data, db)
    
    elif event_type == "customer.subscription.deleted":
        subscription_data = event.get("data", {}).get("object", {})
        return await _handle_subscription_deleted(subscription_data, db)
    
    elif event_type == "invoice.payment_succeeded":
        return True  # Just log for now
    
    else:
        logger.info(f"Unhandled webhook event: {event_type}")
        return True


async def _handle_subscription_updated(subscription_data: dict, db: Session) -> bool:
    """Handle subscription update webhook."""
    try:
        stripe_sub_id = subscription_data.get("id")
        status = subscription_data.get("status")
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()
        
        if subscription:
            subscription.status = status
            
            # Update period dates if available
            if subscription_data.get("current_period_start"):
                subscription.current_period_start = datetime.fromtimestamp(
                    subscription_data["current_period_start"]
                )
            if subscription_data.get("current_period_end"):
                subscription.current_period_end = datetime.fromtimestamp(
                    subscription_data["current_period_end"]
                )
            
            db.commit()
            logger.info(f"Subscription updated: {stripe_sub_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to handle subscription update: {str(e)}")
        return False


async def _handle_subscription_deleted(subscription_data: dict, db: Session) -> bool:
    """Handle subscription cancellation webhook."""
    try:
        stripe_sub_id = subscription_data.get("id")
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()
        
        if subscription:
            subscription.status = "canceled"
            db.commit()
            logger.info(f"Subscription canceled: {stripe_sub_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to handle subscription deletion: {str(e)}")
        return False
