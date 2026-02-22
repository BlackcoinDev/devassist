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
Security Audit Logger for DevAssist.

This module provides structured security event logging for debugging,
forensics, and compliance purposes. All security-relevant events are
logged with consistent formatting and categorization.

Events logged:
- Tool approvals/denials
- Shell command blocks
- Path traversal attempts
- File access denials
- Rate limiting triggers
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Security event categories for audit logging."""

    # Tool execution events
    TOOL_APPROVED = "tool_approved"
    TOOL_DENIED = "tool_denied"

    # Shell security events
    SHELL_BLOCKED_COMMAND = "shell_blocked_command"
    SHELL_BLOCKED_PATTERN = "shell_blocked_pattern"
    SHELL_CWD_VIOLATION = "shell_cwd_violation"

    # File security events
    FILE_ACCESS_DENIED = "file_access_denied"

    # Rate limiting events
    RATE_LIMIT_TRIGGERED = "rate_limit_triggered"


class AuditLogger:
    """
    Structured security audit logger.

    Provides consistent logging format for security events with
    optional file output for persistent audit trails.
    """

    _instance: Optional["AuditLogger"] = None
    _audit_file: Optional[Path] = None

    def __new__(cls) -> "AuditLogger":
        """Singleton pattern for global audit logger."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize audit logger (only once due to singleton)."""
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._audit_file = None

    def configure(self, audit_file_path: Optional[str] = None) -> None:
        """
        Configure the audit logger with optional file output.

        Args:
            audit_file_path: Optional path to audit log file
        """
        if audit_file_path:
            self._audit_file = Path(audit_file_path)
            # Ensure parent directory exists
            self._audit_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Security audit logging to: {self._audit_file}")

    def log_event(
        self,
        event_type: SecurityEventType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ) -> None:
        """
        Log a security event.

        Args:
            event_type: Category of security event
            message: Human-readable description
            details: Optional structured data about the event
            severity: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "severity": severity,
            "message": message,
            "details": details or {}
        }

        # Format for console logging
        log_message = f"[SECURITY] {event_type.value}: {message}"
        if details:
            # Truncate details for console (avoid flooding)
            details_str = json.dumps(details, default=str)
            if len(details_str) > 200:
                details_str = details_str[:200] + "..."
            log_message += f" | {details_str}"

        # Log to appropriate level
        log_level = getattr(logging, severity.upper(), logging.INFO)
        logger.log(log_level, log_message)

        # Write to audit file if configured
        if self._audit_file:
            self._write_to_file(event)

    def _write_to_file(self, event: Dict[str, Any]) -> None:
        """Write event to audit log file as JSON line."""
        if self._audit_file is None:
            return
        try:
            with open(self._audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    # Convenience methods for common events

    def log_tool_approved(
        self,
        tool_name: str,
        args: Dict[str, Any],
        approval_type: str = "user"
    ) -> None:
        """Log tool approval event."""
        self.log_event(
            SecurityEventType.TOOL_APPROVED,
            f"Tool '{tool_name}' approved ({approval_type})",
            {"tool": tool_name, "args": args, "approval_type": approval_type}
        )

    def log_tool_denied(
        self,
        tool_name: str,
        args: Dict[str, Any],
        reason: str
    ) -> None:
        """Log tool denial event."""
        self.log_event(
            SecurityEventType.TOOL_DENIED,
            f"Tool '{tool_name}' denied: {reason}",
            {"tool": tool_name, "args": args, "reason": reason},
            severity="WARNING"
        )

    def log_shell_blocked(
        self,
        command: str,
        reason: str,
        pattern: Optional[str] = None
    ) -> None:
        """Log blocked shell command."""
        details = {"command": command, "reason": reason}
        if pattern:
            details["matched_pattern"] = pattern

        event_type = (
            SecurityEventType.SHELL_BLOCKED_PATTERN
            if pattern
            else SecurityEventType.SHELL_BLOCKED_COMMAND
        )

        self.log_event(
            event_type,
            f"Shell command blocked: {reason}",
            details,
            severity="WARNING"
        )

    def log_path_access_denied(
        self,
        path: str,
        operation: str,
        reason: str
    ) -> None:
        """Log file/directory access denial."""
        self.log_event(
            SecurityEventType.FILE_ACCESS_DENIED,
            f"Access denied to '{path}': {reason}",
            {"path": path, "operation": operation, "reason": reason},
            severity="WARNING"
        )

    def log_cwd_violation(
        self,
        attempted_cwd: str,
        project_root: str
    ) -> None:
        """Log working directory security violation."""
        self.log_event(
            SecurityEventType.SHELL_CWD_VIOLATION,
            f"CWD violation: '{attempted_cwd}' outside project root",
            {"attempted_cwd": attempted_cwd, "project_root": project_root},
            severity="ERROR"
        )

    def log_rate_limit(
        self,
        resource: str,
        current_count: int,
        limit: int
    ) -> None:
        """Log rate limiting trigger."""
        self.log_event(
            SecurityEventType.RATE_LIMIT_TRIGGERED,
            f"Rate limit triggered for '{resource}'",
            {"resource": resource, "count": current_count, "limit": limit},
            severity="WARNING"
        )


# Global singleton instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def configure_audit_logging(audit_file_path: Optional[str] = None) -> None:
    """
    Configure audit logging for the application.

    Args:
        audit_file_path: Optional path to audit log file
    """
    get_audit_logger().configure(audit_file_path)
