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
from src.core.config import Config


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
                Config()

    def test_load_config_with_defaults(self):
        """Test applying default values for optional variables."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '8000',
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
            # No optional variables set
        }):
            config = Config()
            
            # Default values should be applied
            assert config.ollama_url == 'http://localhost:11434'

    def test_load_config_validates_types(self):
        """Test type validation for configuration values."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': 'invalid_port',  # Not an integer
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_load_config_from_custom_path(self):
        """Test loading from non-default .env file."""
        # Create temporary .env file
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = Mock()
            mock_open.return_value.__enter__.return_value.read.return_value = """
LM_STUDIO_URL=http://custom:1234
CHROMA_URL=http://custom:8000
CHROMA_PORT=8000
MODEL_NAME=custom-model
TEMPERATURE=0.5
MAX_HISTORY_PAIRS=5
MAX_TOKENS=2048
"""
            
            config = Config('.env.custom')
            assert config.lm_studio_url == 'http://custom:1234'


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_url_format(self):
        """Test validation of URL format."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'invalid-url',  # Not a valid URL
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '8000',
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_validate_port_range(self):
        """Test validation of port range (1-65535)."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '99999',  # Invalid port
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_validate_model_name_not_empty(self):
        """Test validation that model name is required."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '8000',
            'MODEL_NAME': '',  # Empty model name
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            with pytest.raises(ValueError):
                Config()

    def test_validate_temperature_range(self):
        """Test validation of temperature range (0.0-2.0)."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '8000',
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '3.0',  # Invalid temperature
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            with pytest.raises(ValueError):
                Config()


class TestConfigAccessors:
    """Test configuration accessor methods."""

    def setup_method(self):
        """Set up test configuration."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'CHROMA_URL': 'http://localhost:8000',
            'CHROMA_PORT': '8000',
            'MODEL_NAME': 'qwen3-vl-30b',
            'TEMPERATURE': '0.7',
            'MAX_HISTORY_PAIRS': '10',
            'MAX_TOKENS': '4096'
        }):
            self.config = Config()

    def test_get_config_value(self):
        """Test getting individual config values."""
        assert self.config.get('lm_studio_url') == 'http://localhost:1234'
        assert self.config.get('model_name') == 'qwen3-vl-30b'

    def test_config_to_dict(self):
        """Test exporting config as dictionary."""
        config_dict = self.config.to_dict()
        
        assert 'lm_studio_url' in config_dict
        assert 'chroma_url' in config_dict
        assert 'model_name' in config_dict

    def test_config_immutability(self):
        """Test that config cannot be modified after load."""
        with pytest.raises(AttributeError):
            self.config.lm_studio_url = 'http://new-url:1234'