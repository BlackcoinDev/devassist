"""
Configuration management for DevAssist.

This module provides centralized configuration loading and validation.
All configuration is loaded from environment variables (.env file).

Usage:
    from src.core.config import get_config

    config = get_config()
    print(config.model_name)
    print(config.chroma_host)
"""

import os
import logging
import warnings
from dataclasses import dataclass, field
from typing import Optional

# Application version
APP_VERSION = "0.1.0"


def _setup_logging() -> logging.Logger:
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Suppress verbose HTTP logging from external libraries
    for lib in ["httpx", "httpcore", "chromadb", "chromadb.telemetry",
                "urllib3", "openai"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logger


def _load_dotenv() -> None:
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        # Set OpenMP workaround if configured
        if os.getenv("KMP_DUPLICATE_LIB_OK") == "TRUE":
            os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    except ImportError:
        logging.warning(
            "python-dotenv not available, using system environment variables only"
        )

    # Suppress Pydantic V1 compatibility warnings
    warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")


def _require_env(name: str) -> str:
    """Get required environment variable or raise ValueError."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} environment variable is required")
    return value


def _require_int(name: str) -> int:
    """Get required integer environment variable."""
    return int(_require_env(name))


def _require_float(name: str) -> float:
    """Get required float environment variable."""
    return float(_require_env(name))


def _get_bool(name: str, default: bool = False) -> bool:
    """Get boolean environment variable with default."""
    return os.getenv(name, str(default)).lower() == "true"


@dataclass
class Config:
    """
    Application configuration loaded from environment variables.

    All required settings are validated at startup. Optional settings
    have sensible defaults.

    Attributes:
        # LM Studio Configuration
        lm_studio_url: LM Studio API endpoint
        lm_studio_key: API key for authentication
        model_name: LLM model name

        # Conversation Settings
        max_history_pairs: Max user-assistant pairs to keep
        temperature: LLM creativity (0.0 = deterministic, 1.0 = creative)
        max_input_length: Max user input length

        # Database Configuration
        db_type: Storage type ('sqlite')
        db_path: SQLite database file path

        # Vector Database Configuration
        chroma_host: ChromaDB server host
        chroma_port: ChromaDB server port
        ollama_base_url: Ollama embeddings server
        embedding_model: Embedding model name

        # Logging Configuration
        verbose_logging: Enable verbose logs
        show_llm_reasoning: Show LLM reasoning
        show_token_usage: Show token usage
        show_tool_details: Show tool details
    """

    # LM Studio Configuration
    lm_studio_url: str
    lm_studio_key: str
    model_name: str

    # Conversation Settings
    max_history_pairs: int
    temperature: float
    max_input_length: int

    # Database Configuration
    db_type: str
    db_path: str

    # Vector Database Configuration
    chroma_host: str
    chroma_port: int
    ollama_base_url: str
    embedding_model: str

    # Logging Configuration
    verbose_logging: bool = False
    show_llm_reasoning: bool = True
    show_token_usage: bool = True
    show_tool_details: bool = True

    # Cache file paths
    embedding_cache_file: str = "embedding_cache.json"
    query_cache_file: str = "query_cache.json"

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create Config from environment variables.

        Raises:
            ValueError: If required environment variable is missing
        """
        return cls(
            # LM Studio Configuration
            lm_studio_url=_require_env("LM_STUDIO_URL"),
            lm_studio_key=_require_env("LM_STUDIO_KEY"),
            model_name=_require_env("MODEL_NAME"),

            # Conversation Settings
            max_history_pairs=_require_int("MAX_HISTORY_PAIRS"),
            temperature=_require_float("TEMPERATURE"),
            max_input_length=_require_int("MAX_INPUT_LENGTH"),

            # Database Configuration
            db_type=_require_env("DB_TYPE").lower(),
            db_path=_require_env("DB_PATH"),

            # Vector Database Configuration
            chroma_host=_require_env("CHROMA_HOST"),
            chroma_port=_require_int("CHROMA_PORT"),
            ollama_base_url=_require_env("OLLAMA_BASE_URL"),
            embedding_model=_require_env("EMBEDDING_MODEL"),

            # Logging Configuration
            verbose_logging=_get_bool("VERBOSE_LOGGING", False),
            show_llm_reasoning=_get_bool("SHOW_LLM_REASONING", True),
            show_token_usage=_get_bool("SHOW_TOKEN_USAGE", True),
            show_tool_details=_get_bool("SHOW_TOOL_DETAILS", True),
        )


# Module-level singleton
_config: Optional[Config] = None
_logger: Optional[logging.Logger] = None


def get_config() -> Config:
    """
    Get the application configuration singleton.

    On first call, loads configuration from environment variables.
    Subsequent calls return the cached configuration.

    Returns:
        Config: Application configuration

    Raises:
        ValueError: If required environment variable is missing
    """
    global _config
    if _config is None:
        _load_dotenv()
        _config = Config.from_env()
    return _config


def get_logger() -> logging.Logger:
    """Get the application logger singleton."""
    global _logger
    if _logger is None:
        _logger = _setup_logging()
    return _logger


# Backwards compatibility: Export commonly used config values as module-level
# These are lazily evaluated to avoid loading .env at import time
def _lazy_config_attr(attr: str):
    """Create a property that lazily loads from config."""
    return property(lambda self: getattr(get_config(), attr))


# For backwards compatibility with existing code that imports these directly
# We'll keep module-level constants but they now read from Config
class _ConfigProxy:
    """Proxy object for backwards-compatible config access."""

    @property
    def LM_STUDIO_BASE_URL(self) -> str:
        return get_config().lm_studio_url

    @property
    def LM_STUDIO_API_KEY(self) -> str:
        return get_config().lm_studio_key

    @property
    def MODEL_NAME(self) -> str:
        return get_config().model_name

    @property
    def MAX_HISTORY_PAIRS(self) -> int:
        return get_config().max_history_pairs

    @property
    def TEMPERATURE(self) -> float:
        return get_config().temperature

    @property
    def MAX_INPUT_LENGTH(self) -> int:
        return get_config().max_input_length

    @property
    def DB_TYPE(self) -> str:
        return get_config().db_type

    @property
    def DB_PATH(self) -> str:
        return get_config().db_path

    @property
    def CHROMA_HOST(self) -> str:
        return get_config().chroma_host

    @property
    def CHROMA_PORT(self) -> int:
        return get_config().chroma_port

    @property
    def OLLAMA_BASE_URL(self) -> str:
        return get_config().ollama_base_url

    @property
    def EMBEDDING_MODEL(self) -> str:
        return get_config().embedding_model

    @property
    def VERBOSE_LOGGING(self) -> bool:
        return get_config().verbose_logging

    @property
    def SHOW_LLM_REASONING(self) -> bool:
        return get_config().show_llm_reasoning

    @property
    def SHOW_TOKEN_USAGE(self) -> bool:
        return get_config().show_token_usage

    @property
    def SHOW_TOOL_DETAILS(self) -> bool:
        return get_config().show_tool_details


# Create proxy instance for backwards compatibility
config_proxy = _ConfigProxy()
