#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2025 BlackcoinDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys

"""
Test suite for Configuration Management (src/core/config.py).

Tests cover:
- Configuration loading from .env files
- Configuration validation and type checking
- Configuration accessors and immutability
"""

import os
import pytest
from unittest.mock import patch
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
            'MAX_HISTORY_PAIRS': 'invalid',  # Not an int
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
            config_mod._config = None  # Reset singleton

            c1 = get_config()
            c2 = get_config()
            assert c1 is c2
            assert c1.model_name == 'qwen3-vl-30b'


class TestConfigProxy:
    """Test backwards compatibility config proxy."""

    def test_config_proxy_properties(self):
        """Test all ConfigProxy properties."""
        with patch.dict(os.environ, {
            'LM_STUDIO_URL': 'http://localhost:1234',
            'LM_STUDIO_KEY': 'test-key',
            'MODEL_NAME': 'test-model',
            'MAX_HISTORY_PAIRS': '15',
            'TEMPERATURE': '0.8',
            'MAX_INPUT_LENGTH': '8192',
            'DB_TYPE': 'sqlite',
            'DB_PATH': 'custom.db',
            'CHROMA_HOST': '192.168.1.1',
            'CHROMA_PORT': '9000',
            'OLLAMA_BASE_URL': 'http://localhost:11434',
            'EMBEDDING_MODEL': 'test-embedding',
            'VERBOSE_LOGGING': 'true',
            'SHOW_LLM_REASONING': 'false',
            'SHOW_TOKEN_USAGE': 'true',
            'SHOW_TOOL_DETAILS': 'false'
        }):
            from src.core import config as config_mod
            config_mod._config = None  # Reset singleton

            from src.core.config import config_proxy

            # Test all proxy properties
            assert config_proxy.LM_STUDIO_BASE_URL == 'http://localhost:1234'
            assert config_proxy.LM_STUDIO_API_KEY == 'test-key'
            assert config_proxy.MODEL_NAME == 'test-model'
            assert config_proxy.MAX_HISTORY_PAIRS == 15
            assert config_proxy.TEMPERATURE == 0.8
            assert config_proxy.MAX_INPUT_LENGTH == 8192
            assert config_proxy.DB_TYPE == 'sqlite'
            assert config_proxy.DB_PATH == 'custom.db'
            assert config_proxy.CHROMA_HOST == '192.168.1.1'
            assert config_proxy.CHROMA_PORT == 9000
            assert config_proxy.OLLAMA_BASE_URL == 'http://localhost:11434'
            assert config_proxy.EMBEDDING_MODEL == 'test-embedding'
            assert config_proxy.VERBOSE_LOGGING is True
            assert config_proxy.SHOW_LLM_REASONING is False
            assert config_proxy.SHOW_TOKEN_USAGE is True
            assert config_proxy.SHOW_TOOL_DETAILS is False


class TestConfigEdgeCases:
    """Test edge cases and error handling."""

    def test_dotenv_import_error_handling(self):
        """Test handling when python-dotenv is not available."""

        # Save original dotenv module if present
        dotenv_module = sys.modules.get('dotenv')

        try:
            # Remove dotenv from modules
            if 'dotenv' in sys.modules:
                del sys.modules['dotenv']

            # Mock the import to raise ImportError
            import builtins
            real_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == 'dotenv':
                    raise ImportError("No module named 'dotenv'")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                # Reload the config module to trigger the ImportError path
                import importlib
                from src.core import config as config_mod
                importlib.reload(config_mod)

                # The module should still load, just without dotenv support
                assert config_mod is not None

        finally:
            # Restore original dotenv module
            if dotenv_module:
                sys.modules['dotenv'] = dotenv_module

    def test_kmp_duplicate_lib_workaround(self):
        """Test KMP_DUPLICATE_LIB_OK environment variable handling."""

        # Save original KMP_DUPLICATE_LIB_OK value
        original_kmp_value = os.environ.get('KMP_DUPLICATE_LIB_OK')

        try:
            # Test when KMP_DUPLICATE_LIB_OK is set to TRUE
            with patch.dict(os.environ, {'KMP_DUPLICATE_LIB_OK': 'TRUE'}):
                # Reload the config module to trigger the KMP handling
                import importlib
                from src.core import config as config_mod
                importlib.reload(config_mod)

                # KMP_DUPLICATE_LIB_OK should be set in environment
                assert os.environ.get('KMP_DUPLICATE_LIB_OK') == 'TRUE'

            # Test when KMP_DUPLICATE_LIB_OK is not set
            with patch.dict(os.environ, {}, clear=True):
                # Remove KMP_DUPLICATE_LIB_OK if it was set
                if 'KMP_DUPLICATE_LIB_OK' in os.environ:
                    del os.environ['KMP_DUPLICATE_LIB_OK']

                # Reload the config module
                importlib.reload(config_mod)

                # KMP_DUPLICATE_LIB_OK should not be set
                assert os.environ.get('KMP_DUPLICATE_LIB_OK') is None

        finally:
            # Restore original KMP_DUPLICATE_LIB_OK value
            if original_kmp_value:
                os.environ['KMP_DUPLICATE_LIB_OK'] = original_kmp_value
            elif 'KMP_DUPLICATE_LIB_OK' in os.environ:
                del os.environ['KMP_DUPLICATE_LIB_OK']
