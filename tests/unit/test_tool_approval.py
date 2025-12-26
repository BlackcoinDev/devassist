#!/usr/bin/env python3
"""
Unit tests for Tool Approval System.

Tests cover:
- Approval policies (always, never, ask, auto-conservative, auto-permissive)
- Tool policy resolution and matching
- Wildcard pattern matching
- Configuration loading and persistence
- Shell command security integration
- Edge cases and error handling
"""

import unittest
import tempfile
import json
from pathlib import Path
from src.tools.approval import ToolApprovalManager


class TestApprovalPolicies(unittest.TestCase):
    """Test basic approval policies."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_approval_policy_always(self):
        """Test ALWAYS approval policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["safe_tool"] = "always"

        result = manager.requires_approval("safe_tool", {})

        self.assertFalse(result)  # Always means no approval needed

    def test_approval_policy_never(self):
        """Test NEVER approval policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["dangerous_tool"] = "never"

        result = manager.requires_approval("dangerous_tool", {})

        self.assertTrue(result)  # Never means approval required (will be blocked)

    def test_approval_policy_ask_safe(self):
        """Test ASK policy with safe baseline."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["neutral_tool"] = "ask"

        # baseline=True means operation is safe
        result = manager.requires_approval("neutral_tool", {}, baseline=True)

        self.assertFalse(result)  # Safe baseline, so don't ask

    def test_approval_policy_ask_unsafe(self):
        """Test ASK policy with unsafe baseline."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["neutral_tool"] = "ask"

        # baseline=False means operation is not safe
        result = manager.requires_approval("neutral_tool", {}, baseline=False)

        self.assertTrue(result)  # Not safe, so ask

    def test_approval_policy_auto_conservative_safe(self):
        """Test AUTO_CONSERVATIVE with safe baseline."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["smart_tool"] = "auto-conservative"

        # Safe baseline and no LLM warning
        result = manager.requires_approval(
            "smart_tool", {}, baseline=True, llm_guess=False
        )

        self.assertFalse(result)

    def test_approval_policy_auto_conservative_dangerous_ai(self):
        """Test AUTO_CONSERVATIVE when AI thinks it's dangerous."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["smart_tool"] = "auto-conservative"

        # AI thinks it's dangerous
        result = manager.requires_approval(
            "smart_tool", {}, baseline=True, llm_guess=True
        )

        self.assertTrue(result)  # AI thinks dangerous, ask

    def test_approval_policy_auto_permissive_safe(self):
        """Test AUTO_PERMISSIVE with safe baseline."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["permissive_tool"] = "auto-permissive"

        # Safe baseline but not explicitly dangerous
        result = manager.requires_approval(
            "permissive_tool", {}, baseline=False, llm_guess=False
        )

        self.assertFalse(result)

    def test_approval_policy_auto_permissive_dangerous(self):
        """Test AUTO_PERMISSIVE when AI thinks it's dangerous."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["permissive_tool"] = "auto-permissive"

        # AI thinks it's dangerous
        result = manager.requires_approval(
            "permissive_tool", {}, baseline=False, llm_guess=True
        )

        self.assertTrue(result)


class TestPolicyResolution(unittest.TestCase):
    """Test policy resolution and matching."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_direct_tool_name_match(self):
        """Test direct tool name matching."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["read_file"] = "always"

        policy = manager.get_policy("read_file")

        self.assertEqual(policy, "always")

    def test_default_builtin_tools(self):
        """Test default policy for built-in tools."""
        manager = ToolApprovalManager(self.config_path)

        policy = manager.get_policy("read_file")

        self.assertEqual(policy, "always")

    def test_default_mcp_tools(self):
        """Test default policy for MCP tools."""
        manager = ToolApprovalManager(self.config_path)

        policy = manager.get_policy("mcp_database_query")

        self.assertEqual(policy, "ask")

    def test_unknown_tool_fallback(self):
        """Test fallback for unknown tools."""
        manager = ToolApprovalManager(self.config_path)

        policy = manager.get_policy("unknown_tool")

        # Should fall back to builtin default
        self.assertEqual(policy, "always")


class TestWildcardPatterns(unittest.TestCase):
    """Test wildcard pattern matching."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_wildcard_all_mcp_tools(self):
        """Test wildcard for all MCP tools."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["mcp_*"] = "never"

        policy1 = manager.get_policy("mcp_database_query")
        policy2 = manager.get_policy("mcp_web_fetch")
        policy3 = manager.get_policy("read_file")  # Non-MCP tool

        self.assertEqual(policy1, "never")
        self.assertEqual(policy2, "never")
        self.assertEqual(policy3, "always")  # Uses default

    def test_wildcard_specific_prefix(self):
        """Test wildcard for specific tool prefix."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["mcp_database_*"] = "ask"

        policy1 = manager.get_policy("mcp_database_query")
        policy2 = manager.get_policy("mcp_database_insert")
        policy3 = manager.get_policy("mcp_web_fetch")

        self.assertEqual(policy1, "ask")
        self.assertEqual(policy2, "ask")
        self.assertEqual(policy3, "ask")  # Falls back to mcp default

    def test_wildcard_question_mark_single_char(self):
        """Test wildcard with single character match."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["git_?og"] = "never"

        policy1 = manager.get_policy("git_log")
        policy2 = manager.get_policy("git_dog")
        policy3 = manager.get_policy("git_logs")  # Doesn't match

        self.assertEqual(policy1, "never")
        self.assertEqual(policy2, "never")
        # git_logs should use default
        self.assertNotEqual(policy3, "never")

    def test_wildcard_mcp_specific_server(self):
        """Test wildcard for specific MCP server."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["mcp_sqlite_*"] = "always"

        policy1 = manager.get_policy("mcp_sqlite_query")
        policy2 = manager.get_policy("mcp_sqlite_insert")
        policy3 = manager.get_policy("mcp_postgres_query")

        self.assertEqual(policy1, "always")
        self.assertEqual(policy2, "always")
        self.assertEqual(policy3, "ask")  # Falls back to mcp default


class TestConfigurationManagement(unittest.TestCase):
    """Test configuration loading and persistence."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_load_config_file(self):
        """Test loading configuration from file."""
        config_data = {
            "approvals": {
                "read_file": "always",
                "shell_execute": "ask",
                "write_file": "never",
            },
            "defaults": {"builtin": "always", "mcp": "ask"},
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        manager = ToolApprovalManager(self.config_path)

        self.assertEqual(manager.get_policy("read_file"), "always")
        self.assertEqual(manager.get_policy("shell_execute"), "ask")
        self.assertEqual(manager.get_policy("write_file"), "never")

    def test_config_not_found_uses_defaults(self):
        """Test using defaults when config file doesn't exist."""
        manager = ToolApprovalManager(self.config_path)

        policy = manager.get_policy("read_file")

        self.assertEqual(policy, "always")

    def test_set_policy_creates_config(self):
        """Test that set_policy creates config file if it doesn't exist."""
        manager = ToolApprovalManager(self.config_path)

        success = manager.set_policy("test_tool", "never")

        self.assertTrue(success)
        self.assertTrue(Path(self.config_path).exists())

    def test_set_policy_persists(self):
        """Test that set_policy persists across instances."""
        manager1 = ToolApprovalManager(self.config_path)
        manager1.set_policy("custom_tool", "always")

        manager2 = ToolApprovalManager(self.config_path)
        policy = manager2.get_policy("custom_tool")

        self.assertEqual(policy, "always")

    def test_set_policy_invalid_policy(self):
        """Test that set_policy rejects invalid policies."""
        manager = ToolApprovalManager(self.config_path)

        success = manager.set_policy("tool", "invalid_policy")

        self.assertFalse(success)

    def test_set_policy_preserves_existing_config(self):
        """Test that set_policy preserves existing configuration."""
        config_data = {
            "version": "1.0",
            "approvals": {"existing_tool": "always"},
            "defaults": {"builtin": "ask"},
        }

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        manager = ToolApprovalManager(self.config_path)
        manager.set_policy("new_tool", "never")

        # Reload and check both policies exist
        manager2 = ToolApprovalManager(self.config_path)
        self.assertEqual(manager2.get_policy("existing_tool"), "always")
        self.assertEqual(manager2.get_policy("new_tool"), "never")


class TestShellCommandIntegration(unittest.TestCase):
    """Test integration with shell command security."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_shell_execute_non_ask_policy(self):
        """Test shell_execute with non-ask policies don't invoke ShellSecurity."""
        manager = ToolApprovalManager(self.config_path)

        # Test 'always' policy
        manager.approvals["shell_execute"] = "always"
        result = manager.check_approval("shell_execute", {"command": "ls"})
        self.assertEqual(result, "always")

        # Test 'never' policy
        manager.approvals["shell_execute"] = "never"
        result = manager.check_approval("shell_execute", {"command": "ls"})
        self.assertEqual(result, "never")

    def test_shell_execute_ask_policy_without_args(self):
        """Test shell_execute with ask policy and no command args."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["shell_execute"] = "ask"

        # Without command args, should return 'ask'
        result = manager.check_approval("shell_execute", {})

        self.assertEqual(result, "ask")

    def test_shell_execute_ask_policy_none_args(self):
        """Test shell_execute with ask policy and None args."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["shell_execute"] = "ask"

        # With None args, should handle gracefully
        result = manager.check_approval("shell_execute", None)

        self.assertEqual(result, "ask")


class TestCheckApproval(unittest.TestCase):
    """Test high-level check_approval method."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_check_approval_always_policy(self):
        """Test check_approval with always policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["safe_tool"] = "always"

        result = manager.check_approval("safe_tool")

        self.assertEqual(result, "always")

    def test_check_approval_never_policy(self):
        """Test check_approval with never policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["dangerous_tool"] = "never"

        result = manager.check_approval("dangerous_tool")

        self.assertEqual(result, "never")

    def test_check_approval_ask_policy(self):
        """Test check_approval with ask policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["neutral_tool"] = "ask"

        result = manager.check_approval("neutral_tool")

        self.assertEqual(result, "ask")

    def test_check_approval_auto_conservative_policy(self):
        """Test check_approval with auto-conservative policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["smart_tool"] = "auto-conservative"

        # Auto policies return 'ask' in check_approval (refined later by ChatLoop)
        result = manager.check_approval("smart_tool")

        self.assertEqual(result, "ask")

    def test_check_approval_auto_permissive_policy(self):
        """Test check_approval with auto-permissive policy."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["permissive_tool"] = "auto-permissive"

        result = manager.check_approval("permissive_tool")

        self.assertEqual(result, "ask")

    def test_check_approval_with_tool_args(self):
        """Test check_approval receives tool arguments."""
        manager = ToolApprovalManager(self.config_path)

        # Should not raise exception even with tool_args
        result = manager.check_approval("any_tool", {"arg": "value"})

        self.assertIsNotNone(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Create a temporary config file."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.config_path = f"{self.tmpdir.name}/tool_approvals.json"

    def tearDown(self):
        """Clean up temporary files."""
        self.tmpdir.cleanup()

    def test_empty_tool_name(self):
        """Test handling of empty tool name."""
        manager = ToolApprovalManager(self.config_path)

        policy = manager.get_policy("")

        # Should return some default policy
        self.assertIsNotNone(policy)

    def test_none_llm_guess(self):
        """Test with None llm_guess parameter."""
        manager = ToolApprovalManager(self.config_path)

        result = manager.requires_approval("tool", {}, baseline=False, llm_guess=None)

        # Should handle None llm_guess gracefully
        self.assertIsInstance(result, bool)

    def test_empty_tool_args(self):
        """Test with empty tool_args."""
        manager = ToolApprovalManager(self.config_path)

        result = manager.requires_approval("tool", {})

        self.assertIsInstance(result, bool)

    def test_invalid_config_json(self):
        """Test handling of invalid JSON in config file."""
        with open(self.config_path, "w") as f:
            f.write("{ invalid json }")

        manager = ToolApprovalManager(self.config_path)

        # Should fall back to defaults
        policy = manager.get_policy("read_file")
        self.assertEqual(policy, "always")

    def test_config_with_missing_approvals_key(self):
        """Test config file with missing approvals key."""
        config_data = {"defaults": {"builtin": "ask"}}

        with open(self.config_path, "w") as f:
            json.dump(config_data, f)

        manager = ToolApprovalManager(self.config_path)

        # Should use defaults
        policy = manager.get_policy("read_file")
        self.assertEqual(policy, "ask")  # Uses overridden default

    def test_case_sensitivity_tool_names(self):
        """Test that tool names are case-sensitive."""
        manager = ToolApprovalManager(self.config_path)
        manager.approvals["MyTool"] = "always"

        policy1 = manager.get_policy("MyTool")
        policy2 = manager.get_policy("mytool")

        self.assertEqual(policy1, "always")
        # Different case should use default (for built-in tools, that's "always")
        self.assertEqual(policy2, "always")  # Falls back to builtin default

    def test_set_policy_all_valid_policies(self):
        """Test that all policy types can be set."""
        manager = ToolApprovalManager(self.config_path)

        for policy_value in [
            "always",
            "never",
            "ask",
            "auto-conservative",
            "auto-permissive",
        ]:
            success = manager.set_policy(f"tool_{policy_value}", policy_value)
            self.assertTrue(success, f"Failed to set policy: {policy_value}")


if __name__ == "__main__":
    unittest.main()
