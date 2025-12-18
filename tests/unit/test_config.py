#!/usr/bin/env python3
"""
Test suite for Configuration Management (src/core/config.py).

Tests cover:
- Configuration loading from .env files
- Configuration validation and type checking
- Configuration accessors and immutability
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.core.config import Config, get_config


class TestConfigLoading:
    """Test configuration loading functionality."""

    def test_load_config_from_env(self):
        """Test loading all required variables from .env."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'LM_STUDIO_KEY': 'test-key',
            'MODEL_NAME': 'qwen3-vl-30b',
            'MAX_HISTORY_PAIRS': '10',
            'TEMPERATURE': '0.7',
            'MAX_INPUT_LENGTH': '4096',
            'DB_TYPE': 'sqlite',
            'DB_PATH': 'test.db',
            'CHROMA_HOST': 'localhost',
            'CHROMA_PORT': '8000',
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'EMBEDDING_MODEL': 'qwen3-embedding'
        }):
            config = Config.from_env()
            
            assert config.lm_studio_url == 'http://localhost:1234'
            assert config.model_name == 'qwen3-vl-30b'
            assert config.chroma_port == 8000
            assert config.temperature == 0.7
            assert config.max_history_pairs == 10

    def test_load_config_with_missing_required(self):
        """Test handling of missing required variables."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234'
            # Missing other required variables
        }, clear=True):
            with pytest.raises(ValueError):
                Config.from_env()

    def test_load_config_validates_types(self):
        """Test type validation for configuration values."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'LM_STUDIO_KEY': 'test-key',
            'MODEL_NAME': 'qwen3-vl-30b',
            'MAX_HISTORY_PAIRS': 'invalid', # Not an int
            'TEMPERATURE': '0.7',
            'MAX_INPUT_LENGTH': '4096',
            'DB_TYPE': 'sqlite',
            'DB_PATH': 'test.db',
            'CHROMA_HOST': 'localhost',
            'CHROMA_PORT': '8000',
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'EMBEDDING_MODEL': 'qwen3-embedding'
        }):
            with pytest.raises(ValueError):
                Config.from_env()

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'LM_STUDIO_KEY': 'test-key',
            'MODEL_NAME': 'qwen3-vl-30b',
            'MAX_HISTORY_PAIRS': '10',
            'TEMPERATURE': '0.7',
            'MAX_INPUT_LENGTH': '4096',
            'DB_TYPE': 'sqlite',
            'DB_PATH': 'test.db',
            'CHROMA_HOST': 'localhost',
            'CHROMA_PORT': '8000',
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'EMBEDDING_MODEL': 'qwen3-embedding'
        }):
            from src.core import config as config_mod
            config_mod._config = None # Reset singleton
            
            c1 = get_config()
            c2 = get_config()
            assert c1 is c2
            assert c1.model_name == 'qwen3-vl-30b'