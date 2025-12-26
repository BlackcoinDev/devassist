#!/usr/bin/env python3
"""
Unit tests for Space Commands Handler.

Tests cover:
- Show current space
- List all spaces (success and failure)
- Create space (success, missing name, failure)
- Switch space (success, missing name, failure)
- Delete space (success, cancel, current space, failure)
- Unknown command handling
"""

import unittest
from io import StringIO
import sys
from unittest.mock import patch, MagicMock
from src.commands.handlers.space_commands import handle_space


class TestSpaceShowCurrent(unittest.TestCase):
    """Test showing current space."""

    @patch("src.commands.handlers.space_commands.get_context")
    def test_show_current_space_no_args(self, mock_get_ctx):
        """Test /space with no arguments shows current space."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "my-project"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space([])
        sys.stdout = sys.__stdout__

        self.assertIn("my-project", captured.getvalue())

    @patch("src.commands.handlers.space_commands.get_context")
    def test_show_current_space_empty_string(self, mock_get_ctx):
        """Test /space with empty string shows current space."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space("")
        sys.stdout = sys.__stdout__

        self.assertIn("default", captured.getvalue())


class TestSpaceList(unittest.TestCase):
    """Test listing spaces."""

    @patch("src.commands.handlers.space_commands.list_spaces")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_list_spaces_success(self, mock_get_ctx, mock_list):
        """Test listing multiple spaces."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "project-a"
        mock_get_ctx.return_value = mock_ctx
        mock_list.return_value = ["default", "project-a", "project-b"]

        captured = StringIO()
        sys.stdout = captured
        handle_space(["list"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("default", output)
        self.assertIn("project-a", output)
        self.assertIn("project-b", output)
        self.assertIn("← current", output)

    @patch("src.commands.handlers.space_commands.list_spaces")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_list_spaces_empty(self, mock_get_ctx, mock_list):
        """Test listing when no spaces exist."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx
        mock_list.return_value = []

        captured = StringIO()
        sys.stdout = captured
        handle_space(["list"])
        sys.stdout = sys.__stdout__

        self.assertIn("No spaces found", captured.getvalue())

    @patch("src.commands.handlers.space_commands.list_spaces")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_list_spaces_error(self, mock_get_ctx, mock_list):
        """Test listing spaces when an error occurs."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx
        mock_list.side_effect = Exception("Database error")

        captured = StringIO()
        sys.stdout = captured
        handle_space(["list"])
        sys.stdout = sys.__stdout__

        self.assertIn("Error listing spaces", captured.getvalue())


class TestSpaceCreate(unittest.TestCase):
    """Test creating spaces."""

    @patch("src.commands.handlers.space_commands.ensure_space_collection")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_create_space_success(self, mock_get_ctx, mock_ensure):
        """Test creating a new space."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["create", "new-space"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Created", output)
        self.assertIn("new-space", output)
        mock_ensure.assert_called_once_with("new-space")
        self.assertEqual(mock_ctx.current_space, "new-space")

    @patch("src.commands.handlers.space_commands.get_context")
    def test_create_space_missing_name(self, mock_get_ctx):
        """Test creating space without name shows usage."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["create"])
        sys.stdout = sys.__stdout__

        self.assertIn("Usage:", captured.getvalue())

    @patch("src.commands.handlers.space_commands.ensure_space_collection")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_create_space_error(self, mock_get_ctx, mock_ensure):
        """Test creating space when an error occurs."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx
        mock_ensure.side_effect = Exception("Creation failed")

        captured = StringIO()
        sys.stdout = captured
        handle_space(["create", "bad-space"])
        sys.stdout = sys.__stdout__

        self.assertIn("Error creating space", captured.getvalue())


class TestSpaceSwitch(unittest.TestCase):
    """Test switching spaces."""

    @patch("src.commands.handlers.space_commands.get_context")
    def test_switch_space_success(self, mock_get_ctx):
        """Test switching to a different space."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["switch", "project-x"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Switched", output)
        self.assertIn("project-x", output)
        self.assertEqual(mock_ctx.current_space, "project-x")

    @patch("src.commands.handlers.space_commands.get_context")
    def test_switch_space_missing_name(self, mock_get_ctx):
        """Test switching space without name shows usage."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["switch"])
        sys.stdout = sys.__stdout__

        self.assertIn("Usage:", captured.getvalue())

    @patch("src.commands.handlers.space_commands.get_context")
    def test_switch_space_error(self, mock_get_ctx):
        """Test switching space when an error occurs."""
        mock_ctx = MagicMock()
        # Simulate property setter raising exception
        type(mock_ctx).current_space = property(
            lambda self: "default",
            lambda self, val: (_ for _ in ()).throw(Exception("Switch failed")),
        )
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["switch", "bad-space"])
        sys.stdout = sys.__stdout__

        self.assertIn("Error switching space", captured.getvalue())


class TestSpaceDelete(unittest.TestCase):
    """Test deleting spaces."""

    @patch("builtins.input", return_value="yes")
    @patch("src.commands.handlers.space_commands.delete_space")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_delete_space_success(self, mock_get_ctx, mock_delete, mock_input):
        """Test deleting a space with confirmation."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["delete", "old-space"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Deleted", output)
        self.assertIn("old-space", output)
        mock_delete.assert_called_once_with("old-space")

    @patch("src.commands.handlers.space_commands.get_context")
    def test_delete_space_missing_name(self, mock_get_ctx):
        """Test deleting space without name shows usage."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["delete"])
        sys.stdout = sys.__stdout__

        self.assertIn("Usage:", captured.getvalue())

    @patch("src.commands.handlers.space_commands.get_context")
    def test_delete_current_space_blocked(self, mock_get_ctx):
        """Test cannot delete current space."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "active-project"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["delete", "active-project"])
        sys.stdout = sys.__stdout__

        self.assertIn("Cannot delete the current space", captured.getvalue())

    @patch("builtins.input", return_value="no")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_delete_space_cancelled(self, mock_get_ctx, mock_input):
        """Test deletion cancelled by user."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["delete", "some-space"])
        sys.stdout = sys.__stdout__

        self.assertIn("cancelled", captured.getvalue())

    @patch("builtins.input", return_value="yes")
    @patch("src.commands.handlers.space_commands.delete_space")
    @patch("src.commands.handlers.space_commands.get_context")
    def test_delete_space_error(self, mock_get_ctx, mock_delete, mock_input):
        """Test deleting space when an error occurs."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx
        mock_delete.side_effect = Exception("Delete failed")

        captured = StringIO()
        sys.stdout = captured
        handle_space(["delete", "problem-space"])
        sys.stdout = sys.__stdout__

        self.assertIn("Error deleting space", captured.getvalue())


class TestSpaceUnknownCommand(unittest.TestCase):
    """Test unknown command handling."""

    @patch("src.commands.handlers.space_commands.get_context")
    def test_unknown_command(self, mock_get_ctx):
        """Test unknown space subcommand shows help."""
        mock_ctx = MagicMock()
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space(["unknown"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Unknown space command", output)
        self.assertIn("Usage:", output)


class TestSpaceStringArgs(unittest.TestCase):
    """Test that string arguments are handled correctly."""

    @patch("src.commands.handlers.space_commands.get_context")
    def test_args_as_string(self, mock_get_ctx):
        """Test handling args as string instead of list."""
        mock_ctx = MagicMock()
        mock_ctx.current_space = "default"
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_space("switch new-project")  # String instead of list
        sys.stdout = sys.__stdout__

        self.assertIn("Switched", captured.getvalue())
        self.assertEqual(mock_ctx.current_space, "new-project")


if __name__ == "__main__":
    unittest.main()
