#!/usr/bin/env python3
"""
Mem0 Integration Check Tool
===========================
This script verifies that the Mem0 library is correctly installed
and configured to talk to your local LM Studio and Ollama instances.

Usage:
    python3 tools/check_mem0.py
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import main if needed,
# although we will mostly replicate the config logic to obtain a cleaner test.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_mem0():
    print("🔍 Checking Mem0 Integration...")

    # 1. Check Import
    try:
        from mem0 import Memory

        print("✅ Mem0 library checks out (imported successfully).")
    except ImportError:
        print("❌ Mem0 library NOT found. Please run: pip install -r requirements.txt")
        return

    # 2. Load Environment
    load_dotenv()

    lm_studio_url = os.getenv("LM_STUDIO_URL")
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    model_name = os.getenv("MODEL_NAME")
    embedding_model = os.getenv("EMBEDDING_MODEL")

    if not all([lm_studio_url, ollama_url, model_name, embedding_model]):
        print("❌ Missing environment variables. Check your .env file.")
        return

    print(f"ℹ️  Configuration:")
    print(f"   - LLM: {model_name} at {lm_studio_url}")
    print(f"   - Embedding: {embedding_model} at {ollama_url}")

    # 3. Initialize Memory
    print("\n🔄 Initializing Memory connection...")
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
                "config": {"model": embedding_model, "base_url": ollama_url},
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test_mem0_integration",
                    "path": "chroma_db_mem0_test",
                },
            },
        }

        m = Memory.from_config(mem0_config)
        print("✅ Memory initialized.")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # 4. Test Write
    print("\n📝 Testing Memory Write (Add)...")
    try:
        # We need to mock a user message
        msgs = [{"role": "user", "content": "My favorite color is #FF00FF (Magenta)."}]
        m.add(msgs, user_id="test_user")
        print("✅ Write successful.")
    except Exception as e:
        print(f"❌ Write failed: {e}")
        print("   (Ensure LM Studio and Ollama are running!)")
        return

    # 5. Test Read
    print("\n🔎 Testing Memory Read (Search)...")
    try:
        results = m.search("What is my favorite color?", user_id="test_user")
        print(f"Result: {results}")

        # Verify content
        found = False
        if isinstance(results, dict) and "results" in results:
            for r in results["results"]:
                if "Magenta" in r.get("memory", "") or "#FF00FF" in r.get("memory", ""):
                    found = True
        elif isinstance(results, list):
            for r in results:
                if "Magenta" in r.get("memory", "") or "#FF00FF" in r.get("memory", ""):
                    found = True

        if found:
            print("✅ Verified: Retrieved specific fact from memory.")
        else:
            print(
                "⚠️  Warning: Write succeeded but search didn't return the exact fact immediately."
            )
            print(
                "    (This can happen if the LLM extraction wasn't perfect or indexing is slow)"
            )

    except Exception as e:
        print(f"❌ Search failed: {e}")

    print("\n🎉 Mem0 Check Complete.")


if __name__ == "__main__":
    check_mem0()
