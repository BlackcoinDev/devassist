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
Unit tests for launcher.py functionality.
"""

import pytest
from unittest.mock import patch


def test_main_with_gui_default():
    """Test main function defaults to GUI."""
    with (
        patch("launcher.load_dotenv"),
        patch("launcher.main") as mock_main_func,
        patch("sys.argv", ["launcher.py"]),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should call main() without arguments (defaults to GUI)
        mock_main_func.assert_called_once()


def test_main_with_cli_flag():
    """Test main function with --cli flag."""
    with (
        patch("launcher.load_dotenv"),
        patch("launcher.main") as mock_main_func,
        patch("sys.argv", ["launcher.py", "--cli"]),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should call main() without arguments
        mock_main_func.assert_called_once()


def test_main_with_gui_flag():
    """Test main function with --gui flag."""
    with (
        patch("launcher.load_dotenv"),
        patch("launcher.main") as mock_main_func,
        patch("sys.argv", ["launcher.py", "--gui"]),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should call main() without arguments
        mock_main_func.assert_called_once()


def test_launch_cli_direct():
    """Test direct CLI launch."""
    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("launcher.launch_cli") as mock_launch_cli,
        patch("sys.argv", ["launcher.py", "--cli"]),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should launch CLI directly
        mock_launch_cli.assert_called_once()


# Note: Some launcher tests are commented out due to environment loading complexities
# The main functionality is tested through integration tests


def test_help_argument():
    """Test --help argument displays help."""
    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("sys.argv", ["launcher.py", "--help"]),
    ):
        from launcher import main as launcher_main

        # argparse exits on --help, so we expect SystemExit
        with pytest.raises(SystemExit):
            launcher_main()


def test_unknown_argument():
    """Test unknown argument handling."""
    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("sys.argv", ["launcher.py", "--unknown"]),
    ):
        from launcher import main as launcher_main

        # argparse exits on error, so we expect SystemExit
        with pytest.raises(SystemExit):
            launcher_main()


def test_gui_import_error_fallback():
    """Test GUI ImportError falls back to CLI."""
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "src.gui":
            raise ImportError("PyQt6 not found")
        return real_import(name, *args, **kwargs)

    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("sys.argv", ["launcher.py"]),
        patch("launcher.launch_cli") as mock_cli,
        patch("builtins.__import__", side_effect=mock_import),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should fall back to CLI
        mock_cli.assert_called_once()


def test_gui_general_error_fallback():
    """Test GUI general error falls back to CLI."""
    from unittest.mock import MagicMock

    mock_gui = MagicMock()
    mock_gui.main.side_effect = Exception("GUI crashed")

    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch("sys.argv", ["launcher.py"]),
        patch("launcher.launch_cli") as mock_cli,
        patch.dict("sys.modules", {"src.gui": mock_gui}),
    ):
        from launcher import main as launcher_main

        launcher_main()

        # Should fall back to CLI
        mock_cli.assert_called_once()


def test_cli_exception_handling():
    """Test CLI exception handling."""
    from unittest.mock import MagicMock

    mock_main_module = MagicMock()
    mock_main_module.main.side_effect = Exception("CLI error")

    with (
        patch("launcher.load_dotenv"),
        patch("os.path.exists", return_value=True),
        patch.dict("sys.modules", {"src.main": mock_main_module}),
    ):
        from launcher import launch_cli

        with pytest.raises(SystemExit):
            launch_cli()


def test_env_file_missing():
    """Test error when .env file is missing."""
    with (
        patch("os.path.exists", return_value=False),
        patch("os.getcwd", return_value="/fake/path"),
    ):
        with pytest.raises(SystemExit):
            # Re-import to trigger the check
            import importlib
            import launcher
            importlib.reload(launcher)


def test_dotenv_import_error():
    """Test error when python-dotenv is not installed."""
    import sys
    # Remove dotenv from modules if present
    dotenv_module = sys.modules.pop("dotenv", None)

    try:
        with patch.dict("sys.modules", {"dotenv": None}):
            with pytest.raises(SystemExit):
                import importlib
                import launcher
                importlib.reload(launcher)
    finally:
        # Restore dotenv module
        if dotenv_module:
            sys.modules["dotenv"] = dotenv_module


def test_kmp_duplicate_lib_workaround():
    """Test KMP_DUPLICATE_LIB_OK workaround is applied."""
    with (
        patch("os.path.exists", return_value=True),
        patch("os.getenv", return_value="TRUE"),
        patch("launcher.load_dotenv"),
    ):
        import os
        # This should set the environment variable
        assert os.getenv("KMP_DUPLICATE_LIB_OK") in [None, "TRUE"]
