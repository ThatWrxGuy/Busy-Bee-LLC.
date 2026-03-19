# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Tests for BB-AUTH-EXT-001: External Identity Federation."""

import pytest
import time

from infrastructure.auth.provider_adapter import (
    AuthProviderAdapter,
    AuthUser,
    NoopAuthProvider,
    create_provider_adapter,
    TokenInvalidError,
    TokenExpiredError,
)
from infrastructure.auth.auth_service import (
    AuthService,
    TenantMappingService,
)


class TestNoopAuthProvider:
    """Test noop auth provider."""
    
    def test_verify_token(self):
        """Verify token returns valid payload."""
        provider = NoopAuthProvider()
        
        payload = provider.verify_token("any-token")
        
        assert payload["sub"] == "dev-user"
        assert "email" in payload
    
    def test_get_user(self):
        """Get user returns mock user."""
        provider = NoopAuthProvider()
        
        user = provider.get_user("test-user")
        
        assert user.user_id == "test-user"
        assert user.email == "test-user@example.com"
    
    def test_extract_user_from_token(self):
        """Extract user from token."""
        provider = NoopAuthProvider()
        
        user = provider.extract_user_from_token("test-token")
        
        assert user.user_id == "dev-user"


class TestProviderFactory:
    """Test provider factory."""
    
    def test_create_noop_provider(self):
        """Create noop provider."""
        provider = create_provider_adapter("noop")
        
        assert isinstance(provider, NoopAuthProvider)
    
    def test_create_with_config(self):
        """Create provider with config."""
        provider = create_provider_adapter("noop", {"default_user_id": "custom-user"})
        
        assert provider.default_user_id == "custom-user"
    
    def test_unknown_provider_raises(self):
        """Unknown provider raises error."""
        with pytest.raises(ValueError):
            create_provider_adapter("unknown")


class TestAuthService:
    """Test auth service."""
    
    def test_authenticate_token(self):
        """Authenticate token."""
        service = AuthService()
        
        user = service.authenticate("any-token")
        
        assert user.user_id == "dev-user"
    
    def test_authenticate_missing_header_raises(self):
        """Missing header raises."""
        service = AuthService()
        
        with pytest.raises(TokenInvalidError):
            service.authenticate_request(None)
    
    def test_authenticate_wrong_format_raises(self):
        """Wrong format raises."""
        service = AuthService()
        
        with pytest.raises(TokenInvalidError):
            service.authenticate_request("Basic abc")
    
    def test_create_tenant_context_saas(self):
        """Create SaaS tenant context."""
        service = AuthService()
        
        user = AuthUser(user_id="user-123", email="test@example.com")
        context = service.create_tenant_context(user, mode="saas", tenant_id="tenant-1")
        
        assert context.user_id == "user-123"
        assert context.tenant_id == "tenant-1"
        assert context.is_saas
    
    def test_create_tenant_context_personal(self):
        """Create personal tenant context."""
        service = AuthService()
        
        user = AuthUser(user_id="user-123", email="test@example.com")
        context = service.create_tenant_context(user, mode="personal")
        
        assert context.is_personal
        assert "*" in context.permissions
    
    def test_create_session_token(self):
        """Create session token."""
        service = AuthService()
        
        user = AuthUser(user_id="user-123")
        token = service.create_session_token(user, tenant_id="tenant-1", plan_tier="pro")
        
        assert token  # Should return a JWT string
        assert len(token.split(".")) == 3  # JWT format
    
    def test_verify_and_create_context(self):
        """Verify and create context in one call."""
        service = AuthService()
        
        context = service.verify_and_create_context(
            authorization_header="Bearer test-token",
            mode="saas",
            tenant_id="tenant-1"
        )
        
        assert context.is_saas
        assert context.tenant_id == "tenant-1"


class TestTenantMappingService:
    """Test tenant mapping service."""
    
    def test_map_user_to_tenant(self):
        """Map user to tenant."""
        service = TenantMappingService()
        
        service.map_user_to_tenant("user-1", "tenant-1")
        
        assert service.get_tenant_for_user("user-1") == "tenant-1"
    
    def test_get_tenant_for_unmapped_user(self):
        """Unmapped user returns None."""
        service = TenantMappingService()
        
        assert service.get_tenant_for_user("unknown") is None
    
    def test_unmap_user(self):
        """Unmap user."""
        service = TenantMappingService()
        
        service.map_user_to_tenant("user-1", "tenant-1")
        service.unmap_user("user-1")
        
        assert service.get_tenant_for_user("user-1") is None
    
    def test_get_users_for_tenant(self):
        """Get users for tenant."""
        service = TenantMappingService()
        
        service.map_user_to_tenant("user-1", "tenant-1")
        service.map_user_to_tenant("user-2", "tenant-1")
        service.map_user_to_tenant("user-3", "tenant-2")
        
        users = service.get_users_for_tenant("tenant-1")
        
        assert len(users) == 2
        assert "user-1" in users
        assert "user-2" in users


class TestAuthUser:
    """Test auth user dataclass."""
    
    def test_display_name_from_name(self):
        """Display name uses name."""
        user = AuthUser(user_id="1", name="John Doe")
        
        assert user.display_name == "John Doe"
    
    def test_display_name_from_email(self):
        """Display name falls back to email."""
        user = AuthUser(user_id="1", email="john@example.com")
        
        assert user.display_name == "john@example.com"
    
    def test_display_name_fallback(self):
        """Display name falls back to user_id."""
        user = AuthUser(user_id="user-123")
        
        assert user.display_name == "user-123"


class TestClerkAdapter:
    """Test Clerk adapter (when available)."""
    
    def test_clerk_adapter_import(self):
        """Can import Clerk adapter."""
        try:
            from infrastructure.auth.clerk_adapter import ClerkAdapter
            assert True
        except ImportError:
            pytest.skip("PyJWT not available")
    
    def test_clerk_adapter_creation(self):
        """Can create Clerk adapter."""
        try:
            from infrastructure.auth.clerk_adapter import ClerkAdapter
            
            adapter = ClerkAdapter(
                jwks_url="https://test.clerk.com/.well-known/jwks"
            )
            
            assert adapter.jwks_url == "https://test.clerk.com/.well-known/jwks"
        except ImportError:
            pytest.skip("PyJWT not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
