# SafeFlow AI - Scam Detection Service

A standalone **Python/FastAPI** microservice for analyzing text and detecting scam, fraud, social engineering, and payment redirection risk using OpenAI's GPT model.

## Overview

SafeFlow AI provides a REST API that returns:
- **Risk Score** (0–100, normalized integer)
- **Risk Level** (low/medium/high)
- **Detected Scam Type** (e.g., "invoice fraud", "phishing")
- **Evidence Snippets** from submitted text with severity levels
- **Risk Indicators** and recommendations

### Key Features

✅ **AI-Powered Detection** — OpenAI GPT-4.1-mini  
✅ **Normalized Risk Scores** — Always [0, 100] integer  
✅ **Risk Level Recomputation** — Never trusts model's classification  
✅ **Evidence-Based** — Extracts specific snippets from analyzed text  
✅ **Prompt Injection Defense** — 3-layer protection against adversarial inputs  
✅ **Strict Validation** — Pydantic schema validation for all responses  
✅ **Safe Logging** — Never logs raw user content  
✅ **Extensible** — Designed to support future ML models (LightGBM, Isolation Forest, etc.)  
✅ **Comprehensive Tests** — 29 unit tests covering all components  

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (from https://platform.openai.com/api-keys)

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp ai_service/.env.example ai_service/.env
   # Edit ai_service/.env and add your OPENAI_API_KEY
   ```

### Running the Service

**Development (with auto-reload):**
```bash
uvicorn ai_service.main:app --reload
```

**Production:**
```bash
uvicorn ai_service.main:app --host 0.0.0.0 --port 8000
```

Service runs on `http://localhost:8000`

### Testing

Run all tests:
```bash
pytest tests/ -v
```

**Test Coverage:**
- ✅ 13 risk mapper tests (normalization, level mapping, boundaries)
- ✅ 16 schema validation tests (Pydantic models, constraints)
- ✅ All 29 tests passing

## API Endpoint

### POST /analyze

Analyzes text for scam and fraud risk.

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Urgent: Your account has been compromised. Click here immediately to verify credentials."
  }'
```

**Response:**
```json
{
  "riskScore": 85,
  "riskLevel": "high",
  "detectedScamType": "phishing",
  "explanation": "Multiple phishing indicators detected including urgency pressure, account access request, and suspicious link.",
  "indicators": ["urgency pressure", "authority impersonation", "link spoofing"],
  "evidence": [
    {
      "text": "account has been compromised",
      "reason": "Authority impersonation with account access request",
      "severity": "high"
    },
    {
      "text": "Click here immediately",
      "reason": "Urgency pressure with suspicious link request",
      "severity": "high"
    }
  ],
  "recommendation": "Do not click links in unsolicited messages. Verify account status through official channels directly."
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Project Structure

```
safeflow-ai/
├── ai_service/                 # FastAPI application
│   ├── main.py                 # FastAPI app & endpoint definitions
│   ├── analyzer.py             # OpenAI integration & validation
│   ├── main_service.py         # Service layer & orchestration
│   ├── schemas.py              # Pydantic models (AI response + API DTOs)
│   ├── prompts.py              # System & user prompt templates
│   ├── risk_mapper.py          # Score normalization & level mapping
│   ├── security.py             # Input validation & injection defense
│   ├── errors.py               # Error codes & exceptions
│   ├── __init__.py
│   └── .env.example            # Environment configuration template
├── tests/                      # Test suite
│   ├── test_risk_mapper.py     # Risk mapping tests
│   ├── test_schema.py          # Schema validation tests
│   ├── conftest.py             # Pytest configuration
│   └── __init__.py
├── model/                      # ML model demonstrations (optional)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
└── .env                        # Local environment (not in git)
```

## Architecture

### Dual Schema Design

The service maintains strict separation between two schema layers:

1. **AI Response Schema** (`ScamAiResponse`)
   - Raw JSON contract with OpenAI
   - Validated with Pydantic
   - Can evolve independently

2. **API Response DTO** (`ScamAnalysisResponse`)
   - Clean contract for API clients
   - Derived from AI response
   - Ready for frontend consumption

### Score Normalization Pipeline

```
OpenAI Response
    ↓
Parse JSON
    ↓
Validate Schema (ScamAiResponse)
    ↓
Normalize Score → [0, 100] integer
    ↓
Recompute Risk Level (never trust model)
    ↓
Format Response DTO (ScamAnalysisResponse)
    ↓
HTTP Response
```

### Prompt Injection Defense (3 Layers)

1. **System Prompt Directive**
   - Explicitly instructs model to ignore embedded instructions
   - Clear statement that all content is untrusted

2. **Message Delimiters**
   - User content wrapped in `BEGIN_UNTRUSTED_CONTENT` / `END_UNTRUSTED_CONTENT`
   - Prevents content from being confused with instructions

3. **Heuristic Detection**
   - `security.is_likely_prompt_injection()` detects obvious patterns
   - Examples: "ignore previous instructions", "system prompt", "jailbreak"

## Risk Score Thresholds

| Score Range | Risk Level | Meaning |
|---|---|---|
| 0–39 | **low** | Minimal scam signals detected |
| 40–69 | **medium** | Multiple indicators of fraud |
| 70–100 | **high** | Strong evidence of scam/fraud |

## Error Handling

Standard error responses:

```json
{
  "errorCode": "ANALYSIS_FAILED",
  "message": "Scam analysis could not be completed. Please try again.",
  "details": {}
}
```

Error codes:
- `EMPTY_TEXT_CONTENT` (400) — Text is empty or whitespace-only
- `CONTENT_TOO_LONG` (400) — Text exceeds 20,000 characters
- `ANALYSIS_FAILED` (502) — OpenAI API failure or validation error
- `MODEL_UNAVAILABLE` (503) — OpenAI model not available
- `RATE_LIMITED` (429) — OpenAI rate limit exceeded
- `SERVER_ERROR` (500) — Unexpected server error

## Environment Variables

Set these in `ai_service/.env`:

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key for authentication |
| `SERVICE_PORT` | No | Port to run service on (default: 8000) |
| `SERVICE_HOST` | No | Host to bind to (default: 0.0.0.0) |

## Development

### Code Style

The project uses:
- **Black** — Code formatting
- **Flake8** — Linting
- **MyPy** — Type checking

```bash
black ai_service/ tests/
flake8 ai_service/ tests/
mypy ai_service/
```

### Adding Tests

Tests are in `tests/` directory:

```python
def test_something():
    """Test description."""
    assert True
```

Run with:
```bash
pytest tests/ -v
```

## Extensibility

The architecture is designed to support future ML models:

### Adding a New Model

1. Create a new analyzer class (e.g., `LightGBMAnalyzer`)
2. Implement the same interface as `ScamAiAnalyzer`
3. Update `main.py` to instantiate based on configuration
4. Existing risk normalization and DTOs work with any model

### Future Enhancements

- **LightGBM Integration** — Drop-in replacement for GPT-based analysis
- **Isolation Forest** — Unsupervised outlier detection
- **Graph-Based Scoring** — Analyze relationships between scam signals
- **SHAP Explainability** — Feature importance for predictions
- **Model Ensemble** — Combine multiple models for accuracy
- **Per-Channel Tuning** — Adjust thresholds per communication channel
- **Real-time Learning** — Adapt model based on user feedback

## Security Notes

### Input Validation
- Text length limited to 20,000 characters
- Empty or whitespace-only text rejected
- All input treated as untrusted data

### Logging Safety
- Raw user text **NEVER** logged
- Only truncated preview (first 50 chars) via `safe_log_analysis_request()`
- Risk scores and analysis results logged for monitoring

### Response Validation
- All AI responses validated against strict Pydantic schemas
- Invalid responses rejected and wrapped in service error
- Type safety enforced throughout pipeline

## Deployment

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t safeflow-ai .
docker run -e OPENAI_API_KEY=sk-... -p 8000:8000 safeflow-ai
```

### Environment Configuration

For production, set environment variables:
```bash
export OPENAI_API_KEY=sk-...
export SERVICE_HOST=0.0.0.0
export SERVICE_PORT=8000
uvicorn ai_service.main:app --host $SERVICE_HOST --port $SERVICE_PORT
```

## Troubleshooting

### ModuleNotFoundError: No module named 'ai_service'

Ensure you're running from the project root:
```bash
cd /path/to/safeflow-ai
uvicorn ai_service.main:app --reload
```

### OPENAI_API_KEY not set

Ensure `ai_service/.env` exists with your OpenAI key:
```bash
cp ai_service/.env.example ai_service/.env
# Edit and add your key
```

### Tests failing with import errors

Ensure the venv is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest tests/ -v
```

## Performance

- **Latency:** ~2–5 seconds per request (OpenAI API dependent)
- **Throughput:** Limited by OpenAI rate limits
- **Memory:** ~200–300 MB base + model overhead
- **CPU:** Low (async I/O bound)

## License

[Add appropriate license information]

## Support

For issues or questions:
1. Check error codes in API responses
2. Review server logs for detailed information
3. Ensure OPENAI_API_KEY is valid and has sufficient quota
4. Verify request format matches API specification

## Version

Current: **v1.0.0** (Standalone Python/FastAPI implementation)