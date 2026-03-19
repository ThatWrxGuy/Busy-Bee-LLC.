"""Tests for signal processing and normalization."""

import pytest
from unittest.mock import Mock, MagicMock
from psip import create_psip


class TestProcessSignal:
    """Test process_signal() stores normalized records."""

    def test_process_signal_stores_normalized_record(self, mocker):
        """Verify process_signal() stores normalized record, not raw input."""
        # Mock the signal system and memory
        signal_system = mocker.Mock()
        memory = mocker.Mock()
        
        # Create mock emitted signal
        emitted = mocker.Mock()
        emitted.id = "sig-1"
        emitted.source = "app"
        emitted.signal_type = "metric"
        emitted.domain = "finance"
        emitted.payload = {"x": 1}
        
        signal_system.emit.return_value = emitted
        
        # Create PSIP with mocks
        psip = create_psip(signal_system=signal_system, memory=memory)
        
        # Process a signal with raw input
        psip.process_signal({
            "source": "app",
            "type": "metric",
            "domain": "finance",
            "payload": {"x": 1},
            "importance": 0.9,
        })
        
        # Verify emit was called
        signal_system.emit.assert_called_once_with(
            source="app",
            signal_type="metric",
            domain="finance",
            payload={"x": 1},
            priority=mocker.ANY  # Can't easily predict the enum
        )
        
        # Verify memory.store was called with NORMALIZED record
        memory.store.assert_called_once()
        call_kwargs = memory.store.call_args.kwargs
        
        assert call_kwargs["memory_type"] == "signal"
        assert call_kwargs["content"]["id"] == "sig-1"
        assert call_kwargs["content"]["source"] == "app"
        assert call_kwargs["content"]["signal_type"] == "metric"
        assert call_kwargs["content"]["domain"] == "finance"
        assert call_kwargs["content"]["payload"] == {"x": 1}
        assert call_kwargs["domain"] == "finance"
        assert call_kwargs["importance"] == 0.9

    def test_process_signal_returns_emitted_signal(self, mocker):
        """Verify process_signal() returns the emitted signal."""
        signal_system = mocker.Mock()
        memory = mocker.Mock()
        
        emitted = mocker.Mock()
        signal_system.emit.return_value = emitted
        
        psip = create_psip(signal_system=signal_system, memory=memory)
        result = psip.process_signal({"source": "test"})
        
        assert result is emitted

    def test_process_signal_uses_defaults(self, mocker):
        """Verify process_signal() uses sensible defaults."""
        signal_system = mocker.Mock()
        memory = mocker.Mock()
        
        emitted = mocker.Mock()
        emitted.id = "sig-default"
        emitted.source = "unknown"
        emitted.signal_type = "general"
        emitted.domain = "general"
        emitted.payload = {}
        
        signal_system.emit.return_value = emitted
        
        psip = create_psip(signal_system=signal_system, memory=memory)
        psip.process_signal({})  # Empty input
        
        # Check emit was called with defaults
        signal_system.emit.assert_called_once()
        call_kwargs = signal_system.emit.call_args.kwargs
        assert call_kwargs["source"] == "unknown"
        assert call_kwargs["signal_type"] == "general"
        assert call_kwargs["domain"] == "general"
        assert call_kwargs["payload"] == {}

    def test_process_signal_stores_normalized_not_raw(self, mocker):
        """Verify we store normalized data, not the original raw input."""
        signal_system = mocker.Mock()
        memory = mocker.Mock()
        
        emitted = mocker.Mock()
        emitted.id = "sig-123"
        emitted.source = "custom-source"
        emitted.signal_type = "custom-type"
        emitted.domain = "health"
        emitted.payload = {"custom": "payload"}
        
        signal_system.emit.return_value = emitted
        
        psip = create_psip(signal_system=signal_system, memory=memory)
        
        # Call with raw input
        psip.process_signal({
            "source": "custom-source",
            "type": "custom-type",
            "domain": "health",
            "payload": {"custom": "payload"},
            "importance": 0.5,
        })
        
        # The key assertion: content should come from the emitted signal
        # not from the raw input
        call_kwargs = memory.store.call_args.kwargs
        stored_content = call_kwargs["content"]
        
        # These should match the emitted signal, not the raw input
        assert stored_content["id"] == "sig-123"
        assert stored_content["source"] == "custom-source"
        assert stored_content["signal_type"] == "custom-type"
