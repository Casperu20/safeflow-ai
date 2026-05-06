# SafeFlow AI

A comprehensive scam and fraud risk detection platform combining TypeScript/NestJS backend services with a standalone Python/FastAPI AI microservice.

## Overview

SafeFlow AI analyzes text for scam, fraud, social engineering, payment redirection, invoice fraud, impersonation, phishing, urgency pressure, suspicious account changes, and attempts to bypass verification.

### Key Features

- **AI-Powered Detection**: OpenAI GPT-4.1-mini for intelligent scam analysis
- **Risk Scoring**: Normalized risk scores (0–100) with categorical levels (low/medium/high)
- **Evidence-Based**: Extracts specific evidence snippets from analyzed text
- **Prompt Injection Protected**: Multi-layer defense against adversarial inputs
- **Extensible**: Designed to support future ML models (LightGBM, Isolation Forest, graph-based scoring)
- **Safe Logging**: Never logs raw user content, only safe truncated previews
- **Dual Architecture**: TypeScript services + Python AI microservice

## Project Structure

```
safeflow-ai/
├── src/                    # TypeScript/NestJS backend services
│   ├── main.ts
│   ├── app.module.ts
│   └── scam-analysis/
│       ├── scam-analysis.controller.ts
│       ├── scam-analysis.service.ts
│       ├── ai/              # AI integration layer
│       │   ├── scam-ai-analyzer.ts
│       │   ├── scam-ai.prompt.ts
│       │   ├── scam-ai.schema.ts
│       │   └── scam-risk.mapper.ts
│       ├── dto/             # Data transfer objects
│       │   ├── scam-analysis-request.dto.ts
│       │   ├── scam-analysis-response.dto.ts
│       │   └── evidence-snippet.dto.ts
│       ├── errors/
│       └── utils/
├── ai-service/             # Python/FastAPI AI microservice (STANDALONE)
│   ├── __init__.py
│   ├── main.py             # FastAPI app with /analyze endpoint
│   ├── analyzer.py         # OpenAI integration
│   ├── main_service.py     # Service layer
│   ├── schemas.py          # Pydantic models
│   ├── prompts.py          # AI prompts
│   ├── risk_mapper.py      # Score normalization
│   ├── security.py         # Input validation & injection defense
│   ├── errors.py           # Error codes & exceptions
│   └── .env.example        # Environment template
├── tests/                  # Test suite
│   ├── test_risk_mapper.py
│   ├── test_schema.py
│   └── conftest.py
├── model/                  # ML model demonstrations
├── requirements.txt        # All Python dependencies
├── tsconfig.json
├── package.json
└── README.md               # This file
```

## Python AI Service (Standalone)

### What is the AI Service?

The `ai-service/` folder contains a **standalone FastAPI application** that provides REST API endpoints for scam risk analysis. It can be deployed independently from the TypeScript backend.

### Features

- **FastAPI REST API**: Modern, fast, auto-documented HTTP API
- **OpenAI Integration**: Direct integration with GPT-4.1-mini
- **Strict Schema Separation**: AI response schema separate from API DTO
- **Response Validation**: Pydantic validation of all AI responses
- **Score Normalization**: All scores normalized to [0, 100] integer range
- **Risk Level Recomputation**: Always recomputed from normalized score (never trust model)
- **Prompt Injection Defense**: 3-layer protection against adversarial inputs
- **Comprehensive Logging**: Safe logging with no raw user text exposure

### API Endpoint

#### POST /analyze

Analyzes text for scam and fraud risk.

**Request:**
```json
{
  "text": "Dear valued customer, please verify your account immediately by clicking this link."
}
```

**Response (200 OK):**
```json
{
  "riskScore": 82,
  "riskLevel": "high",
  "detectedScamType": "phishing",
  "explanation": "Multiple phishing indicators detected including urgency pressure, suspicious link request, and account verification demand.",
  "indicators": ["urgency pressure", "link spoofing", "authority impersonation"],
  "evidence": [
    {
      "text": "verify your account immediately",
      "reason": "Urgency pressure combined with account access request",
      "severity": "high"
    },
    {
      "text": "clicking this link",
      "reason": "Suspicious link request typical of phishing",
      "severity": "high"
    }
  ],
  "recommendation": "Do not click links in unsolicited messages. Verify account status through official channels directly."
}
```

**Error Response (4xx/5xx):**
```json
{
  "errorCode": "ANALYSIS_FAILED",
  "message": "Scam analysis could not be completed. Please try again.",
  "details": {}
}
```

### Setup & Installation

#### Prerequisites

- Python 3.9+
- OpenAI API key (from https://platform.openai.com/api-keys)

#### Installation

1. **Create a virtual environment (from project root):**
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
   cp ai-service/.env.example ai-service/.env
   # Edit ai-service/.env and add your OPENAI_API_KEY
   ```

### Running the Service

**Development (with auto-reload):**
```bash
cd ai-service
uvicorn main:app --reload
```

**Production:**
```bash
cd ai-service
uvicorn main:app --host 0.0.0.0 --port 8000
```

Service will be available at `http://localhost:8000`

**Health Check:**
```bash
curl http://localhost:8000/health
```

### Usage Example

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Urgent: Your account has been compromised. Click here immediately to secure it."
  }'
```

### Testing

```bash
pytest tests/ -v
```

Test coverage includes:
- Risk score normalization and level mapping (18+ tests)
- Schema validation for Pydantic models (20+ tests)
- Edge cases and boundary conditions

## Architecture Highlights

### Strict Schema Separation

The service maintains strict separation between two schema layers:

1. **AI Response Schema** (`ScamAiResponse`)
   - Raw contract with OpenAI
   - Validated with Pydantic
   - Can evolve independently of API

2. **API Response DTO** (`ScamAnalysisResponse`)
   - Clean contract for API clients
   - Derived from AI response
   - Ready for frontend consumption

### Component Flow

```
API Request
    ↓
[Input Validation] → Check non-empty, size limits
    ↓
[ScamAiAnalyzer] → Call OpenAI API
    ↓
[Response Parsing] → Parse JSON
    ↓
[Schema Validation] → Validate against ScamAiResponse
    ↓
[Score Normalization] → Clamp to [0, 100]
    ↓
[Risk Level Recomputation] → Map score to level
    ↓
[Response Formatting] → Convert to API DTO
    ↓
HTTP Response
```

### Prompt Injection Defense (3 Layers)

**Layer 1: System Prompt Directive**
- Explicitly instructs model to ignore embedded instructions
- Clear statement that all content is untrusted

**Layer 2: Message Delimiters**
- User content wrapped in `BEGIN_UNTRUSTED_CONTENT` / `END_UNTRUSTED_CONTENT`
- Prevents content from being confused with instructions

**Layer 3: Heuristic Detection**
- `security.is_likely_prompt_injection()` detects obvious patterns
- Examples: "ignore previous instructions", "system prompt", "jailbreak"

### Safe Logging

- Raw user text **NEVER** logged
- Only truncated preview (first 50 chars) via `safe_log_analysis_request()`
- Risk scores and levels logged for monitoring
- Analysis results logged without user data exposure

## Error Handling

Standard error codes:

| Error Code | Status | Description |
|------------|--------|-------------|
| `EMPTY_TEXT_CONTENT` | 400 | Text is empty or whitespace-only |
| `CONTENT_TOO_LONG` | 400 | Text exceeds 20,000 character limit |
| `ANALYSIS_FAILED` | 502 | OpenAI API call or response validation failed |
| `MODEL_UNAVAILABLE` | 503 | OpenAI model not available |
| `RATE_LIMITED` | 429 | OpenAI rate limit exceeded |
| `SERVER_ERROR` | 500 | Unexpected server error |

## Environment Variables

Create `ai-service/.env` with:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

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
3. Update `main.py` to instantiate the new analyzer based on configuration
4. Existing risk normalization and DTOs work with any model

### Future Enhancements

- **LightGBM Integration**: Drop-in replacement for GPT-based analysis
- **Isolation Forest**: Unsupervised outlier detection for scam patterns
- **Graph-Based Scoring**: Analyze relationships between scam signals
- **SHAP Explainability**: Provide feature importance for predictions
- **Model Ensemble**: Combine multiple models for improved accuracy
- **Per-Channel Tuning**: Adjust risk thresholds per communication channel
- **Real-time Learning**: Adapt model based on user feedback

## Comparison: TypeScript vs Python Implementation

| Feature | TypeScript (NestJS) | Python (FastAPI) |
|---------|---|---|
| Framework | NestJS | FastAPI |
| Validation | class-validator | Pydantic |
| Schema Format | Zod | Pydantic models |
| Async | RxJS/Promises | async/await |
| OpenAI SDK | TypeScript | Python |
| Prompt Injection Defense | ✓ | ✓ |
| Score Normalization | ✓ | ✓ |
| Risk Level Recomputation | ✓ | ✓ |
| Schema Separation | ✓ | ✓ |
| Safe Logging | ✓ | ✓ |
| Extensibility | ✓ | ✓ |

Both implementations maintain **identical logic and security postures**.

## Quick Start

### Full Stack (TypeScript + Python)

```bash
# Install all dependencies
pip install -r requirements.txt
npm install

# Configure AI service
cp ai-service/.env.example ai-service/.env
# Edit ai-service/.env with OPENAI_API_KEY

# Run tests
pytest tests/ -v
npm test

# Start Python AI service
cd ai-service
uvicorn main:app --reload

# In another terminal, start TypeScript service
npm run start
```

## License

[Add appropriate license information]

## Support

For issues or questions:
1. Check error codes in API responses
2. Review server logs for detailed error information
3. Ensure OPENAI_API_KEY is valid and has sufficient quota
4. Verify request format matches API specification