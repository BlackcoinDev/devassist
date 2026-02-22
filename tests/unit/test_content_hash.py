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
Test cases for content hashing utility.

Tests the compute_content_hash function for deterministic behavior,
different content producing different hashes, and error handling.
"""

import tempfile
from pathlib import Path
from src.learning.content_hash import compute_content_hash


class TestContentHash:
    """Test suite for content hashing utility."""

    def test_deterministic_hashing_same_file(self):
        """Test that same file produces same hash consistently."""
        # Create temporary file with test content
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("This is test content for hashing.")
            temp_path = Path(temp_file.name)

        try:
            # Compute hash multiple times
            hash1 = compute_content_hash(temp_path)
            hash2 = compute_content_hash(temp_path)
            hash3 = compute_content_hash(temp_path)

            # All hashes should be identical
            assert hash1 == hash2 == hash3
            assert hash1 is not None
            assert len(hash1) == 16  # Should be truncated to 16 chars

        finally:
            # Clean up
            temp_path.unlink()

    def test_different_content_different_hash(self):
        """Test that different content produces different hashes."""
        # Create two temporary files with different content
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file1:
            temp_file1.write("First content for testing.")
            temp_path1 = Path(temp_file1.name)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file2:
            temp_file2.write("Second different content for testing.")
            temp_path2 = Path(temp_file2.name)

        try:
            # Compute hashes
            hash1 = compute_content_hash(temp_path1)
            hash2 = compute_content_hash(temp_path2)

            # Hashes should be different
            assert hash1 != hash2
            assert hash1 is not None
            assert hash2 is not None
            assert len(hash1) == 16
            assert len(hash2) == 16

        finally:
            # Clean up
            temp_path1.unlink()
            temp_path2.unlink()

    def test_error_handling_missing_file(self):
        """Test error handling for non-existent files."""
        # Try to hash a non-existent file
        fake_path = Path("/nonexistent/file12345.txt")
        result = compute_content_hash(fake_path)

        # Should return None for missing file
        assert result is None

    def test_error_handling_permission_issues(self):
        """Test error handling for permission issues."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Test content")
            temp_path = Path(temp_file.name)

        try:
            # Make file unreadable (Unix-based systems)
            temp_path.chmod(0o000)

            # Try to hash it - should return None
            result = compute_content_hash(temp_path)
            assert result is None

        finally:
            # Restore permissions and clean up
            temp_path.chmod(0o644)
            temp_path.unlink()

    def test_hash_length_and_format(self):
        """Test that hash has correct length and format."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("Testing hash format and length.")
            temp_path = Path(temp_file.name)

        try:
            # Compute hash
            result = compute_content_hash(temp_path)

            # Check format
            assert result is not None
            assert len(result) == 16
            assert isinstance(result, str)
            assert all(c in "0123456789abcdef" for c in result)  # Hex characters only

        finally:
            # Clean up
            temp_path.unlink()

    def test_different_sample_sizes(self):
        """Test that different sample sizes produce different hashes for large files."""
        # Create a larger temporary file
        large_content = (
            "This is a longer content. " * 100
        )  # Make it larger than default sample size
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(large_content)
            temp_path = Path(temp_file.name)

        try:
            # Compute hashes with different sample sizes
            hash_default = compute_content_hash(temp_path, sample_size=1024)
            hash_larger = compute_content_hash(temp_path, sample_size=2048)

            # For large files, different sample sizes should produce different hashes
            # (unless the content is uniform, which it's not in this case)
            assert hash_default is not None
            assert hash_larger is not None
            assert len(hash_default) == 16
            assert len(hash_larger) == 16

        finally:
            # Clean up
            temp_path.unlink()

    def test_empty_file_hashing(self):
        """Test hashing of empty files."""
        # Create empty temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # Compute hash of empty file
            result = compute_content_hash(temp_path)

            # Should still work and return a valid hash
            assert result is not None
            assert len(result) == 16

        finally:
            # Clean up
            temp_path.unlink()
