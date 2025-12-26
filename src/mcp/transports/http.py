"""
HTTP transport for MCP (SSE).
"""

import aiohttp
import logging
from typing import Any, Dict, Optional
from .base import Transport

logger = logging.getLogger(__name__)


class HttpTransport(Transport):
    """Transport over HTTP/SSE."""

    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self) -> None:
        """Create aiohttp session."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        logger.info(f"Connected to MCP HTTP server: {self.url}")

    async def close(self) -> None:
        """Close session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message via POST."""
        if not self.session:
            raise ConnectionError("Not connected")

        async with self.session.post(self.url, json=message) as response:
            response.raise_for_status()

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message (Polling/SSE implementation pending)."""
        # Note: True SSE implementation requires continuous reading
        # For this prototype, we'll assume a request-response model or
        # simplified polling if needed.
        # In full MCP, this would use a persistent connection.
        raise NotImplementedError(
            "HTTP/SSE receive not fully implemented in this version"
        )
