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
AI Assistant GUI Application v0.2.0 - PyQt6 Graphical Interface

GRAPHICAL USER INTERFACE for the intelligent AI assistant system, providing a modern,
user-friendly alternative to the command-line interface with identical functionality.

CORE FEATURES:
==============
🖥️ MODERN INTERFACE:
- PyQt6-based responsive GUI with dark/light theme support
- Real-time chat display with persistent message history
- Streaming response rendering as AI generates text
- Rich markdown formatting for code blocks, lists, and emphasis

🎛️ USER CONTROLS:
- One-click command buttons for common operations (/help, /clear, /memory)
- Settings panel for context mode and learning behavior control
- Space/workspace selector for managing isolated knowledge bases
- Model information display and status updates

🤖 AI INTEGRATION:
- Full access to 8 AI tools (read_file, write_file, parse_document, search_web, etc.)
- Natural language processing with autonomous tool calling
- Context-aware conversations using ChromaDB knowledge base
- Document intelligence with qwen3-vl-30b multimodal analysis

💾 DATA MANAGEMENT:
- SQLite conversation persistence across sessions
- ChromaDB vector database integration for knowledge storage
- Real-time synchronization with CLI interface state
- Secure file operations within current directory sandbox

ARCHITECTURAL INTEGRATION:
=========================
This GUI serves as a complete frontend for the main.py backend, providing:
- Identical slash command support (/learn, /vectordb, /mem0, /populate, etc.)
- Same AI tool calling capabilities with qwen3-vl-30b
- Consistent error handling and status reporting
- Unified configuration via .env file requirements

INTERACTION MODES:
=================
1. Direct Commands: Click buttons or type /commands for immediate execution
2. Natural Language: Chat naturally, AI autonomously calls tools as needed
3. Document Processing: Upload/analyze documents with multimodal AI understanding
4. Knowledge Management: Teach AI, inspect knowledge base, manage workspaces

TECHNICAL STACK:
===============
- Frontend: PyQt6 for cross-platform GUI development
- Backend: LangChain integration with main.py core logic
- AI: qwen3-vl-30b via LM Studio for chat and tool calling
- Embeddings: qwen3-embedding via Ollama for vectorization
- Storage: ChromaDB v2 for knowledge, SQLite for conversations
- Styling: QSS (Qt Style Sheets) for theme customization

USAGE WORKFLOW:
==============
1. Launch GUI → Loads configuration from .env
2. Initialize → Connects to LM Studio, ChromaDB, Ollama
3. Chat → Natural conversation with AI tool calling
4. Commands → Direct slash commands for system control
5. Documents → Parse files with multimodal AI analysis
6. Knowledge → Teach and query learned information
7. Spaces → Manage isolated knowledge workspaces

The GUI maintains complete feature parity with the CLI while providing
an intuitive, modern interface for AI-assisted development and research.
"""

import sys
import os
import logging
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
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from datetime import datetime
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the AI assistant backend
# We'll need to refactor some functions to be importable

# Initialize variables (will be imported from main.py)
conversation_history: List = []
CONTEXT_MODE: str = "auto"
LEARNING_MODE: str = "normal"
MODEL_NAME: str = ""  # Will be set from environment
CHROMA_HOST: str = ""  # Will be set from environment
CHROMA_PORT: int = 0  # Will be set from environment
MAX_HISTORY_PAIRS: int = 0  # Will be set from environment

# Check for optional dependencies
try:
    import markdown

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    markdown = None

# Backend availability will be determined at runtime
BACKEND_AVAILABLE = False

# Population availability (for document processing)
POPULATION_AVAILABLE = True

# Functions from main.py will be imported locally where needed

# Functions from main.py will be imported when needed


class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, user_input):
        super().__init__()
        self.user_input = user_input

    def run(self):
        try:
            # Import configuration and core functions
            from src.main import (
                load_memory,
                save_memory,
                get_relevant_context,
                get_llm,
                get_vectorstore,
                trim_history,
                CONTEXT_MODE,
                LEARNING_MODE,
                MODEL_NAME,
                CURRENT_SPACE,
                conversation_history,
                CHROMA_HOST,
                CHROMA_PORT,
                MAX_HISTORY_PAIRS,
                VERBOSE_LOGGING,
                list_spaces,
                switch_space,
                delete_space,
                get_space_collection_name,
                load_current_space,
                save_current_space,
            )

            if not BACKEND_AVAILABLE:
                logger.error("AIWorker: Backend not available")
                self.response_ready.emit(
                    "❌ Backend not available. Please run main.py first to set up the environment."
                )
                return

            current_llm = get_llm()
            if current_llm is None:
                logger.error("AIWorker: LLM not available")
                self.response_ready.emit(
                    "❌ LLM not available. Please ensure LM Studio is running with a model loaded."
                )
                return

            # Import required classes
            from langchain_core.messages import HumanMessage, AIMessage

            # Add user message to history
            conversation_history.append(HumanMessage(content=self.user_input))

            # Get context if available
            current_vectorstore = get_vectorstore()
            context = (get_relevant_context(self.user_input)
                       if current_vectorstore else "")

            # Simple context integration (can be enhanced)
            if context and CONTEXT_MODE != "off":
                # Add context to conversation
                conversation_history.append(
                    HumanMessage(content=f"Context: {context}"))
                logger.info(
                    f"Added context to conversation ({
                        len(context)} chars)")

            # Generate response
            response = current_llm.invoke(conversation_history)
            conversation_history.append(AIMessage(content=response.content))
            self.response_ready.emit(response.content)

            # Trim conversation history to prevent memory bloat
            conversation_history[:] = trim_history(
                conversation_history, MAX_HISTORY_PAIRS
            )

            # Auto-save conversation
            save_memory(conversation_history)

            # MEM0 TEACHING (Background Thread) - Store user input as memory
            from src.main import user_memory

            if user_memory:

                def run_mem0_add(text):
                    try:
                        if user_memory is not None:
                            # Mem0 expects messages as list of dicts with role/content
                            messages = [{"role": "user", "content": text}]
                            user_memory.add(messages, user_id="default_user")
                            if VERBOSE_LOGGING:
                                logger.info(
                                    f"Mem0: Stored memory from GUI: '{text[:50]}...'"
                                )
                    except Exception as ex:
                        # Only log Mem0 errors if verbose logging is enabled
                        if VERBOSE_LOGGING:
                            logger.warning(
                                f"Mem0 GUI background add failed: {ex}")

                # Run learning in background to not block GUI
                import threading

                threading.Thread(
                    target=run_mem0_add, args=(
                        self.user_input,)).start()

            logger.info(
                f"AIWorker: Successfully processed response ({
                    len(response.content)
                } chars)"
            )

        except Exception as e:
            logger.error(f"AIWorker: Error processing request: {e}")
            self.error_occurred.emit(f"Error: {str(e)}")


class PopulateWorker(QThread):
    """Worker thread for codebase population to keep GUI responsive."""

    progress = pyqtSignal(str)  # Signal for progress updates
    finished = pyqtSignal(str)  # Signal when population is complete
    error = pyqtSignal(str)  # Signal for errors

    def __init__(self, dir_path, vectorstore):
        super().__init__()
        self.dir_path = dir_path
        self.vectorstore = vectorstore

    def run(self):
        """Perform codebase population in background thread."""
        try:
            import os
            import glob

            # Import langchain components - should work now that langchain is
            # installed
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            from langchain_community.document_loaders import TextLoader

            # Supported file extensions
            extensions = [
                "*.py",
                "*.js",
                "*.ts",
                "*.cpp",
                "*.c",
                "*.h",
                "*.hpp",
                "*.java",
                "*.cs",
                "*.php",
                "*.rb",
                "*.go",
                "*.rs",
                "*.swift",
                "*.kt",
                "*.scala",
            ]

            total_files = 0
            processed_files = 0

            # Count total files first
            for ext in extensions:
                pattern = os.path.join(self.dir_path, "**", ext)
                total_files += len(glob.glob(pattern, recursive=True))

            if total_files == 0:
                self.error.emit(
                    f"No supported code files found in {
                        self.dir_path}")
                return

            self.progress.emit(f"Found {total_files} code files to process")

            # Initialize text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )

            all_docs = []

            # Process each file type
            for ext in extensions:
                pattern = os.path.join(self.dir_path, "**", ext)
                files = glob.glob(pattern, recursive=True)

                for file_path in files:
                    try:
                        # Load and split the document
                        loader = TextLoader(file_path, encoding="utf-8")
                        documents = loader.load()
                        chunks = text_splitter.split_documents(documents)

                        # Add metadata
                        for chunk in chunks:
                            chunk.metadata["source"] = file_path
                            chunk.metadata["added_at"] = str(datetime.now())

                        all_docs.extend(chunks)
                        processed_files += 1

                        # Progress update every 10 files
                        if processed_files % 10 == 0:
                            self.progress.emit(
                                f"Processed {processed_files}/{total_files} files...")

                    except Exception as e:
                        self.progress.emit(
                            f"Warning: Could not process {file_path}: {str(e)}"
                        )
                        continue

            if not all_docs:
                self.error.emit("No documents were successfully processed")
                return

            # Add to vector database in batches to prevent timeouts and memory
            # issues
            if self.vectorstore:
                total_chunks = len(all_docs)
                batch_size = 1000  # Process in batches of 1000 chunks
                added_chunks = 0

                self.progress.emit(
                    f"Adding {total_chunks} document chunks to vector database in batches...")

                try:
                    for i in range(0, total_chunks, batch_size):
                        batch = all_docs[i: i + batch_size]
                        batch_number = (i // batch_size) + 1
                        total_batches = (
                            total_chunks + batch_size - 1) // batch_size

                        self.progress.emit(
                            f"Adding batch {batch_number}/{total_batches} ({
                                len(batch)
                            } chunks)..."
                        )

                        # Add batch to vector database
                        self.vectorstore.add_documents(batch)
                        added_chunks += len(batch)

                        # Progress update
                        self.progress.emit(
                            f"Added {added_chunks}/{total_chunks} chunks to database...")

                    self.finished.emit(
                        f"Successfully added {added_chunks} chunks from {processed_files} files to the knowledge base!")

                except Exception as e:
                    self.error.emit(
                        f"Failed to add documents to vector database: {
                            str(e)}. Added {added_chunks}/{total_chunks} chunks before error.")

            else:
                self.error.emit("Vector database not available")

        except Exception as e:
            self.error.emit(f"Population error: {str(e)}")


class AIAssistantGUI(QMainWindow):
    """
    Main GUI Window for AI Assistant v0.2.0

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
    - Full access to all 8 AI tools (read_file, write_file, parse_document, search_web, etc.)
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
        from src.main import load_current_space

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
        self.setWindowTitle("AI Assistant v0.2.0 - Learning Edition")
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
        self.theme_button = QPushButton(
            "🌙 Dark" if self.dark_theme else "☀️ Light")
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
        self.learning_combo.currentTextChanged.connect(
            self.change_learning_mode)
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
        text = text.replace(
            "&",
            "&amp;").replace(
            "<",
            "&lt;").replace(
            ">",
            "&gt;")

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
        palette.setColor(
            QPalette.ColorRole.Text, QColor(
                255, 255, 255))  # White text
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
        palette.setColor(
            QPalette.ColorRole.Link, QColor(
                42, 130, 218))  # Blue links
        palette.setColor(
            QPalette.ColorRole.LinkVisited, QColor(128, 160, 200)
        )  # Visited link color

        self.setPalette(palette)

        # Style the chat display with dark theme
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Style the input field with dark theme
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                font-size: 10pt;
            }
        """)

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
                button.setStyleSheet(
                    button_style.replace(
                        "#0078d4", "#107c10"))

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
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(
                0, 0, 0))  # Black text
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
        palette.setColor(
            QPalette.ColorRole.Text, QColor(
                0, 0, 0))  # Black text
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
        palette.setColor(
            QPalette.ColorRole.Link, QColor(
                0, 0, 255))  # Blue links
        palette.setColor(
            QPalette.ColorRole.LinkVisited, QColor(128, 0, 128)
        )  # Purple visited links

        self.setPalette(palette)

        # Style the chat display with light theme
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Style the input field with light theme
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
                font-size: 10pt;
            }
        """)

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
                button.setStyleSheet(
                    button_style.replace(
                        "#0078d4", "#107c10"))

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
        from src.main import load_memory

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
                    self.chat_display.append(
                        f"<b>You:</b><br>{formatted_content}<br>")
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
                self.chat_display.append(
                    f"<b>Message:</b><br>{formatted_content}<br>")

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
                next_msg = current_text.find(
                    "<b>AI Assistant:</b>", ai_start + 1)
            if next_msg == -1:
                next_msg = len(current_text)

            # Replace the content between AI start and next message
            before = current_text[: ai_start + len("<b>AI Assistant:</b><br>")]
            after = current_text[next_msg:] if next_msg < len(
                current_text) else ""
            new_text = before + formatted_content + after

            self.chat_display.setHtml(new_text)

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def display_vector_database(self):
        """Display vector database contents (similar to CLI /vectordb)."""
        from src.main import get_vectorstore

        try:
            import requests

            self.chat_display.append(
                "<b>AI Assistant:</b><br>--- Vector Database Contents ---<br>"
            )

            # Determine the correct collection ID
            collection_id = None

            # Try to get from vectorstore first
            current_vectorstore = get_vectorstore()
            if (
                current_vectorstore
                and hasattr(current_vectorstore, "_collection")
                and current_vectorstore._collection
            ):
                collection_id = current_vectorstore._collection.id

            # If not found, try to find collection with most documents
            if not collection_id:
                try:
                    list_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
                    list_response = requests.get(list_url, timeout=10)
                    if list_response.status_code == 200:
                        collections = list_response.json()
                        max_count = 0
                        for coll in collections:
                            coll_id = coll.get("id")
                            if coll_id:
                                count_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections/{coll_id}/count"
                                count_response = requests.get(
                                    count_url, timeout=10)
                                if count_response.status_code == 200:
                                    count = count_response.json()
                                    if isinstance(
                                            count, dict) and "count" in count:
                                        count = count["count"]
                                    if isinstance(
                                            count, int) and count > max_count:
                                        max_count = count
                                        collection_id = coll_id
                except Exception as e:
                    self.chat_display.append(
                        f"Error finding collection: {e}<br>")

            if not collection_id:
                self.chat_display.append(
                    "Could not determine active collection.<br>")
                return

            # Get documents from ChromaDB
            get_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}/get"
            params = {"limit": 20}

            response = requests.post(get_url, json=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                docs = []

                if "documents" in data and data["documents"]:
                    for i, doc_content in enumerate(data["documents"]):
                        metadata = {}
                        if (
                            "metadatas" in data
                            and data["metadatas"]
                            and i < len(data["metadatas"])
                        ):
                            metadata = data["metadatas"][i] or {}

                        class SimpleDoc:
                            def __init__(self, content, meta):
                                self.page_content = content
                                self.metadata = meta

                        doc = SimpleDoc(doc_content, metadata)
                        docs.append(doc)

                if docs:
                    self.chat_display.append(
                        f"Found {len(docs)} documents in knowledge base:<br><br>"
                    )
                    for i, doc in enumerate(docs, 1):
                        content_preview = (
                            doc.page_content[:100] + "..."
                            if len(doc.page_content) > 100
                            else doc.page_content
                        )
                        self.chat_display.append(
                            f"{i}. Content: {content_preview}<br>")
                        if doc.metadata:
                            source = doc.metadata.get("source", "unknown")
                            added_at = doc.metadata.get("added_at", "unknown")
                            self.chat_display.append(
                                f"   Source: {source}<br>")
                            if added_at != "unknown":
                                self.chat_display.append(
                                    f"   Added: {added_at}<br>")
                        self.chat_display.append("<br>")
                else:
                    self.chat_display.append(
                        "No documents found in the knowledge base.<br>"
                    )
                    self.chat_display.append(
                        "Use /learn to add information or /populate to add codebases.<br>"
                    )
            else:
                self.chat_display.append(
                    f"Failed to retrieve documents: HTTP {
                        response.status_code}<br>")
                self.chat_display.append(
                    "Vector database connection may have issues.<br>"
                )

            self.chat_display.append("--- End Vector Database ---<br>")

        except Exception as e:
            self.chat_display.append(
                f"<b>AI Assistant:</b><br>❌ Error displaying vector database: {str(e)}<br><br>"
            )

    def display_mem0_memory(self):
        """Display Mem0 personalized memory contents (similar to CLI /mem0)."""
        # Import at runtime to get the initialized value
        import src.main

        user_memory = src.main.user_memory

        try:
            self.chat_display.append(
                "<b>AI Assistant:</b><br>--- Mem0 Personalized Memory Contents ---<br>"
            )

            if user_memory is None:
                self.chat_display.append(
                    "❌ Mem0 personalized memory not available.<br>"
                )
                return

            memories = user_memory.get_all(user_id="default_user")

            if not memories or not memories.get("results"):
                self.chat_display.append(
                    "📊 No personalized memories stored yet.<br>")
                self.chat_display.append(
                    "Memories are automatically created from your conversations.<br>"
                )
                return

            results = memories["results"]
            self.chat_display.append(f"📊 Memories: {len(results)}<br>")
            self.chat_display.append("👤 User ID: user<br><br>")

            if results:
                self.chat_display.append("🧠 Sample Memories:<br>")
                for i, memory in enumerate(results[:5]):
                    content = memory.get("memory", "No content")
                    if len(content) > 200:
                        content = content[:200] + "..."
                    self.chat_display.append(f"  {i + 1}. {content}<br>")
                if len(results) > 5:
                    self.chat_display.append(
                        f"  ... and {len(results) - 5} more<br>")

            self.chat_display.append("--- End Mem0 Memory ---<br><br>")

        except Exception as e:
            self.chat_display.append(
                f"<b>AI Assistant:</b><br>❌ Error displaying Mem0 memory: {str(e)}<br><br>"
            )

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

    def on_populate_progress(self, message):
        """Handle population progress updates."""
        self.chat_display.append(f"<i>{message}</i><br>")
        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def on_populate_finished(self, message):
        """Handle completion of codebase population."""
        self.chat_display.append(f"<b>AI Assistant:</b><br>✅ {message}<br>")

        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("Ready")

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def on_populate_error(self, error_msg):
        """Handle population errors."""
        self.chat_display.append(
            f"<b>AI Assistant:</b><br>❌ Population failed: {error_msg}<br>"
        )

        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("Ready")

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
        from src.main import switch_space, list_spaces

        global CURRENT_SPACE
        if switch_space(space_name):
            CURRENT_SPACE = space_name
            self.status_label.setText(f"Space: {space_name}")
            # Update the combo box to reflect current spaces
            self.space_combo.clear()
            self.space_combo.addItems(list_spaces())
            self.space_combo.setCurrentText(CURRENT_SPACE)
        else:
            self.status_label.setText(
                f"Failed to switch to space: {space_name}")
            # Reset to current space
            self.space_combo.setCurrentText(CURRENT_SPACE)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.dark_theme = not self.dark_theme
        self.apply_styling()

        # Update theme button text and icon
        if self.dark_theme:
            self.theme_button.setText("🌙 Dark")
            self.theme_button.setStyleSheet("""
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
            """)
        else:
            self.theme_button.setText("☀️ Light")
            self.theme_button.setStyleSheet("""
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
            """)

    def handle_quit(self):
        """Handle quit commands."""
        from src.main import save_memory

        formatted_response = self.markdown_to_html(
            "Goodbye! Have a great day!")
        self.chat_display.append(
            f"<b>AI Assistant:</b><br>{formatted_response}<br>")
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
        """Handle slash commands locally (like CLI)."""
        command = command_text[1:].strip().lower(
        )  # Remove leading slash and normalize

        # Import required functions if backend is available
        if not BACKEND_AVAILABLE:
            self.chat_display.append(
                "<b>AI Assistant:</b><br>❌ Backend not available for commands<br>"
            )
            return

        from src.main import (
            save_memory,
            get_space_collection_name,
            list_spaces,
            switch_space,
            delete_space,
            get_vectorstore,
        )

        # Declare globals for mode variables
        global CONTEXT_MODE, LEARNING_MODE

        try:
            # /memory - Display current conversation history
            if command == "memory":
                self.chat_display.append(
                    "<b>AI Assistant:</b><br>--- Conversation Memory ---<br>"
                )
                for i, msg in enumerate(conversation_history):
                    if hasattr(msg, "type"):
                        msg_type = (
                            "System"
                            if msg.type == "system"
                            else ("User" if msg.type == "human" else "AI")
                        )
                        content = str(msg.content) if msg.content else ""
                        preview = (
                            content[:100] + "..." if len(content) > 100 else content
                        )
                        # Escape HTML characters in preview
                        preview = (
                            preview.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                        )
                        self.chat_display.append(
                            f"{i + 1}. [{msg_type}] {preview}<br>")
                    else:
                        content = str(msg)
                        preview = (
                            content[:100] + "..." if len(content) > 100 else content
                        )
                        # Escape HTML characters in preview
                        preview = (
                            preview.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                        )
                        self.chat_display.append(f"{i + 1}. {preview}<br>")
                self.chat_display.append(
                    f"Total messages: {
                        len(conversation_history)
                    }<br>--- End Memory ---<br>"
                )

            # /clear - Reset conversation memory
            elif command == "clear":
                # Clear conversation history
                conversation_history[:] = []

                # Save the cleared state
                save_memory(conversation_history)

                # Clear display and show confirmation
                self.chat_display.clear()
                self.chat_display.append(
                    "<b>AI Assistant:</b><br>Conversation memory cleared. Starting fresh.<br>"
                )

                # Add a new system message for the fresh start
                from langchain_core.messages import SystemMessage

                conversation_history.append(
                    SystemMessage(content="Lets get some coding done..")
                )
                save_memory(conversation_history)

            # /export - Export conversation history
            elif command.startswith("export"):
                export_format = command[7:].strip() if len(
                    command) > 7 else "json"
                if not conversation_history:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br>No conversation history to export.<br>"
                    )
                else:
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"conversation_export_{timestamp}.{
                        export_format if export_format != 'markdown' else 'md'
                    }"

                    try:
                        if export_format == "json":
                            # Export as JSON
                            import json

                            export_data = {
                                "export_timestamp": datetime.now().isoformat(),
                                "total_messages": len(conversation_history),
                                "messages": [],
                            }

                            for i, msg in enumerate(conversation_history):
                                msg_type = (
                                    type(msg).__name__.replace(
                                        "Message", "").lower())
                                export_data["messages"].append(
                                    {
                                        "index": i + 1,
                                        "type": msg_type,
                                        "content": str(msg.content),
                                        "timestamp": datetime.now().isoformat(),
                                    }
                                )

                            with open(filename, "w", encoding="utf-8") as f:
                                json.dump(
                                    export_data, f, indent=2, ensure_ascii=False)

                        else:  # markdown
                            # Export as Markdown
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(
                                    "# AI Assistant Conversation Export\n\n")
                                f.write(
                                    f"**Export Date:** {
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    }\n"
                                )
                                f.write(
                                    f"**Total Messages:** {
                                        len(conversation_history)
                                    }\n\n"
                                )
                                f.write("---\n\n")

                                for i, msg in enumerate(conversation_history):
                                    msg_type = type(msg).__name__.replace(
                                        "Message", "")
                                    content = str(msg.content)

                                    # Format based on message type
                                    if msg_type == "Human":
                                        f.write(
                                            f"## User Message {
                                                i + 1}\n\n{content}\n\n")
                                    elif msg_type == "AI":
                                        f.write(
                                            f"## AI Response {
                                                i + 1}\n\n{content}\n\n")
                                    elif msg_type == "System":
                                        f.write(
                                            f"### System Message {i + 1}\n\n*{
                                                content
                                            }*\n\n"
                                        )
                                    else:
                                        f.write(
                                            f"## {msg_type} Message {
                                                i + 1}\n\n{content}\n\n")

                                    f.write("---\n\n")

                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>✅ Conversation exported to: {filename}<br>")
                        self.chat_display.append(
                            f"📊 Messages exported: {
                                len(conversation_history)}<br>")
                        self.chat_display.append(
                            f"📄 Format: {export_format}<br>")

                    except Exception as e:
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Failed to export conversation: {e}<br>")

            # /space - Space/workspace management
            elif command.startswith("space"):
                space_cmd = command[6:].strip()  # Remove 'space ' prefix

                if not space_cmd:
                    # Show current space
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Current space: {CURRENT_SPACE}<br>")
                    self.chat_display.append(
                        f"Collection: {
                            get_space_collection_name(CURRENT_SPACE)}<br>")
                    self.chat_display.append("<br><b>Usage:</b><br>")
                    self.chat_display.append(
                        "  /space list &nbsp;&nbsp;&nbsp;&nbsp; - List all spaces<br>"
                    )
                    self.chat_display.append(
                        "  /space create &lt;name&gt; - Create new space<br>"
                    )
                    self.chat_display.append(
                        "  /space switch &lt;name&gt; - Switch to space<br>"
                    )
                    self.chat_display.append(
                        "  /space delete &lt;name&gt; - Delete space<br>"
                    )
                    self.chat_display.append(
                        "  /space current &nbsp;&nbsp; - Show current space<br><br>"
                    )
                    return

                if space_cmd == "list":
                    spaces = list_spaces()
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Available spaces ({len(spaces)}):<br>"
                    )
                    for space in spaces:
                        marker = " ← current" if space == CURRENT_SPACE else ""
                        self.chat_display.append(f"  • {space}{marker}<br>")
                    self.chat_display.append("<br>")

                elif space_cmd == "current":
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Current space: {CURRENT_SPACE}<br>")
                    self.chat_display.append(
                        f"Collection: {
                            get_space_collection_name(CURRENT_SPACE)
                        }<br><br>"
                    )

                elif space_cmd.startswith("create "):
                    new_space = space_cmd[7:].strip()
                    if not new_space:
                        self.chat_display.append(
                            "<b>AI Assistant:</b><br>❌ Usage: /space create &lt;name&gt;<br><br>"
                        )
                        return

                    if new_space in list_spaces():
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Space '{new_space}' already exists<br><br>")
                        return

                    if switch_space(new_space):
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>✅ Created and switched to space: {new_space}<br>")
                        self.chat_display.append(
                            f"Collection: {
                                get_space_collection_name(new_space)
                            }<br><br>"
                        )
                        # Update the space combo box
                        self.space_combo.clear()
                        self.space_combo.addItems(list_spaces())
                        self.space_combo.setCurrentText(CURRENT_SPACE)
                    else:
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Failed to create space: {new_space}<br><br>")

                elif space_cmd.startswith("switch "):
                    target_space = space_cmd[7:].strip()
                    if not target_space:
                        self.chat_display.append(
                            "<b>AI Assistant:</b><br>❌ Usage: /space switch &lt;name&gt;<br><br>"
                        )
                        return

                    if target_space not in list_spaces():
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Space '{target_space}' does not exist<br>")
                        self.chat_display.append(
                            f"Use '/space create {target_space}' to create it first<br><br>")
                        return

                    if switch_space(target_space):
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>✅ Switched to space: {target_space}<br>")
                        self.chat_display.append(
                            f"Collection: {
                                get_space_collection_name(target_space)
                            }<br><br>"
                        )
                        # Update the space combo box
                        self.space_combo.setCurrentText(CURRENT_SPACE)
                    else:
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Failed to switch to space: {target_space}<br><br>")

                elif space_cmd.startswith("delete "):
                    target_space = space_cmd[7:].strip()
                    if not target_space:
                        self.chat_display.append(
                            "<b>AI Assistant:</b><br>❌ Usage: /space delete &lt;name&gt;<br><br>"
                        )
                        return

                    if target_space == "default":
                        self.chat_display.append(
                            "<b>AI Assistant:</b><br>❌ Cannot delete the default space<br><br>"
                        )
                        return

                    if target_space not in list_spaces():
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Space '{target_space}' does not exist<br><br>")
                        return

                    # For GUI, we'll just delete without confirmation for
                    # simplicity
                    if delete_space(target_space):
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>✅ Deleted space: {target_space}<br><br>")
                        # Update the space combo box
                        self.space_combo.clear()
                        self.space_combo.addItems(list_spaces())
                        if CURRENT_SPACE not in list_spaces():
                            # If current space was deleted, switch to default
                            switch_space("default")
                            self.space_combo.setCurrentText(CURRENT_SPACE)
                    else:
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Failed to delete space: {target_space}<br><br>")

                else:
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>❌ Unknown space command: {space_cmd}<br>")
                    self.chat_display.append("Use '/space' for help<br><br>")

            # /vectordb - Show vector database contents
            elif command == "vectordb":
                self.display_vector_database()

            # /mem0 - Show personalized memory contents
            elif command == "mem0":
                self.display_mem0_memory()

            # /learn - Add information to knowledge base
            elif command.startswith("learn"):
                learn_text = command[5:].strip()  # Remove 'learn' prefix
                if not learn_text:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br>❌ Usage: /learn &lt;information to remember&gt;<br><br>"
                    )
                    return

                current_vectorstore = get_vectorstore()
                if not current_vectorstore:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br>❌ Vector database not available.<br>"
                    )
                    self.chat_display.append(
                        "ChromaDB is required for learning features.<br><br>"
                    )
                    return

                try:
                    # Import required classes
                    from langchain_core.documents import Document

                    # Create document with metadata
                    metadata = {
                        "source": "user-input",
                        "added_at": str(datetime.now()),
                        "space": CURRENT_SPACE,
                    }

                    doc = Document(page_content=learn_text, metadata=metadata)

                    # Add to vector database
                    current_vectorstore.add_documents([doc])

                    # Save memory
                    save_memory(conversation_history)

                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>✅ Learned: {learn_text[:50]}"
                    )
                    if len(learn_text) > 50:
                        self.chat_display.append("...")
                    self.chat_display.append("<br><br>")

                except Exception as e:
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>❌ Failed to learn: {str(e)}<br><br>"
                    )

            # /populate - Populate vector database with code files
            elif command.startswith("populate"):
                if not POPULATION_AVAILABLE:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br>❌ Population functionality not available.<br>"
                    )
                    self.chat_display.append(
                        "Required langchain modules could not be imported.<br>"
                    )
                    return

                dir_path = command[8:].strip()  # Remove 'populate' prefix
                if not dir_path:
                    self.chat_display.append(
                        "<b>AI Assistant:</b><br><b>Usage:</b> /populate /path/to/directory<br>"
                    )
                    self.chat_display.append(
                        "<b>Example:</b> /populate /Users/username/projects/myapp<br>"
                    )
                    self.chat_display.append(
                        "<b>Example:</b> /populate src/<br><br>")
                    self.chat_display.append(
                        "For advanced options (--dry-run, --direct-api), use the tools/populate_codebase.py script.<br>"
                    )
                    self.chat_display.append(
                        "This will recursively scan and add all code files to the vector database.<br>"
                    )
                else:
                    # Validate directory exists
                    if not os.path.exists(dir_path):
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Directory not found: {dir_path}<br>")
                        return

                    if not os.path.isdir(dir_path):
                        self.chat_display.append(
                            f"<b>AI Assistant:</b><br>❌ Path is not a directory: {dir_path}<br>")
                        return

                    # Start population in background thread
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>🔍 Starting codebase population from: {dir_path}<br>")
                    self.chat_display.append(
                        "This may take a while depending on the codebase size...<br>"
                    )

                    # Disable input during population
                    self.input_field.setEnabled(False)
                    self.send_button.setEnabled(False)
                    self.status_label.setText("Populating database...")

                    # Start population worker
                    current_vectorstore = get_vectorstore()
                    self.populate_worker = PopulateWorker(
                        dir_path, current_vectorstore)
                    self.populate_worker.progress.connect(
                        self.on_populate_progress)
                    self.populate_worker.finished.connect(
                        self.on_populate_finished)
                    self.populate_worker.error.connect(self.on_populate_error)
                    self.populate_worker.start()

            # /model - Show current model information
            elif command == "model":
                model_info = f"Current model: {MODEL_NAME}<br>"
                model_info += "To use a different model:<br>"
                model_info += "1. Load the model in LM Studio<br>"
                model_info += "2. Set MODEL_NAME in .env file<br>"
                model_info += "3. Restart the application<br>"
                self.chat_display.append(
                    f"<b>AI Assistant:</b><br>{model_info}")

            # /context - Control context integration
            elif command.startswith("context"):
                mode = command[7:].strip()
                if mode in ["auto", "on", "off"]:
                    CONTEXT_MODE = mode
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Context integration mode set to: <b>{mode}</b><br>")
                    if mode == "auto":
                        self.chat_display.append(
                            "AI will automatically decide when to use context from knowledge base.<br>"
                        )
                    elif mode == "on":
                        self.chat_display.append(
                            "AI will always include relevant context from knowledge base.<br>"
                        )
                    elif mode == "off":
                        self.chat_display.append(
                            "AI will never include context from knowledge base.<br>"
                        )
                else:
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Current context mode: <b>{CONTEXT_MODE}</b><br>")
                    self.chat_display.append("Usage: /context auto|on|off<br>")
                    self.chat_display.append(
                        "&nbsp;&nbsp;auto - AI decides when to use context (default)<br>"
                    )
                    self.chat_display.append(
                        "&nbsp;&nbsp;on &nbsp;&nbsp; - Always include relevant context<br>"
                    )
                    self.chat_display.append(
                        "&nbsp;&nbsp;off &nbsp; - Never include context from knowledge base<br>"
                    )

            # /learning - Control learning behavior
            elif command.startswith("learning"):
                mode = command[8:].strip()
                if mode in ["normal", "strict", "off"]:
                    LEARNING_MODE = mode
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Learning mode set to: <b>{mode}</b><br>")
                    if mode == "normal":
                        self.chat_display.append(
                            "AI will learn from /learn commands and provide context when relevant.<br>"
                        )
                    elif mode == "strict":
                        self.chat_display.append(
                            "AI will only use learned information for explicit learning queries.<br>"
                        )
                    elif mode == "off":
                        self.chat_display.append(
                            "AI will not use or reference learned information.<br>"
                        )
                else:
                    self.chat_display.append(
                        f"<b>AI Assistant:</b><br>Current learning mode: <b>{LEARNING_MODE}</b><br>")
                    self.chat_display.append(
                        "Usage: /learning normal|strict|off<br>")
                    self.chat_display.append(
                        "&nbsp;&nbsp;normal - Balanced learning and context usage (default)<br>"
                    )
                    self.chat_display.append(
                        "&nbsp;&nbsp;strict - Minimal context, focused on learning queries<br>"
                    )
                    self.chat_display.append(
                        "&nbsp;&nbsp;off &nbsp;&nbsp;&nbsp; - Disable all learning and context features<br>"
                    )

            # /help - Display available commands
            elif command in ["help", "h", "?"]:
                help_html = """--- Available Commands ---<br>
/memory &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Show conversation history<br>
/vectordb &nbsp;&nbsp;&nbsp;&nbsp; - Show knowledge base statistics<br>
/mem0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Show personalized memory contents<br>
/model &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Show current model information<br>
/space &lt;cmd&gt; &nbsp;&nbsp;&nbsp; - Space/workspace management (list/create/switch/delete)<br>
/context &lt;mode&gt; - Control context integration (auto/on/off)<br>
/learning &lt;mode&gt; - Control learning behavior (normal/strict/off)<br>
/populate &lt;path&gt; - Add code files from directory to vector DB<br>
/clear &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Clear conversation history<br>
/learn &lt;text&gt; &nbsp;&nbsp; - Add information to knowledge base<br>
/export &lt;fmt&gt; &nbsp; - Export conversation (json/markdown)<br>
/help &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Show this help message<br>
<br>
Regular commands (no slash needed):<br>
quit &nbsp;&nbsp;&nbsp; - Exit the application<br>
exit &nbsp;&nbsp;&nbsp; - Exit the application<br>
q &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - Exit the application<br>
<br>
Note: Quit commands work after AI finishes responding.<br>
Use Ctrl+C for immediate interruption.<br>
--- End Help ---"""
                self.chat_display.append(
                    f"<b>AI Assistant:</b><br>{help_html}")

            # Unknown command
            else:
                self.chat_display.append(
                    f"<b>AI Assistant:</b><br>Unknown command: /{command}<br>"
                )
                self.chat_display.append(
                    "Type /help for available commands<br>")

        except Exception as e:
            self.chat_display.append(
                f"<b>AI Assistant:</b><br>Error processing command: {str(e)}<br>"
            )

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def closeEvent(self, a0):
        """Handle application close."""
        from src.main import save_memory

        try:
            if BACKEND_AVAILABLE:
                save_memory(conversation_history)
                logger.info("Conversation memory saved during GUI shutdown")
        except Exception as e:
            logger.error(f"Failed to save memory during shutdown: {e}")
        if a0:
            a0.accept()


def main():
    """Main GUI application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("AI Assistant")
    app.setApplicationVersion("0.2.0")
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

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
