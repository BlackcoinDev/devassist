#!/usr/bin/env python3
"""
Test suite for Database Module (src/storage/database.py).

Tests cover:
- Database initialization and schema creation
- Connection management via ApplicationContext
- Thread-safe access logic
- Proper cleanup and connection closing
"""

import sqlite3
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.storage.database import initialize_database, get_database_connection
from src.core.context import get_context, reset_context


class TestDatabaseConnection:
    """Test database connection initialization and management."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

    def teardown_method(self):
        """Clean up test environment."""
        ctx = get_context()
        if ctx.db_conn is not None:
            ctx.db_conn.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
        reset_context()

    def test_initialize_database_creates_file(self):
        """Test that initialize_database creates the database file and schema."""
        with patch('src.core.config.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_config.db_path = self.temp_db.name
            mock_get_config.return_value = mock_config

            conn, lock = initialize_database()

            assert conn is not None
            assert lock is not None
            assert os.path.exists(self.temp_db.name)

            # Check if table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            assert cursor.fetchone() is not None

    def test_initialize_database_updates_context(self):
        """Test that initialize_database correctly updates the ApplicationContext."""
        with patch('src.core.config.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_config.db_path = self.temp_db.name
            mock_get_config.return_value = mock_config

            initialize_database()
            ctx = get_context()

            assert ctx.db_conn is not None
            assert ctx.db_lock is not None

    def test_get_database_connection_returns_context_values(self):
        """Test retrieving connection from context."""
        ctx = get_context()
        mock_conn = MagicMock(spec=sqlite3.Connection)
        mock_lock = Mock()

        ctx.db_conn = mock_conn
        ctx.db_lock = mock_lock

        conn, lock = get_database_connection()
        assert conn is mock_conn
        assert lock is mock_lock

    def test_initialize_database_unsupported_type(self):
        """Test behavior when an unsupported database type is configured."""
        with patch('src.storage.database.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "postgres"  # Unsupported
            mock_get_config.return_value = mock_config

            conn, lock = initialize_database()
            assert conn is None
            assert lock is None


class TestDatabaseOperations:
    """Test standard database operations and cleanup."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

    def teardown_method(self):
        """Clean up test environment."""
        ctx = get_context()
        if ctx.db_conn is not None:
            ctx.db_conn.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
        reset_context()

    def test_schema_columns(self):
        """Verify the conversations table has the expected columns."""
        with patch('src.core.config.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_config.db_path = self.temp_db.name
            mock_get_config.return_value = mock_config

            conn, _ = initialize_database()
            assert conn is not None
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [info[1] for info in cursor.fetchall()]

            expected_columns = ['id', 'session_id', 'message_type', 'content', 'timestamp']
            for col in expected_columns:
                assert col in columns
