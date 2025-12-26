#!/usr/bin/env python3
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
Test suite for CommandRegistry - Plugin system for slash commands.

Tests cover:
- Decorator-based registration
- Command dispatch and execution
- Alias handling
- Category organization
- Error handling
- Registry introspection methods
"""

from unittest.mock import Mock, patch
from src.commands.registry import CommandRegistry, register_command


class TestCommandRegistration:
    """Test command registration via decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        CommandRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        CommandRegistry.clear()

    def test_register_simple_command(self):
        """Test registering a basic command."""

        @CommandRegistry.register("test")
        def handle_test(args):
            return "executed"

        assert CommandRegistry.has_command("test")
        assert "test" in CommandRegistry.get_commands()

    def test_register_with_description(self):
        """Test registering command with description."""

        @CommandRegistry.register("help", "Show help text")
        def handle_help(args):
            pass

        commands = CommandRegistry.get_commands()
        assert commands["help"] == "Show help text"

    def test_register_with_category(self):
        """Test registering command with category."""

        @CommandRegistry.register("config", "Config command", category="settings")
        def handle_config(args):
            pass

        categories = CommandRegistry.get_categories()
        assert "settings" in categories
        assert "config" in categories["settings"]

    def test_register_with_aliases(self):
        """Test registering command with aliases."""

        @CommandRegistry.register("help", "Show help", aliases=["h", "?"])
        def handle_help(args):
            return "help"

        assert CommandRegistry.has_command("help")
        assert CommandRegistry.has_command("h")
        assert CommandRegistry.has_command("?")

    def test_register_command_convenience_function(self):
        """Test using register_command convenience function."""

        @register_command("test", "Test command")
        def handle_test(args):
            pass

        assert CommandRegistry.has_command("test")


class TestCommandDispatch:
    """Test command execution and dispatch."""

    def setup_method(self):
        """Clear registry and set up test commands."""
        CommandRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        CommandRegistry.clear()

    def test_dispatch_registered_command(self):
        """Test dispatching a registered command."""
        mock_handler = Mock()

        @CommandRegistry.register("test")
        def handle_test(args):
            mock_handler(args)

        result = CommandRegistry.dispatch("test", ["arg1", "arg2"])

        assert result is True
        mock_handler.assert_called_once_with(["arg1", "arg2"])

    def test_dispatch_unknown_command(self):
        """Test dispatching an unregistered command."""
        result = CommandRegistry.dispatch("unknown", [])
        assert result is False

    def test_dispatch_with_alias(self):
        """Test dispatching via alias."""
        mock_handler = Mock()

        @CommandRegistry.register("help", aliases=["h"])
        def handle_help(args):
            mock_handler(args)

        result = CommandRegistry.dispatch("h", [])

        assert result is True
        mock_handler.assert_called_once()

    def test_dispatch_with_error_handling(self):
        """Test that errors during execution are caught."""

        @CommandRegistry.register("error")
        def handle_error(args):
            raise ValueError("Test error")

        # Should return True (command found) but not raise exception
        with patch("src.commands.registry.logger") as mock_logger:
            result = CommandRegistry.dispatch("error", [])
            assert result is True
            mock_logger.error.assert_called_once()

    def test_dispatch_empty_args(self):
        """Test dispatching with empty arguments."""
        called = []

        @CommandRegistry.register("test")
        def handle_test(args):
            called.append(args)

        CommandRegistry.dispatch("test", [])
        assert called == [[]]


class TestRegistryIntrospection:
    """Test registry query and introspection methods."""

    def setup_method(self):
        """Clear registry and register test commands."""
        CommandRegistry.clear()

        @CommandRegistry.register("help", "Show help", category="info")
        def handle_help(args):
            pass

        @CommandRegistry.register("config", "Configure app", category="settings")
        def handle_config(args):
            pass

        @CommandRegistry.register("debug", "Debug mode", category="settings")
        def handle_debug(args):
            pass

    def teardown_method(self):
        """Clear registry after each test."""
        CommandRegistry.clear()

    def test_get_commands_returns_copy(self):
        """Test that get_commands returns a copy, not reference."""
        commands = CommandRegistry.get_commands()
        commands["fake"] = "Fake command"

        # Original should not be modified
        assert "fake" not in CommandRegistry.get_commands()

    def test_get_categories_groups_correctly(self):
        """Test that commands are grouped by category."""
        categories = CommandRegistry.get_categories()

        assert "info" in categories
        assert "settings" in categories
        assert "help" in categories["info"]
        assert "config" in categories["settings"]
        assert "debug" in categories["settings"]

    def test_get_categories_returns_copy(self):
        """Test that get_categories returns a copy."""
        categories = CommandRegistry.get_categories()
        categories["fake"] = ["fake"]

        # Original should not be modified
        assert "fake" not in CommandRegistry.get_categories()

    def test_has_command_positive(self):
        """Test has_command returns True for registered commands."""
        assert CommandRegistry.has_command("help") is True
        assert CommandRegistry.has_command("config") is True

    def test_has_command_negative(self):
        """Test has_command returns False for unregistered commands."""
        assert CommandRegistry.has_command("unknown") is False
        assert CommandRegistry.has_command("") is False

    def test_clear_removes_all_commands(self):
        """Test that clear removes all registered commands."""
        assert CommandRegistry.has_command("help")

        CommandRegistry.clear()

        assert not CommandRegistry.has_command("help")
        assert len(CommandRegistry.get_commands()) == 0
        assert len(CommandRegistry.get_categories()) == 0


class TestMultipleRegistrations:
    """Test edge cases with multiple registrations."""

    def setup_method(self):
        """Clear registry before each test."""
        CommandRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        CommandRegistry.clear()

    def test_reregister_same_name_overwrites(self):
        """Test that re-registering a command overwrites previous."""

        @CommandRegistry.register("test")
        def handler1(args):
            return "first"

        @CommandRegistry.register("test")
        def handler2(args):
            return "second"

        # Second registration should overwrite
        result = []
        CommandRegistry._commands["test"](result)
        # The function reference should be handler2
        assert CommandRegistry._commands["test"] is handler2

    def test_multiple_categories(self):
        """Test commands across multiple categories."""

        @CommandRegistry.register("cmd1", category="cat1")
        def h1(args):
            pass

        @CommandRegistry.register("cmd2", category="cat2")
        def h2(args):
            pass

        @CommandRegistry.register("cmd3", category="cat1")
        def h3(args):
            pass

        categories = CommandRegistry.get_categories()
        assert len(categories["cat1"]) == 2
        assert len(categories["cat2"]) == 1

    def test_alias_to_different_commands(self):
        """Test that different commands can have same alias behavior."""

        @CommandRegistry.register("cmd1", aliases=["a"])
        def h1(args):
            return "cmd1"

        # This will overwrite alias "a"
        @CommandRegistry.register("cmd2", aliases=["a"])
        def h2(args):
            return "cmd2"

        # Last registration wins
        assert CommandRegistry.has_command("a")
        assert CommandRegistry._commands["a"] is h2


class TestCommandArguments:
    """Test command argument handling."""

    def setup_method(self):
        """Clear registry before each test."""
        CommandRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        CommandRegistry.clear()

    def test_command_receives_args_list(self):
        """Test that commands receive arguments as list."""
        received_args = []

        @CommandRegistry.register("test")
        def handle_test(args):
            received_args.extend(args)

        CommandRegistry.dispatch("test", ["arg1", "arg2", "arg3"])
        assert received_args == ["arg1", "arg2", "arg3"]

    def test_command_with_complex_args(self):
        """Test commands can receive complex argument types."""
        received_args = []

        @CommandRegistry.register("test")
        def handle_test(args):
            received_args.append(args)

        test_args = [{"key": "value"}, 123, ["nested", "list"]]
        CommandRegistry.dispatch("test", test_args)
        assert received_args[0] == test_args
