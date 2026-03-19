"""Tests for PSIP factory construction."""

import pytest
from psip import PSIP, create_psip, DOMAIN_CONFIG, DomainName


class TestFactoryConstruction:
    """Test create_psip factory function."""

    def test_create_psip_returns_psip_instance(self):
        """Verify create_psip() returns a usable PSIP instance."""
        psip = create_psip()
        assert isinstance(psip, PSIP)

    def test_create_psip_has_domains(self):
        """Verify PSIP has domains from DOMAIN_CONFIG."""
        psip = create_psip()
        assert psip.domains
        assert len(psip.domains) == len(DOMAIN_CONFIG)

    def test_create_psip_has_signal_system(self):
        """Verify PSIP has a signal system."""
        psip = create_psip()
        assert psip.signal_system is not None

    def test_create_psip_has_memory(self):
        """Verify PSIP has a memory engine."""
        psip = create_psip()
        assert psip.memory is not None

    def test_create_psip_has_governance(self):
        """Verify PSIP has governance components."""
        psip = create_psip()
        assert psip.executive_council is not None
        assert psip.risk_governor is not None

    def test_create_psip_with_custom_capital(self):
        """Verify PSIP respects custom capital value."""
        psip = create_psip(total_capital=500000)
        # Capital coordinator should be initialized with custom capital
        assert psip.capital_coordinator is not None

    def test_domains_match_domain_config_keys(self):
        """Verify domain keys match DOMAIN_CONFIG keys."""
        psip = create_psip()
        domain_keys = set(psip.domains.keys())
        config_keys = {key.value for key in DOMAIN_CONFIG.keys()}
        assert domain_keys == config_keys

    def test_create_psip_accepts_injected_dependencies(self):
        """Verify PSIP accepts injected dependencies."""
        mock_signal_system = object()
        mock_memory = object()
        
        psip = create_psip(
            signal_system=mock_signal_system,
            memory=mock_memory
        )
        
        assert psip.signal_system is mock_signal_system
        assert psip.memory is mock_memory
