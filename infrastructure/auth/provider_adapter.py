# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Auth Provider Adapter Interface.

Abstract interface for external identity providers (Clerk, Auth0, Supabase).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class AuthError(Exception):
    """Base auth exception."""
    pass


class TokenInvalidError(AuthError):
    """Raised when token is invalid."""
    pass


class TokenExpiredError(AuthError):
    """Raised when token has expired."""
    pass


class UserNotFoundError(AuthError):
    """Raised when user not found."""
    pass


@dataclass
class AuthUser:
    """User information from auth provider."""
    user_id: str
    email: str | None = None
    name: str | None = None
    avatar_url: str | None = None
    metadata: dict[str, Any] | None = None
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.name or self.email or self.user_id


class AuthProviderAdapter(ABC):
    """Abstract adapter for auth providers.
    
    Implement this interface for Clerk, Auth0, Supabase, etc.
    """
    
    @abstractmethod
    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode a token.
        
        Args:
            token: JWT token from request
            
        Returns:
            Token payload dict
            
        Raises:
            TokenInvalidError: If token is invalid
            TokenExpiredError: If token is expired
        """
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> AuthUser:
        """Get user details from provider.
        
        Args:
            user_id: User ID from provider
            
        Returns:
            AuthUser object
            
        Raises:
            UserNotFoundError: If user not found
        """
        pass
    
    def extract_user_from_token(self, token: str) -> AuthUser:
        """Extract user info from token without provider lookup.
        
        Default implementation uses token payload.
        Override for providers that need external lookup.
        
        Args:
            token: JWT token
            
        Returns:
            AuthUser from token payload
        """
        payload = self.verify_token(token)
        
        return AuthUser(
            user_id=payload.get("sub", ""),
            email=payload.get("email"),
            name=payload.get("name"),
            avatar_url=payload.get("avatar_url") or payload.get("picture"),
            metadata=payload
        )
    
    def create_context_data(self, user: AuthUser) -> dict[str, Any]:
        """Create context data for TenantContext from auth user.
        
        Args:
            user: AuthUser from provider
            
        Returns:
            Dict with context data
        """
        return {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.display_name,
            "source": "external_auth",
            "avatar_url": user.avatar_url,
        }


class NoopAuthProvider(AuthProviderAdapter):
    """No-op adapter for development/testing.
    
    Accepts any token and returns mock user.
    """
    
    def __init__(self, default_user_id: str = "dev-user") -> None:
        self.default_user_id = default_user_id
    
    def verify_token(self, token: str) -> dict[str, Any]:
        """Always returns valid payload."""
        return {
            "sub": self.default_user_id,
            "email": f"{self.default_user_id}@example.com",
            "name": "Dev User",
            "iat": 0,
            "exp": 9999999999,
        }
    
    def get_user(self, user_id: str) -> AuthUser:
        """Returns mock user."""
        return AuthUser(
            user_id=user_id,
            email=f"{user_id}@example.com",
            name=f"User {user_id}"
        )


# Provider type
ProviderType = str  # "clerk", "auth0", "supabase", "noop"


def create_provider_adapter(
    provider_type: ProviderType,
    config: dict[str, Any] | None = None
) -> AuthProviderAdapter:
    """Factory function to create auth provider adapter.
    
    Args:
        provider_type: Type of provider ("clerk", "auth0", "supabase", "noop")
        config: Provider configuration
        
    Returns:
        AuthProviderAdapter implementation
    """
    config = config or {}
    
    if provider_type == "clerk":
        from infrastructure.auth.clerk_adapter import ClerkAdapter
        return ClerkAdapter(
            jwks_url=config.get("jwks_url"),
            api_key=config.get("api_key")
        )
    elif provider_type == "auth0":
        from infrastructure.auth.auth0_adapter import Auth0Adapter
        return Auth0Adapter(
            domain=config.get("domain", ""),
            audience=config.get("audience", "")
        )
    elif provider_type == "supabase":
        from infrastructure.auth.supabase_adapter import SupabaseAdapter
        return SupabaseAdapter(
            url=config.get("url", ""),
            anon_key=config.get("anon_key", "")
        )
    elif provider_type == "noop":
        return NoopAuthProvider(
            default_user_id=config.get("default_user_id", "dev-user")
        )
    else:
        raise ValueError(f"Unknown auth provider: {provider_type}")


# Default instance
_default_provider: AuthProviderAdapter | None = None


def get_auth_provider() -> AuthProviderAdapter:
    """Get the default auth provider.
    
    Uses NOOP provider by default.
    Configure via environment in production.
    """
    global _default_provider
    if _default_provider is None:
        # In production: load from config/env
        _default_provider = NoopAuthProvider()
    return _default_provider


def set_auth_provider(provider: AuthProviderAdapter) -> None:
    """Set the default auth provider."""
    global _default_provider
    _default_provider = provider
