# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Auth Service.

High-level authentication service that coordinates providers.
"""

from __future__ import annotations

from typing import Any

from busybee_contracts.tenant_context import TenantContext, create_personal_context
from infrastructure.auth.provider_adapter import (
    AuthProviderAdapter,
    AuthUser,
    TokenInvalidError,
    TokenExpiredError,
    get_auth_provider,
    set_auth_provider,
)
from infrastructure.auth.jwt_service import JWTService, create_jwt_token


class AuthService:
    """Authentication service coordinating providers.
    
    This service:
    - Verifies tokens from external providers
    - Creates internal TenantContext
    - Issues session tokens
    - Manages tenant mapping
    """
    
    def __init__(
        self,
        provider: AuthProviderAdapter | None = None,
        jwt_service: JWTService | None = None
    ) -> None:
        self.provider = provider or get_auth_provider()
        self.jwt_service = jwt_service or JWTService("auth-secret-key")
    
    def authenticate(self, token: str) -> AuthUser:
        """Authenticate a token and return user.
        
        Args:
            token: JWT token from request
            
        Returns:
            AuthUser from provider
            
        Raises:
            TokenInvalidError: If token is invalid
            TokenExpiredError: If token is expired
        """
        return self.provider.extract_user_from_token(token)
    
    def authenticate_request(
        self,
        authorization_header: str | None
    ) -> AuthUser:
        """Authenticate from Authorization header.
        
        Args:
            authorization_header: Authorization header value (Bearer token)
            
        Returns:
            AuthUser
            
        Raises:
            TokenInvalidError: If token missing or invalid
        """
        if not authorization_header:
            raise TokenInvalidError("Missing Authorization header")
        
        if not authorization_header.startswith("Bearer "):
            raise TokenInvalidError("Invalid Authorization header format")
        
        token = authorization_header[7:]  # Remove "Bearer "
        return self.authenticate(token)
    
    def create_tenant_context(
        self,
        user: AuthUser,
        mode: str = "saas",
        tenant_id: str | None = None,
        plan_tier: str = "free"
    ) -> TenantContext:
        """Create TenantContext from authenticated user.
        
        Args:
            user: Authenticated user
            mode: Execution mode (saas or personal)
            tenant_id: Optional tenant ID (for SaaS)
            plan_tier: Plan tier from billing
            
        Returns:
            TenantContext for the user
        """
        if mode == "personal":
            return create_personal_context(user_id=user.user_id)
        
        # SaaS mode - requires tenant
        if not tenant_id:
            # Map user to tenant (in production: lookup in tenant store)
            tenant_id = f"tenant_{user.user_id}"
        
        return TenantContext(
            tenant_id=tenant_id,
            user_id=user.user_id,
            mode="saas",
            plan_tier=plan_tier,
            metadata=user.metadata or {}
        )
    
    def create_session_token(
        self,
        user: AuthUser,
        tenant_id: str | None = None,
        plan_tier: str = "free",
        expires_in: int = 3600
    ) -> str:
        """Create internal session token.
        
        Args:
            user: Authenticated user
            tenant_id: Tenant ID
            plan_tier: Plan tier
            expires_in: Token expiry in seconds
            
        Returns:
            JWT session token
        """
        return create_jwt_token(
            user_id=user.user_id,
            tenant_id=tenant_id,
            mode="saas" if tenant_id else "personal",
            plan=plan_tier,
            expires_in=expires_in
        )
    
    def verify_and_create_context(
        self,
        authorization_header: str | None,
        mode: str = "saas",
        tenant_id: str | None = None,
        plan_tier: str = "free"
    ) -> TenantContext:
        """Verify token and create TenantContext in one call.
        
        Args:
            authorization_header: Authorization header
            mode: Execution mode
            tenant_id: Tenant ID
            plan_tier: Plan tier
            
        Returns:
            TenantContext
            
        Raises:
            TokenInvalidError: If token invalid
            TokenExpiredError: If token expired
        """
        user = self.authenticate_request(authorization_header)
        return self.create_tenant_context(user, mode, tenant_id, plan_tier)


class TenantMappingService:
    """Service for managing user-to-tenant mappings.
    
    In production, this would store mappings in a database.
    """
    
    def __init__(self) -> None:
        # user_id -> tenant_id
        self._mappings: dict[str, str] = {}
    
    def get_tenant_for_user(self, user_id: str) -> str | None:
        """Get tenant ID for user."""
        return self._mappings.get(user_id)
    
    def map_user_to_tenant(self, user_id: str, tenant_id: str) -> None:
        """Map user to tenant."""
        self._mappings[user_id] = tenant_id
    
    def unmap_user(self, user_id: str) -> None:
        """Remove user mapping."""
        if user_id in self._mappings:
            del self._mappings[user_id]
    
    def get_users_for_tenant(self, tenant_id: str) -> list[str]:
        """Get all users in a tenant."""
        return [
            uid for uid, tid in self._mappings.items()
            if tid == tenant_id
        ]


# Default instances
_auth_service: AuthService | None = None
_tenant_mapping: TenantMappingService | None = None


def get_auth_service() -> AuthService:
    """Get the default auth service."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def get_tenant_mapping_service() -> TenantMappingService:
    """Get the default tenant mapping service."""
    global _tenant_mapping
    if _tenant_mapping is None:
        _tenant_mapping = TenantMappingService()
    return _tenant_mapping
