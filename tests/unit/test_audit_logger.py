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


"""Tests for the security audit logger module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.security.audit_logger import (
    AuditLogger,
    SecurityEventType,
    get_audit_logger,
    configure_audit_logging,
)


class TestSecurityEventType:
    """Test SecurityEventType enum."""

    def test_event_types_exist(self):
        """Test that all expected event types are defined."""
        assert SecurityEventType.TOOL_APPROVED.value == "tool_approved"
        assert SecurityEventType.SHELL_BLOCKED_COMMAND.value == "shell_blocked_command"
        assert SecurityEventType.FILE_ACCESS_DENIED.value == "file_access_denied"
        assert SecurityEventType.RATE_LIMIT_TRIGGERED.value == "rate_limit_triggered"

    def test_event_types_are_strings(self):
        """Test that event type values are strings."""
        for event_type in SecurityEventType:
            assert isinstance(event_type.value, str)


class TestAuditLogger:
    """Test AuditLogger class."""

    def test_singleton_pattern(self):
        """Test that AuditLogger is a singleton."""
        logger1 = AuditLogger()
        logger2 = AuditLogger()
        assert logger1 is logger2

    def test_log_event_logs_to_logger(self):
        """Test that log_event logs to the Python logger."""
        audit_logger = get_audit_logger()

        with patch("src.security.audit_logger.logger") as mock_logger:
            audit_logger.log_event(
                SecurityEventType.TOOL_APPROVED,
                "Test message",
                {"key": "value"}
            )

            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args
            assert "[SECURITY]" in call_args[0][1]

    def test_log_event_writes_to_file(self):
        """Test that log_event writes to audit file when configured."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            audit_file = Path(tmp_dir) / "audit.log"
            audit_logger = get_audit_logger()
            audit_logger.configure(str(audit_file))

            audit_logger.log_event(
                SecurityEventType.SHELL_BLOCKED_COMMAND,
                "Command blocked",
                {"command": "rm -rf /"}
            )

            assert audit_file.exists()
            content = audit_file.read_text()
            event = json.loads(content.strip())
            assert event["event_type"] == "shell_blocked_command"
            assert event["message"] == "Command blocked"
            assert event["details"]["command"] == "rm -rf /"

            # Reset for other tests
            audit_logger._audit_file = None

    def test_log_tool_approved(self):
        """Test log_tool_approved convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_tool_approved(
                "shell_execute",
                {"command": "ls"},
                "auto"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == SecurityEventType.TOOL_APPROVED
            assert "shell_execute" in call_args[0][1]

    def test_log_tool_denied(self):
        """Test log_tool_denied convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_tool_denied(
                "shell_execute",
                {"command": "rm -rf /"},
                "Dangerous command"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == SecurityEventType.TOOL_DENIED
            assert call_args[1]["severity"] == "WARNING"

    def test_log_shell_blocked(self):
        """Test log_shell_blocked convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_shell_blocked("rm -rf /", "Blocked command")

            mock_log.assert_called_once()
            assert mock_log.call_args[0][0] == SecurityEventType.SHELL_BLOCKED_COMMAND

    def test_log_shell_blocked_with_pattern(self):
        """Test log_shell_blocked with pattern sets correct event type."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_shell_blocked(
                "cat file | grep pattern",
                "Pipe character blocked",
                pattern="|"
            )

            mock_log.assert_called_once()
            assert mock_log.call_args[0][0] == SecurityEventType.SHELL_BLOCKED_PATTERN

    def test_log_path_access_denied(self):
        """Test log_path_access_denied convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_path_access_denied(
                "/etc/passwd",
                "read",
                "Path outside sandbox"
            )

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == SecurityEventType.FILE_ACCESS_DENIED
            assert "/etc/passwd" in call_args[0][1]

    def test_log_cwd_violation(self):
        """Test log_cwd_violation convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_cwd_violation("/tmp/outside", "/home/project")

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == SecurityEventType.SHELL_CWD_VIOLATION
            assert call_args[1]["severity"] == "ERROR"

    def test_log_rate_limit(self):
        """Test log_rate_limit convenience method."""
        audit_logger = get_audit_logger()

        with patch.object(audit_logger, "log_event") as mock_log:
            audit_logger.log_rate_limit("api_calls", 100, 100)

            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[0][0] == SecurityEventType.RATE_LIMIT_TRIGGERED


class TestModuleFunctions:
    """Test module-level functions."""

    def test_get_audit_logger_returns_singleton(self):
        """Test get_audit_logger returns singleton instance."""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()
        assert logger1 is logger2

    def test_configure_audit_logging(self):
        """Test configure_audit_logging configures the logger."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            audit_file = Path(tmp_dir) / "test.log"
            configure_audit_logging(str(audit_file))

            logger = get_audit_logger()
            assert logger._audit_file == audit_file

            # Reset
            logger._audit_file = None
