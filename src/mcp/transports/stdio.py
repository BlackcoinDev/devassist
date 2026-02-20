"""
Stdio transport for MCP.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from .base import Transport
from src.core.constants import SAFE_ENV_VARS

logger = logging.getLogger(__name__)


def get_safe_env() -> Dict[str, str]:
    """Return a filtered environment dictionary containing only safe variables."""
    return {k: v for k, v in os.environ.items() if k in SAFE_ENV_VARS}


class StdioTransport(Transport):
    """Transport over standard input/output of a subprocess."""

    def __init__(
        self, command: str, args: List[str], env: Optional[Dict[str, str]] = None
    ):
        self.command = command
        self.args = args
        # Use safe environment by default to prevent information leakage
        self.env = env or get_safe_env()
        self.process: Optional[asyncio.subprocess.Process] = None

    async def connect(self) -> None:
        """Start the subprocess."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env,
            )
            logger.info(f"Started MCP stdio server: {self.command} {self.args}")
        except Exception as e:
            logger.error(f"Failed to start stdio server: {e}")
            raise

    async def close(self) -> None:
        """Terminate the subprocess."""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error closing stdio transport: {e}")
            finally:
                self.process = None

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message to subprocess stdin."""
        if not self.process or not self.process.stdin:
            raise ConnectionError("Not connected")

        try:
            json_str = json.dumps(message) + "\n"
            self.process.stdin.write(json_str.encode("utf-8"))
            await self.process.stdin.drain()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Read message from subprocess stdout."""
        if not self.process or not self.process.stdout:
            raise ConnectionError("Not connected")

        try:
            line = await self.process.stdout.readline()
            if not line:
                return None
            return json.loads(line.decode("utf-8"))
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            raise
