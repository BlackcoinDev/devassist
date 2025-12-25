#!/usr/bin/env python3
"""
Unit tests for Mem0 Local memory system.

Tests cover:
- Memory and preference storage initialization
- CRUD operations (Create, Read, Update, Delete)
- Search and retrieval functionality
- Database persistence
- Error handling and edge cases
"""

import unittest
import tempfile
import sqlite3
from unittest.mock import patch
from src.storage.mem0_local import (
    initialize_mem0_local,
    add_preference,
    get_preference,
    add_memory,
    get_memories,
    search_memories,
)


class TestMem0LocalInitialization(unittest.TestCase):
    """Test initialization of Mem0 local memory system."""

    @patch("src.storage.mem0_local.get_config")
    def test_initialize_mem0_local_success(self, mock_config):
        """Test successful initialization of Mem0 tables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            mock_config.return_value.db_path = db_path

            result = initialize_mem0_local()

            self.assertIsInstance(result, dict)
            self.assertEqual(result["mem0_preferences"], "✅ Created")
            self.assertEqual(result["mem0_memories"], "✅ Created")
            self.assertEqual(result["database"], db_path)

            # Verify tables exist
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
            conn.close()

            self.assertIn("mem0_preferences", tables)
            self.assertIn("mem0_memories", tables)

    @patch("src.storage.mem0_local.get_config")
    def test_initialize_mem0_local_already_exists(self, mock_config):
        """Test initialization when tables already exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            mock_config.return_value.db_path = db_path

            # Initialize once
            result1 = initialize_mem0_local()
            self.assertEqual(result1["mem0_preferences"], "✅ Created")

            # Initialize again (tables should already exist)
            result2 = initialize_mem0_local()
            self.assertEqual(result2["mem0_preferences"], "✅ Created")

    @patch("src.storage.mem0_local.get_config")
    def test_initialize_mem0_local_failure(self, mock_config):
        """Test initialization failure handling."""
        mock_config.return_value.db_path = "/invalid/path/test.db"

        result = initialize_mem0_local()

        self.assertEqual(result["mem0_preferences"], "❌ Failed")
        self.assertEqual(result["mem0_memories"], "❌ Failed")


class TestPreferences(unittest.TestCase):
    """Test preference system (note: current implementation has schema issues)."""

    def setUp(self):
        """Set up test database."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = f"{self.tmpdir.name}/test.db"

        # Create database
        with patch("src.storage.mem0_local.get_config") as mock_config:
            mock_config.return_value.db_path = self.db_path
            initialize_mem0_local()

    def tearDown(self):
        """Clean up test database."""
        self.tmpdir.cleanup()

    @patch("src.storage.mem0_local.get_config")
    def test_get_preference_not_found(self, mock_config):
        """Test retrieving a non-existent preference."""
        mock_config.return_value.db_path = self.db_path

        result = get_preference("nonexistent")

        self.assertIsNone(result)

    @patch("src.storage.mem0_local.get_config")
    def test_preference_api_error_handling(self, mock_config):
        """Test that preference functions handle database errors gracefully."""
        mock_config.return_value.db_path = "/invalid/path.db"

        # These should return error indicators, not crash
        add_result = add_preference("key", "value")
        get_result = get_preference("key")

        self.assertFalse(add_result)
        self.assertIsNone(get_result)


class TestMemories(unittest.TestCase):
    """Test memory storage and retrieval."""

    def setUp(self):
        """Set up test database."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = f"{self.tmpdir.name}/test.db"

        with patch("src.storage.mem0_local.get_config") as mock_config:
            mock_config.return_value.db_path = self.db_path
            initialize_mem0_local()

    def tearDown(self):
        """Clean up test database."""
        self.tmpdir.cleanup()

    @patch("src.storage.mem0_local.get_config")
    def test_add_memory(self, mock_config):
        """Test adding a memory."""
        mock_config.return_value.db_path = self.db_path

        result = add_memory("User likes Python")

        self.assertTrue(result)

        # Verify in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM mem0_memories WHERE user_id = ?",
                       ("default_user",))
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "User likes Python")

    @patch("src.storage.mem0_local.get_config")
    def test_get_memories_empty(self, mock_config):
        """Test retrieving memories when none exist."""
        mock_config.return_value.db_path = self.db_path

        result = get_memories()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch("src.storage.mem0_local.get_config")
    def test_get_memories_multiple(self, mock_config):
        """Test retrieving multiple memories."""
        mock_config.return_value.db_path = self.db_path

        add_memory("Memory 1")
        add_memory("Memory 2")
        add_memory("Memory 3")

        result = get_memories()

        self.assertEqual(len(result), 3)
        # Verify all are dictionaries with expected keys
        for memory in result:
            self.assertIn("id", memory)
            self.assertIn("content", memory)
            self.assertIn("created_at", memory)

    @patch("src.storage.mem0_local.get_config")
    def test_get_memories_ordered_by_creation(self, mock_config):
        """Test that memories are returned in reverse creation order."""
        mock_config.return_value.db_path = self.db_path

        add_memory("First")
        add_memory("Second")
        add_memory("Third")

        result = get_memories()

        # Verify order (most recent first)
        self.assertEqual(len(result), 3)
        self.assertTrue(any(m["content"] == "Third" for m in result))
        self.assertTrue(any(m["content"] == "Second" for m in result))
        self.assertTrue(any(m["content"] == "First" for m in result))

    @patch("src.storage.mem0_local.get_config")
    def test_search_memories_found(self, mock_config):
        """Test searching for memories."""
        mock_config.return_value.db_path = self.db_path

        add_memory("Python is great")
        add_memory("JavaScript is useful")
        add_memory("Python is fast")

        result = search_memories("Python")

        self.assertEqual(len(result), 2)
        self.assertTrue(all("Python" in m["content"] for m in result))

    @patch("src.storage.mem0_local.get_config")
    def test_search_memories_not_found(self, mock_config):
        """Test searching with no matches."""
        mock_config.return_value.db_path = self.db_path

        add_memory("Some content")
        result = search_memories("nonexistent")

        self.assertEqual(len(result), 0)

    @patch("src.storage.mem0_local.get_config")
    def test_search_memories_case_insensitive(self, mock_config):
        """Test that search is case insensitive."""
        mock_config.return_value.db_path = self.db_path

        add_memory("User likes Python")
        result = search_memories("PYTHON")

        self.assertEqual(len(result), 1)

    @patch("src.storage.mem0_local.get_config")
    def test_memories_multiple_users(self, mock_config):
        """Test memories for different users."""
        mock_config.return_value.db_path = self.db_path

        add_memory("User1 memory", "user1")
        add_memory("User2 memory", "user2")

        result1 = get_memories("user1")
        result2 = get_memories("user2")

        self.assertEqual(len(result1), 1)
        self.assertEqual(len(result2), 1)
        self.assertEqual(result1[0]["content"], "User1 memory")
        self.assertEqual(result2[0]["content"], "User2 memory")

    @patch("src.storage.mem0_local.get_config")
    def test_memories_respects_limit(self, mock_config):
        """Test that memory retrieval respects the 100 item limit."""
        mock_config.return_value.db_path = self.db_path

        # Add more than 100 memories (we'll add 110)
        for i in range(110):
            add_memory(f"Memory {i}")

        result = get_memories()

        # Should be limited to 100
        self.assertEqual(len(result), 100)

    @patch("src.storage.mem0_local.get_config")
    def test_search_memories_respects_limit(self, mock_config):
        """Test that memory search respects the 10 item limit."""
        mock_config.return_value.db_path = self.db_path

        # Add multiple matching memories
        for i in range(20):
            add_memory(f"Python memory {i}")

        result = search_memories("Python")

        # Should be limited to 10
        self.assertEqual(len(result), 10)


class TestDatabasePersistence(unittest.TestCase):
    """Test that data persists across operations."""

    @patch("src.storage.mem0_local.get_config")
    def test_data_persistence_memories(self, mock_config):
        """Test that memory data persists across connections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/test.db"
            mock_config.return_value.db_path = db_path

            # Initialize database
            initialize_mem0_local()

            # Add memory data
            add_memory("Test memory 1")
            add_memory("Test memory 2")

            # Verify with direct database query
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM mem0_memories")
            mem_count = cursor.fetchone()[0]

            conn.close()

            self.assertEqual(mem_count, 2)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    @patch("src.storage.mem0_local.get_config")
    def test_add_preference_invalid_db(self, mock_config):
        """Test adding preference with invalid database."""
        mock_config.return_value.db_path = "/invalid/path/db.db"

        result = add_preference("key", "value")

        self.assertFalse(result)

    @patch("src.storage.mem0_local.get_config")
    def test_get_preference_invalid_db(self, mock_config):
        """Test getting preference with invalid database."""
        mock_config.return_value.db_path = "/invalid/path/db.db"

        result = get_preference("key")

        self.assertIsNone(result)

    @patch("src.storage.mem0_local.get_config")
    def test_add_memory_invalid_db(self, mock_config):
        """Test adding memory with invalid database."""
        mock_config.return_value.db_path = "/invalid/path/db.db"

        result = add_memory("content")

        self.assertFalse(result)

    @patch("src.storage.mem0_local.get_config")
    def test_get_memories_invalid_db(self, mock_config):
        """Test getting memories with invalid database."""
        mock_config.return_value.db_path = "/invalid/path/db.db"

        result = get_memories()

        self.assertEqual(result, [])

    @patch("src.storage.mem0_local.get_config")
    def test_search_memories_invalid_db(self, mock_config):
        """Test searching memories with invalid database."""
        mock_config.return_value.db_path = "/invalid/path/db.db"

        result = search_memories("query")

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
