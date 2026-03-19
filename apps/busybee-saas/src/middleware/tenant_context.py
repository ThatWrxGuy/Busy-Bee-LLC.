# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""SaaS Tenant Context Middleware with JWT enforcement.

This middleware enforces tenant scoping and validates JWT tokens.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from busybee_contracts.tenant_context import TenantContext
from infrastructure.auth.jwt_service import (
    JWTError,
    JWTExpiredError,
    JWTInvalidSignatureError,
    JWTMissingClaimError,
    get_jwt_service,
)


class UnauthorizedError(Exception):
    """Raised when authentication fails."""
    pass


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject TenantContext into SaaS requests.
    
    Validates JWT token and enforces tenant scope.
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/ready", "/", "/docs", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next):
        # Check if path is public
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Extract JWT from Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header", "code": "UNAUTHORIZED"},
                status_code=401
            )
        
        token = auth_header[7:]  # Remove "Bearer "
        
        # Verify JWT
        try:
            service = get_jwt_service()
            payload = service.verify_token(token)
        except JWTExpiredError:
            return JSONResponse(
                {"detail": "Token has expired", "code": "TOKEN_EXPIRED"},
                status_code=401
            )
        except JWTInvalidSignatureError:
            return JSONResponse(
                {"detail": "Invalid token signature", "code": "INVALID_TOKEN"},
                status_code=401
            )
        except JWTMissingClaimError as e:
            return JSONResponse(
                {"detail": str(e), "code": "MISSING_CLAIM"},
                status_code=401
            )
        except JWTError as e:
            return JSONResponse(
                {"detail": f"Token validation failed: {e}", "code": "TOKEN_INVALID"},
                status_code=401
            )
        
        # Create TenantContext from JWT
        try:
            context = TenantContext.from_jwt_payload(payload)
        except ValueError as e:
            return JSONResponse(
                {"detail": str(e), "code": "INVALID_CONTEXT"},
                status_code=401
            )
        
        # Validate required scope for SaaS
        try:
            context.require_scope()
        except ValueError as e:
            return JSONResponse(
                {"detail": str(e), "code": "TENANT_SCOPE_REQUIRED"},
                status_code=401
            )
        
        # Attach to request state
        request.state.tenant_context = context
        
        # Process request
        response = await call_next(request)
        
        # Add tenant header to response for debugging
        if context.tenant_id:
            response.headers["X-Tenant-Id"] = context.tenant_id
        
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
