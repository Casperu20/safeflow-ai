import httpx
import pytest

from app.api.routes import scam_analysis as scam_analysis_route
from app.main import app
from app.schemas.errors import ApiError
from app.utils.file_validation import MAX_FILE_SIZE_BYTES


@pytest.mark.anyio
async def test_get_scam_analysis_config() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/scam-analysis/config")

    assert response.status_code == 200
    assert response.json() == {
        "inputTypes": ["text", "pdf", "image"],
        "acceptedFileTypes": {
            "pdf": ["application/pdf"],
            "image": ["image/png", "image/jpeg", "image/webp"],
        },
        "limits": {
            "maxTextLength": 10000,
            "maxFileSizeMB": 10,
            "maxPdfPages": None,
        },
        "riskThresholds": {
            "low": [0, 39],
            "medium": [40, 69],
            "high": [70, 100],
        },
        "processingMode": "synchronous",
        "analysisMode": "mock",
    }


@pytest.mark.anyio
async def test_post_scam_analysis_with_valid_text_json(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_analyze_text(_: str):
        return {
            "riskScore": 86,
            "riskLevel": "high",
            "detectedScamType": "Payment redirection scam",
            "explanation": "Suspicious urgency and payment change request.",
            "indicators": ["Urgent language", "New payment details"],
            "evidence": [
                {
                    "text": "new bank details immediately",
                    "reason": "Payment redirection pressure",
                    "severity": "high",
                }
            ],
            "recommendation": "Verify payment details through a trusted channel.",
        }

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", fake_analyze_text)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={
                "inputType": "text",
                "content": "Urgent: verify now and use the new bank details immediately.",
            },
        )

    assert response.status_code == 200

    payload = response.json()
    assert payload["riskScore"] == 86
    assert payload["riskLevel"] == "high"
    assert payload["detectedScamType"] == "Payment redirection scam"
    assert payload["recommendation"]
    assert payload["indicators"]
    assert payload["evidence"]


@pytest.mark.anyio
async def test_post_scam_analysis_text_ai_service_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_analyze_text(_: str):
        raise ApiError(
            status_code=503,
            error_code="AI_SERVICE_UNAVAILABLE",
            message="AI service is unavailable.",
            details={"serviceUrl": "http://127.0.0.1:8000"},
        )

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", failing_analyze_text)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={"inputType": "text", "content": "test"},
        )

    assert response.status_code == 503
    assert response.json()["errorCode"] == "AI_SERVICE_UNAVAILABLE"


@pytest.mark.anyio
async def test_post_scam_analysis_text_ai_service_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_analyze_text(_: str):
        raise ApiError(
            status_code=504,
            error_code="AI_SERVICE_TIMEOUT",
            message="AI service request timed out.",
            details={"serviceUrl": "http://127.0.0.1:8000"},
        )

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", failing_analyze_text)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={"inputType": "text", "content": "test"},
        )

    assert response.status_code == 504
    assert response.json()["errorCode"] == "AI_SERVICE_TIMEOUT"


@pytest.mark.anyio
async def test_post_scam_analysis_text_ai_service_error_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def failing_analyze_text(_: str):
        raise ApiError(
            status_code=502,
            error_code="AI_SERVICE_ERROR",
            message="AI service returned an error response.",
            details={"serviceUrl": "http://127.0.0.1:8000", "statusCode": 500},
        )

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", failing_analyze_text)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={"inputType": "text", "content": "test"},
        )

    assert response.status_code == 502
    assert response.json()["errorCode"] == "AI_SERVICE_ERROR"


@pytest.mark.anyio
async def test_post_scam_analysis_with_empty_text() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={"inputType": "text", "content": "   \n\t  "},
        )

    assert response.status_code == 400
    assert response.json() == {
        "errorCode": "EMPTY_TEXT_CONTENT",
        "message": "Text content cannot be empty.",
        "details": {
            "content": ["This field is required when inputType is text."],
        },
    }


@pytest.mark.anyio
async def test_post_scam_analysis_with_unsupported_input_type() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            json={"inputType": "audio", "content": "Suspicious voice note"},
        )

    assert response.status_code == 400
    assert response.json() == {
        "errorCode": "INVALID_INPUT_TYPE",
        "message": "inputType must be one of: text, pdf, image.",
        "details": {
            "inputType": ["Allowed values are text, pdf, image."],
        },
    }


@pytest.mark.anyio
async def test_post_scam_analysis_with_pdf_upload() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "pdf"},
            files={
                "file": ("invoice-payment.pdf", b"%PDF-1.4 mock document", "application/pdf"),
            },
        )

    assert response.status_code == 200

    payload = response.json()
    assert payload["riskScore"] == 77
    assert payload["riskLevel"] == "high"
    assert payload["detectedScamType"] == "Payment redirection scam"
    assert payload["analysisMode"] == "mock"


@pytest.mark.anyio
async def test_post_scam_analysis_with_image_upload() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "image"},
            files={
                "file": ("payment-screenshot.png", b"mock png payload", "image/png"),
            },
        )

    assert response.status_code == 200

    payload = response.json()
    assert payload["riskScore"] == 82
    assert payload["riskLevel"] == "high"
    assert payload["detectedScamType"] == "Payment redirection scam"
    assert payload["analysisMode"] == "mock"


@pytest.mark.anyio
async def test_post_scam_analysis_rejects_unsupported_file_type() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "image"},
            files={
                "file": ("notes.txt", b"not an image", "text/plain"),
            },
        )

    assert response.status_code == 415
    assert response.json() == {
        "errorCode": "UNSUPPORTED_FILE_TYPE",
        "message": "Unsupported file type.",
        "details": {
            "file": [
                "Accepted MIME types for image are: image/jpeg, image/png, image/webp."
            ]
        },
    }


@pytest.mark.anyio
async def test_post_scam_analysis_rejects_file_too_large() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "pdf"},
            files={
                "file": (
                    "large.pdf",
                    b"x" * (MAX_FILE_SIZE_BYTES + 1),
                    "application/pdf",
                ),
            },
        )

    assert response.status_code == 413
    assert response.json() == {
        "errorCode": "FILE_TOO_LARGE",
        "message": "File size must be under 10MB.",
        "details": {
            "file": ["Maximum allowed file size is 10MB."]
        },
    }