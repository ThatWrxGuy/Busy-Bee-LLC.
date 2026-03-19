# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""SaaS Tenant Context Middleware with JWT and External Auth.

This middleware enforces tenant scoping and validates JWT/Auth tokens.
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
from infrastructure.auth.provider_adapter import (
    AuthError,
    TokenInvalidError,
    TokenExpiredError as AuthTokenExpiredError,
    get_auth_provider,
)


class UnauthorizedError(Exception):
    """Raised when authentication fails."""
    pass


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject TenantContext into SaaS requests.
    
    Supports both internal JWT and external auth providers (Clerk, Auth0).
    """
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/ready", "/", "/docs", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next):
        # Check if path is public
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing or invalid Authorization header", "code": "UNAUTHORIZED"},
                status_code=401
            )
        
        token = auth_header[7:]  # Remove "Bearer "
        
        # Try external auth provider first (Clerk, Auth0, etc.)
        context = await self._authenticate_external(token)
        
        # If no external provider, try internal JWT
        if context is None:
            context = await self._authenticate_internal(token)
        
        if context is None:
            return JSONResponse(
                {"detail": "Authentication failed", "code": "AUTH_FAILED"},
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
    
    async def _authenticate_external(self, token: str) -> TenantContext | None:
        """Try external auth provider."""
        try:
            provider = get_auth_provider()
            
            # Skip if NoopAuthProvider (dev mode)
            if provider.__class__.__name__ == "NoopAuthProvider":
                return None
            
            user = provider.extract_user_from_token(token)
            
            # Get plan from billing (would integrate with Stripe in production)
            plan_tier = "free"  # Default
            
            return TenantContext.from_jwt_payload(
                type('Payload', (), {
                    'subject': user.user_id,
                    'tenant_id': f"tenant_{user.user_id}",
                    'mode': 'saas',
                    'plan': plan_tier,
                    'permissions': [],
                    'issued_at': 0,
                    'expires_at': 9999999999
                })()
            )
        except (AuthError, TokenInvalidError, AuthTokenExpiredError):
            return None
        except Exception:
            return None
    
    async def _authenticate_internal(self, token: str) -> TenantContext | None:
        """Try internal JWT authentication."""
        try:
            service = get_jwt_service()
            payload = service.verify_token(token)
            
            # Create TenantContext from JWT
            return TenantContext.from_jwt_payload(payload)
        except (JWTError, JWTExpiredError, JWTInvalidSignatureError, JWTMissingClaimError, ValueError):
            return None
    
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
