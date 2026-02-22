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
Base transport classes for MCP.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
