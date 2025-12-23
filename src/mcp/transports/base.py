"""
Base transport classes for MCP.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncIterator

class Transport(ABC):
    """Abstract base class for MCP transports."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the server."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""
        pass

    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a JSON-RPC message."""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive a JSON-RPC message."""
        pass
