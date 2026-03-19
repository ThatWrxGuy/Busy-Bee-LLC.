# Environment Setup Guide

## BB-SAAS-001 Multi-Tenant SaaS Environment Setup

This guide covers setting up the environment for running Busy Bee as a multi-tenant SaaS platform.

---

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+
- Node.js 18+ (for frontend)

---

## Environment Variables

### Core Configuration

```bash
# Application
APP_NAME=busy-bee
APP_ENV=production
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/busybee
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secure-jwt-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

### Authentication Providers

#### Clerk
```bash
AUTH_PROVIDER=clerk
CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
CLERK_WEBHOOK_SECRET=whsec_xxx
```

#### Auth0
```bash
AUTH_PROVIDER=auth0
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=xxx
AUTH0_CLIENT_SECRET=xxx
AUTH0_AUDIENCE=https://api.busybee.com
```

#### Supabase
```bash
AUTH_PROVIDER=supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
```

### Credential Vault

```bash
CREDENTIAL_VAULT_KEY=your-32-byte-base64-encoded-key
CREDENTIAL_VAULT_SALT=your-16-byte-salt
```

Generate secure keys:
```bash
# Generate vault key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate salt  
python -c "import os; print(os.urandom(16).hex())"
```

### Multi-Tenancy

```bash
# Enable tenant isolation (required for SaaS)
DEFAULT_TENANT_ISOLATION=true
ENFORCE_WORKSPACE_ISOLATION=true

# Tenant limits
MAX_WORKSPACES_PER_TENANT=10
MAX_USERS_PER_TENANT=100
```

### Domain Connectors

#### Plaid
```bash
PLAID_CLIENT_ID=xxx
PLAID_SECRET=xxx
PLAID_ENV=sandbox|development|production
```

#### Alpaca
```bash
ALPACA_API_KEY=xxx
ALPACA_SECRET_KEY=xxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

#### Google
```bash
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=https://api.busybee.com/auth/google/callback
```

---

## Database Setup

### Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or with Docker
docker-compose exec api alembic upgrade head
```

### Seed Initial Data

```bash
# Create default roles and permissions
python -m scripts.seed_permissions
```

---

## Running the Application

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-api.txt

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.api.main:app --reload --port 8000
```

### Docker Production

```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## Frontend Integration (Base44)

### Environment Variables

```bash
# API
NEXT_PUBLIC_API_URL=https://api.busybee.com
NEXT_PUBLIC_WS_URL=wss://api.busybee.com/ws

# Auth
NEXT_PUBLIC_AUTH_PROVIDER=clerk
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxx
```

### API Integration

```typescript
// Example: Fetching dashboard data
const response = await fetch('/api/dashboard', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
```

---

## Testing

### Run Tenant Isolation Tests

```bash
pytest tests/multi_tenant/ -v
```

### Run All Tests

```bash
pytest tests/ -v --cov=src
```

---

## Monitoring

### Health Check

```bash
curl https://api.busybee.com/health
```

### Metrics

Metrics are exposed at `/metrics` in Prometheus format.

---

## Troubleshooting

### Authentication Issues

1. Verify JWT_SECRET_KEY is set
2. Check token expiration
3. Validate AUTH_PROVIDER configuration

### Tenant Isolation Issues

1. Ensure DEFAULT_TENANT_ISOLATION=true
2. Check TenantContext is passed to all operations
3. Verify database queries include tenant_id filter

### Connector Issues

1. Verify credential vault keys are set
2. Check connector health at `/api/connectors/status`
3. Review logs for authentication errors
