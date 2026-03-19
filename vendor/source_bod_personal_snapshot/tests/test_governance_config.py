"""Tests for DOMAIN_CONFIG-driven initialization."""

import pytest
from psip import create_psip, DOMAIN_CONFIG, DomainName


class TestGovernanceConfig:
    """Test that DOMAIN_CONFIG drives governance initialization."""

    def test_council_members_from_config(self):
        """Verify council members match DOMAIN_CONFIG."""
        psip = create_psip()
        
        # Check each domain's config creates a council member
        for domain_name, config in DOMAIN_CONFIG.items():
            domain_key = domain_name.value
            expected_id = config.member_id
            
            # Find the member by ID (using correct attribute name: id)
            members = psip.executive_council.members
            member = next((m for m in members if m.id == expected_id), None)
            
            assert member is not None, f"Member {expected_id} not found"
            assert member.name == config.short_name
            assert member.role == config.title
            assert member.domain == domain_key
            assert member.vote_weight == config.governance.priority_weight

    def test_risk_thresholds_from_config(self):
        """Verify risk thresholds match DOMAIN_CONFIG."""
        psip = create_psip()
        
        for domain_name, config in DOMAIN_CONFIG.items():
            domain_key = domain_name.value
            governance = config.governance
            
            # Check thresholds exist for this domain
            thresholds = psip.risk_governor.thresholds
            domain_threshold = thresholds.get(domain_key)
            
            assert domain_threshold is not None, f"Threshold for {domain_key} not found"
            # RiskThreshold uses: max_risk_score, escalation_threshold, requires_approval_above
            assert domain_threshold.max_risk_score == governance.risk_threshold_high
            assert domain_threshold.escalation_threshold == governance.risk_threshold_medium
            assert domain_threshold.requires_approval_above == governance.risk_threshold_low

    def test_domain_priorities_from_config(self):
        """Verify domain priorities match DOMAIN_CONFIG."""
        psip = create_psip()
        
        for domain_name, config in DOMAIN_CONFIG.items():
            domain_key = domain_name.value
            
            # Check priority exists (currently using fixed priority of 5)
            priorities = psip.priority_router.domain_priorities
            domain_priority = priorities.get(domain_key)
            
            assert domain_priority is not None, f"Priority for {domain_key} not found"
            assert domain_priority == 5

    def test_all_domains_have_council_members(self):
        """Verify all domains have council members."""
        psip = create_psip()
        member_ids = {m.id for m in psip.executive_council.members}
        
        expected_ids = {config.member_id for config in DOMAIN_CONFIG.values()}
        assert member_ids == expected_ids
