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
Tool Approval System - Advanced permission management for AI tools.

This module provides fine-grained control over tool execution with support for:
- Manual policies: always, never, ask
- Automated policies: auto-conservative, auto-permissive
- Wildcard patterns
- Context-aware validation
"""

import json
import logging
import fnmatch
from pathlib import Path
from typing import Dict, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ApprovalPolicy(str, Enum):
    """Available approval policies."""

    ALWAYS = "always"
    NEVER = "never"
    ASK = "ask"
    AUTO_CONSERVATIVE = "auto-conservative"
    AUTO_PERMISSIVE = "auto-permissive"


class ToolApprovalManager:
    """
    Manages tool execution permissions with support for advanced policies.
    """

    def __init__(self, config_path: str = "config/tool_approvals.json"):
        self.config_path = Path(config_path)
        self.approvals: Dict[str, str] = {}
        self.defaults: Dict[str, str] = {
            "builtin": "always",
            "mcp": "ask",
            "global": "ask",
        }
        self.load_config()

    def load_config(self) -> None:
        """Load approval settings from JSON config file."""
        if not self.config_path.exists():
            logger.info(
                f"Tool approval config not found at {self.config_path}. Using defaults."
            )
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.approvals = data.get("approvals", {})
                self.defaults.update(data.get("defaults", {}))
            logger.debug(f"Loaded {len(self.approvals)} tool approval rules.")
        except Exception as e:
            logger.error(f"Error loading tool approval config: {e}")

    def get_policy(self, tool_name: str) -> str:
        """
        Get the configured policy for a tool.
        """
        # 1. Check direct tool name match
        if tool_name in self.approvals:
            return self.approvals[tool_name]

        # 2. Check wildcard patterns
        for pattern, policy in self.approvals.items():
            if fnmatch.fnmatch(tool_name, pattern):
                return policy

        # 3. Fallback to category defaults
        if tool_name.startswith("mcp_"):
            return self.defaults.get("mcp", "ask")

        return self.defaults.get("builtin", "always")

    def requires_approval(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        baseline: bool = False,
        llm_guess: Optional[bool] = None,
    ) -> bool:
        """
        Determine if a tool call requires user confirmation based on policy.

        Args:
            tool_name: Name of the tool
            tool_args: Tool arguments
            baseline: The baseline 'is_safe' result from security validators
            llm_guess: Optional AI guess if the action is irreversible/dangerous

        Returns:
            bool: True if user approval is required
        """
        policy = self.get_policy(tool_name)

        if policy == ApprovalPolicy.ALWAYS:
            return False
        if policy == ApprovalPolicy.NEVER:
            return True  # Will be blocked in registry
        if policy == ApprovalPolicy.ASK:
            return not baseline  # If baseline is safe, don't ask, else ask

        # Advanced policies
        if policy == ApprovalPolicy.AUTO_CONSERVATIVE:
            # Requires approval if NOT baseline safe OR if AI thinks it's dangerous
            return (not baseline) or (llm_guess is True)

        if policy == ApprovalPolicy.AUTO_PERMISSIVE:
            # Requires approval only if AI explicitly thinks it's dangerous
            return llm_guess is True

        return True  # Default to secure 'ask'

    def check_approval(
        self, tool_name: str, tool_args: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        High-level check used by ToolRegistry.
        Returns 'always', 'ask', or 'never'.
        """
        policy = self.get_policy(tool_name)

        # Immediate returns for static policies
        if policy in [ApprovalPolicy.ALWAYS, ApprovalPolicy.NEVER, ApprovalPolicy.ASK]:
            # For shell_execute, ask 'ShellSecurity' first
            if tool_name == "shell_execute" and tool_args:
                from src.security.shell_security import ShellSecurity

                command = tool_args.get("command", "")
                try:
                    status, _, _ = ShellSecurity.validate_command(command)
                    if status == "blocked":
                        return ApprovalPolicy.NEVER
                    if status == "safe" and policy == ApprovalPolicy.ASK:
                        return ApprovalPolicy.ALWAYS
                except Exception:
                    return ApprovalPolicy.NEVER
            return str(policy)

        # For auto policies, default to 'ask' in the registry.
        # The ChatLoop will refine this by calling requires_approval with more context.
        return ApprovalPolicy.ASK

    def set_policy(self, tool_name: str, policy: str) -> bool:
        """
        Set and persist a policy for a tool.
        """
        if policy not in [p.value for p in ApprovalPolicy]:
            logger.error(f"Invalid policy: {policy}")
            return False

        self.approvals[tool_name] = policy

        try:
            # Load existing file to preserve structure if possible
            data = {
                "version": "1.0",
                "approvals": self.approvals,
                "defaults": self.defaults,
            }
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    try:
                        existing = json.load(f)
                        data["version"] = existing.get("version", "1.0")
                        data["defaults"] = existing.get("defaults", self.defaults)
                    except Exception:
                        pass  # Non-critical - use defaults if file is malformed
                        pass

            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save tool approval config: {e}")
            return False
