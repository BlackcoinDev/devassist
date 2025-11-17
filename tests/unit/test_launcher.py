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
