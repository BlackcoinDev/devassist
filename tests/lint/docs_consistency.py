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
Documentation consistency validation script.
Validates that documentation matches code truth.
"""
import re
from typing import Any
import sys
from pathlib import Path
# Add project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.facts import get_all_facts


def extract_number_from_text(text: str, pattern: str) -> int | None:
    """Extract number from text using regex pattern."""
    match = re.search(pattern, text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def check_readme() -> dict[str, Any]:
    """Check README.md for consistency."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return {"status": "missing", "errors": ["README.md not found"]}

    content = readme_path.read_text()
    facts = get_all_facts()

    results = {"status": "ok", "matches": [], "mismatches": []}

    # Check test count
    test_pattern = (
        r"(\d+)\s*(?:tests?|functional\s+tests?|integration\s+tests?|total\s+tests?)"
    )
    found_test_count = extract_number_from_text(content, test_pattern)

    if found_test_count is not None:
        if found_test_count == facts["test_count"]:
            results["matches"].append(f"Test count: {facts['test_count']}")
        else:
            results["mismatches"].append(
                f"Test count: README says {found_test_count}, actual is {facts['test_count']}"
            )

    return results


def check_architecture() -> dict[str, Any]:
    """Check docs/ARCHITECTURE.md for consistency."""
    arch_path = Path("docs/ARCHITECTURE.md")
    if not arch_path.exists():
        return {"status": "missing", "errors": ["docs/ARCHITECTURE.md not found"]}

    content = arch_path.read_text()
    facts = get_all_facts()

    results = {"status": "ok", "matches": [], "mismatches": []}

    # Check handler count
    handler_pattern = r"(\d+)\s*(?:handlers?|command\s+handlers?)"
    found_handler_count = extract_number_from_text(content, handler_pattern)

    if found_handler_count is not None:
        if found_handler_count == facts["handler_count"]:
            results["matches"].append(f"Handler count: {facts['handler_count']}")
        else:
            results["mismatches"].append(
                f"Handler count: ARCHITECTURE says {found_handler_count}, actual is {facts['handler_count']}"
            )

    # Check tool count
    tool_pattern = r"(\d+)\s*(?:tools?|tool\s+executors?)"
    found_tool_count = extract_number_from_text(content, tool_pattern)

    if found_tool_count is not None:
        if found_tool_count == facts["tool_count"]:
            results["matches"].append(f"Tool count: {facts['tool_count']}")
        else:
            results["mismatches"].append(
                f"Tool count: ARCHITECTURE says {found_tool_count}, actual is {facts['tool_count']}"
            )

    return results


def check_test_plan() -> dict[str, Any]:
    """Check docs/TEST_PLAN.md for consistency."""
    test_plan_path = Path("docs/TEST_PLAN.md")
    if not test_plan_path.exists():
        return {"status": "missing", "errors": ["docs/TEST_PLAN.md not found"]}

    content = test_plan_path.read_text()
    facts = get_all_facts()

    results = {"status": "ok", "matches": [], "mismatches": []}

    # Check test count
    test_pattern = (
        r"(\d+)\s*(?:tests?|test\s+cases?|functional\s+tests?|integration\s+tests?)"
    )
    found_test_count = extract_number_from_text(content, test_pattern)

    if found_test_count is not None:
        if found_test_count == facts["test_count"]:
            results["matches"].append(f"Test count: {facts['test_count']}")
        else:
            results["mismatches"].append(
                f"Test count: TEST_PLAN says {found_test_count}, actual is {facts['test_count']}"
            )

    return results


def check_agents() -> dict[str, Any]:
    """Check AGENTS.md for consistency."""
    agents_path = Path("AGENTS.md")
    if not agents_path.exists():
        return {"status": "missing", "errors": ["AGENTS.md not found"]}

    content = agents_path.read_text()
    facts = get_all_facts()

    results = {"status": "ok", "matches": [], "mismatches": []}

    # Check test count
    test_pattern = (
        r"(\d+)\s*(?:tests?|functional\s+tests?|integration\s+tests?|total\s+tests?)"
    )
    found_test_count = extract_number_from_text(content, test_pattern)

    if found_test_count is not None:
        if found_test_count == facts["test_count"]:
            results["matches"].append(f"Test count: {facts['test_count']}")
        else:
            results["mismatches"].append(
                f"Test count: AGENTS says {found_test_count}, actual is {facts['test_count']}"
            )

    # Check handler count
    handler_pattern = r"(\d+)\s*(?:handlers?|command\s+handlers?)"
    found_handler_count = extract_number_from_text(content, handler_pattern)

    if found_handler_count is not None:
        if found_handler_count == facts["handler_count"]:
            results["matches"].append(f"Handler count: {facts['handler_count']}")
        else:
            results["mismatches"].append(
                f"Handler count: AGENTS says {found_handler_count}, actual is {facts['handler_count']}"
            )

    # Check tool count
    tool_pattern = r"(\d+)\s*(?:tools?|tool\s+executors?)"
    found_tool_count = extract_number_from_text(content, tool_pattern)

    if found_tool_count is not None:
        if found_tool_count == facts["tool_count"]:
            results["matches"].append(f"Tool count: {facts['tool_count']}")
        else:
            results["mismatches"].append(
                f"Tool count: AGENTS says {found_tool_count}, actual is {facts['tool_count']}"
            )

    # Check module count
    module_pattern = r"(\d+)\s*(?:modules?|src\s+modules?|subdirectories?)"
    found_module_count = extract_number_from_text(content, module_pattern)

    if found_module_count is not None:
        if found_module_count == facts["module_count"]:
            results["matches"].append(f"Module count: {facts['module_count']}")
        else:
            results["mismatches"].append(
                f"Module count: AGENTS says {found_module_count}, actual is {facts['module_count']}"
            )

    # Check env var count
    env_pattern = r"(\d+)\s*(?:env\s+vars?|environment\s+variables?|config\s+options?)"
    found_env_count = extract_number_from_text(content, env_pattern)

    if found_env_count is not None:
        actual_env_count = len(facts["env_vars"])
        if found_env_count == actual_env_count:
            results["matches"].append(f"Env var count: {actual_env_count}")
        else:
            results["mismatches"].append(
                f"Env var count: AGENTS says {found_env_count}, actual is {actual_env_count}"
            )

    return results


def main() -> int:
    """Main validation function."""
    print("=== Documentation Consistency Check ===")
    print()

    # Get ground truth
    try:
        facts = get_all_facts()
        print("Ground Truth:")
        print(f"- Tests: {facts['test_count']}")
        print(f"- Handlers: {facts['handler_count']}")
        print(f"- Tools: {facts['tool_count']}")
        print(f"- Modules: {facts['module_count']}")
        print(f"- Env Vars: {len(facts['env_vars'])}")
        print()
    except Exception as e:
        print(f"Error: Could not extract ground truth: {e}")
        return 2

    # Check each documentation file
    all_mismatches = []

    print("Checking README.md...")
    readme_result = check_readme()
    if readme_result.get("status") == "ok":
        for match in readme_result["matches"]:
            print(f"✓ {match}")
        for mismatch in readme_result["mismatches"]:
            print(f"✗ {mismatch}")
            all_mismatches.append(mismatch)
    else:
        print(f"✗ {readme_result['errors'][0]}")
        all_mismatches.append(readme_result["errors"][0])
    print()

    print("Checking docs/ARCHITECTURE.md...")
    arch_result = check_architecture()
    if arch_result.get("status") == "ok":
        for match in arch_result["matches"]:
            print(f"✓ {match}")
        for mismatch in arch_result["mismatches"]:
            print(f"✗ {mismatch}")
            all_mismatches.append(mismatch)
    else:
        print(f"✗ {arch_result['errors'][0]}")
        all_mismatches.append(arch_result["errors"][0])
    print()

    print("Checking docs/TEST_PLAN.md...")
    test_plan_result = check_test_plan()
    if test_plan_result.get("status") == "ok":
        for match in test_plan_result["matches"]:
            print(f"✓ {match}")
        for mismatch in test_plan_result["mismatches"]:
            print(f"✗ {mismatch}")
            all_mismatches.append(mismatch)
    else:
        print(f"✗ {test_plan_result['errors'][0]}")
        all_mismatches.append(test_plan_result["errors"][0])
    print()

    print("Checking AGENTS.md...")
    agents_result = check_agents()
    if agents_result.get("status") == "ok":
        for match in agents_result["matches"]:
            print(f"✓ {match}")
        for mismatch in agents_result["mismatches"]:
            print(f"✗ {mismatch}")
            all_mismatches.append(mismatch)
    else:
        print(f"✗ {agents_result['errors'][0]}")
        all_mismatches.append(agents_result["errors"][0])
    print()

    # Summary
    mismatch_count = len(all_mismatches)
    print(f"Summary: {mismatch_count} mismatches found")

    return 1 if mismatch_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
