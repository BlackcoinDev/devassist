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
