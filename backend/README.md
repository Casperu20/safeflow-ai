# SafeFlow AI Backend

FastAPI backend for SafeFlow AI. The backend supports authentication, scam analysis, and per-user analysis history while keeping the existing `POST /api/scam-analysis` contract stable.

## What The Backend Does

- Authenticates users with JWT Bearer tokens
- Analyzes plain text, PDFs, and images
- Saves authenticated analyses to persistent history
- Keeps anonymous analysis available for the existing frontend flow
- Redacts sensitive data in stored previews and evidence
- Never stores uploaded files permanently for history

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- `pwdlib` with Argon2 password hashing
- PyJWT for access tokens
- PyMuPDF + Pillow + pytesseract for document extraction

## Requirements

- Python 3.11+
- Tesseract OCR installed and available in `PATH` for OCR-backed uploads
- A configured `JWT_SECRET_KEY`

## Environment Variables

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

Production startup fails if `JWT_SECRET_KEY` is missing.

## Local Setup

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
..\.venv\Scripts\python.exe -m alembic upgrade head
```

## Migration Commands

Apply migrations:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Create a new migration after future schema changes:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
```

## Run The Backend Locally

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API root: `http://127.0.0.1:8000`

OpenAPI docs: `http://127.0.0.1:8000/docs`

## Auth Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/auth/recover-password`

Register request:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "fullName": "Example User"
}
```

Register/login response:

```json
{
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "fullName": "Example User",
    "role": "user",
    "createdAt": "2026-05-15T12:00:00Z"
  },
  "accessToken": "jwt_token",
  "tokenType": "bearer"
}
```

## Analysis Endpoints

- `GET /api/scam-analysis/config`
- `POST /api/scam-analysis`

`POST /api/scam-analysis` accepts:

- JSON text submissions: `{"inputType":"text","content":"..."}`
- `multipart/form-data` for PDFs and images with `inputType` plus `file`

Authenticated analysis automatically saves history.

Anonymous analysis still returns a normal result but does not create a history record.

Authenticated analysis example:

```bash
curl -X POST http://127.0.0.1:8000/api/scam-analysis \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"inputType":"text","content":"Urgent: verify now and use the new bank details immediately."}'
```

## History Endpoints

- `GET /api/analysis-history`
- `GET /api/analysis-history/{analysisId}`
- `DELETE /api/analysis-history/{analysisId}`

History list example:

```bash
curl http://127.0.0.1:8000/api/analysis-history \
  -H "Authorization: Bearer <token>"
```

History response shape:

```json
{
  "items": [
    {
      "analysisId": "analysis_123",
      "inputType": "text",
      "originalFilename": null,
      "inputPreview": "Urgent: verify now and use the new bank details immediately.",
      "riskScore": 86,
      "riskLevel": "high",
      "detectedScamType": "Payment redirection scam",
      "explanation": "The message contains urgency, account pressure, or payment redirection cues that are commonly used in scams.",
      "indicators": ["Urgent language", "New payment details"],
      "recommendation": "Do not proceed with the payment or verification request. Confirm the request using a trusted contact method.",
      "evidence": [
        {
          "text": "Please pay immediately to the [redacted-number].",
          "reason": "Urgency and new payment details",
          "severity": "high"
        }
      ],
      "extractionMethod": "plain_text",
      "analysisMode": "mock",
      "createdAt": "2026-05-15T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Error Format

All controlled application errors use:

```json
{
  "errorCode": "INVALID_CREDENTIALS",
  "message": "Invalid email or password.",
  "details": {}
}
```

Examples of auth/history error codes:

- `EMAIL_ALREADY_EXISTS`
- `INVALID_CREDENTIALS`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `INVALID_TOKEN`
- `TOKEN_EXPIRED`
- `HISTORY_ITEM_NOT_FOUND`
- `SERVER_ERROR`

## Tests

Run backend tests:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest
```

Run only auth/history tests:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest tests/test_auth_history.py
```

## Security Notes

- Passwords are hashed with Argon2; raw passwords are never stored or logged.
- JWTs are signed with an environment-driven secret.
- CORS is restricted to the configured frontend origin and local development hosts.
- History stores a short sanitized preview plus result metadata, not raw files and not the full extracted document.
- Evidence and previews are redacted for emails, URLs, phone numbers, IBAN-like values, and long digit sequences.

## Current Limitations

- No refresh-token flow yet.
- No server-side token revocation list yet.
- No rate limiting or brute-force protection yet.
- `recover-password` is an acknowledgement endpoint only.
- OCR requires Tesseract on the host machine.
