# API Documentation

## Authentication Endpoints

### Sign Up
```
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}

Response (201):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-02-16T10:00:00",
    "trial_start": "2024-02-16T10:00:00",
    "trial_end": "2024-02-17T10:00:00",
    "has_active_subscription": false
  }
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": { ... }
}
```

### Get Current User
```
GET /api/auth/me
Authorization: Bearer <access_token>

Response (200):
{
  "id": "user-id",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-02-16T10:00:00",
  "trial_start": "2024-02-16T10:00:00",
  "trial_end": "2024-02-17T10:00:00",
  "has_active_subscription": false
}
```

---

## Provisioning Endpoints

### Start Environment
```
POST /api/provision/start
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "user-id",
  "environment_type": "openclaw",
  "custom_env": {}
}

Response (200):
{
  "user_id": "user-id",
  "status": {
    "status": "running",
    "container_id": "container-id",
    "subdomain": "user-abc123",
    "url": "https://user-abc123.openclaw.ai",
    "created_at": "2024-02-16T10:05:00",
    "error_message": null
  },
  "trial_end": "2024-02-17T10:00:00"
}
```

### Check Environment Status
```
GET /api/provision/status/{user_id}
Authorization: Bearer <access_token>

Response (200):
{
  "user_id": "user-id",
  "status": { ... }
}
```

### Stop Environment
```
POST /api/provision/stop
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "user-id"
}

Response (200):
{
  "success": true
}
```

---

## Billing Endpoints

### Get Available Plans
```
GET /api/billing/plans

Response (200):
[
  {
    "id": "plan-starter",
    "name": "Starter",
    "price": 39.0,
    "currency": "usd",
    "interval": "month",
    "features": [
      "1 concurrent environment",
      "2 GB RAM",
      "1 vCPU",
      "Community support"
    ],
    "stripe_price_id": "price_xxx"
  },
  {
    "id": "plan-pro",
    "name": "Professional",
    "price": 59.0,
    "currency": "usd",
    "interval": "month",
    "features": [
      "3 concurrent environments",
      "4 GB RAM",
      "2 vCPU",
      "Email support"
    ],
    "stripe_price_id": "price_yyy"
  }
]
```

### Create Subscription
```
POST /api/billing/subscribe
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan_id": "plan-pro",
  "payment_method_id": "pm_card_xxx"
}

Response (200):
{
  "id": "sub-id",
  "user_id": "user-id",
  "plan_id": "plan-pro",
  "status": "active",
  "current_period_end": "2024-03-16T10:00:00",
  "stripe_subscription_id": "sub_xxx"
}
```

### Stripe Webhook
```
POST /api/billing/webhook
X-Stripe-Signature: <signature>
Content-Type: application/json

{ ...webhook payload... }

Response (200):
{
  "received": true
}
```

---

## Error Responses

All errors follow this format:

```
{
  "detail": "Error message here"
}
```

### Common Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

---

## Rate Limiting

API Rate Limits:
- Auth endpoints: 10 requests/second
- API endpoints: 10 requests/second  
- General endpoints: 100 requests/minute

Headers returned with each response:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## Authentication

All authenticated endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens expire based on `JWT_EXPIRATION_HOURS` setting (default: 24 hours).

To refresh, login again to get a new token.

---

## Webhooks

### Stripe Events Handled

- `customer.subscription.updated` - Subscription status changed
- `customer.subscription.deleted` - Subscription canceled
- `invoice.payment_succeeded` - Payment completed

Webhook signature verification is performed on the backend.

---

**API Version:** 0.1.0  
**Last Updated:** February 16, 2026
