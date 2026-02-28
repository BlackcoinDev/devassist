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
Content hashing utility for deduplication in the learning system.

This module provides robust content-based hashing for file deduplication,
ensuring that identical content is not stored multiple times in the knowledge base.
"""

import hashlib
from pathlib import Path
from typing import Optional


def compute_content_hash(file_path: Path, sample_size: int = 1024) -> Optional[str]:
    """
    Compute a content-based hash for file deduplication.

    This function hashes the first N bytes of a file combined with its file size
    to create a robust fingerprint for deduplication purposes. The hash is
    truncated to 16 characters for storage efficiency while maintaining good
    collision resistance.

    Args:
        file_path: Path to the file to hash
        sample_size: Number of bytes to read from the beginning of the file (default: 1024)

    Returns:
        Truncated SHA-256 hash (16 characters) as a string, or None if file cannot be read

    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there are permission issues or other file access problems
    """
    try:
        # Get file size for inclusion in hash
        file_size = file_path.stat().st_size

        # Read first sample_size bytes from the file
        with open(file_path, "rb") as file:
            file_content = file.read(sample_size)

        # Create SHA-256 hash object
        sha256_hash = hashlib.sha256()

        # Update hash with file content and size
        sha256_hash.update(file_content)
        sha256_hash.update(str(file_size).encode("utf-8"))

        # Get full hash and truncate to 16 characters for efficiency
        full_hash = sha256_hash.hexdigest()
        truncated_hash = full_hash[:16]

        return truncated_hash

    except FileNotFoundError:
        # File does not exist
        return None

    except IOError:
        # Permission issues or other file access problems
        return None

    except Exception:
        # Any other unexpected errors
        return None


def compute_string_hash(content: str) -> str:
    """Compute a content-based hash for string deduplication.

    This function hashes string content to create a fingerprint for
    deduplication purposes. Used by /learn command for string content.

    Args:
        content: String content to hash

    Returns:
        Truncated SHA-256 hash (16 characters) as a string
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content.encode("utf-8"))
    full_hash = sha256_hash.hexdigest()
    return full_hash[:16]
