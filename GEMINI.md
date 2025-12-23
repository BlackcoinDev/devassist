# Gemini Code Assistant Project Context

This document provides context for the AI Assistant Chat Application, a Python-based interactive AI chat assistant.

## Project Overview

The project is an advanced interactive AI chat assistant powered by LangChain, with a choice of Large Language Models (LLMs) via LM Studio, and a ChromaDB vector database for knowledge storage. It features a dual interface (GUI and CLI), robust learning capabilities, multi-format document processing, and a comprehensive set of tools for interacting with the local environment.

### Key Technologies

* **Core Framework**: LangChain
* **LLM Serving**: LM Studio (e.g., with `qwen3-vl-30b`)
* **Vector Database**: ChromaDB v2
* **Embeddings**: Ollama
* **GUI**: PyQt6
* **CLI**: Standard terminal with `rich` for enhanced output.
* **Dependencies**: `requirements.txt` includes `langchain`, `chromadb`, `PyQt6`, `requests`, `pydantic`, and more.

### Architecture

The application is launched via `launcher.py`, which can start either a GUI (`src/gui.py`) or a CLI (`src/main.py`). It uses a modular architecture with clear separation of concerns:

* **`src/core`**: Core application logic, including configuration (`config.py`) and a central `ApplicationContext` for dependency injection.
* **`src/storage`**: Persistence layer, managing the SQLite database for conversation history (`database.py`, `memory.py`).
* **`src/vectordb`**: Handles interaction with the ChromaDB vector store.
* **`src/commands`**: A registry for slash commands available to the user.
* **`src/tools`**: A registry for tools that the AI can use to interact with the system (e.g., file system, web search, git).
* **`src/security`**: Implements security features like input sanitization and path security.

The architecture is designed to be "local-first", with all processing happening locally for privacy and control.

## Building and Running

### Prerequisites

* Python 3.13+
* `uv` package manager (recommended)
* LM Studio running with a loaded model.
* ChromaDB v2 server running.
* Ollama service running for embeddings.
* Git

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/BlackcoinDev/devassist.git
    cd devassist
    ```

2. **Create and activate a virtual environment:**

    ```bash
    uv venv venv --python 3.13
    source venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    uv pip install -r requirements.txt
    ```

4. **Configure the environment:**
    * Copy `.env.example` to `.env`.
    * Edit `.env` to provide the necessary configuration for LM Studio, ChromaDB, and Ollama.

### Running the Application

* **Launch the GUI:**

    ```bash
    uv run python launcher.py --gui
    ```

* **Launch the CLI:**

    ```bash
    uv run python launcher.py --cli
    ```

    or

    ```bash
    uv run python launcher.py
    ```

## Development Conventions

### Code Style and Quality

* The project uses `flake8`, `mypy`, `vulture`, `codespell`, and `autopep8` for linting and code quality.
* A consolidated linting script is available at `tests/lint/lint.py`.
* The code is fully type-hinted and aims for high test coverage.

### Testing

* The project uses `pytest` for testing.
* Tests are organized into `unit`, `integration`, and `security` categories.
* The test suite can be run with `pytest`.

### Command and Tool System

* The application uses a self-registering plugin system for both user-facing slash commands and AI-usable tools.
* New commands can be added by creating a handler in `src/commands/handlers/` with the `@CommandRegistry.register()` decorator.
* New AI tools can be added by creating an executor in `src/tools/executors/` with the `@ToolRegistry.register()` decorator.

### Key Files

* `launcher.py`: The main entry point for the application.
* `src/main.py`: The core logic for the CLI interface.
* `src/gui.py`: The implementation of the PyQt6 GUI.
* `.env.example`: A template for the required `.env` configuration file.
* `requirements.txt`: A list of all Python dependencies.
* `docs/ARCHITECTURE.md`: A detailed overview of the project's architecture.
* `README.md`: A comprehensive guide to the project.
