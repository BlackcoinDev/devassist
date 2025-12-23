"""
SSE transport for MCP.
"""
from .http import HttpTransport

class SseTransport(HttpTransport):
    """
    Server-Sent Events transport.
    Extends HttpTransport but adds event stream handling.
    """
    pass
