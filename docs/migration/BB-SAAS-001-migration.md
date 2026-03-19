# BB-SAAS-001 Migration Guide

## Multi-Tenant SaaS Foundation Migration

This document outlines the migration path for implementing multi-tenant capabilities in Busy Bee.

---

## Overview

BB-SAAS-001 transforms Busy Bee from a single-context intelligence engine into a multi-tenant SaaS Life Operating System.

### Key Changes

1. **Tenant Isolation** - All data now scoped by tenant_id
2. **Role-Based Access Control** - Granular permissions per user
3. **Connector Framework** - Domain-specific API integrations
4. **Governance & Approvals** - Human-in-the-loop for financial actions
5. **Executive Dashboard** - Unified control plane

---

## Migration Steps

### Phase 1: Database Schema Updates

Add tenant_id to all existing tables:

```sql
-- Users table
ALTER TABLE users ADD COLUMN tenant_id VARCHAR(255);
ALTER TABLE users ADD COLUMN workspace_id VARCHAR(255);
ALTER TABLE users ADD COLUMN roles JSON;

-- Agents table
ALTER TABLE agents ADD COLUMN tenant_id VARCHAR(255);

-- Data tables
ALTER TABLE data ADD COLUMN tenant_id VARCHAR(255);
ALTER TABLE data ADD COLUMN workspace_id VARCHAR(255);
```

### Phase 2: Environment Variables

Add the following environment variables:

```bash
# Authentication
AUTH_PROVIDER=clerk|auth0|supabase|internal
CLERK_PUBLISHABLE_KEY=xxx
CLERK_SECRET_KEY=xxx
AUTH0_DOMAIN=xxx
AUTH0_CLIENT_ID=xxx
AUTH0_CLIENT_SECRET=xxx

# Credential Vault
CREDENTIAL_VAULT_KEY=your-secure-32-byte-key
CREDENTIAL_VAULT_SALT=your-16-byte-salt

# Multi-tenancy
DEFAULT_TENANT_ISOLATION=true
ENFORCE_WORKSPACE_ISOLATION=true
```

### Phase 3: API Updates

Update all API endpoints to:

1. Require Authorization header
2. Extract TenantContext from JWT
3. Scope all queries by tenant_id
4. Return tenant-scoped responses

### Phase 4: Frontend Integration

Update Base44 frontend to:

1. Implement login/signup flows
2. Store JWT in secure storage
3. Include JWT in all API requests
4. Handle tenant context in state

---

## Breaking Changes

### TenantContext Changes

The `TenantContext` dataclass now includes:

- `workspace_id: str | None` - Workspace within tenant
- `roles: FrozenSet[str]` - User roles
- `permissions: FrozenSet[str]` - Computed permissions from roles

### Data Path Changes

All data storage now requires tenant scoping:

```python
# Old (single-tenant)
path = "/data/agents"

# New (multi-tenant)
path = context.get_data_path("agents")
# Returns: /tenants/{tenant_id}/workspaces/{workspace_id}/agents
```

### Permission Changes

New permission system requires role assignment:

```python
# Old - implicit permissions
if user.is_admin: ...

# New - explicit permissions  
if context.has_permission(Permissions.TENANT_ADMIN): ...
```

---

## Rollback Plan

If issues occur:

1. **Database**: Run migration rollback scripts
2. **Environment**: Set `AUTH_PROVIDER=internal` for fallback
3. **Code**: Feature flags for gradual rollout

---

## Testing

Run tenant isolation tests:

```bash
pytest tests/multi_tenant/test_tenant_isolation.py -v
```

Verify:
- No cross-tenant data access
- Permission enforcement
- Credential isolation
- Audit log completeness

---

## Deployment Checklist

- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Auth provider credentials set
- [ ] Credential vault keys generated
- [ ] Tenant isolation tests passing
- [ ] API version updated to v2
- [ ] Frontend integrated
- [ ] Monitoring alerts configured
