# 🤖 AI Operations Assistant

> A **production-ready, multi-agent AI system** that autonomously plans, executes, verifies, and **remembers** complex tasks — powered by **Gemini 3.5 Flash**, **LangGraph**, **Pinecone Vector DB**, and real-world APIs.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-ff6b35?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-12B76A?logo=pinecone&logoColor=white)](https://pinecone.io)
[![Gemini](https://img.shields.io/badge/Gemini-3.5%20Flash-4285F4?logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-a855f7)](LICENSE)

---

## 📸 Screenshots

### API Response – Weather Task
> *Add screenshot of curl response or Swagger UI result here*
> 📷 `screenshots/weather_response.png`

<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Weather Task Response](screenshots/weather_response.png) -->

---

### LangGraph Workflow in Server Logs
> *Add screenshot of terminal showing the full LangGraph node flow*
> 📷 `screenshots/server_logs.png`

<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Server Logs](screenshots/server_logs.png) -->

---

### Pinecone Dashboard – Vector Records Saved
> *Add screenshot of Pinecone dashboard showing upserted memory records*
> 📷 `screenshots/pinecone_dashboard.png`

<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Pinecone Dashboard](screenshots/pinecone_dashboard.png) -->

---

### Swagger UI – Interactive API Docs
> *Add screenshot of http://localhost:8000/docs*
> 📷 `screenshots/swagger_ui.png`

<!-- SCREENSHOT PLACEHOLDER -->
<!-- ![Swagger UI](screenshots/swagger_ui.png) -->

---

## 🎯 What This System Does

Given a **plain English task** like:
> *"Check the weather in London and format it as a JSON summary"*

The AI Operations Assistant:

1. **🧠 Recalls past memory** — Queries Pinecone for similar tasks already solved before
2. **📋 Plans intelligently** — Gemini 3.5 Flash breaks the task into structured, typed steps
3. **⚡ Executes autonomously** — Calls real APIs (GitHub, OpenWeatherMap, NewsAPI) with retry logic
4. **✅ Self-verifies** — Validates outputs against expected schemas, catches errors
5. **💾 Saves to memory** — Stores successful plans as 768-dim vectors in Pinecone for future recall

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
│  └──────────┘    └──────────┘    └──────────┘              │
│       ▲                               │                     │
│       │                               ▼                     │
│  ┌──────────┐ ◀──── pass ──── ┌──────────────┐             │
│  │  Save    │                 │   Verifier   │             │
│  │  Memory  │                 │   Node       │             │
│  └──────────┘                 └──────────────┘             │
│                                       │ fail (retry)        │
│                                       ▼                     │
│                               ┌──────────────┐             │
│                               │   Executor   │ (re-run)    │
│                               └──────────────┘             │
└─────────────────────────────────────────────────────────────┘

Pinecone Vector DB ──── embeddings ──── Google gemini-embedding-001
```

---

## 📁 Project Structure

```
ai_ops_assistant/
│
├── main.py                    # FastAPI server entry point
├── requirements.txt           # All Python dependencies
├── .env                       # Your secret API keys (never commit!)
├── .env.example               # Template for .env
├── manifest.json              # Tool registry & system config
│
├── agents/                    # The "Brains"
│   ├── planner.py             # Decomposes tasks into typed step plans
│   ├── executor.py            # Executes steps, calls tools, handles retries
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
│   ├── github_tool.py         # GitHub REST API (search, repo details)
│   ├── weather_tool.py        # OpenWeatherMap API (current weather)
│   └── news_tool.py           # NewsAPI (latest headlines)
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

# Install all dependencies
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

> ⚠️ **Pinecone Index Setup**: Create your index with **dimension = 768**, metric = **cosine**, and name it `ai-ops-memory` (or update `PINECONE_INDEX_NAME` to match).

---

## ▶️ Running the Application

Start the server:
```bash
python main.py
```

Expected startup output:
```
INFO:memory.vector_store:Successfully connected to Pinecone index 'ai-ops-memory'
INFO:workflow.graph:Successfully compiled LangGraph StateGraph workflow
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Usage & Examples

### Example 1: Weather Check
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Check the weather in London and format it as a JSON summary"}'
```

**Expected server log flow:**
```
[LangGraph: Memory Node]    Querying Pinecone for past memory...
[LangGraph: Planner Node]   Creating plan with 1 steps
[LangGraph: Executor Node]  Executing step: Get London Weather → WeatherTool ✅
[LangGraph: Verifier Node]  Confidence: 1.0, Issues: 0 → Routing to SaveMemory
[LangGraph: SaveMemory Node] Upserted to Pinecone ✅ {'upserted_count': 1}
```

---

### Example 2: GitHub Search
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 Python web frameworks on GitHub by stars"}'
```

---

### Example 3: News Headlines
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 AI news headlines from the US today"}'
```

---

### Example 4: Multi-Step Task 🌟
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find top Python ML repos on GitHub AND get the weather in San Francisco"}'
```

---

### Example 5: Memory Recall Test
Run a task **twice**. On the second run, watch the logs — the system will retrieve the previously saved plan from Pinecone:
```bash
# First run — saves to Pinecone
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Get current weather in Tokyo"}'

# Second run — recalls from Pinecone memory
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "What is the weather like in Tokyo?"}'
```

---

## 🔄 LangGraph Workflow Detail

The system is built on a **LangGraph StateGraph** with the following nodes and edges:

| Node | Role | Description |
|:---|:---|:---|
| `memory_node` | **Recall** | Embeds the task and queries Pinecone for similar past successes |
| `planner_node` | **Plan** | Gemini 3.5 Flash decomposes the task into validated JSON step plans |
| `executor_node` | **Act** | Executes each tool call with retry logic and error handling |
| `verifier_node` | **Verify** | Validates results against expected output schema; routes on failure |
| `save_memory_node` | **Remember** | Saves successful plan + verification as a 768-dim Pinecone vector |

**Conditional Edge Logic:**
- If `verifier_node` passes → route to `save_memory_node` → **END**
- If `verifier_node` fails and `retry_count < max_retries` → route back to `executor_node`
- If `retry_count >= max_retries` → route to `save_memory_node` → **END** (with error state)

---

## ❓ Troubleshooting

**Q: `404 NOT_FOUND` for embedding model**
> A: Only `models/gemini-embedding-001` is supported. The code already uses this. If you forked an older version, update `memory/vector_store.py`.

**Q: Pinecone upsert fails with dimension mismatch**
> A: Your Pinecone index must be created with **dimension = 768**. The code sets `output_dimensionality=768` automatically.

**Q: `KeyError: 'task_summary'` in planner**
> A: This was a legacy bug. It is fixed. Restart your server after pulling latest changes.

**Q: GitHub API rate limit (403)**
> A: You have not set `GITHUB_TOKEN` in `.env`. Without a token, GitHub limits you to 60 requests/hour. With a token: 5,000/hour.

**Q: `bash: -H: command not found`**
> A: On Windows Git Bash, use `\` for multi-line curl commands, or run the entire command on a single line.

**Q: `ImportError: No module named 'pinecone'`**
> A: Run `pip install -r requirements.txt` with your virtual environment activated.

---

## 🗺️ Roadmap / Future Improvements

- [ ] Add a React / Next.js frontend dashboard
- [ ] Stream LLM responses via Server-Sent Events (SSE)
- [ ] Add more tools: SQL query tool, code execution tool, Slack notification tool
- [ ] Add per-user memory namespacing in Pinecone
- [ ] Implement async parallel tool execution for multi-step tasks
- [ ] Add OpenTelemetry tracing for full observability
- [ ] Docker + docker-compose deployment configuration

---

## 📄 License

This project is licensed under the **MIT License**.

---

*Developed as part of a 24-Hour GenAI Intern Assignment – AI Operations Track*
