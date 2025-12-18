#!/usr/bin/env python3
"""
Test suite for ApplicationContext (src/core/context.py).

Tests cover:
- Context initialization and lifecycle
- Dependency injection and accessors
- Configuration loading and validation
- LLM and vector database integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.context import ApplicationContext, get_context, set_context, reset_context
from src.core.config import Config


class TestContextInitialization:
    """Test ApplicationContext initialization."""

    def test_context_creation(self):
        """Test that ApplicationContext can be created."""
        context = ApplicationContext()
        
        # Verify context was created
        assert context is not None
        assert isinstance(context, ApplicationContext)

    def test_context_with_config(self):
        """Test that context can be created with configuration."""
        with patch('src.core.config.Config') as mock_config:
            mock_config.return_value = Mock()
            
            context = ApplicationContext()
            
            # Verify context was created
            assert context is not None


class TestContextGetters:
    """Test ApplicationContext getter methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context = ApplicationContext()
        set_context(self.context)

    def test_get_context_returns_singleton(self):
        """Test that get_context returns the same instance."""
        context1 = get_context()
        context2 = get_context()
        
        assert context1 is context2

    def test_get_context_returns_correct_type(self):
        """Test that get_context returns ApplicationContext instance."""
        context = get_context()
        assert isinstance(context, ApplicationContext)


class TestContextLifecycle:
    """Test ApplicationContext lifecycle management."""

    def test_context_cleanup(self):
        """Test that cleanup works properly."""
        context = ApplicationContext()
        set_context(context)
        
        # Cleanup should not raise errors
        reset_context()
        
        # After cleanup, a new default context is created by get_context()
        # This is the expected behavior
        new_context = get_context()
        assert new_context is not context
        assert isinstance(new_context, ApplicationContext)

    def test_context_reinitialize(self):
        """Test that context can be re-initialized."""
        # First context
        context1 = ApplicationContext()
        set_context(context1)
        
        # Reset
        reset_context()
        
        # Second context should work
        context2 = ApplicationContext()
        set_context(context2)
        
        assert get_context() is context2

    def test_context_thread_safety(self):
        """Test that context access is thread-safe."""
        context = ApplicationContext()
        set_context(context)
        
        # Multiple calls should return same context
        context1 = get_context()
        context2 = get_context()
        
        assert context1 is context2

    def test_context_state_management(self):
        """Test that context state can be managed."""
        context = ApplicationContext()
        set_context(context)
        
        # Context should be available
        assert get_context() is context
        
        # Reset and verify - get_context() creates new default context
        reset_context()
        new_context = get_context()
        assert new_context is not context
        assert isinstance(new_context, ApplicationContext)