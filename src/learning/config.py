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
Auto-learn configuration module.

Provides configuration dataclass for auto-learn feature with environment variable loading.
"""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class AutoLearnConfig:
    """
    Configuration for auto-learn feature.

    Attributes:
        auto_learn_on_startup: Enable auto-learning on application startup
        auto_learn_max_file_size_mb: Maximum file size for auto-learning (MB)
        auto_learn_timeout_seconds: Timeout for auto-learning operations (seconds)
        auto_learn_collection_name: ChromaDB collection name for auto-learned knowledge
    """

    # Auto-learn settings
    auto_learn_on_startup: bool = True
    auto_learn_max_file_size_mb: int = 5
    auto_learn_timeout_seconds: int = 30
    auto_learn_collection_name: str = "agents_knowledge"

    @classmethod
    def from_env(cls) -> "AutoLearnConfig":
        """
        Create AutoLearnConfig from environment variables.

        Uses environment variables with AUTO_LEARN_ prefix if available,
        otherwise falls back to default values.
        """
        return cls(
            auto_learn_on_startup=cls._get_bool("AUTO_LEARN_ON_STARTUP", True),
            auto_learn_max_file_size_mb=cls._get_int("AUTO_LEARN_MAX_FILE_SIZE_MB", 5),
            auto_learn_timeout_seconds=cls._get_int("AUTO_LEARN_TIMEOUT_SECONDS", 30),
            auto_learn_collection_name=cls._get_str(
                "AUTO_LEARN_COLLECTION_NAME", "agents_knowledge"
            ),
        )

    @staticmethod
    def _get_bool(name: str, default: bool) -> bool:
        """Get boolean environment variable with default."""
        return os.getenv(name, str(default)).lower() == "true"

    @staticmethod
    def _get_int(name: str, default: int) -> int:
        """Get integer environment variable with default."""
        try:
            return int(os.getenv(name, str(default)))
        except ValueError:
            return default

    @staticmethod
    def _get_str(name: str, default: str) -> str:
        """Get string environment variable with default."""
        return os.getenv(name, default)


# Module-level singleton
_auto_learn_config: Optional[AutoLearnConfig] = None


def get_auto_learn_config() -> AutoLearnConfig:
    """
    Get the auto-learn configuration singleton.

    Creates the configuration from environment variables on first call.
    """
    global _auto_learn_config
    if _auto_learn_config is None:
        _auto_learn_config = AutoLearnConfig.from_env()
    return _auto_learn_config
