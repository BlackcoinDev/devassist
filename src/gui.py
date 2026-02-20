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
AI Assistant GUI Application v0.3.0 - PyQt6 Graphical Interface

GRAPHICAL USER INTERFACE for the intelligent AI assistant system, providing a modern,
user-friendly alternative to the command-line interface with identical functionality.

The GUI maintains complete feature parity with the CLI while providing
an intuitive, modern interface for AI-assisted development and research.
"""

from src.storage.memory import load_memory
from src.core.config import get_config
import logging
import sys
import asyncio

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QSplitter,
    QGroupBox,
    QComboBox,
    QLabel,
)
from PyQt6.QtGui import QPalette, QColor, QTextCursor
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QWaitCondition, QMutex
from typing import List, Any
from langchain_core.messages import BaseMessage

# Import qasync for asyncio integration with PyQt6
try:
    import qasync

    QASYNC_AVAILABLE = True
except ImportError:
    QASYNC_AVAILABLE = False

# Type alias for conversation history
ConversationHistory = List[BaseMessage]

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
_config = get_config()

# Import the AI assistant backend
# We'll need to refactor some functions to be importable

# Initialize variables (will be imported from main.py)
conversation_history: ConversationHistory = []
CONTEXT_MODE: str = "auto"
LEARNING_MODE: str = "normal"
MODEL_NAME: str = ""  # Will be set from environment
CHROMA_HOST: str = ""  # Will be set from environment
CHROMA_PORT: int = 0  # Will be set from environment
MAX_HISTORY_PAIRS: int = 0  # Will be set from environment

# Check for optional dependencies
markdown: Any = None
try:
    import markdown

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

# Backend availability will be determined at runtime
BACKEND_AVAILABLE = False

# Functions from main.py will be imported locally where needed


class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()
    confirmation_required = pyqtSignal(str, dict)  # tool_name, args

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._confirmation_result = False

    def ask_confirmation(self, tool_name: str, args: dict) -> bool:
        """Called by ChatLoop to request user approval."""
        self._mutex.lock()
        self.confirmation_required.emit(tool_name, args)
        self._wait_condition.wait(self._mutex)
        result = self._confirmation_result
        self._mutex.unlock()
        return result

    def set_confirmation_result(self, approved: bool):
        """Called by GUI thread to resume worker."""
        self._mutex.lock()
        self._confirmation_result = approved
        self._wait_condition.wakeAll()
        self._mutex.unlock()

    def run(self):
        try:
            from src.core.chat_loop import ChatLoop
            from src.main import get_llm

            if not BACKEND_AVAILABLE:
                self.error_occurred.emit("❌ Backend not available.")
                return

            if get_llm() is None:
                self.error_occurred.emit("❌ LLM not available.")
                return

            orchestrator = ChatLoop(confirmation_callback=self.ask_confirmation)
            response_content = orchestrator.run_iteration(self.user_input)

            self.response_ready.emit(response_content)

            # MEM0 TEACHING (Background Thread)
            from src.main import user_memory

            if user_memory:

                def run_mem0_add(text):
                    try:
                        messages = [{"role": "user", "content": text}]
                        user_memory.add(messages, user_id="default_user")
                    except Exception:
                        pass

                import threading

                threading.Thread(target=run_mem0_add, args=(self.user_input,)).start()

        except Exception as e:
            logger.error(f"AIWorker Error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class AIAssistantGUI(QMainWindow):
    """
    Main GUI Window for AI Assistant v0.3.0

    This class implements the complete PyQt6-based graphical interface for the AI assistant,
    providing a modern, user-friendly alternative to the CLI with identical functionality.

    KEY COMPONENTS:
    ===============
    - Chat Display: Scrollable text area showing conversation history with markdown rendering
    - Input System: Text field for user input with Enter key and Send button support
    - Command Buttons: One-click access to common operations (/help, /clear, /memory, etc.)
    - Settings Panel: Dropdown controls for context mode and learning behavior
    - Status Display: Real-time model information and system status updates
    - Space Selector: Dropdown for managing isolated knowledge workspaces

    AI INTEGRATION:
    ===============
     - Full access to all 13 AI tools (read_file, write_file, parse_document,
       search_web, shell_execute, git_status, git_diff, git_log, etc.)
    - Autonomous tool calling based on natural language understanding
    - Context-aware conversations using ChromaDB knowledge base
    - Document processing with qwen3-vl-30b multimodal analysis

    TECHNICAL FEATURES:
    ===================
    - Streaming responses: Real-time display as AI generates text
    - Markdown rendering: Rich formatting for code, lists, and emphasis
    - Theme support: Dark/light mode with QSS styling
    - Error handling: Comprehensive error display and recovery
    - State persistence: Maintains conversation and settings across sessions

    WORKFLOW INTEGRATION:
    ====================
    1. User types message or clicks command button
    2. Input sent to main.py backend via worker thread
    3. AI processes with tool calling and context retrieval
    4. Response streamed back and rendered with markdown
    5. Conversation history updated and persisted to SQLite

    THREADING ARCHITECTURE:
    ======================
    - Main thread: GUI event handling and display updates
    - Worker thread: AI processing and tool execution
    - Signal/slot system: Thread-safe communication between GUI and backend

    This GUI maintains complete feature parity with the CLI interface while providing
    an intuitive, modern experience for AI-assisted development and research.
    """

    def __init__(self):
        super().__init__()

        # Import functions from main.py
        from src.vectordb.spaces import load_current_space

        self.worker = None
        self.dark_theme = True  # Default to dark theme
        self.markdown_converter = None
        if MARKDOWN_AVAILABLE and markdown is not None:
            # Configure markdown with extensions for better formatting
            self.markdown_converter = markdown.Markdown(
                extensions=["extra", "codehilite", "toc"],
                extension_configs={
                    "codehilite": {
                        "linenums": False,
                        "guess_lang": False,
                    }
                },
            )

        self.init_ui()
        self.load_conversation()

        # Load the last used space
        global CURRENT_SPACE
        CURRENT_SPACE = load_current_space()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("AI Assistant v0.3.0 - Learning Edition")
        self.setGeometry(100, 100, 1000, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Chat area
        chat_widget = self.create_chat_panel()
        splitter.addWidget(chat_widget)

        # Right panel - Controls
        control_widget = self.create_control_panel()
        splitter.addWidget(control_widget)

        # Set splitter proportions
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

        # Apply styling
        self.apply_styling()

    def create_chat_panel(self):
        """Create the chat display and input area."""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)  # Enable HTML rendering
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(
            "Type your message or command (e.g., /help)..."
        )
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)

        return chat_widget

    def create_control_panel(self):
        """Create the control panel with buttons and settings."""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        model_label = QLabel(f"Model: {MODEL_NAME}")
        status_layout.addWidget(model_label)

        control_layout.addWidget(status_group)

        # Quick Commands section
        commands_group = QGroupBox("Quick Commands")
        commands_layout = QVBoxLayout(commands_group)

        commands = [
            ("Help", "/help"),
            ("Clear Chat", "/clear"),
            ("Show Memory", "/memory"),
            ("Vector DB", "/vectordb"),
            ("Mem0 Memory", "/mem0"),
            ("Model Info", "/model"),
            ("Export Chat", "/export json"),
        ]

        for label, command in commands:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
            commands_layout.addWidget(btn)

        control_layout.addWidget(commands_group)

        # Settings section
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Theme toggle
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_button = QPushButton("🌙 Dark" if self.dark_theme else "☀️ Light")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_button)
        settings_layout.addLayout(theme_layout)

        # Context mode
        context_layout = QHBoxLayout()
        context_layout.addWidget(QLabel("Context:"))
        self.context_combo = QComboBox()
        self.context_combo.addItems(["auto", "on", "off"])
        self.context_combo.setCurrentText(CONTEXT_MODE)
        self.context_combo.currentTextChanged.connect(self.change_context_mode)
        context_layout.addWidget(self.context_combo)
        settings_layout.addLayout(context_layout)

        # Learning mode
        learning_layout = QHBoxLayout()
        learning_layout.addWidget(QLabel("Learning:"))
        self.learning_combo = QComboBox()
        self.learning_combo.addItems(["normal", "strict", "off"])
        self.learning_combo.setCurrentText(LEARNING_MODE)
        self.learning_combo.currentTextChanged.connect(self.change_learning_mode)
        learning_layout.addWidget(self.learning_combo)
        settings_layout.addLayout(learning_layout)

        # Space selector
        space_layout = QHBoxLayout()
        space_layout.addWidget(QLabel("Space:"))
        self.space_combo = QComboBox()
        # Will be populated when backend is available
        self.space_combo.addItems(["default"])
        self.space_combo.setCurrentText(CURRENT_SPACE)
        self.space_combo.currentTextChanged.connect(self.change_space)
        space_layout.addWidget(self.space_combo)
        settings_layout.addLayout(space_layout)

        control_layout.addWidget(settings_group)

        # Add stretch to push everything to top
        control_layout.addStretch()

        return control_widget

    def markdown_to_html(self, text):
        """Convert markdown text to HTML with theme-appropriate styling."""
        if not MARKDOWN_AVAILABLE or not self.markdown_converter:
            # Escape HTML characters and convert basic formatting
            return self.plain_text_to_html(text)

        try:
            # Convert markdown to HTML
            html = self.markdown_converter.convert(text)

            # Add theme-appropriate styling
            if self.dark_theme:
                # Dark theme styles
                style_wrapper = f"""
                <div style="color: #ffffff; font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt; line-height: 1.4;">
                {html}
                </div>
                """
            else:
                # Light theme styles
                style_wrapper = f"""
                <div style="color: #000000; font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt; line-height: 1.4;">
                {html}
                </div>
                """

            return style_wrapper
        except Exception as e:
            print(f"Markdown conversion error: {e}")
            return self.plain_text_to_html(text)

    def plain_text_to_html(self, text):
        """Convert plain text to basic HTML with formatting."""
        # Escape HTML characters
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Convert basic markdown-like formatting
        import re

        # Bold: **text** or __text__
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"__(.*?)__", r"<b>\1</b>", text)

        # Italic: *text* or _text_
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
        text = re.sub(r"_(.*?)_", r"<i>\1</i>", text)

        # Code: `text`
        text = re.sub(
            r"`([^`]+)`",
            r'<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">\1</code>',
            text,
        )

        # Convert newlines to <br>
        text = text.replace("\n", "<br>")

        # Add theme-appropriate styling
        if self.dark_theme:
            return f"<div style=\"color: #ffffff; font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt; line-height: 1.4;\">{text}</div>"
        else:
            return f"<div style=\"color: #000000; font-family: 'Consolas', 'Monaco', monospace; font-size: 10pt; line-height: 1.4;\">{text}</div>"

    def apply_styling(self):
        """Apply styling to the GUI based on current theme."""
        if self.dark_theme:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        """Apply dark theme styling to the GUI."""
        # Set dark theme color palette
        palette = QPalette()

        # Window and base colors
        palette.setColor(
            QPalette.ColorRole.Window, QColor(45, 45, 45)
        )  # Dark gray background
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(255, 255, 255)
        )  # White text
        palette.setColor(
            QPalette.ColorRole.Base, QColor(30, 30, 30)
        )  # Darker base for inputs
        palette.setColor(
            QPalette.ColorRole.AlternateBase, QColor(45, 45, 45)
        )  # Alternate base
        palette.setColor(
            QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255)
        )  # Light tooltips
        palette.setColor(
            QPalette.ColorRole.ToolTipText, QColor(0, 0, 0)
        )  # Dark tooltip text

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))  # White text
        palette.setColor(
            QPalette.ColorRole.BrightText, QColor(255, 255, 255)
        )  # Bright white text
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor(42, 130, 218)
        )  # Blue highlight
        palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
        )  # White highlighted text

        # Button colors
        palette.setColor(
            QPalette.ColorRole.Button, QColor(60, 60, 60)
        )  # Dark button background
        palette.setColor(
            QPalette.ColorRole.ButtonText, QColor(255, 255, 255)
        )  # White button text

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))  # Blue links
        palette.setColor(
            QPalette.ColorRole.LinkVisited, QColor(128, 160, 200)
        )  # Visited link color

        self.setPalette(palette)

        # Style the chat display with dark theme
        self.chat_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """
        )

        # Style the input field with dark theme
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-size: 10pt;
            }
        """
        )

        # Style buttons with dark theme
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """

        self.send_button.setStyleSheet(button_style)

        # Apply to all buttons in control panel with different colors
        for button in self.findChildren(QPushButton):
            if (
                button != self.send_button and button != self.theme_button
            ):  # Send and theme buttons already styled
                button.setStyleSheet(button_style.replace("#0078d4", "#107c10"))

        # Style combo boxes for dark theme
        combo_style = """
            QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 3px;
                font-size: 9pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
            }
        """

        for combo in self.findChildren(QComboBox):
            combo.setStyleSheet(combo_style)

        # Style labels
        label_style = """
            QLabel {
                color: #ffffff;
                font-size: 9pt;
            }
        """

        for label in self.findChildren(QLabel):
            label.setStyleSheet(label_style)

        # Style group boxes
        group_style = """
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
                font-size: 10pt;
            }
        """

        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(group_style)

    def apply_light_theme(self):
        """Apply light theme styling to the GUI."""
        # Set light theme color palette
        palette = QPalette()

        # Window and base colors
        palette.setColor(
            QPalette.ColorRole.Window, QColor(240, 240, 240)
        )  # Light gray background
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))  # Black text
        palette.setColor(
            QPalette.ColorRole.Base, QColor(255, 255, 255)
        )  # White base for inputs
        palette.setColor(
            QPalette.ColorRole.AlternateBase, QColor(240, 240, 240)
        )  # Light alternate base
        palette.setColor(
            QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255)
        )  # White tooltips
        palette.setColor(
            QPalette.ColorRole.ToolTipText, QColor(0, 0, 0)
        )  # Black tooltip text

        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))  # Black text
        palette.setColor(
            QPalette.ColorRole.BrightText, QColor(255, 255, 255)
        )  # White bright text
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor(42, 130, 218)
        )  # Blue highlight
        palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
        )  # White highlighted text

        # Button colors
        palette.setColor(
            QPalette.ColorRole.Button, QColor(240, 240, 240)
        )  # Light button background
        palette.setColor(
            QPalette.ColorRole.ButtonText, QColor(0, 0, 0)
        )  # Black button text

        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))  # Blue links
        palette.setColor(
            QPalette.ColorRole.LinkVisited, QColor(128, 0, 128)
        )  # Purple visited links

        self.setPalette(palette)

        # Style the chat display with light theme
        self.chat_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
        """
        )

        # Style the input field with light theme
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 10pt;
            }
        """
        )

        # Style buttons with light theme
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """

        self.send_button.setStyleSheet(button_style)

        # Apply to all buttons in control panel with different colors
        for button in self.findChildren(QPushButton):
            if (
                button != self.send_button and button != self.theme_button
            ):  # Send and theme buttons already styled
                button.setStyleSheet(button_style.replace("#0078d4", "#107c10"))

        # Style combo boxes for light theme
        combo_style = """
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
                font-size: 9pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #000000;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #0078d4;
            }
        """

        for combo in self.findChildren(QComboBox):
            combo.setStyleSheet(combo_style)

        # Style labels
        label_style = """
            QLabel {
                color: #000000;
                font-size: 9pt;
            }
        """

        for label in self.findChildren(QLabel):
            label.setStyleSheet(label_style)

        # Style group boxes
        group_style = """
            QGroupBox {
                color: #000000;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
                font-size: 10pt;
            }
        """

        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(group_style)

    def load_conversation(self):
        """Load existing conversation history."""
        try:
            if BACKEND_AVAILABLE:
                global conversation_history
                conversation_history = load_memory()
                self.display_conversation()
                self.status_label.setText("Conversation loaded")
            else:
                self.chat_display.append(
                    "⚠️ Backend not available. Limited functionality."
                )
        except Exception as e:
            self.chat_display.append(f"⚠️ Error loading conversation: {e}")

    def display_conversation(self):
        """Display the current conversation in the chat area."""
        self.chat_display.clear()

        for msg in conversation_history[-50:]:  # Show last 50 messages
            if hasattr(msg, "type"):
                if msg.type == "human":
                    formatted_content = self.markdown_to_html(msg.content)
                    self.chat_display.append(f"<b>You:</b><br>{formatted_content}<br>")
                elif msg.type == "ai":
                    formatted_content = self.markdown_to_html(msg.content)
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>{formatted_content}<br>"
                    )
                else:
                    formatted_content = self.markdown_to_html(msg.content)
                    self.chat_display.append(
                        f"<b>System:</b><br>{formatted_content}<br>"
                    )
            else:
                formatted_content = self.markdown_to_html(str(msg))
                self.chat_display.append(f"<b>Message:</b><br>{formatted_content}<br>")

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def send_message(self):
        """Send user message to AI or handle commands locally."""
        try:
            message = self.input_field.text().strip()
            if not message:
                return

            if _config.verbose_logging:
                logger.info(f"GUI: Processing user message ({len(message)} chars)")

            # Clear input field
            self.input_field.clear()

            # Check for quit commands
            if message.lower() in ["quit", "exit", "q"]:
                self.handle_quit()
                return

            # Process slash commands locally (like CLI)
            if message.startswith("/"):
                self.handle_slash_command(message)
                return

            # Display user message with HTML formatting (only for regular
            # messages)
            formatted_message = self.markdown_to_html(message)
            self.chat_display.append(f"<b>You:</b><br>{formatted_message}<br>")

            # Regular message - send to AI
            # Disable input while processing
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
            self.status_label.setText("Processing...")

            # Start AI worker thread
            self.worker = AIWorker(message)
            self.worker.response_ready.connect(self.on_response_chunk)
            self.worker.error_occurred.connect(self.on_error)
            self.worker.finished.connect(self.on_processing_finished)
            self.worker.confirmation_required.connect(self.handle_confirmation)
            self.worker.start()
        except Exception as e:
            print(f"ERROR in send_message: {e}")
            self.chat_display.append(
                f"<b>Error:</b><br>Failed to send message: {e}<br>"
            )
            # Re-enable input
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            self.status_label.setText("Error")

    def handle_confirmation(self, tool_name: str, args: dict):
        """Show a dialog to confirm tool execution."""
        from PyQt6.QtWidgets import QMessageBox

        msg = "<b>Security Approval Required</b><br><br>"
        msg += f"The AI wants to use the tool: <code>{tool_name}</code><br>"
        msg += f"Arguments: <code>{args}</code><br><br>"
        msg += "Do you want to allow this action?"

        reply = QMessageBox.question(
            self,
            "Tool Execution Approval",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        approved = reply == QMessageBox.StandardButton.Yes
        if self.worker:
            self.worker.set_confirmation_result(approved)

    def send_command(self, command):
        """Send a slash command."""
        self.input_field.setText(command)
        self.send_message()

    def on_response_chunk(self, chunk):
        """Handle incoming response chunk for streaming display."""
        if not hasattr(self, "_current_response"):
            self._current_response = ""
            self.chat_display.append("<b>AI Assistant:</b><br>")

        self._current_response += chunk
        # Update the display with the current accumulated response
        self.update_streaming_response(self._current_response)

    def update_streaming_response(self, content):
        """Update the streaming AI response in the chat display."""
        # Convert the accumulated content to HTML
        formatted_content = self.markdown_to_html(content)

        # Get the current text and replace the last AI response
        current_text = self.chat_display.toHtml()

        # Find the last AI response and replace it
        # This is a simplified approach - in production, you'd want more robust
        # HTML manipulation
        ai_start = current_text.rfind("<b>AI Assistant:</b><br>")
        if ai_start != -1:
            # Find the next message or end
            next_msg = current_text.find("<b>You:</b>", ai_start + 1)
            if next_msg == -1:
                next_msg = current_text.find("<b>AI Assistant:</b>", ai_start + 1)
            if next_msg == -1:
                next_msg = len(current_text)

            # Replace the content between AI start and next message
            before = current_text[: ai_start + len("<b>AI Assistant:</b><br>")]
            after = current_text[next_msg:] if next_msg < len(current_text) else ""
            new_text = before + formatted_content + after

            self.chat_display.setHtml(new_text)

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def on_error(self, error_msg):
        """Handle processing errors."""
        formatted_error = self.markdown_to_html(f"❌ Error: {error_msg}")
        self.chat_display.append(f"<b>Error:</b><br>{formatted_error}<br>")
        self.status_label.setText("Error occurred")

    def on_processing_finished(self):
        """Handle completion of AI processing."""
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("Ready")

        # Clear streaming state
        if hasattr(self, "_current_response"):
            delattr(self, "_current_response")

        # Refresh conversation display
        self.display_conversation()

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def change_context_mode(self, mode):
        """Change context integration mode."""
        global CONTEXT_MODE
        CONTEXT_MODE = mode
        self.status_label.setText(f"Context mode: {mode}")

    def change_learning_mode(self, mode):
        """Change learning behavior mode."""
        global LEARNING_MODE
        LEARNING_MODE = mode
        self.status_label.setText(f"Learning mode: {mode}")

    def change_space(self, space_name):
        """Change current workspace/space."""
        from src.vectordb.spaces import switch_space, list_spaces

        global CURRENT_SPACE
        if switch_space(space_name):
            CURRENT_SPACE = space_name
            self.status_label.setText(f"Space: {space_name}")
            # Update the combo box to reflect current spaces
            self.space_combo.clear()
            self.space_combo.addItems(list_spaces())
            self.space_combo.setCurrentText(CURRENT_SPACE)
        else:
            self.status_label.setText(f"Failed to switch to space: {space_name}")
            # Reset to current space
            self.space_combo.setCurrentText(CURRENT_SPACE)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_theme = not self.dark_theme
        self.apply_styling()

        # Update theme button text and icon
        if self.dark_theme:
            self.theme_button.setText("🌙 Dark")
            self.theme_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            """
            )
        else:
            self.theme_button.setText("☀️ Light")
            self.theme_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """
            )

    def handle_quit(self):
        """Handle quit commands."""
        from src.storage.memory import save_memory

        formatted_response = self.markdown_to_html("Goodbye! Have a great day!")
        self.chat_display.append(f"<b>AI Assistant:</b><br>{formatted_response}<br>")
        self.status_label.setText("Goodbye!")

        # Save conversation and close after a short delay
        try:
            if BACKEND_AVAILABLE:
                save_memory(conversation_history)
        except Exception:
            pass  # Ignore errors during shutdown

        # Close the application after a brief delay
        QTimer.singleShot(1000, self.close)

    def handle_slash_command(self, command_text):
        """Handle slash commands using CommandRegistry (shared with CLI)."""
        if not BACKEND_AVAILABLE:
            self.chat_display.append(
                "<b>AI Assistant:</b><br>❌ Backend not available for commands<br>"
            )
            return

        try:
            import io
            import sys
            from src.commands.registry import CommandRegistry

            # Parse command: remove leading '/', split into name and args
            cmd_text = command_text.lstrip("/").strip()
            parts = cmd_text.split(maxsplit=1)
            if not parts:
                return

            cmd_name = parts[0]
            cmd_args = parts[1].split() if len(parts) > 1 else []

            # Capture stdout from command handlers
            captured_output = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = captured_output
                handled = CommandRegistry.dispatch(cmd_name, cmd_args)
            finally:
                sys.stdout = old_stdout

            # Get output from command handler
            output = captured_output.getvalue()

            if handled:
                if output:
                    # Escape HTML characters for safe display
                    result_html = (
                        output.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>{result_html}<br>"
                    )
                else:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br>Command executed successfully<br>"
                    )
            else:
                self.chat_display.append(
                    f"<b>AI Assistant:</b><br>❌ Unknown command: /{cmd_name}<br>"
                )
                self.chat_display.append("Type /help for available commands<br>")

        except Exception as e:
            logger.error(f"Error handling slash command: {e}")
            self.chat_display.append(f"<b>AI Assistant:</b><br>❌ Error: {str(e)}<br>")

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def closeEvent(self, a0):
        """Handle application close."""
        from src.storage.memory import save_memory

        try:
            if BACKEND_AVAILABLE:
                save_memory(conversation_history)
                if _config.verbose_logging:
                    logger.info("Conversation memory saved during GUI shutdown")
        except Exception as e:
            logger.error(f"Failed to save memory during shutdown: {e}")
        if a0:
            a0.accept()


def main():
    """Main GUI application entry point with qasync support."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("AI Assistant")
    app.setApplicationVersion("0.3.0")
    app.setOrganizationName("Blackcoin Development")

    # Initialize backend components (same as CLI)
    if BACKEND_AVAILABLE:
        try:
            from src.main import initialize_application

            if not initialize_application():
                print(
                    "❌ Backend initialization failed. GUI will run with limited functionality."
                )
        except Exception as e:
            print(f"❌ Failed to initialize backend: {e}")
            print("GUI will run with limited functionality.")

    # Create and show main window
    window = AIAssistantGUI()
    window.show()

    # Start event loop with qasync if available
    if QASYNC_AVAILABLE:
        # Use qasync for asyncio integration
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        with loop:
            loop.run_forever()
    else:
        # Fall back to standard Qt event loop
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
