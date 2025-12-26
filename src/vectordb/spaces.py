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
Space management for DevAssist.

Spaces are isolated workspaces, each with its own ChromaDB collection.
This allows users to maintain separate knowledge bases for different projects.
"""

import json
import os
import logging
from typing import List

from src.core.context import get_context, set_current_space
from src.vectordb.client import get_chromadb_client

logger = logging.getLogger(__name__)


def get_space_collection_name(space_name: str) -> str:
    """
    Get the ChromaDB collection name for a given space.

    Args:
        space_name: User-facing space name

    Returns:
        Collection name for ChromaDB

    Naming Convention:
        - "default" space uses "knowledge_base" collection
        - Other spaces use "space_{name}" collection
    """
    if space_name == "default":
        return "knowledge_base"
    return f"space_{space_name}"


def ensure_space_collection(space_name: str) -> bool:
    """
    Ensure a collection exists for the given space.

    ChromaDB will create the collection when documents are first added,
    so this function mainly validates the space name.

    Args:
        space_name: Space to ensure

    Returns:
        True if space is valid and ready
    """
    ctx = get_context()
    if ctx.vectorstore is None:
        return False

    try:
        # ChromaDB will create collection on first document add
        # Just validate the space name here
        return True
    except Exception as e:
        logger.error(f"Failed to ensure collection for space {space_name}: {e}")
        return False


def list_spaces() -> List[str]:
    """
    List all available spaces.

    Returns:
        List of space names, always including "default"
    """
    try:
        client = get_chromadb_client()
        collections = client.list_collections()

        spaces = ["default"]  # Always include default space
        for coll in collections:
            name = coll.get("name", "")
            if name.startswith("space_"):
                space_name = name[6:]  # Remove "space_" prefix
                if space_name not in spaces:
                    spaces.append(space_name)

        return spaces

    except Exception as e:
        logger.error(f"Error listing spaces: {e}")
        return ["default"]


def delete_space(space_name: str) -> bool:
    """
    Delete a space and its collection.

    Args:
        space_name: Space to delete (cannot be "default")

    Returns:
        True if deleted successfully
    """
    if space_name == "default":
        logger.warning("Cannot delete default space")
        return False

    try:
        client = get_chromadb_client()
        collection_name = get_space_collection_name(space_name)
        return client.delete_collection(collection_name)

    except Exception as e:
        logger.error(f"Failed to delete space {space_name}: {e}")
        return False


def switch_space(space_name: str) -> bool:
    """
    Switch to a different space.

    Args:
        space_name: Space to switch to

    Returns:
        True if switch was successful
    """
    if not ensure_space_collection(space_name):
        return False

    set_current_space(space_name)
    save_current_space()
    return True


def save_current_space() -> None:
    """
    Save the current space to persistent storage.

    Writes to space_settings.json in the current directory.
    """
    ctx = get_context()
    try:
        settings = {"current_space": ctx.current_space}
        with open("space_settings.json", "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save space settings: {e}")


def load_current_space() -> str:
    """
    Load the current space from persistent storage.

    Returns:
        Space name from settings, or "default" if not found
    """
    try:
        if os.path.exists("space_settings.json"):
            with open("space_settings.json", "r") as f:
                settings = json.load(f)
                return settings.get("current_space", "default")
    except Exception as e:
        logger.warning(f"Failed to load space settings: {e}")
    return "default"
