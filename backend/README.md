# SafeFlow AI Backend

Mock FastAPI backend for the SafeFlow AI MVP. This service provides a stable frontend integration contract for text, PDF, and image scam analysis requests without implementing a real model, OCR, PDF parsing, authentication, or persistence yet.

## Requirements

- Python 3.11+
- PowerShell or another shell capable of setting environment variables

## Setup

```powershell
Set-Location backend
& "C:/Program Files/Python313/python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set the environment variables before starting the app:

```powershell
$env:ENVIRONMENT = "development"
$env:FRONTEND_ORIGIN = "http://localhost:3000"
```

Note: the current frontend is a Vite app and will use `http://localhost:5173` unless you override its port. If you keep the Vite default, set `FRONTEND_ORIGIN` to `http://localhost:5173` to avoid CORS failures during development.

## Run Locally

```powershell
Set-Location backend
& "C:/Program Files/Python313/python.exe" -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

OpenAPI docs are available at `http://127.0.0.1:8000/docs`.

## Environment Variables

- `ENVIRONMENT`: runtime environment label. Use `development` for local work.
- `FRONTEND_ORIGIN`: allowed frontend origin for CORS.

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
  "analysisMode": "mock"
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

- No real scam detection model yet
- No OCR yet
- No PDF extraction yet
- No database yet
- Mock risk scoring only
- No authentication or dashboard integration yet
