# 🤖 AI Operations Assistant

> A **production-ready, multi-agent AI system** that autonomously plans, executes, verifies, and **remembers** complex tasks — powered by **Gemini 3.5 Flash**, **LangGraph**, **Model Context Protocol (MCP)**, **Pinecone Vector DB**, and real-world APIs.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-ff6b35?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-7000FF?logo=protocol&logoColor=white)](https://modelcontextprotocol.io)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-12B76A?logo=pinecone&logoColor=white)](https://pinecone.io)
[![Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-a855f7)](LICENSE)

---

## 📸 Screenshots

### API Response – Weather Task
<img width="613" height="617" alt="Screenshot 2026-08-14 164927" src="https://github.com/user-attachments/assets/450421b6-b58f-4005-9513-476d3d539d09" />


<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Weather Task Response](screenshots/weather_response.png) -->

---

### LangGraph & MCP Server Logs
<img width="605" height="762" alt="Screenshot 2026-08-14 165053" src="https://github.com/user-attachments/assets/97592308-635f-401b-b623-af2db76a44ad" />


<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Server Logs](screenshots/server_logs.png) -->

---

### Pinecone Dashboard – Vector Records Saved
<img width="1801" height="790" alt="image" src="https://github.com/user-attachments/assets/efef3c88-9054-41a8-a2e0-47af23d1e639" />


<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Pinecone Dashboard](screenshots/pinecone_dashboard.png) -->

---

### Swagger UI – Interactive API Docs
<img width="1760" height="1500" alt="image" src="https://github.com/user-attachments/assets/be64b420-7be1-4860-9e63-3a7a8fc293df" />


<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Swagger UI](screenshots/swagger_ui.png) -->

---

## 🎯 What This System Does

Given a **plain English task** like:
> *"Check the weather in London and format it as a JSON summary"*

The AI Operations Assistant:

1. **🧠 Recalls past memory** — Queries Pinecone for similar tasks already solved before
2. **🔌 Connects to MCP Server** — Establishes stdio session with `mcp_server.py` via `langchain-mcp-adapters`
3. **📋 Plans intelligently** — Gemini 3.5 Flash breaks the task into structured, typed steps using 7 registered MCP tools
4. **⚡ Executes autonomously** — Runs MCP tool calls (GitHub, OpenWeatherMap, NewsAPI) over stdio transport with retry logic
5. **✅ Self-verifies** — Validates outputs against expected schemas, catches errors
6. **💾 Saves to memory** — Stores successful plans as 768-dim vectors in Pinecone for future recall

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server (:8000)                    │
│                     POST /api/submit                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph StateGraph Workflow                   │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Memory  │───▶│ Planner  │───▶│ Executor │              │
│  │  Node    │    │  Node    │    │  Node    │              │
│  └──────────┘    └────┬─────┘    └────┬─────┘              │
│       ▲               │               │                     │
│       │               └───────┬───────┘                     │
│       │           load_mcp_tools()                          │
│  ┌──────────┐                 ▼                             │
│  │  Save    │    ┌─────────────────────────┐                │
│  │  Memory  │◀───│   MCP ClientSession     │                │
│  └──────────┘    └────────────┬────────────┘                │
│                               │ stdio transport             │
│                               ▼                             │
│                  ┌─────────────────────────┐                │
│                  │  FastMCP Server         │                │
│                  │  (mcp_server.py)        │                │
│                  │  7 Registered Tools     │                │
│                  └─────────────────────────┘                │
│                               │                             │
│                               ▼                             │
│                      ┌─────────────────┐                    │
│                      │  Verifier Node  │                    │
│                      └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘

Pinecone Vector DB ──── embeddings ──── Google gemini-embedding-001
```

---

## 🔌 Model Context Protocol (MCP) Integration

This project uses the **Model Context Protocol (MCP)** to expose modular API tools over standard input/output (`stdio`) transport via `mcp_server.py`.

### Registered MCP Tools (7 Tools Total)

| Category | Tool Name | Description |
|:---|:---|:---|
| 🐙 **GitHub** | `github_search_repos` | Search GitHub repositories matching a query string |
| 🐙 **GitHub** | `github_get_repo` | Get detailed information for a specific GitHub repository |
| 🐙 **GitHub** | `github_get_repos_batch` | Get details for multiple GitHub repositories at once |
| 🌤️ **Weather** | `weather_current` | Get current weather conditions for a specified city |
| 🌤️ **Weather** | `weather_forecast` | Get multi-day weather forecast for a specified city |
| 📰 **News** | `news_search` | Search news articles matching keyword queries |
| 📰 **News** | `news_top_headlines` | Get top headlines by category or country |

Tools are initialized via `FastMCP` and dynamically loaded into the LangGraph workflow using **`langchain-mcp-adapters`**:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

server_params = StdioServerParameters(command="python", args=["mcp_server.py"])

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        mcp_tools = await load_mcp_tools(session)
```

---

## 📁 Project Structure

```
ai_ops_assistant/
│
├── main.py                    # FastAPI server entry point
├── mcp_server.py              # FastMCP Server exposing 7 MCP tools over stdio
├── requirements.txt           # All Python dependencies
├── .env                       # Your secret API keys (never commit!)
├── .env.example               # Template for .env
├── manifest.json              # Tool registry & system config
│
├── agents/                    # The "Brains"
│   ├── planner.py             # Decomposes tasks into typed step plans via MCP tools
│   ├── executor.py            # Executes steps via MCP tool adapters with retries
│   └── verifier.py            # Validates outputs against expected schemas
│
├── workflow/
│   └── graph.py               # LangGraph StateGraph definition
│                              # (Memory→Planner→Executor→Verifier→SaveMemory)
│
├── llm/
│   ├── gemini_client.py       # Gemini 3.5 Flash wrapper (JSON generation)
│   └── prompts/               # Strictly typed JSON prompt templates
│       ├── planner_prompt.py
│       └── verifier_prompt.py
│
├── memory/
│   └── vector_store.py        # Pinecone + gemini-embedding-001 (768-dim)
│                              # save_successful_task / search_similar_tasks
│
├── tools/                     # The "Hands"
│   ├── base_tool.py           # Abstract ToolInterface + ToolResponse
│   ├── github_tool.py         # GitHub REST API implementation
│   ├── weather_tool.py        # OpenWeatherMap API implementation
│   ├── news_tool.py           # NewsAPI implementation
│   └── langchain_tools.py     # Dynamic MCP tool loader utilities
│
├── services/
│   └── workflow_service.py    # Bridges FastAPI request to LangGraph
│
└── tests/
    └── test_integration.py    # Integration test suite
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|:---|:---|
| **LLM** | Google Gemini 3.5 Flash (`models/gemini-3.5-flash`) |
| **Tool Protocol** | Model Context Protocol (MCP via `FastMCP`) |
| **MCP Adapters** | `langchain-mcp-adapters` over stdio transport |
| **Embeddings** | Google `models/gemini-embedding-001` (768-dim) |
| **Orchestration** | LangGraph StateGraph (conditional edges, cyclic retry) |
| **Vector Memory** | Pinecone Serverless Index |
| **API Framework** | FastAPI + Uvicorn |
| **Real-World APIs** | OpenWeatherMap · GitHub REST · NewsAPI |
| **Runtime** | Python 3.10+ |

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites

Make sure you have **Python 3.10+** installed:
```bash
python --version
```

### 2. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd ai_ops_assistant

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install all dependencies (including mcp & langchain-mcp-adapters)
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the template and fill in your keys:
```bash
cp .env.example .env
```

Open `.env` and set the following:

```env
GEMINI_API_KEY=AIzaSy...
GITHUB_TOKEN=ghp_...
OPENWEATHER_KEY=...
NEWSAPI_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=ai-ops-memory
```

#### 🔑 Where to Get Each Key

| Key | Cost | Link | Steps |
|:---|:---|:---|:---|
| `GEMINI_API_KEY` | **Free** | [Google AI Studio](https://aistudio.google.com/app/apikey) | Sign in → "Get API Key" → Copy |
| `GITHUB_TOKEN` | **Free** | [GitHub Settings](https://github.com/settings/tokens) | "Generate new token (classic)" → select `public_repo` |
| `OPENWEATHER_KEY` | **Free** | [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) | Sign up → Verify email → [API Keys](https://home.openweathermap.org/api_keys) |
| `NEWSAPI_KEY` | **Free** | [NewsAPI](https://newsapi.org/register) | Register → Copy key from dashboard |
| `PINECONE_API_KEY` | **Free** | [Pinecone Console](https://app.pinecone.io) | Create account → Create index (dimension: **768**) → Copy API key |

---

## ▶️ Running the Application

Start the server:
```bash
python main.py
```

Expected startup output:
```text
INFO:memory.vector_store:Successfully connected to Pinecone index 'ai-ops-memory'
INFO:workflow.graph:Successfully compiled LangGraph StateGraph workflow with MCP tool support
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Usage & Examples

### Example 1: Weather Check (via MCP)
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Check the weather in London and format it as a JSON summary"}'
```

**Expected server log flow:**
```text
[LangGraph: Memory Node]    Querying Pinecone for past memory...
[LangGraph: Planner Node]   Creating plan for task...
[MCP Session]               Successfully loaded 7 tools via load_mcp_tools()
[LangGraph: Executor Node]  Executing step via MCP Tool: 'weather_current' ✅
[LangGraph: Verifier Node]  Confidence: 1.0, Issues: 0 → Routing to SaveMemory
[LangGraph: SaveMemory Node] Upserted to Pinecone ✅ {'upserted_count': 1}
```

---

### Example 2: GitHub Search (via MCP)
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 Python web frameworks on GitHub by stars"}'
```

---

### Example 3: News Headlines (via MCP)
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 AI news headlines from the US today"}'
```

---

### Example 4: Memory Recall Test
Run a task **twice**. On the second run, watch the logs — the system will retrieve the previously saved plan from Pinecone vector memory:
```bash
# First run — saves vector to Pinecone
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Get current weather in Tokyo"}'

# Second run — recalls vector memory from Pinecone
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "What is the weather like in Tokyo?"}'
```

---

## 🔄 LangGraph & MCP Workflow Detail

| Node | Role | Description |
|:---|:---|:---|
| `memory_node` | **Recall** | Embeds task and queries Pinecone for similar past task memories |
| `planner_node` | **Plan** | Loads 7 tools via `load_mcp_tools()` and creates structured step plans with Gemini 3.5 |
| `executor_node` | **Act** | Calls FastMCP server tools over stdio transport with exponential retries |
| `verifier_node` | **Verify** | Validates results against expected schema; routes on failure |
| `save_memory_node` | **Remember** | Saves successful plan + verification as a 768-dim vector to Pinecone |

---

## ❓ Troubleshooting

**Q: `Cannot find module langchain_mcp_adapters`**
> A: Run `pip install -r requirements.txt` to install `langchain-mcp-adapters` and `mcp`.

**Q: `429 Quota Exceeded` from Gemini API**
> A: You hit Google's free tier rate limit (20 requests per minute). Simply wait 10-15 seconds before running the next request.

**Q: Pinecone dimension mismatch**
> A: Your Pinecone index must be created with **dimension = 768** to match `models/gemini-embedding-001`.

---

## 📄 License

This project is licensed under the **MIT License**.

---

*Developed as part of a 24-Hour GenAI Intern Assignment – AI Operations Track*
