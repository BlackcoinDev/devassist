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
Mem0 Integration Check Tool
"""

import os
import sys
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


def check_mem0():
    """Check if Mem0 is properly installed and configured."""
    print("🔍 Checking Mem0 Integration...")

    # 1. Check Import
    try:
        # Import mem0 and access Memory class without type: ignore
        mem0_module = __import__("mem0")
        Memory = mem0_module.Memory

        print("✅ Mem0 library found")
    except ImportError:
        print("❌ Mem0 library NOT installed. Run: pip install -r requirements.txt")
        return False

    # 2. Load Environment
    load_dotenv()

    # 3. Check Environment Variables
    lm_studio_url = os.getenv("LM_STUDIO_URL")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    model_name = os.getenv("MODEL_NAME")
    embedding_model = os.getenv("EMBEDDING_MODEL")
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_port = os.getenv("CHROMA_PORT", "8000")

    if not all([lm_studio_url, ollama_url, model_name, embedding_model, chroma_host]):
        print("❌ Missing environment variables. Check your .env file.")
        print(
            "   Required: LM_STUDIO_URL, OLLAMA_BASE_URL, MODEL_NAME, EMBEDDING_MODEL, CHROMA_HOST"
        )
        return False

    # 4. Test Configuration
    print("\n📋 Configuration Check:")
    print(f"   LLM: {model_name} at {lm_studio_url}")
    print(f"   Ollama: {embedding_model} at {ollama_url}")
    print(f"   ChromaDB: {chroma_host}:{chroma_port}")

    # 5. Test Memory Initialization with ChromaDB vector store
    print("\n🔄 Testing Mem0 Initialization with ChromaDB vector store...")
    try:
        mem0_config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": model_name,
                    "openai_base_url": lm_studio_url,
                    "api_key": "lm-studio",
                    "temperature": 0.1,
                },
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": embedding_model,
                    "base_url": ollama_url,
                },
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "mem0_personalized_memory",
                    "host": chroma_host,
                    "port": chroma_port,
                },
            },
        }

        m = Memory.from_config(mem0_config)
        print("✅ Mem0 initialized with ChromaDB vector store")

        # 6. Test Memory Write
        print("\n📝 Testing Mem0 Write...")
        try:
            # Test adding a user preference
            m.add(
                messages=[
                    {"role": "user", "content": "My preferred model is qwen3-vl-30b"}
                ],
                user_id="default_user",
            )
            print("✅ Added user preference")

            # Test retrieving from memory
            results = m.search("What is my preferred model?", user_id="default_user")
            if isinstance(results, dict) and "results" in results:
                found = any(
                    "qwen3" in r.get("memory", "") or "#FF00FF" in r.get("memory", "")
                    for r in results["results"]
                )
                if found:
                    print("✅ Memory read test passed")
                else:
                    print(
                        "⚠️  Memory read returned results but didn't find expected content"
                    )
        except Exception as e:
            print(f"❌ Memory test failed: {e}")
            return False
    except Exception as e:
        print(f"❌ Mem0 initialization failed: {e}")
        return False

    print("\n🎉 Mem0 Integration Check Complete!")
    return True


if __name__ == "__main__":
    success = check_mem0()
    sys.exit(0 if success else 1)
