# AI Assistant Manual v0.3.0

Welcome to your local AI Assistant! This manual provides a comprehensive guide
to understanding and using the advanced features of your AI companion, including
its agentic tool usage, autonomous learning, and workspace management.

## 🌟 Core Philosophy

This AI Assistant is designed to be **Local, Private, and Agency-Driven**.

- **Local**: It runs on your machine using local models (via LM Studio/Ollama) or API keys you

  control.

- **Private**: Your conversations are stored locally in SQLite. Learned knowledge and memories are

  stored securely on your ChromaDB server.

- **Agency-Driven**: The AI isn't just a chatbot; it has "hands" (tools) to read files, browse the

  web, and manage its own memory.

---

## 🚀 Key Concepts

### 1. Context & Learning Modes

By default, the AI is smart but conservative about using its long-term memory to
avoid confusing you with irrelevant facts.

- **Auto (Default)**: The AI *only* checks its knowledge base if you ask

"meta" questions (e.g., "What have you learned?", "What do you know about
usage?"). It **does not** automatically use private data for general questions
like "What is X?".

- **On**: The AI searches its knowledge base for *every* query. This is the

**RAG (Retrieval Augmented Generation)** mode. Use this when you want answers
specifically from your document set.

- **Off**: The AI relies solely on its pre-trained model (general knowledge).

**Command:** `/context <auto|on|off>`

### 2. Workspaces (Spaces)

Spaces allow you to isolate knowledge into different buckets. This prevents the
AI from mixing up information between different projects (e.g., "Finance" vs
"Coding").

- **Isolation**: Each space has its own dedicated collection in the Vector

Database (e.g., `space_finance`).

- **Persistence**: The app remembers your last used space

(`space_settings.json`).

- **Safety**: switching spaces completely changes what the AI "knows".

**Commands:**

- `/space list` - Show all spaces.
- `/space switch <name>` - Create or switch to a space.
- `/space delete <name>` - Nuke a space.

### 3. Agentic Tool Calling

The AI can "decide" to use tools without you explicitly asking.

- **Example**: If you say "Create a file called test.py", it calls

`write_file`.

- **Example**: If you say "Read the README", it calls `read_file`.
- **Example**: If you ask "What's the latest news on AI?", it calls

`search_web` to search DuckDuckGo.

- **Example**: If you say "Run npm install", it calls `shell_execute` (CLI

only).

- **Example**: If you ask "What files changed?", it calls `git_status`.
- **Example**: If you say "Find all TODO comments", it calls `code_search`.
- **Auto-Learning**: If you correct the AI or provide a definition it didn't

know (e.g., "Actually, 'like-for-like' in finance means..."), it may
autonomously call `learn_information` to save that fact for ever.

### 4. Shell Execution (CLI Only)

In CLI mode, the AI can execute shell commands using an allowlist-based
security model:

- **Safe Commands**: `git`, `npm`, `python`, `pytest`, etc. run without
  confirmation
- **Blocked Commands**: `rm`, `sudo`, `chmod`, etc. are always denied
- **Safe Environment**: Commands run in a sanitized environment (sensitive env vars removed)
- **Unknown Commands**: Require user confirmation before execution

**Example**:

1. **You**: "Run pytest to check the tests."
2. **AI**: *Calls `shell_execute("pytest")`* → Executes immediately (safe)
3. **AI**: "Tests completed. 42 passed, 0 failed."

### 5. Git Integration

The AI has dedicated tools for git operations:

- `git_status()` - See what files have changed
- `git_diff()` - View the actual changes
- `git_log()` - Browse commit history
- `git_show()` - Inspect specific commits

**Example**:

1. **You**: "What did I change today?"
2. **AI**: *Calls `git_status()` and `git_diff()`*
3. **AI**: "You modified 3 files: main.py, config.py, and README.md..."

### 6. Code Search

Fast regex search across your codebase using ripgrep:

**Example**:

1. **You**: "Find all TODO comments in the project."
2. **AI**: *Calls `code_search("TODO")`*
3. **AI**: "Found 12 TODO comments across 8 files..."

### 7. MCP Integration

Connect external tool servers via Model Context Protocol:

- **stdio**: Local subprocess servers (e.g., filesystem, database)
- **HTTP**: Remote REST-based servers
- **SSE**: Streaming server events

**Configuration**: Edit `config/mcp_servers.json` to add servers.

### 8. Tool Approval System

Control which tools require confirmation:

| Mode     | Behavior                    |
| -------- | --------------------------- |
| `always` | Execute without asking      |
| `ask`    | Prompt before execution     |
| `never`  | Block execution entirely    |

**Configuration**: Edit `config/tool_approvals.json` to customize.

### 9. Resource Limits & Security

To prevent abuse and ensure stability, the following limits enforce fair usage:

| Tool Category | Rate Limit | Reset Period |
| ------------- | ---------- | ------------ |
| **Shell**     | 10 calls   | 1 minute     |
| **Git**       | 20 calls   | 1 minute     |
| **File**      | 60 calls   | 1 minute     |
| **Web**       | 10 calls   | 1 minute     |

> [!WARNING]
> If you exceed these limits, the tool will fail with a `RateLimitError`. Wait a minute and try again.
>
> **Security Audit**: All rate limit violations, tool approvals, and blocked commands are logged to the secure audit log for review.

---

### 4. Personalized Memory (Mem0)

**Your AI now "knows" you.**
Unlike the Knowledge Base (which stores facts about *topics*), Mem0 creates a
dynamic profile of **your** preferences, coding style, and personal context.

- **Automatic**: You don't need to run `/learn`. The system silently observes

your messages in the background.

- **Adaptive**: If you say "I prefer Python 3.10 type hints", Mem0 remembers

`User Preference: Python 3.10 Type Hints`.

- **Contextual**: For every future message, the AI checks Mem0: "Who is this

user? How do they like their code?" and adapts the response automatically.

**Example**:

1. **You**: "I hate verbose comments."
2. **Mem0**: *Silently adds preference*.
3. **You**: "Write a function to sum a list."
4. **AI**: Generates clean code with minimal comments, because it *remembers*.

**Mem0 Features:**

- **Automatic Learning**: No explicit commands needed - learns from every interaction
- **Persistent Memory**: Remembers preferences across sessions
- **Contextual Awareness**: Adapts responses based on your history and style
- **Preference Tracking**: Tracks coding style, language preferences, and work patterns

---

## 📄 Document & Web Processing

We utilize **Docling**, a unified document processing engine, to handle
everything from PDFs to Websites.

### The `/web` Command

Ingest any webpage directly into your knowledge base.

- **Usage**: `/web https://example.com`
- **What happens**:
    1. **Fetch**: Downloads the HTML.
    2. **Clean**: Docling strips navigation, ads, and boilerplate.
    3. **Convert**: Transforms content into clean, structured Markdown.
    4. **Embed**: Saves the content to ChromaDB in your current Space.

### The `/populate` Command

Mass-ingest an entire directory of code and documents.

- **Usage**: `/populate ./my-project`
- **Supports**: Python, JS, Markdown, PDF, Images, Excel, and more.

---

## 📚 Command Reference

| Command                  | Description                                                          |
| ------------------------ | -------------------------------------------------------------------- |
| **`/web <url>`**         | Scrape and learn a webpage using Docling.                            |
| **`/context <mode>`**    | Set context mode (`auto`, `on`, `off`). Use `on` for RAG.            |
| **`/space <cmd>`**       | Manage workspaces (`list`, `switch`, `delete`).                      |
| **`/learn <text>`**      | Manually add a snippet of text to memory.                            |
| **`/populate <dir>`**    | Bulk learn files from a folder.                                      |
| **`/memory`**            | Show recent conversation history.                                    |
| **`/vectordb`**          | View knowledge base statistics and sources.                          |
| **`/mem0`**              | Peek at personalized memory contents.                                |
| **`/read <file>`**       | Read a local file.                                                   |
| **`/write <file>`**      | Create or edit a file.                                               |
| **`/clear`**             | Wipe the current conversation context (but not long-term memory).    |
| **`/approve <tool> <m>`**| Set tool approval mode (`ask`, `always`, `never`).                   |
| **`/mcp list`**          | List connected MCP servers and their tools.                          |
| **`/mcp connect <name>`**| Connect to an MCP server from config.                                |
| **`/help`**              | Show the help menu.                                                  |

---

## 💡 Usage Scenarios

### Scenario 1: Learning from the Web

**Goal**: Teach the AI about a niche topic (e.g., Blackcoin) from a website.

1. **Action**: `/web https://blackcoin.nl/`
2. **Result**: The AI confirms "✅ Learned from web: Blackcoin...".
3. **Test**: `/context on` (important!) -> "What is Blackcoin?"
4. **Answer**: The AI answers using the data it just scraped.

### Scenario 2: Project Isolation

**Goal**: Keep your "Gaming" project separate from your "Work" project.

1. **Action**: `/space switch gaming`
2. **Action**: `/learn Mario is a plumber.`
3. **Action**: `/space switch work`
4. **Action**: `/learn Mario is a senior developer.`
5. **Result**: When in `gaming` space, Mario is a plumber. When in `work`, he

is a dev. The facts never collide.

### Scenario 3: Teaching Definitions (Agentic Flow)

**Goal**: Correct the AI's understanding.

1. **User**: "What is 'like-for-like' in finance?"
2. **AI**: "I don't know."
3. **User**: "It refers to comparing similar assets to eliminate distortions."
4. **AI (Internal)**: *Detects knowledge gap filled.* -> **Calls

`learn_information` tool automatically.**

1. **AI**: "Thanks! I've learned that definition."
2. **Future**: The AI now knows this permanently.

### Scenario 4: Running Shell Commands (CLI)

**Goal**: Execute development commands through the AI.

1. **Action**: "Run the tests and tell me if anything fails."
2. **AI**: *Calls `shell_execute("pytest")`*
3. **Result**: The AI runs pytest and summarizes the results.
4. **Note**: Works only in CLI mode, not GUI.

### Scenario 5: Code Review with Git

**Goal**: Understand what changed in your codebase.

1. **Action**: "Show me what I changed since yesterday."
2. **AI**: *Calls `git_log()` and `git_diff()`*
3. **Result**: The AI shows your recent commits and summarizes the changes.

### Scenario 6: Finding Code Patterns

**Goal**: Search for specific patterns across your codebase.

1. **Action**: "Find all functions that use async/await."
2. **AI**: *Calls `code_search("async def")`*
3. **Result**: Lists all async functions with file paths and line numbers.

### Scenario 7: Using MCP Servers

**Goal**: Connect external tools via MCP.

1. **Action**: `/mcp connect filesystem`
2. **Result**: AI gains access to MCP filesystem tools.
3. **Action**: "List files in /home/user/documents using MCP."
4. **AI**: *Calls `mcp_filesystem_list_directory()`*
5. **Result**: Returns the directory listing from the MCP server.

---

## 🛠 Technical Details

For comprehensive technical architecture details, please refer to the
[ARCHITECTURE.md](ARCHITECTURE.md) document.

**Key Technical Components:**

- **Vector DB**: ChromaDB (stores embeddings)
- **Embeddings**: `qwen3-embedding` (via Ollama)
- **LLM**: `qwen3-vl-30b` (via LM Studio)
- **Processing**: Docling (for all file/web parsing)
- **Personalization**: Mem0 (User Preference Graph)

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system architecture, data
flow diagrams, and technical implementation details.
