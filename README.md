# AI Operations Assistant

A production-ready multi-agent system for automated task execution using the Gemini 2.0 Flash model. This system implements a Planner-Executor-Verifier architecture to break down complex tasks, execute them using third-party APIs, and validate results.

## 🏗️ Architecture

The system follows a strict three-agent architecture:

1. **Planner Agent**: Analyzes user tasks and creates structured execution plans with tool selection and step ordering
2. **Executor Agent**: Executes plan steps by calling appropriate tools with retry logic and error handling
3. **Verifier Agent**: Validates execution results, performs quality checks, and assembles final output with confidence scoring

Each agent uses dedicated prompt files with strict JSON schema enforcement to ensure deterministic, reliable outputs.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API Keys:
  - Gemini API key (required)
  - GitHub token (recommended for higher rate limits)
  - OpenWeatherMap API key (required for weather queries)
  - NewsAPI key (optional)

### Installation

```bash
# Clone or navigate to the repository
cd ai_ops_assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
OPENWEATHER_KEY=your_openweather_key_here
NEWSAPI_KEY=your_newsapi_key_here
PORT=8000
```

### Running the Application

```bash
# Start the server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### `POST /api/submit`

Submit a task for complete execution (recommended endpoint).

**Request:**
```json
{
  "task": "Find top 3 Python web frameworks on GitHub with > 5k stars and current weather in Bangalore"
}
```

**Response:**
```json
{
  "plan": { ... },
  "executor_results": [ ... ],
  "verification": {
    "final_output": {
      "summary": "Task: Find top 3 Python web frameworks on GitHub and Bangalore weather. Completed 3/3 steps successfully. Found 3 GitHub repositories. Top result: django/django (75000 stars). Weather in Bangalore: 24°C, Clear",
      "evidence": [ ... ],
      "confidence": 0.95
    },
    "issues": [],
    "confidence": 0.95,
    "verifier_metadata": { ... }
  }
}
```

### `POST /api/plan`

Create an execution plan only.

**Request:**
```json
{
  "task": "Get weather in London"
}
```

### `POST /api/execute`

Execute a pre-created plan.

**Request:**
```json
{
  "plan": { ... }
}
```

### `POST /api/verify`

Verify execution results.

**Request:**
```json
{
  "plan": { ... },
  "executor_results": [ ... ]
}
```

## 🛠️ Available Tools

### GitHubTool

Interacts with GitHub API for repository search and details.

**Operations:**
- `search_repos`: Search for repositories
- `get_repo`: Get details for a specific repository
- `get_repos_batch`: Get details for multiple repositories

**Example inputs:**
```json
{
  "operation": "search_repos",
  "query": "python web framework",
  "per_page": 10,
  "sort": "stars",
  "order": "desc"
}
```

### WeatherTool

Fetches weather data from OpenWeatherMap.

**Operations:**
- `current_weather`: Get current weather for a city
- `forecast`: Get weather forecast

**Example inputs:**
```json
{
  "operation": "current_weather",
  "city": "Bangalore",
  "units": "metric"
}
```

### NewsTool

Fetches news articles from NewsAPI.

**Operations:**
- `search_news`: Search for news articles
- `top_headlines`: Get top headlines

**Example inputs:**
```json
{
  "operation": "search_news",
  "query": "artificial intelligence",
  "language": "en",
  "page_size": 10
}
```

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_planner.py -v

# Run integration tests
pytest tests/test_integration.py -v -s

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

- **test_planner.py**: Tests plan creation, schema validation, and multi-tool planning
- **test_executor.py**: Tests tool execution, retry logic, and error handling
- **test_verifier.py**: Tests result validation, issue detection, and confidence scoring
- **test_integration.py**: Tests complete workflows end-to-end

## 📝 Example Tasks

### GitHub Repository Search

```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task":"Find top 5 Python machine learning libraries on GitHub"}'
```

### Weather Query

```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task":"Get current weather in Tokyo and New York"}'
```

### Multi-Tool Task

```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task":"Find top 3 Python web frameworks on GitHub with >5k stars and current weather in Bangalore, then create a summary"}'
```

### News Search

```bash
curl -X POST http://localhost:8000/api/submit \
  -H "Content-Type: application/json" \
  -d '{"task":"Find recent news about artificial intelligence"}'
```

## 🔧 Architecture Details

### Agent Prompts

All agent prompts are stored in `llm/prompts/` as JSON files:

- **planner_prompt.json**: Instructs the Planner to create structured execution plans
- **executor_prompt.json**: Guides the Executor in tool orchestration
- **verifier_prompt.json**: Defines validation rules and output assembly

Each prompt enforces strict JSON schemas to ensure deterministic outputs.

### Error Handling

- **Retry Logic**: Automatic retry with exponential backoff for API failures (configurable per step)
- **Partial Results**: Executor returns partial results if some steps fail
- **Validation**: Verifier detects missing fields and provides fix actions
- **Re-execution**: Failed steps can be automatically re-run based on verifier feedback

### LLM Integration

- **Model**: Gemini 2.0 Flash (gemini-2.0-flash-exp)
- **Response Format**: JSON-only responses with schema validation
- **Temperature**: 0.1 for deterministic outputs
- **Retry**: Up to 2 retries with correction prompts for invalid JSON

## 📂 Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── planner.py          # Planner agent implementation
│   ├── executor.py         # Executor agent implementation
│   └── verifier.py         # Verifier agent implementation
├── tools/
│   ├── __init__.py
│   ├── base_tool.py        # Base tool interface
│   ├── github_tool.py      # GitHub API integration
│   ├── weather_tool.py     # OpenWeatherMap integration
│   └── news_tool.py        # NewsAPI integration
├── llm/
│   ├── __init__.py
│   ├── gemini_client.py    # Gemini API client
│   └── prompts/
│       ├── planner_prompt.json
│       ├── executor_prompt.json
│       └── verifier_prompt.json
├── tests/
│   ├── __init__.py
│   ├── test_planner.py
│   ├── test_executor.py
│   ├── test_verifier.py
│   └── test_integration.py
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔍 Verification Plan

The Verifier performs the following checks:

1. **Schema Validation**: Ensures each step's output matches expected schema
2. **Success Rate**: Calculates percentage of successful steps
3. **Data Type Validation**: Verifies data types (e.g., numeric values for stars)
4. **Required Fields**: Checks presence of all required fields
5. **Cross-Checks**: Performs lightweight factual validation where possible
6. **Confidence Scoring**: Assigns confidence based on validation results

## 🚨 Error Handling

### API Rate Limits

- **GitHub**: Uses token authentication for higher limits; implements backoff on 403 errors
- **OpenWeatherMap**: Handles 404 for invalid cities; respects rate limits
- **NewsAPI**: Validates API key; handles 401 errors gracefully

### Retry Strategy

- Exponential backoff: 2^attempt seconds (2s, 4s, 8s)
- Configurable retry count per step (0-5)
- Partial results returned if some steps succeed

## 📊 Monitoring and Logging

All components use Python's logging module with structured logs:

- **INFO**: Normal operations, step completions
- **WARNING**: Retries, non-critical issues
- **ERROR**: Failures, exceptions

Logs include timestamps, component names, and contextual information.

## 🔐 Security

- API keys stored in environment variables (never in code)
- `.env` file excluded from version control
- Input validation using Pydantic models
- No execution of arbitrary code

## 🤝 Contributing

To extend the system:

1. **Add a new tool**: Create a class inheriting from `ToolInterface` in `tools/`
2. **Register the tool**: Add to `Executor.__init__()` and update prompt templates
3. **Add tests**: Create test cases in `tests/`
4. **Update documentation**: Add tool description to README

## 📄 License

This project is provided as-is for the 24-Hour GenAI Intern Assignment.

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"

Ensure `.env` file exists and contains valid API key.

### "GitHub API rate limit exceeded"

Add `GITHUB_TOKEN` to `.env` for higher rate limits (5000 req/hour vs 60).

### "City not found" (Weather)

Verify city name spelling; use English names (e.g., "Bangalore" not "Bengaluru").

### Tests failing

Ensure all API keys are configured in `.env` before running tests.

## 📞 Support

For issues or questions, please refer to the implementation details in the code comments or check the test files for usage examples.
