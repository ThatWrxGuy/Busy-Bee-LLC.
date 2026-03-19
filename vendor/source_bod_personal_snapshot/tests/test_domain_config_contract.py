"""Tests for BB-CONFIG-001: Immutable Domain Configuration Contract."""

import pytest
from dataclasses import FrozenInstanceError

from psip_config import (
    DomainConfig,
    GovernanceConfig,
    RoleConfig,
    validate_domain_config,
    validate_domain_config_collection,
)
from psip import DOMAIN_CONFIG, create_psip


class TestGovernanceConfigImmutability:
    """Test GovernanceConfig is properly frozen."""

    def test_governance_config_is_frozen(self):
        """Verify GovernanceConfig is frozen."""
        config = GovernanceConfig()
        with pytest.raises(FrozenInstanceError):
            config.risk_threshold_high = 0.5

    def test_governance_config_uses_tuple_for_council_members(self):
        """Verify council_members is a tuple."""
        config = GovernanceConfig(council_members=("a", "b", "c"))
        assert isinstance(config.council_members, tuple)

    def test_governance_config_council_members_normalized(self):
        """Verify council members are normalized to tuples."""
        config = GovernanceConfig(council_members=["a", "b"])
        assert isinstance(config.council_members, tuple)
        assert config.council_members == ("a", "b")


class TestRoleConfigImmutability:
    """Test RoleConfig is properly frozen."""

    def test_role_config_is_frozen(self):
        """Verify RoleConfig is frozen."""
        config = RoleConfig()
        with pytest.raises(FrozenInstanceError):
            config.observer_enabled = False


class TestDomainConfigImmutability:
    """Test DomainConfig is properly frozen."""

    def test_domain_config_is_frozen(self):
        """Verify DomainConfig is frozen."""
        config = DomainConfig(name="finance")
        with pytest.raises(FrozenInstanceError):
            config.enabled = False

    def test_domain_config_nested_governance_is_frozen(self):
        """Verify nested GovernanceConfig is also frozen."""
        config = DomainConfig(
            name="finance",
            governance=GovernanceConfig(risk_threshold_high=0.8)
        )
        with pytest.raises(FrozenInstanceError):
            config.governance.risk_threshold_high = 0.5

    def test_domain_config_nested_roles_is_frozen(self):
        """Verify nested RoleConfig is also frozen."""
        config = DomainConfig(
            name="finance",
            roles=RoleConfig(observer_enabled=False)
        )
        with pytest.raises(FrozenInstanceError):
            config.roles.observer_enabled = True


class TestDomainConfigDefaults:
    """Test DomainConfig default values."""

    def test_domain_config_defaults(self):
        """Verify defaults are stable."""
        config = DomainConfig(name="health")
        assert config.enabled is True
        assert config.roles.observer_enabled is True
        assert config.roles.strategist_enabled is True
        assert config.roles.governor_enabled is True

    def test_governance_config_defaults(self):
        """Verify GovernanceConfig defaults."""
        config = GovernanceConfig()
        assert config.risk_threshold_high == 0.7
        assert config.risk_threshold_medium == 0.5
        assert config.risk_threshold_low == 0.6
        assert config.priority_weight == 1.0
        assert config.council_members == ()


class TestDomainConfigValidation:
    """Test config validation."""

    def test_empty_domain_name_raises(self):
        """Verify empty domain name fails."""
        with pytest.raises(ValueError):
            DomainConfig(name="")

    def test_whitespace_only_domain_name_raises(self):
        """Verify whitespace-only domain name fails."""
        with pytest.raises(ValueError):
            DomainConfig(name="   ")

    def test_invalid_risk_threshold_raises(self):
        """Verify invalid risk threshold fails."""
        with pytest.raises(ValueError):
            GovernanceConfig(risk_threshold_high=1.5)

    def test_negative_risk_threshold_raises(self):
        """Verify negative risk threshold fails."""
        with pytest.raises(ValueError):
            GovernanceConfig(risk_threshold_high=-0.1)

    def test_negative_priority_weight_raises(self):
        """Verify negative priority weight fails."""
        with pytest.raises(ValueError):
            GovernanceConfig(priority_weight=-1.0)

    def test_validate_domain_config_collection_empty_raises(self):
        """Verify empty config collection fails."""
        with pytest.raises(ValueError):
            validate_domain_config_collection({})


class TestDomainConfigDerivedProperties:
    """Test DomainConfig derived properties."""

    def test_member_id_derived_from_name(self):
        """Verify member_id is derived."""
        config = DomainConfig(name="finance")
        assert config.member_id == "fin"

    def test_short_name_derived(self):
        """Verify short_name is derived."""
        assert DomainConfig(name="finance").short_name == "CFO"
        assert DomainConfig(name="health").short_name == "CHO"
        assert DomainConfig(name="career").short_name == "CCO"
        assert DomainConfig(name="relationships").short_name == "CRO"
        assert DomainConfig(name="intelligence").short_name == "CIO"
        assert DomainConfig(name="life_architecture").short_name == "CLA"

    def test_title_derived(self):
        """Verify title is derived."""
        assert DomainConfig(name="finance").title == "Chief Financial Officer"
        assert DomainConfig(name="health").title == "Chief Health Officer"

    def test_risk_thresholds_property(self):
        """Verify risk_thresholds property returns tuple."""
        config = GovernanceConfig(
            risk_threshold_high=0.8,
            risk_threshold_medium=0.5,
            risk_threshold_low=0.3
        )
        assert config.risk_thresholds == (0.8, 0.5, 0.3)


class TestFactoryCompatibility:
    """Test config works with factory."""

    def test_factory_accepts_domain_config_instances(self):
        """Verify create_psip works with new config."""
        psip = create_psip()
        assert psip is not None
        assert psip.domains

    def test_domains_built_from_config(self):
        """Verify domains are built from config."""
        psip = create_psip()
        # Should have all domains from DOMAIN_CONFIG
        assert len(psip.domains) == len(DOMAIN_CONFIG)


class TestGovernancePropagation:
    """Test config values propagate to runtime."""

    def test_governance_values_propagate_from_config(self):
        """Verify governance values come from config."""
        psip = create_psip()
        
        # Check a specific domain's thresholds
        finance_threshold = psip.risk_governor.thresholds.get("finance")
        assert finance_threshold is not None
        assert finance_threshold.max_risk_score == 0.7
        assert finance_threshold.escalation_threshold == 0.5
        assert finance_threshold.requires_approval_above == 0.6

    def test_all_domains_have_thresholds(self):
        """Verify all domains get thresholds from config."""
        psip = create_psip()
        for domain_name in DOMAIN_CONFIG.keys():
            domain_key = domain_name.value
            threshold = psip.risk_governor.thresholds.get(domain_key)
            assert threshold is not None, f"Missing threshold for {domain_key}"

    def test_all_domains_have_council_members(self):
        """Verify all domains get council members from config."""
        psip = create_psip()
        member_ids = {m.id for m in psip.executive_council.members}
        
        expected_ids = {config.member_id for config in DOMAIN_CONFIG.values()}
        assert member_ids == expected_ids
