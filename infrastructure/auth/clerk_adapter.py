# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Clerk Auth Adapter.

Adapter for Clerk as identity provider.
"""

from __future__ import annotations

from typing import Any
import time

from infrastructure.auth.provider_adapter import (
    AuthProviderAdapter,
    AuthUser,
    TokenInvalidError,
    TokenExpiredError,
)


class ClerkAdapter(AuthProviderAdapter):
    """Adapter for Clerk identity provider.
    
    Clerk provides:
    - JWT verification via JWKS
    - User metadata
    - Session management
    - OAuth providers (Google, Apple, etc.)
    
    Docs: https://clerk.com/docs
    """
    
    def __init__(
        self,
        jwks_url: str | None = None,
        api_key: str | None = None,
        secret_key: str | None = None
    ) -> None:
        self.jwks_url = jwks_url or "https://api.clerk.com/v1/.well-known/jwks"
        self.api_key = api_key or ""
        self.secret_key = secret_key or ""
    
    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify Clerk JWT token.
        
        In production, verify signature using JWKS.
        This is a simplified version for demonstration.
        
        Args:
            token: Clerk JWT token
            
        Returns:
            Token payload
            
        Raises:
            TokenInvalidError: If token is invalid
            TokenExpiredError: If token is expired
        """
        # In production: use jwt.decode with JWKS
        # For now, decode without verification (demo only)
        try:
            import jwt
            # Decode without verification for demo
            # Production: use verify_jwt_token() with JWKS
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "verify_iat": True,
                }
            )
            
            # Check expiration
            exp = payload.get("exp", 0)
            if exp < time.time():
                raise TokenExpiredError("Token has expired")
            
            # Verify issuer
            iss = payload.get("iss", "")
            if not iss.startswith("https://clerk."):
                raise TokenInvalidError("Invalid token issuer")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(f"Invalid token: {e}")
    
    def get_user(self, user_id: str) -> AuthUser:
        """Get user details from Clerk.
        
        In production, call Clerk API.
        
        Args:
            user_id: Clerk user ID
            
        Returns:
            AuthUser from Clerk
        """
        # In production: call Clerk API
        # GET https://api.clerk.com/v1/users/{user_id}
        # Headers: Authorization: Bearer {secret_key}
        
        # Demo implementation
        return AuthUser(
            user_id=user_id,
            email=f"{user_id}@example.com",
            name=f"User {user_id[:8]}",
            metadata={"source": "clerk"}
        )
    
    def get_user_by_email(self, email: str) -> AuthUser | None:
        """Get user by email address.
        
        Args:
            email: User email
            
        Returns:
            AuthUser or None if not found
        """
        # In production: call Clerk API
        # GET https://api.clerk.com/v1/users?email_address={email}
        return None
    
    def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """List active sessions for user.
        
        Args:
            user_id: Clerk user ID
            
        Returns:
            List of session objects
        """
        # In production: call Clerk API
        # GET https://api.clerk.com/v1/users/{user_id}/sessions
        return []
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session.
        
        Args:
            session_id: Clerk session ID
            
        Returns:
            True if successful
        """
        # In production: call Clerk API
        # POST https://api.clerk.com/v1/sessions/{session_id}/revoke
        return True


class ClerkWebhooks:
    """Handler for Clerk webhook events.
    
    Docs: https://clerk.com/docs/webhooks/overview
    """
    
    @staticmethod
    def handle_user_created(event: dict[str, Any]) -> dict[str, Any]:
        """Handle user.created webhook."""
        data = event.get("data", {})
        return {
            "action": "user_created",
            "user_id": data.get("id"),
            "email": data.get("email_addresses", [{}])[0].get("email_address"),
        }
    
    @staticmethod
    def handle_user_updated(event: dict[str, Any]) -> dict[str, Any]:
        """Handle user.updated webhook."""
        data = event.get("data", {})
        return {
            "action": "user_updated",
            "user_id": data.get("id"),
        }
    
    @staticmethod
    def handle_user_deleted(event: dict[str, Any]) -> dict[str, Any]:
        """Handle user.deleted webhook."""
        data = event.get("data", {})
        return {
            "action": "user_deleted",
            "user_id": data.get("id"),
        }
    
    @staticmethod
    def handle_session_created(event: dict[str, Any]) -> dict[str, Any]:
        """Handle session.created webhook."""
        data = event.get("data", {})
        return {
            "action": "session_created",
            "session_id": data.get("id"),
            "user_id": data.get("user_id"),
        }
    
    @staticmethod
    def handle_event(event_type: str, event_data: dict[str, Any]) -> dict[str, Any]:
        """Route webhook event to handler."""
        handlers = {
            "user.created": ClerkWebhooks.handle_user_created,
            "user.updated": ClerkWebhooks.handle_user_updated,
            "user.deleted": ClerkWebhooks.handle_user_deleted,
            "session.created": ClerkWebhooks.handle_session_created,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        
        return {"action": "ignored", "type": event_type}
