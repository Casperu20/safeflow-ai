# SafeFlow AI

SafeFlow AI is a local three-app stack for scam-risk analysis of payment-related content. Users can sign up, log in, submit text/PDF/image content for analysis, and view their saved analysis history.

## Local Stack

- `frontend`: `http://127.0.0.1:5173`
- `backend`: `http://127.0.0.1:8000`
- `ai_service`: `http://127.0.0.1:8001`

## Main Features

- JWT-based MVP authentication with session restore through `GET /api/auth/me`
- Scam analysis for text, PDF, and image uploads through `POST /api/scam-analysis`
- Persistent per-user analysis history in SQLite through `GET /api/analysis-history`
- OCR support for images and scanned PDFs when Tesseract is installed on the host
- Anonymous analysis still works; history is only saved when a valid Bearer token is present

## Backend Setup

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Required backend environment variables for local development:

```env
ENVIRONMENT=development
FRONTEND_ORIGIN=http://127.0.0.1:5173
DATABASE_URL=sqlite:///./safeflow.db
JWT_SECRET_KEY=change_this_in_production_please_use_a_long_random_value
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
AI_SERVICE_URL=http://127.0.0.1:8001
AI_SERVICE_TIMEOUT_SECONDS=60
ANALYSIS_MODE=ai
OCR_ENABLED=true
OCR_LANG=eng
OCR_TIMEOUT_SECONDS=20
MAX_FILE_SIZE_MB=10
MAX_PDF_PAGES=5
MAX_IMAGE_WIDTH=4000
MAX_IMAGE_HEIGHT=4000
MIN_EXTRACTED_TEXT_CHARS=20
MAX_TEXT_LENGTH=10000
MAX_AI_INPUT_CHARS=20000
```

Run migrations before starting the backend:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

## Frontend Setup

```powershell
Set-Location frontend
npm install
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api"
```

## Tesseract OCR

Windows:

```powershell
winget install --id UB-Mannheim.TesseractOCR -e
tesseract --version
```

If Tesseract is missing, OCR-backed uploads return `503 OCR_RUNTIME_UNAVAILABLE` and `/api/scam-analysis/config` reports `ocrEnabled: false`.

## Start The Full Stack

Terminal 1: AI service

```powershell
Set-Location ai_service
$env:OPENAI_API_KEY = "your-openai-key"
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Terminal 2: backend

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 3: frontend

```powershell
Set-Location frontend
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api"
npm run dev
```

## API Summary

Auth:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/auth/recover-password`

Analysis:

- `GET /api/scam-analysis/config`
- `POST /api/scam-analysis`

History:

- `GET /api/analysis-history`
- `GET /api/analysis-history/{analysisId}`
- `DELETE /api/analysis-history/{analysisId}`

Health:

- `GET /health`
- `GET /api/health`

## Example Requests

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "fullName": "Example User"
  }'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }'
```

Authenticated scam analysis:

```bash
curl -X POST http://127.0.0.1:8000/api/scam-analysis \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "inputType": "text",
    "content": "Urgent: verify now and use the new bank details immediately."
  }'
```

History:

```bash
curl http://127.0.0.1:8000/api/analysis-history \
  -H "Authorization: Bearer <token>"
```

## Manual Verification Flow

1. Open the frontend and create an account on `/signup`.
2. Log in on `/login`.
3. Submit text, a text PDF, or an OCR-capable image/PDF from the home page.
4. Open `/history` and confirm the saved record appears only for that user.
5. Click a history item and confirm the result page reopens with stored details.

## Security Notes

- Passwords are hashed with Argon2 through `pwdlib`; plaintext passwords are never stored.
- JWT secrets come from environment variables; production startup fails if the secret is missing.
- History stores only sanitized previews and analysis metadata, not raw uploaded files or full extracted documents.
- Frontend stores the JWT in `localStorage` for this MVP to support session restore. This is convenient for development but has an XSS trade-off; a hardened production design should move to httpOnly cookies or a stronger token strategy.
- CORS is restricted to the configured frontend origin plus the local 5173 development hosts.

## Current Limitations

- OCR depends on a system Tesseract installation.
- `recover-password` is currently a non-delivering MVP acknowledgement endpoint.
- JWT logout is client-side only; there is no token revocation or refresh-token flow yet.
- There is no rate limiting or account lockout yet.

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

| Variable         | Required | Description                            |
| ---------------- | -------- | -------------------------------------- |
| `OPENAI_API_KEY` | Yes      | OpenAI API key for authentication      |
| `SERVICE_PORT`   | No       | Port to run service on (default: 8001) |
| `SERVICE_HOST`   | No       | Host to bind to (default: 0.0.0.0)     |

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
CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:

```bash
docker build -t safeflow-ai .
docker run -e OPENAI_API_KEY=sk-... -p 8001:8001 safeflow-ai
```

### Environment Configuration

For production, set environment variables:

```bash
export OPENAI_API_KEY=sk-...
export SERVICE_HOST=0.0.0.0
export SERVICE_PORT=8001
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
