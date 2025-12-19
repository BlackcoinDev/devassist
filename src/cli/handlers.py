"""
CLI Command Handlers

This module contains all the command handler functions extracted from main.py
for better code organization and maintainability.
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Import necessary modules
from src.storage import (
    load_memory,
    save_memory,
    trim_history,
    cleanup_memory,
)
from src.vectordb import (
    list_spaces,
    switch_space,
    delete_space,
    get_space_collection_name,
    load_current_space,
    save_current_space,
)
from src.core.config import APP_VERSION
from src.core.context import get_context

# These will be imported from main when needed to avoid circular imports
# conversation_history, vectorstore, embeddings, llm, chunk_text, get_relevant_context


def handle_read_command(file_path: str):
    """Handle /read command to read file contents."""
    if not file_path:
        print("\n❌ Usage: /read <file_path>")
        print("Example: /read README.md\n")
        return

    try:
        # Security: Only allow reading files in current directory and
        # subdirectories
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        # Check if the file is within the current directory
        if not full_path.startswith(current_dir):
            print(f"\n❌ Access denied: Cannot read files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        if not os.path.exists(full_path):
            print(f"\n❌ File not found: {file_path}\n")
            return

        if not os.path.isfile(full_path):
            print(f"\n❌ Not a file: {file_path}\n")
            return

        # Check file size (limit to 1MB to prevent memory issues)
        file_size = os.path.getsize(full_path)
        if file_size > 1024 * 1024:  # 1MB limit
            print(f"\n❌ File too large: {file_size} bytes (max 1MB)")
            print("Use a text editor to view large files\n")
            return

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        print(f"\n📄 File: {file_path}")
        print(f"📊 Size: {file_size} bytes")
        print("-" * 50)
        print(content)
        print("-" * 50)
        print(f"✅ File read successfully\n")

    except UnicodeDecodeError:
        print(f"\n❌ Cannot read binary file: {file_path}")
        print("This appears to be a binary file. Use /list to see file types.\n")
    except Exception as e:
        print(f"\n❌ Failed to read file: {e}\n")


def handle_write_command(args: str):
    """Handle /write command to write content to a file."""
    if not args:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Example: /write notes.txt This is my note\n")
        return

    # Split on first space to separate file path from content
    parts = args.split(" ", 1)
    if len(parts) < 2:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Content is required\n")
        return

    file_path, content = parts

    try:
        # Security: Only allow writing files in current directory and
        # subdirectories
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        # Check if the file is within the current directory
        if not full_path.startswith(current_dir):
            print(f"\n❌ Access denied: Cannot write files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        # Create directory if it doesn't exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✅ File written: {file_path}")
        print(f"📊 Content length: {len(content)} characters\n")

    except Exception as e:
        print(f"\n❌ Failed to write file: {e}\n")


def handle_list_command(dir_path: str = ""):
    """Handle /list command to list directory contents."""
    try:
        if not dir_path:
            target_dir = os.getcwd()
        else:
            # Security: Only allow listing directories in current directory
            current_dir = os.getcwd()
            full_path = os.path.abspath(dir_path)

            if not full_path.startswith(current_dir):
                print(
                    f"\n❌ Access denied: Cannot list directories outside current directory"
                )
                print(f"Current directory: {current_dir}\n")
                return

            if not os.path.exists(full_path):
                print(f"\n❌ Directory not found: {dir_path}\n")
                return

            if not os.path.isdir(full_path):
                print(f"\n❌ Not a directory: {dir_path}\n")
                return

            target_dir = full_path

        print(f"\n📁 Directory: {os.path.relpath(target_dir, os.getcwd()) or '.'}")
        print("-" * 50)

        items = os.listdir(target_dir)
        if not items:
            print("📂 (empty directory)")
        else:
            # Separate files and directories
            dirs = []
            files = []

            for item in sorted(items):
                full_item_path = os.path.join(target_dir, item)
                if os.path.isdir(full_item_path):
                    dirs.append(item + "/")
                else:
                    files.append(item)

            # Display directories first, then files
            for item in dirs + files:
                print(f"  {item}")

        print("-" * 50)
        print(f"📊 Total items: {len(items)}\n")

    except Exception as e:
        print(f"\n❌ Failed to list directory: {e}\n")


def handle_pwd_command():
    """Handle /pwd command to show current working directory."""
    current_dir = os.getcwd()
    print(f"\n📍 Current directory: {current_dir}\n")


# Additional functions will be added as needed to avoid circular imports
# For now, focus on the core file operations that don't have complex dependencies


def handle_clear_command() -> bool:
    """Handle /clear command to reset conversation memory."""
    # Confirm before clearing
    print("\n⚠️  This will clear all conversation history.")
    print("This action cannot be undone.")
    try:
        response = input("Are you sure? (y/N): ").strip().lower()
        if response not in ["y", "yes"]:
            print("❌ Operation cancelled\n")
            return False
    except (KeyboardInterrupt, EOFError):
        print("\n❌ Operation cancelled\n")
        return False

    # Clear memory - this will be handled by the calling function in main.py
    # Just return True to indicate the command should proceed
    return True


def handle_learn_command(content: str):
    """Handle /learn command."""
    # Import here to avoid circular imports
    from src.main import (
        vectorstore,
        embeddings,
        CURRENT_SPACE,
        CHROMA_HOST,
        CHROMA_PORT,
        api_session,
        logger,
        operation_count,
    )

    # Check if vector database is available
    if vectorstore is None:
        print(
            "\nVector database not available. ChromaDB is required for learning features.\n"
        )
        return

    # Extract content after 'learn ' command
    if not content:
        print("\nUsage: /learn <information to remember>\n")
        return

    try:
        # Import Document class for creating knowledge entries
        from langchain_core.documents import Document

        # Create document with metadata
        doc = Document(
            page_content=content,  # The information to remember
            metadata={
                "source": "user-input",  # Mark as manually added via /learn command
                "added_at": str(datetime.now()),  # Timestamp for tracking
            },
        )

        # Add to vector database for current space
        # Generate embeddings and use direct HTTP API calls to ChromaDB v2

        # Generate embeddings using Ollama
        try:
            embeddings_result = embeddings.embed_documents([doc.page_content])
            if embeddings_result and len(embeddings_result) > 0:
                embedding_vector = embeddings_result[0]

                # Get collection for current space
                collection_name = get_space_collection_name(CURRENT_SPACE)
                collection_id = None

                # Find or create the collection
                try:
                    list_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
                    list_response = api_session.get(list_url, timeout=10)
                    if list_response.status_code == 200:
                        collections = list_response.json()
                        for coll in collections:
                            if coll.get("name") == collection_name:
                                collection_id = coll.get("id")
                                break

                    # If collection doesn't exist, create it
                    if not collection_id:
                        create_url = f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/tenants/default_tenant/databases/default_database/collections"
                        create_payload = {"name": collection_name}
                        create_response = api_session.post(
                            create_url, json=create_payload, timeout=10
                        )
                        if create_response.status_code == 201:
                            collection_id = create_response.json().get("id")
                            logger.info(
                                f"Created new collection for space {CURRENT_SPACE}: {collection_name}"
                            )
                        else:
                            logger.error(
                                f"Failed to create collection: HTTP {
                                    create_response.status_code
                                }"
                            )
                            raise Exception("Collection creation failed")

                except Exception as e:
                    logger.error(
                        f"Error managing collection for space {CURRENT_SPACE}: {e}"
                    )
                    raise

                # Add document to the space's collection
                add_url = (
                    f"http://{CHROMA_HOST}:{CHROMA_PORT}/api/v2/"
                    f"tenants/default_tenant/databases/default_database/"
                    f"collections/{collection_id}/add"
                )

                # Prepare the document data with embeddings
                doc_id = f"doc_{len(doc.page_content)}_{int(datetime.now().timestamp() * 1000000)}"
                payload = {
                    "ids": [doc_id],
                    "embeddings": [embedding_vector],
                    "documents": [doc.page_content],
                    "metadatas": [doc.metadata] if doc.metadata else [{}],
                }

                # Make the API call to add the document
                headers = {"Content-Type": "application/json"}
                response = api_session.post(
                    add_url, json=payload, headers=headers, timeout=10
                )

                if response.status_code == 201:
                    logger.info(
                        f"Document added successfully to space {CURRENT_SPACE}: {doc_id}"
                    )
                else:
                    logger.error(
                        f"Failed to add document to space {CURRENT_SPACE}: {
                            response.status_code
                        } - {response.text}"
                    )
                    raise Exception("Document addition failed")

            else:
                logger.error("Failed to generate embeddings")
                raise Exception("Embedding generation failed")

        except Exception as e:
            logger.error(f"Error with direct ChromaDB v2 API: {e}")
            # Fallback to LangChain method
            try:
                vectorstore.add_documents([doc])
                logger.debug("Used LangChain fallback for document addition")
            except Exception as fallback_e:
                logger.error(f"LangChain fallback also failed: {fallback_e}")
                print(f"\n❌ Failed to learn: {e}\n")
                return

        # Periodic memory cleanup
        operation_count += 1
        if operation_count % 50 == 0:
            cleanup_memory()

        print(f"\n✅ Learned: {content[:50]}...\n")

    except Exception as e:
        print(f"\n❌ Failed to learn: {e}\n")


def show_vectordb():
    """
    Display information about the current vector database contents.

    Shows collection statistics, chunk count, unique sources, and content insights
    from the ChromaDB vector database. Provides insights into the AI's knowledge base.
    """
    # Import here to avoid circular imports
    from src.main import vectorstore, CURRENT_SPACE

    if vectorstore is None:
        print("\n❌ Vector database not available.\n")
        return

    # Initialize variables that may be used in error handling
    collection_name = get_space_collection_name(CURRENT_SPACE)
