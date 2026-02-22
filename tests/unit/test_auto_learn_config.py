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

"""
Test cases for AutoLearnConfig configuration.

This module tests the AutoLearnConfig dataclass and environment variable loading.
"""

import os
from unittest.mock import patch

from src.learning.config import AutoLearnConfig, get_auto_learn_config


class TestAutoLearnConfig:
    """Test AutoLearnConfig dataclass functionality."""

    def test_default_values(self):
        """Test that AutoLearnConfig has correct default values."""
        config = AutoLearnConfig()

        assert config.auto_learn_on_startup is True
        assert config.auto_learn_max_file_size_mb == 5
        assert config.auto_learn_timeout_seconds == 30
        assert config.auto_learn_collection_name == "agents_knowledge"

    def test_from_env_defaults(self):
        """Test AutoLearnConfig.from_env() with no environment variables set."""
        # Clear any existing environment variables
        for var in [
            "AUTO_LEARN_ON_STARTUP",
            "AUTO_LEARN_MAX_FILE_SIZE_MB",
            "AUTO_LEARN_TIMEOUT_SECONDS",
            "AUTO_LEARN_COLLECTION_NAME",
        ]:
            if var in os.environ:
                del os.environ[var]

        config = AutoLearnConfig.from_env()

        assert config.auto_learn_on_startup is True
        assert config.auto_learn_max_file_size_mb == 5
        assert config.auto_learn_timeout_seconds == 30
        assert config.auto_learn_collection_name == "agents_knowledge"

    @patch.dict(
        os.environ,
        {
            "AUTO_LEARN_ON_STARTUP": "false",
            "AUTO_LEARN_MAX_FILE_SIZE_MB": "10",
            "AUTO_LEARN_TIMEOUT_SECONDS": "60",
            "AUTO_LEARN_COLLECTION_NAME": "custom_knowledge",
        },
    )
    def test_from_env_custom_values(self):
        """Test AutoLearnConfig.from_env() with custom environment variables."""
        config = AutoLearnConfig.from_env()

        assert config.auto_learn_on_startup is False
        assert config.auto_learn_max_file_size_mb == 10
        assert config.auto_learn_timeout_seconds == 60
        assert config.auto_learn_collection_name == "custom_knowledge"

    def test_get_auto_learn_config_singleton(self):
        """Test that get_auto_learn_config() returns the same instance."""
        config1 = get_auto_learn_config()
        config2 = get_auto_learn_config()

        assert config1 is config2  # Same instance

    @patch.dict(
        os.environ,
        {
            "AUTO_LEARN_MAX_FILE_SIZE_MB": "invalid",
            "AUTO_LEARN_TIMEOUT_SECONDS": "not_a_number",
        },
    )
    def test_invalid_env_values_fallback_to_defaults(self):
        """Test that invalid environment values fall back to defaults."""
        config = AutoLearnConfig.from_env()

        # Should fall back to defaults when parsing fails
        assert config.auto_learn_max_file_size_mb == 5
        assert config.auto_learn_timeout_seconds == 30


class TestCoreConfigAutoLearnIntegration:
    """Test that core Config class includes auto-learn configuration."""

    def test_core_config_has_auto_learn_fields(self):
        """Test that the main Config class has auto-learn fields."""
        from src.core.config import Config

        config = Config(
            # Required fields with minimal values
            lm_studio_url="http://localhost:1234",
            lm_studio_key="test_key",
            model_name="test_model",
            max_history_pairs=5,
            temperature=0.7,
            max_input_length=1000,
            db_type="sqlite",
            db_path="test.db",
            chroma_host="localhost",
            chroma_port=8000,
            ollama_base_url="http://localhost:11434",
            embedding_model="test_embedding",
            # Auto-learn fields
            auto_learn_on_startup=True,
            auto_learn_max_file_size_mb=5,
            auto_learn_timeout_seconds=30,
            auto_learn_collection_name="agents_knowledge",
        )

        assert config.auto_learn_on_startup is True
        assert config.auto_learn_max_file_size_mb == 5
        assert config.auto_learn_timeout_seconds == 30
        assert config.auto_learn_collection_name == "agents_knowledge"

    @patch.dict(
        os.environ,
        {
            "LM_STUDIO_URL": "http://localhost:1234",
            "LM_STUDIO_KEY": "test_key",
            "MODEL_NAME": "test_model",
            "MAX_HISTORY_PAIRS": "5",
            "TEMPERATURE": "0.7",
            "MAX_INPUT_LENGTH": "1000",
            "DB_TYPE": "sqlite",
            "DB_PATH": "test.db",
            "CHROMA_HOST": "localhost",
            "CHROMA_PORT": "8000",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "EMBEDDING_MODEL": "test_embedding",
            "AUTO_LEARN_ON_STARTUP": "false",
            "AUTO_LEARN_MAX_FILE_SIZE_MB": "15",
            "AUTO_LEARN_TIMEOUT_SECONDS": "45",
            "AUTO_LEARN_COLLECTION_NAME": "test_collection",
        },
    )
    def test_core_config_from_env_with_auto_learn_vars(self):
        """Test that Config.from_env() loads auto-learn environment variables."""
        from src.core.config import Config

        config = Config.from_env()

        assert config.auto_learn_on_startup is False
        assert config.auto_learn_max_file_size_mb == 15
        assert config.auto_learn_timeout_seconds == 45
        assert config.auto_learn_collection_name == "test_collection"
