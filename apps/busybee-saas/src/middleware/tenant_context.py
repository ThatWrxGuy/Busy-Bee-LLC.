# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""SaaS Tenant Context Middleware.

This middleware enforces tenant scoping for all SaaS requests.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from busybee_contracts.tenant_context import TenantContext


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject TenantContext into SaaS requests.
    
    Currently uses header-based resolution (bootstrap path).
    Later, replace with signed auth claims.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant/user from headers (bootstrap path)
        tenant_id = request.headers.get("X-Tenant-Id")
        user_id = request.headers.get("X-User-Id")
        
        # Also check query params for flexibility
        if not tenant_id:
            tenant_id = request.query_params.get("tenant_id")
        if not user_id:
            user_id = request.query_params.get("user_id")
        
        # Check for authorization header (future: JWT)
        auth_header = request.headers.get("Authorization")
        
        # Create context
        context = TenantContext(
            tenant_id=tenant_id,
            user_id=user_id,
            mode="saas",
            permissions=frozenset(),  # Resolved from auth in production
            plan_tier=self._resolve_plan_tier(request),
            metadata={
                "auth_type": "bearer" if auth_header else "header",
                "path": request.url.path,
            }
        )
        
        # Validate required scope
        if request.url.path not in ["/health", "/ready", "/"]:
            try:
                context.require_tenant()
                context.require_user()
            except ValueError as exc:
                return JSONResponse(
                    {"detail": str(exc), "code": "TENANT_SCOPE_REQUIRED"},
                    status_code=401
                )
        
        # Attach to request state
        request.state.tenant_context = context
        
        # Process request
        response = await call_next(request)
        
        # Add tenant header to response for debugging
        if tenant_id:
            response.headers["X-Tenant-Id"] = tenant_id
        
        return response
    
    def _resolve_plan_tier(self, request: Request) -> str:
        """Resolve plan tier from headers or default."""
        return request.headers.get("X-Plan-Tier", "free")


class TenantContextDependency:
    """FastAPI dependency for extracting TenantContext."""
    
    @staticmethod
    def get(request: Request) -> TenantContext:
        """Get TenantContext from request state."""
        if not hasattr(request.state, "tenant_context"):
            # Return default if not set (e.g., health checks)
            return TenantContext(
                tenant_id=None,
                user_id=None,
                mode="saas",
            )
        return request.state.tenant_context
