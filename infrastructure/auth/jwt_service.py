# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""JWT Service for identity verification.

This module provides JWT token generation and verification.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from base64 import b64decode, b64encode
from dataclasses import dataclass, field
from typing import Any


class JWTError(Exception):
    """Base JWT exception."""
    pass


class JWTExpiredError(JWTError):
    """Raised when token has expired."""
    pass


class JWTInvalidSignatureError(JWTError):
    """Raised when signature is invalid."""
    pass


class JWTMissingClaimError(JWTError):
    """Raised when required claim is missing."""
    pass


@dataclass
class JWTPayload:
    """JWT payload with claims."""
    subject: str  # user_id
    tenant_id: str | None = None
    mode: str = "personal"
    plan: str = "free"
    permissions: list[str] = field(default_factory=list)
    issued_at: int = field(default_factory=lambda: int(time.time()))
    expires_at: int = field(default_factory=lambda: int(time.time()) + 3600)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return time.time() > self.expires_at
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to JWT claims dict."""
        return {
            "sub": self.subject,
            "tenant_id": self.tenant_id,
            "mode": self.mode,
            "plan": self.plan,
            "permissions": self.permissions,
            "iat": self.issued_at,
            "exp": self.expires_at,
            **self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JWTPayload:
        """Create from JWT claims dict."""
        return cls(
            subject=data.get("sub", ""),
            tenant_id=data.get("tenant_id"),
            mode=data.get("mode", "personal"),
            plan=data.get("plan", "free"),
            permissions=data.get("permissions", []),
            issued_at=data.get("iat", int(time.time())),
            expires_at=data.get("exp", int(time.time()) + 3600),
            metadata={k: v for k, v in data.items() 
                     if k not in {"sub", "tenant_id", "mode", "plan", "permissions", "iat", "exp"}}
        )


class JWTService:
    """JWT token service.
    
    In production, use proper JWT library (PyJWT) with asymmetric keys.
    This implementation uses HMAC for demonstration.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, payload: JWTPayload) -> str:
        """Create a JWT token."""
        # Header
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_encoded = self._base64url_encode(json.dumps(header))
        
        # Payload
        payload_encoded = self._base64url_encode(json.dumps(payload.to_dict()))
        
        # Signature
        signature = self._sign(f"{header_encoded}.{payload_encoded}")
        signature_encoded = self._base64url_encode(signature)
        
        return f"{header_encoded}.{payload_encoded}.{signature_encoded}"
    
    def verify_token(self, token: str) -> JWTPayload:
        """Verify and decode a JWT token.
        
        Raises:
            JWTExpiredError: If token is expired
            JWTInvalidSignatureError: If signature is invalid
            JWTMissingClaimError: If required claims are missing
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise JWTError("Invalid token format")
        
        header_encoded, payload_encoded, signature_encoded = parts
        
        # Verify signature
        expected_signature = self._sign(f"{header_encoded}.{payload_encoded}")
        expected_signature_encoded = self._base64url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_encoded, expected_signature_encoded):
            raise JWTInvalidSignatureError("Invalid token signature")
        
        # Decode payload
        payload_data = json.loads(self._base64url_decode(payload_encoded))
        payload = JWTPayload.from_dict(payload_data)
        
        # Check expiration
        if payload.is_expired:
            raise JWTExpiredError("Token has expired")
        
        # Validate required claims
        if not payload.subject:
            raise JWTMissingClaimError("Missing 'sub' claim")
        
        if payload.mode == "saas" and not payload.tenant_id:
            raise JWTMissingClaimError("SaaS mode requires 'tenant_id'")
        
        return payload
    
    def _sign(self, data: str) -> str:
        """Create HMAC signature."""
        return hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).digest()
    
    def _base64url_encode(self, data: str | bytes) -> str:
        """Base64 URL-safe encoding."""
        if isinstance(data, bytes):
            return b64encode(data).rstrip(b"=").decode()
        return b64encode(data.encode()).rstrip(b"=").decode()
    
    def _base64url_decode(self, data: str) -> str:
        """Base64 URL-safe decoding."""
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        return b64decode(data).decode()


class JWTBuilder:
    """Builder for JWT payloads."""
    
    def __init__(self) -> None:
        self._payload = JWTPayload(subject="")
    
    def with_subject(self, subject: str) -> JWTBuilder:
        """Set subject (user_id)."""
        self._payload.subject = subject
        return self
    
    def with_tenant_id(self, tenant_id: str) -> JWTBuilder:
        """Set tenant_id."""
        self._payload.tenant_id = tenant_id
        return self
    
    def with_mode(self, mode: str) -> JWTBuilder:
        """Set execution mode."""
        self._payload.mode = mode
        return self
    
    def with_plan(self, plan: str) -> JWTBuilder:
        """Set plan tier."""
        self._payload.plan = plan
        return self
    
    def with_permissions(self, permissions: list[str]) -> JWTBuilder:
        """Set permissions."""
        self._payload.permissions = permissions
        return self
    
    def with_expiry(self, seconds: int) -> JWTBuilder:
        """Set expiry in seconds from now."""
        self._payload.expires_at = int(time.time()) + seconds
        return self
    
    def with_metadata(self, key: str, value: Any) -> JWTBuilder:
        """Add metadata."""
        self._payload.metadata[key] = value
        return self
    
    def build(self) -> JWTPayload:
        """Build the payload."""
        return self._payload


# Default instance (use secure key in production)
_default_service: JWTService | None = None


def get_jwt_service(secret_key: str | None = None) -> JWTService:
    """Get the default JWT service."""
    global _default_service
    if _default_service is None:
        # In production, load from secure config
        key = secret_key or "dev-secret-key-change-in-production"
        _default_service = JWTService(key)
    return _default_service


def create_jwt_token(
    user_id: str,
    tenant_id: str | None = None,
    mode: str = "personal",
    plan: str = "free",
    permissions: list[str] | None = None,
    expires_in: int = 3600
) -> str:
    """Helper to create a JWT token."""
    service = get_jwt_service()
    payload = JWTPayload(
        subject=user_id,
        tenant_id=tenant_id,
        mode=mode,
        plan=plan,
        permissions=permissions or [],
        expires_at=int(time.time()) + expires_in
    )
    return service.create_token(payload)


def verify_jwt_token(token: str) -> JWTPayload:
    """Helper to verify a JWT token."""
    service = get_jwt_service()
    return service.verify_token(token)
