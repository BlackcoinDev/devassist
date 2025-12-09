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
AI Assistant Launcher v0.1 - Unified Interface Selector

UNIFIED ENTRY POINT for the AI assistant application, providing seamless access to both
graphical and command-line interfaces with identical functionality and configuration.

PURPOSE:
========
This launcher serves as the single entry point for the entire AI assistant system,
abstracting away the complexity of choosing between GUI and CLI while ensuring
consistent configuration loading and initialization across all interfaces.

SUPPORTED INTERFACES:
====================
🖥️  GUI MODE (Default):
    - Modern PyQt6 interface with dark/light themes
    - Real-time streaming responses with markdown rendering
    - One-click command buttons and settings panels
    - Complete feature parity with CLI functionality

💻 CLI MODE:
    - Traditional terminal-based interface
    - Full slash command support (/learn, /vectordb, /mem0, etc.)
    - Direct tool access and system control
    - Optimized for power users and automation

CONFIGURATION MANAGEMENT:
=======================
🔧 Environment Loading:
    - Loads .env file (REQUIRED - no hardcoded defaults)
    - Validates all required environment variables
    - Provides clear error messages for missing configuration
    - Supports system environment variable overrides

REQUIRED ENVIRONMENT VARIABLES:
    - LM_STUDIO_URL: qwen3-vl-30b endpoint via LM Studio
    - LM_STUDIO_KEY: API authentication key
    - MODEL_NAME: AI model identifier
    - CHROMA_HOST/PORT: ChromaDB v2 server connection
    - OLLAMA_BASE_URL: Ollama embeddings server
    - EMBEDDING_MODEL: qwen3-embedding model name
    - DB_TYPE/DB_PATH: SQLite conversation storage
    - And additional application settings...

LAUNCH OPTIONS:
==============
--gui (default): Launch PyQt6 graphical interface
--cli: Launch command-line interface
--help: Display usage information

ARCHITECTURAL ROLE:
==================
1. Configuration Validation: Ensures all required settings are present
2. Interface Selection: Routes to appropriate UI based on user preference
3. Error Handling: Provides clear feedback for configuration issues
4. Dependency Checking: Validates required services are available
5. Initialization: Prepares environment for main application launch

INTEGRATION POINTS:
==================
- main.py: CLI backend with AI tool calling and conversation logic
- gui.py: PyQt6 frontend with identical feature set
- .env: Configuration file (MANDATORY)
- External Services: LM Studio, ChromaDB, Ollama (all required)

USAGE EXAMPLES:
==============
# Launch GUI (recommended for new users)
python3 launcher.py

# Launch CLI (for power users/automation)
python3 launcher.py --cli

# Check available options
python3 launcher.py --help

This launcher ensures consistent behavior across all interfaces while providing
the flexibility to choose the most appropriate interaction method for each use case.
"""

import sys
import argparse
import os

# Load environment variables from .env file for configuration management
# - Allows sensitive settings (API keys, URLs) to be stored securely
# - Falls back to system environment variables if .env not available
# - Essential for deployment flexibility and security
try:
    from dotenv import load_dotenv

    # Check if .env file exists - it's now required
    env_file_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_file_path):
        load_dotenv()
        print("✅ Loaded environment variables from .env file")
    else:
        print("❌ ERROR: No .env file found!")
        print("Please copy .env.example to .env and configure it for your environment.")
        print("Example: cp .env.example .env")
        sys.exit(1)

    # Set OpenMP workaround if configured
    if os.getenv("KMP_DUPLICATE_LIB_OK") == "TRUE":
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        print("✅ Applied OpenMP library conflict workaround")

except ImportError:
    print("❌ ERROR: python-dotenv is required but not installed!")
    print("Install it with: pip install python-dotenv")
    sys.exit(1)


def main():
    """
    Main launcher function that parses command line arguments and starts
    the appropriate interface (GUI or CLI) for the AI assistant.
    """
    parser = argparse.ArgumentParser(
        description="AI Assistant v0.1 - Learning Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 launcher.py              # Launch GUI (default)
  python3 launcher.py --cli        # Launch CLI version
  python3 launcher.py --gui        # Launch GUI version (explicit)

The GUI provides a modern interface with:
- Chat display with message history
- Quick command buttons
- Settings panel for behavior control
- Real-time streaming responses

The CLI provides the traditional terminal interface with:
- All slash commands
- Direct text input/output
- Full control over AI behavior
        """,
    )

    parser.add_argument(
        "--cli", "--terminal", action="store_true", help="Launch CLI (terminal) version"
    )

    parser.add_argument(
        "--gui", "--interface", action="store_true", help="Launch GUI version (default)"
    )

    # Help is automatically added by argparse

    args = parser.parse_args()

    # Determine which interface to launch
    launch_gui = not args.cli  # GUI is default unless --cli is specified

    if launch_gui:
        print("🚀 Launching AI Assistant GUI...")
        try:
            from src.gui import main as gui_main

            gui_main()
        except ImportError as e:
            print(f"❌ GUI not available: {e}")
            print("💡 Install PyQt6: pip install PyQt6")
            print("🔄 Falling back to CLI...")
            launch_cli()
        except Exception as e:
            print(f"❌ GUI error: {e}")
            print("🔄 Falling back to CLI...")
            launch_cli()
    else:
        print("🚀 Launching AI Assistant CLI...")
        launch_cli()


def launch_cli():
    """
    Launch the Command Line Interface version of the AI assistant.

    Imports and runs the main CLI application with full functionality
    including all slash commands and interactive chat.
    """
    try:
        from src.main import main as cli_main

        cli_main()
    except Exception as e:
        print(f"❌ CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
