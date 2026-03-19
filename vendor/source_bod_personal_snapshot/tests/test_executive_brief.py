"""Tests for executive brief generation."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from psip import create_psip, TRADE_INTELLIGENCE_AVAILABLE


class TestExecutiveBrief:
    """Test generate_executive_brief() behavior."""

    def test_generate_executive_brief_basic_structure(self, mocker):
        """Verify brief has expected structure."""
        psip = create_psip()
        
        # Mock the brief generator
        mock_brief = Mock()
        mock_brief.format_brief.return_value = "Executive Brief"
        psip.brief_generator = mocker.Mock()
        psip.brief_generator.generate.return_value = mock_brief
        
        # Mock domains to avoid actual analysis
        for chief in psip.domains.values():
            chief.analyze_signals = mocker.Mock(return_value=Mock())
            chief.generate_strategy = mocker.Mock(return_value=Mock(id="s1", title="Test", priority=1, action_items=[]))
            chief.create_report = mocker.Mock(return_value=Mock(recommendations=[]))
            chief.get_active_strategies = mocker.Mock(return_value=[])
            chief.get_domain_status = mocker.Mock(return_value="active")
        
        result = psip.generate_executive_brief(include_trade_intelligence=False)
        
        # Verify brief generator was called
        psip.brief_generator.generate.assert_called_once()
        
        # Get the call args
        call_args = psip.brief_generator.generate.call_args
        domain_reports = call_args[0][0]
        
        # Should have reports for all domains
        assert len(domain_reports) == 6

    def test_generate_executive_brief_without_trade_intelligence(self, mocker):
        """Verify brief works when trade intelligence is disabled."""
        psip = create_psip()
        
        # Mock brief generator
        mock_brief = Mock()
        psip.brief_generator = mocker.Mock()
        psip.brief_generator.generate.return_value = mock_brief
        
        # Mock domains
        for chief in psip.domains.values():
            chief.analyze_signals = mocker.Mock(return_value=Mock())
            chief.generate_strategy = mocker.Mock(return_value=Mock(id="s1", title="Test", priority=1, action_items=[]))
            chief.create_report = mocker.Mock(return_value=Mock(recommendations=[]))
            chief.get_active_strategies = mocker.Mock(return_value=[])
            chief.get_domain_status = mocker.Mock(return_value="active")
        
        result = psip.generate_executive_brief(include_trade_intelligence=False)
        
        # Should call generate with empty tactical trade insights
        call_args = psip.brief_generator.generate.call_args
        tactical_insights = call_args[0][3]
        
        assert tactical_insights == []

    @patch('psip.TRADE_INTELLIGENCE_AVAILABLE', True)
    @patch('psip.get_latest_spy0dte_trade_insight')
    @patch('psip.build_finance_trade_summary_appendix')
    @patch('psip.build_trade_opportunity')
    @patch('psip.build_trade_risk')
    @patch('psip.build_trade_action')
    def test_generate_executive_brief_with_trade_intelligence(
        self, mock_action, mock_risk, mock_opp, mock_summary, mock_insight, mocker
    ):
        """Verify brief enriches finance domain when trade intelligence available."""
        # Setup mocks
        mock_trade = Mock()
        mock_trade.to_dict.return_value = {"insight": "data"}
        mock_insight.return_value = mock_trade
        
        mock_summary.return_value = "(Trade: Bullish)"
        mock_opp.return_value = {"type": "opportunity", "details": "test"}
        mock_risk.return_value = {"type": "risk", "details": "test"}
        mock_action.return_value = {"type": "action", "details": "test"}
        
        psip = create_psip()
        
        # Mock brief generator
        mock_brief = Mock()
        psip.brief_generator = mocker.Mock()
        psip.brief_generator.generate.return_value = mock_brief
        
        # Mock domains
        for chief in psip.domains.values():
            chief.analyze_signals = mocker.Mock(return_value=Mock())
            chief.generate_strategy = mocker.Mock(return_value=Mock(id="s1", title="Test", priority=1, action_items=[]))
            chief.create_report = mocker.Mock(return_value=Mock(recommendations=[]))
            chief.get_active_strategies = mocker.Mock(return_value=[])
            chief.get_domain_status = mocker.Mock(return_value="active")
        
        result = psip.generate_executive_brief(include_trade_intelligence=True)
        
        # Verify trade intelligence was attempted
        mock_insight.assert_called_once()
        
        # Verify brief generator was called with trade insights
        call_args = psip.brief_generator.generate.call_args
        tactical_insights = call_args[0][3]
        
        assert len(tactical_insights) == 1

    def test_generate_executive_brief_handles_trade_intelligence_failure(self, mocker):
        """Verify brief handles trade intelligence failure gracefully."""
        psip = create_psip()
        
        # Mock brief generator
        mock_brief = Mock()
        psip.brief_generator = mocker.Mock()
        psip.brief_generator.generate.return_value = mock_brief
        
        # Mock domains
        for chief in psip.domains.values():
            chief.analyze_signals = mocker.Mock(return_value=Mock())
            chief.generate_strategy = mocker.Mock(return_value=Mock(id="s1", title="Test", priority=1, action_items=[]))
            chief.create_report = mocker.Mock(return_value=Mock(recommendations=[]))
            chief.get_active_strategies = mocker.Mock(return_value=[])
            chief.get_domain_status = mocker.Mock(return_value="active")
        
        # Even if trade intelligence throws, should still return brief
        with patch('psip.TRADE_INTELLIGENCE_AVAILABLE', True):
            with patch('psip.get_latest_spy0dte_trade_insight', side_effect=Exception("Trade API down")):
                result = psip.generate_executive_brief(include_trade_intelligence=True)
        
        # Should still return a brief (graceful degradation)
        assert result is not None

    def test_trade_intelligence_available_flag(self):
        """Verify TRADE_INTELLIGENCE_AVAILABLE is a boolean."""
        assert isinstance(TRADE_INTELLIGENCE_AVAILABLE, bool)
