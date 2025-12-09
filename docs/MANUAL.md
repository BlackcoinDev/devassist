# AI Assistant Manual

Welcome to your local AI Assistant! This manual provides a comprehensive guide to understanding and using the advanced features of your AI companion, including its agentic tool usage, autonomous learning, and workspace management.

## 🌟 Core Philosophy

This AI Assistant is designed to be **Local, Private, and Agency-Driven**.
- **Local**: It runs on your machine using local models (via LM Studio/Ollama) or API keys you control.
- **Private**: All your conversations and learned knowledge are stored locally in SQLite and ChromaDB.
- **Agency-Driven**: The AI isn't just a chatbot; it has "hands" (tools) to read files, browse the web, and manage its own memory.

---

## 🚀 Key Concepts

### 1. Context & Learning Modes
By default, the AI is smart but conservative about using its long-term memory to avoid confusing you with irrelevant facts.

*   **Auto (Default)**: The AI *only* checks its knowledge base if you ask "meta" questions (e.g., "What have you learned?", "What do you know about usage?"). It **does not** automatically use private data for general questions like "What is X?".
*   **On**: The AI searches its knowledge base for *every* query. This is the **RAG (Retrieval Augmented Generation)** mode. Use this when you want answers specifically from your document set.
*   **Off**: The AI relies solely on its pre-trained model (general knowledge).

**Command:** `/context <auto|on|off>`

### 2. Workspaces (Spaces)
Spaces allow you to isolate knowledge into different buckets. This prevents the AI from mixing up information between different projects (e.g., "Finance" vs "Coding").

*   **Isolation**: Each space has its own dedicated collection in the Vector Database (e.g., `space_finance`).
*   **Persistence**: The app remembers your last used space (`space_settings.json`).
*   **Safety**: switching spaces completely changes what the AI "knows".

**Commands:**
*   `/space list` - Show all spaces.
*   `/space switch <name>` - Create or switch to a space.
*   `/space delete <name>` - Nuke a space.

### 3. Agentic Tool Calling
The AI can "decide" to use tools without you explicitly asking.
*   **Example**: If you say "Create a file called test.py", it calls `write_file`.
*   **Example**: If you say "Read the README", it calls `read_file`.
*   **Auto-Learning**: If you correct the AI or provide a definition it didn't know (e.g., "Actually, 'like-for-like' in finance means..."), it may autonomously call `learn_information` to save that fact for ever.

---

### 4. Personalized Memory (Mem0)
**Your AI now "knows" you.**
Unlike the Knowledge Base (which stores facts about *topics*), Mem0 creates a dynamic profile of **your** preferences, coding style, and personal context.

*   **Automatic**: You don't need to run `/learn`. The system silently observes your messages in the background.
*   **Adaptive**: If you say "I prefer Python 3.10 type hints", Mem0 remembers `User Preference: Python 3.10 Type Hints`.
*   **Contextual**: For every future message, the AI checks Mem0: "Who is this user? How do they like their code?" and adapts the response automatically.

**Example**:
1.  **You**: "I hate verbose comments."
2.  **Mem0**: *Silently adds preference*.
3.  **You**: "Write a function to sum a list."
4.  **AI**: Generates clean code with minimal comments, because it *remembers*.

---

## 📄 Document & Web Processing

We utilize **Docling**, a unified document processing engine, to handle everything from PDFs to Websites.

### The `/web` Command
Ingest any webpage directly into your knowledge base.

*   **Usage**: `/web https://example.com`
*   **What happens**:
    1.  **Fetch**: Downloads the HTML.
    2.  **Clean**: Docling strips navigation, ads, and boilerplate.
    3.  **Convert**: Transforms content into clean, structured Markdown.
    4.  **Embed**: Saves the content to ChromaDB in your current Space.

### The `/populate` Command
Mass-ingest an entire directory of code and documents.

*   **Usage**: `/populate ./my-project`
*   **Supports**: Python, JS, Markdown, PDF, Images, Excel, and more.

---

## 📚 Command Reference

| Command | Description |
| :--- | :--- |
| **`/web <url>`** | **NEW!** Scrape and learn a webpage using Docling. |
| **`/context <mode>`** | Set context mode (`auto`, `on`, `off`). Use `on` for RAG. |
| **`/space <cmd>`** | Manage workspaces (`list`, `switch`, `delete`). |
| **`/learn <text>`** | Manually add a snippet of text to memory. |
| **`/populate <dir>`** | Bulk learn files from a folder. |
| **`/memory`** | Show recent conversation history. |
| **`/vectordb`** | Peek at what is stored in the vector DB. |
| **`/read <file>`** | Read a local file. |
| **`/write <file>`** | Create or edit a file. |
| **`/clear`** | Wipe the current conversation context (but not long-term memory). |
| **`/help`** | Show the help menu. |

---

## 💡 Usage Scenarios

### Scenario 1: Learning from the Web
**Goal**: Teach the AI about a niche topic (e.g., Blackcoin) from a website.
1.  **Action**: `/web https://blackcoin.nl/`
2.  **Result**: The AI confirms "✅ Learned from web: Blackcoin...".
3.  **Test**: `/context on` (important!) -> "What is Blackcoin?"
4.  **Answer**: The AI answers using the data it just scraped.

### Scenario 2: Project Isolation
**Goal**: Keep your "Gaming" project separate from your "Work" project.
1.  **Action**: `/space switch gaming`
2.  **Action**: `/learn Mario is a plumber.`
3.  **Action**: `/space switch work`
4.  **Action**: `/learn Mario is a senior developer.`
5.  **Result**: When in `gaming` space, Mario is a plumber. When in `work`, he is a dev. The facts never collide.

### Scenario 3: Teaching Definitions (Agentic Flow)
**Goal**: Correct the AI's understanding.
1.  **User**: "What is 'like-for-like' in finance?"
2.  **AI**: "I don't know."
3.  **User**: "It refers to comparing similar assets to eliminate distortions."
4.  **AI (Internal)**: *Detects knowledge gap filled.* -> **Calls `learn_information` tool automatically.**
5.  **AI**: "Thanks! I've learned that definition."
6.  **Future**: The AI now knows this permanently.

---

## 🛠 Technical Details
*   **Vector DB**: ChromaDB (stores embeddings).
*   **Embeddings**: `qwen3-embedding` (via Ollama).
*   **LLM**: `qwen3-vl-30b` (via LM Studio).
*   **Processing**: Docling (for all file/web parsing).
*   **Personalization**: Mem0 (User Preference Graph).
