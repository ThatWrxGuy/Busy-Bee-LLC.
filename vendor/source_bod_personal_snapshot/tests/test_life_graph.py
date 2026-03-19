"""Tests for life graph building edge cases."""

import pytest
from unittest.mock import Mock
from psip import create_psip


class TestBuildLifeGraph:
    """Test build_life_graph() edge cases."""

    def test_build_life_graph_empty_list_uses_provided_signals(self, mocker):
        """Verify build_life_graph([]) uses provided empty list, not fallback."""
        psip = create_psip()
        
        # Mock the graph builder and life graph
        psip.graph_builder = mocker.Mock()
        psip.life_graph = mocker.Mock()
        
        # Mock the result
        result = mocker.Mock()
        result.nodes_created = 0
        result.edges_created = 0
        
        psip.graph_builder.build_from_signals.return_value = result
        psip.life_graph.get_graph_summary.return_value = {"nodes": 0, "edges": 0}
        
        # Call with empty list
        output = psip.build_life_graph([])
        
        # Verify build_from_signals was called with the empty list
        psip.graph_builder.build_from_signals.assert_called_once_with([])
        
        # Verify full_build was NOT called
        psip.graph_builder.full_build.assert_not_called()
        
        # Verify result
        assert output["nodes_created"] == 0

    def test_build_life_graph_with_signals_uses_provided_signals(self, mocker):
        """Verify build_life_graph(signals) passes signals to builder."""
        psip = create_psip()
        
        psip.graph_builder = mocker.Mock()
        psip.life_graph = mocker.Mock()
        
        test_signals = [
            {"source": "wearable", "type": "sleep", "value": 7.5},
            {"source": "bank", "type": "spending", "value": 150.0},
        ]
        
        result = mocker.Mock()
        result.nodes_created = 2
        result.edges_created = 1
        
        psip.graph_builder.build_from_signals.return_value = result
        psip.life_graph.get_graph_summary.return_value = {"nodes": 2, "edges": 1}
        
        output = psip.build_life_graph(test_signals)
        
        psip.graph_builder.build_from_signals.assert_called_once_with(test_signals)
        psip.graph_builder.full_build.assert_not_called()
        assert output["nodes_created"] == 2

    def test_build_life_graph_none_triggers_full_build(self, mocker):
        """Verify build_life_graph(None) falls back to full_build."""
        psip = create_psip()
        
        psip.graph_builder = mocker.Mock()
        psip.life_graph = mocker.Mock()
        
        result = mocker.Mock()
        result.nodes_created = 10
        result.edges_created = 5
        
        psip.graph_builder.full_build.return_value = result
        psip.life_graph.get_graph_summary.return_value = {"nodes": 10, "edges": 5}
        
        output = psip.build_life_graph(None)
        
        psip.graph_builder.full_build.assert_called_once()
        psip.graph_builder.build_from_signals.assert_not_called()
        assert output["nodes_created"] == 10

    def test_build_life_graph_no_argument_triggers_full_build(self, mocker):
        """Verify build_life_graph() with no args falls back to full_build."""
        psip = create_psip()
        
        psip.graph_builder = mocker.Mock()
        psip.life_graph = mocker.Mock()
        
        result = mocker.Mock()
        result.nodes_created = 10
        result.edges_created = 5
        
        psip.graph_builder.full_build.return_value = result
        psip.life_graph.get_graph_summary.return_value = {"nodes": 10, "edges": 5}
        
        output = psip.build_life_graph()
        
        psip.graph_builder.full_build.assert_called_once()
        psip.graph_builder.build_from_signals.assert_not_called()
        assert output["nodes_created"] == 10
