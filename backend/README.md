# SafeFlow AI Backend

FastAPI backend for SafeFlow AI. Text input and text-based PDF uploads are forwarded to the AI analysis microservice, while image uploads remain on the mock path until OCR is implemented.

## Requirements

- Python 3.11+
- PowerShell or another shell capable of setting environment variables

## Setup

```powershell
Set-Location backend
& "C:/Program Files/Python313/python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

This installs the backend runtime plus the `openai` client needed when you run the local `ai_service` from the same virtual environment.

Set the environment variables before starting the app:

```powershell
$env:ENVIRONMENT = "development"
$env:FRONTEND_ORIGIN = "http://localhost:5173"
$env:AI_SERVICE_URL = "http://127.0.0.1:8001"
$env:AI_SERVICE_TIMEOUT_SECONDS = "60"
```

The local stack uses these fixed ports:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`
- AI service: `http://127.0.0.1:8001`

## Run Locally

Start each application in a separate terminal.

Terminal 1: AI service

```powershell
Set-Location ..
$env:OPENAI_API_KEY = "your-openai-key"
& "C:/Program Files/Python313/python.exe" -m uvicorn ai_service.main:app --reload --host 127.0.0.1 --port 8001
```

If `ai_service` fails with `ModuleNotFoundError: No module named 'openai'`, reinstall dependencies in the active virtual environment with `python -m pip install -r backend/requirements.txt`.

Terminal 2: backend

```powershell
Set-Location backend
$env:ENVIRONMENT = "development"
$env:FRONTEND_ORIGIN = "http://localhost:5173"
$env:AI_SERVICE_URL = "http://127.0.0.1:8001"
$env:AI_SERVICE_TIMEOUT_SECONDS = "60"
& "C:/Program Files/Python313/python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 3: frontend

```powershell
Set-Location ..\frontend
$env:VITE_API_BASE_URL = "http://127.0.0.1:8000/api"
npm run dev
```

The API will be available at `http://127.0.0.1:8000`.

OpenAPI docs are available at `http://127.0.0.1:8000/docs`.

## Environment Variables

- `ENVIRONMENT`: runtime environment label. Use `development` for local work.
- `FRONTEND_ORIGIN`: allowed frontend origin for CORS.
- `AI_SERVICE_URL`: base URL of the internal AI analysis microservice.
- `AI_SERVICE_TIMEOUT_SECONDS`: backend timeout in seconds for responses from `ai_service`.

## Endpoints

- `GET /health`
- `GET /api/health`
- `GET /api/scam-analysis/config`
- `POST /api/scam-analysis`

## API Contract Summary

`POST /api/scam-analysis` accepts either JSON for text analysis:

```json
{
  "inputType": "text",
  "content": "Suspicious message goes here"
}
```

Or `multipart/form-data` using these field names:

- `inputType`: `text`, `pdf`, or `image`
- `content`: optional text field, only valid for `inputType=text`
- `file`: uploaded file, required for `inputType=pdf` or `inputType=image`

## Example Requests

Text JSON request:

```bash
curl -X POST http://127.0.0.1:8000/api/scam-analysis \
  -H "Content-Type: application/json" \
  -d '{"inputType":"text","content":"Urgent: please verify now and use the new bank details."}'
```

Multipart file upload:

```bash
curl -X POST http://127.0.0.1:8000/api/scam-analysis \
  -F "inputType=pdf" \
  -F "file=@invoice.pdf;type=application/pdf"
```

## Example Response

```json
{
  "analysisId": "analysis_123e4567-e89b-12d3-a456-426614174000",
  "riskScore": 86,
  "riskLevel": "high",
  "detectedScamType": "Payment redirection scam",
  "explanation": "The message contains urgency, account pressure, or payment redirection cues that are commonly used in scams.",
  "indicators": [
    "Urgent language",
    "Forced verification",
    "New payment details"
  ],
  "recommendation": "Do not proceed with the payment or verification request. Confirm the request using a trusted contact method.",
  "evidence": [
    {
      "text": "Matched phrase: urgent",
      "reason": "Urgency and pressure language",
      "severity": "high"
    }
  ],
  "analysisMode": "ai"
}
```

## Error Shape

All application errors use this structure:

```json
{
  "errorCode": "EMPTY_TEXT_CONTENT",
  "message": "Text content cannot be empty.",
  "details": {
    "content": ["This field is required when inputType is text."]
  }
}
```

## Tests

Run the backend tests with:

```powershell
Set-Location backend
& "C:/Program Files/Python313/python.exe" -m pytest
```

## Known Limitations

- OCR is not implemented yet, so image uploads still use mock analysis
- PDF analysis works only for text-based PDFs; scanned PDFs still require OCR
- No database yet
- Image risk scoring is still mock-only
- No authentication or dashboard integration yet
