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
Project Linting Script v0.3.0
Runs comprehensive linting checks on all code in the project.
"""

import os
import sys
import subprocess
import shlex
import re
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize Rich Console
console = Console()


class LintConfig:
    EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        "venv",
        "node_modules",
        "faiss_index",
        "chroma_data",
        "blackcoin-more",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
    }
    REQUIRED_FILES = [
        "src/main.py",
        "src/gui.py",
        "launcher.py",
        "AGENTS.md",
        "README.md",
        "docs/MIGRATION.md",
    ]
    EXPECTED_DIRS = ["venv", "tests", "src"]


class Linter:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent.resolve()
        self.python_files: List[Path] = []
        self.shell_files: List[Path] = []

    def find_files(self):
        """Locate all relevant files respecting exclusion rules."""
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in LintConfig.EXCLUDED_DIRS]
            for file in files:
                filepath = Path(root) / file
                if file.endswith(".py"):
                    self.python_files.append(filepath)
                elif file.endswith(".sh") or (
                    file.startswith(".") and "bash" in file
                ):  # heuristic for shell files
                    self.shell_files.append(filepath)

    def run_check(self, name: str, command: str) -> bool:
        """Run a shell command and report status."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )

            if result.returncode == 0:
                return True

            # Special handling for tools that might print to stdout even on failure
            error_msg = result.stderr.strip() or result.stdout.strip()

            console.print(f"[bold red]❌ {name} failed:[/bold red]")
            console.print(
                Panel(error_msg, title=f"{name} Output", border_style="red")
            )
            return False
        except Exception as e:
            console.print(f"[bold red]❌ Execution error for {name}: {e}[/bold red]")
            return False

    def check_syntax(self) -> bool:
        """Check Python syntax."""
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        return self.run_check(
            "Syntax Check", f"python3 -m py_compile {files_str}"
        )

    def check_flake8(self) -> bool:
        """Run Flake8."""
        # Relies on setup.cfg for configuration
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        return self.run_check("Flake8", f"flake8 {files_str}")

    def check_autopep8(self) -> bool:
        """Run Autopep8 in diff mode."""
        # Using exit-code to fail if there are diffs
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        # We need to manually check if output is empty because autopep8 --diff returns 0 even if changes
        cmd = f"autopep8 --diff --max-line-length=180 {files_str}"

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=self.root_dir
        )
        if result.stdout.strip():
            console.print("[bold red]❌ Autopep8 found formatting issues:[/bold red]")
            console.print(
                Panel(
                    result.stdout[:2000],
                    title="Autopep8 Diff",
                    border_style="red",
                )
            )
            return False
        return True

    def check_mypy(self) -> bool:
        """Run MyPy."""
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        return self.run_check("MyPy", f"mypy {files_str}")

    def check_bandit(self) -> bool:
        """Run Bandit."""
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        return self.run_check("Bandit", f"bandit -c .bandit -r {files_str}")

    def check_vulture(self) -> bool:
        """Run Vulture with dead code suppression."""
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        cmd = f"vulture {files_str} --ignore-decorators=register,patch,fixture,mock"

        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=self.root_dir
        )
        if result.returncode == 0:
            return True

        # Filter false positives logic
        error_lines = result.stdout.strip().split("\n")
        real_issues = []
        ignore_patterns = [
            "closeEvent",
            "_default_params",
            "handle_",
            "execute_",
            "handler",
            "mock_",
            r"\bh[0-9]\b",
        ]

        for line in error_lines:
            if not any(
                re.search(p, line) if "h" in p else p in line
                for p in ignore_patterns
            ):
                real_issues.append(line)

        if real_issues:
            console.print("[bold red]❌ Vulture found dead code:[/bold red]")
            for issue in real_issues[:10]:
                console.print(f"   {issue}")
            return False

        return True

    def check_codespell(self) -> bool:
        """Run Codespell."""
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.python_files
        )
        return self.run_check("Codespell", f"codespell {files_str}")

    def check_shellcheck(self) -> bool:
        """Run Shellcheck if available."""
        if not self.shell_files:
            return True
        files_str = " ".join(
            shlex.quote(str(f.relative_to(self.root_dir))) for f in self.shell_files
        )

        # Check if shellcheck exists
        if (
            subprocess.run(
                "which shellcheck", shell=True, capture_output=True
            ).returncode
            != 0
        ):
            console.print("[yellow]⚠️ Shellcheck not installed, skipping.[/yellow]")
            return True

        return self.run_check("Shellcheck", f"shellcheck {files_str}")

    def validate_structure(self) -> bool:
        """Validate project structure."""
        missing = []
        for f in LintConfig.REQUIRED_FILES:
            if not (self.root_dir / f).exists():
                missing.append(f)

        for d in LintConfig.EXPECTED_DIRS:
            if not (self.root_dir / d).is_dir():
                missing.append(d + "/")

        if missing:
            console.print(
                "[bold red]❌ Missing required files/directories:[/bold red]"
            )
            for m in missing:
                console.print(f"   {m}")
            return False
        return True

    def run_all(self):
        console.print(
            Panel.fit("🔧 DevAssist Linting Suite v0.3.0", style="bold blue")
        )
        self.find_files()
        console.print(
            f"📁 Found [bold]{len(self.python_files)}[/bold] Python files and [bold]{len(self.shell_files)}[/bold] Shell scripts."
        )

        checks = [
            ("Structure", self.validate_structure),
            ("Syntax", self.check_syntax),
            ("Flake8", self.check_flake8),
            ("Autopep8", self.check_autopep8),
            ("MyPy", self.check_mypy),
            ("Bandit", self.check_bandit),
            ("Vulture", self.check_vulture),
            ("Codespell", self.check_codespell),
            ("Shellcheck", self.check_shellcheck),
        ]

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            for name, func in checks:
                task_id = progress.add_task(f"Running {name}...", total=1)
                passed = func()
                progress.update(task_id, completed=1)
                results.append((name, passed))
                if not passed:
                    # Continue running other checks to show full report
                    pass

        # Summary Table
        table = Table(title="Linting Results")
        table.add_column("Check", style="cyan")
        table.add_column("Status", justify="center")

        success = True
        for name, passed in results:
            status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
            table.add_row(name, status)
            if not passed:
                success = False

        console.print(table)

        if success:
            console.print(
                Panel("🎉 All checks passed! Ready to commit.", style="green")
            )
            sys.exit(0)
        else:
            console.print(
                Panel(
                    "❌ Some checks failed. Please fix them before committing.",
                    style="red",
                )
            )
            sys.exit(1)


if __name__ == "__main__":
    Linter().run_all()
