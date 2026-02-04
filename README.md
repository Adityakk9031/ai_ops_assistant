# 🤖 AI Operations Assistant

A production-ready **multi-agent system** that autonomously plans, executes, and verifies complex tasks using real APIs. Built with **FastAPI**, **Gemini 2.0 Flash**, and a **Planner-Executor-Verifier** architecture.

![Architecture](https://img.shields.io/badge/Architecture-Planner%20%E2%86%92%20Executor%20%E2%86%92%20Verifier-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🚀 Features

- **🧠 Intelligent Planning**: Breaks down natural language requests into executable steps.
- **⚡ Autonomous Execution**: Calls real APIs (GitHub, Weather, News) to gather data.
- **✅ Self-Verification**: Validates results, detects issues, and auto-corrects mistakes.
- **🛠️ Extensible Tools**:
  - **GitHub Tool**: Search repos, get details, detailed analytics.
  - **Weather Tool**: Real-time weather data via OpenWeatherMap.
  - **News Tool**: Latest headlines via NewsAPI.

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisite
Ensure you have **Python 3.10+** installed.
```bash
python --version
```

### 2. Clone & Install
```bash
# Clone the repository (if applicable)
git clone <repo-url>
cd ai_ops_assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Confiugre API Keys (Crucial Step!)
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Edit `.env` and add your keys. **Here is how to get them:**

#### 🔑 **Gemini API Key (Required)**
- **Cost**: Free
- **Where**: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Action**: Sign in -> "Get API Key" -> Copy.
- **Set in .env**: `GEMINI_API_KEY=AIzaSy...`

#### 🐙 **GitHub Token (Highly Recommended)**
- **Cost**: Free
- **Why**: Increases rate limit from 60/hr to 5,000/hr.
- **Where**: [GitHub Developer Settings](https://github.com/settings/tokens)
- **Action**: "Generate new token (classic)" -> Select **`public_repo`** scope -> Copy.
- **Set in .env**: `GITHUB_TOKEN=ghp_...`

#### 🌤️ **OpenWeatherMap Key (Required for Weather)**
- **Cost**: Free
- **Where**: [OpenWeatherMap Sign Up](https://home.openweathermap.org/users/sign_up)
- **Action**: Sign up -> Verify Email -> [API Keys](https://home.openweathermap.org/api_keys) -> Copy.
- **Set in .env**: `OPENWEATHER_KEY=...`

#### 📰 **NewsAPI Key (Optional)**
- **Cost**: Free
- **Where**: [NewsAPI Register](https://newsapi.org/register)
- **Set in .env**: `NEWSAPI_KEY=...`

---

## ▶️ Running the Application

Start the server using Python:

```bash
python main.py
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```
*(Press `Ctrl+C` to stop)*

---

## 🧪 Usage & Examples

You can interact with the assistant via `curl` or the Swagger UI.

**Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Example 1: GitHub Search
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find top 3 Python web frameworks on GitHub"}'
```

### Example 2: Weather Check
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Get current weather in London"}'
```

### Example 3: Complex Multi-Step Task 🌟
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find top 3 Python web frameworks on GitHub AND check the current weather in San Francisco"}'
```

### Example 4: News Search 📰
```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task": "Find the top 3 headlines about AI technology in the US"}'
```

---

## 🏗️ Project Architecture

```
ai_ops_assistant/
├── agents/             # The "Brains"
│   ├── planner.py      # Plans steps (Gemini 2.0)
│   ├── executor.py     # Runs tools
│   └── verifier.py     # Checks results
├── tools/              # The "Hands"
│   ├── github_tool.py
│   ├── weather_tool.py
│   └── news_tool.py
├── llm/                # AI Integration
│   ├── gemini_client.py
│   └── prompts/        # Strictly typed JSON prompts
├── main.py             # FastAPI Server
└── requirements.txt    # Dependencies
```

---

## ❓ Troubleshooting

**Q: `404 models/gemini-2.5-flash-exp not found`**
A: Restart your server. Ensure `llm/gemini_client.py` uses `gemini-2.0-flash-exp` or `gemini-2.5-flash` (whichever is available to you).

**Q: `KeyError: '\n "task_summary"'`**
A: This was a bug in the Planner prompt. It has been fixed! Restart the server.

**Q: GitHub API rate limit exceeded**
A: You didn't set a `GITHUB_TOKEN` in `.env`. See Setup Step 3.

**Q: `bash: -H: command not found`**
A: On Windows Git Bash, don't use the caret `^` for line breaks. Use `\` or put everything on one line.

---

**Developed for the 24-Hour GenAI Intern Assignment – AI Operations**
