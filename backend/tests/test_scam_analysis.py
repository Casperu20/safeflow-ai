import httpx
import pytest

from app.api.routes import scam_analysis as scam_analysis_route
from app.main import app
from app.schemas.errors import ApiError
from app.utils.file_validation import MAX_FILE_SIZE_BYTES


def _build_text_pdf_bytes(text: str) -> bytes:
    escaped_text = (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )
    stream = f"BT\n/F1 12 Tf\n72 720 Td\n({escaped_text}) Tj\nET\n".encode("latin-1")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    pdf_bytes = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes += obj

    startxref = len(pdf_bytes)
    pdf_bytes += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    pdf_bytes += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf_bytes += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf_bytes += b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
    pdf_bytes += f"startxref\n{startxref}\n%%EOF".encode("ascii")
    return pdf_bytes


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
        "analysisMode": "hybrid",
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
            details={"serviceUrl": "http://127.0.0.1:8001", "timeoutSeconds": 60.0},
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


def test_ai_service_client_uses_configured_timeout() -> None:
    from app.services.ai_service_client import AiServiceClient

    client = AiServiceClient(base_url="http://127.0.0.1:8001")

    assert client.timeout_seconds == 60.0


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
async def test_post_scam_analysis_with_pdf_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_payload: dict[str, str] = {}

    async def fake_analyze_text(text: str):
        captured_payload["text"] = text
        return {
            "riskScore": 72,
            "riskLevel": "high",
            "detectedScamType": "Payment redirection scam",
            "explanation": "Extracted PDF text indicates a payment change request.",
            "indicators": ["Urgent language", "New payment details"],
            "evidence": [
                {
                    "text": "Urgent verify now new bank details",
                    "reason": "Payment redirection pressure",
                    "severity": "high",
                }
            ],
            "recommendation": "Verify the request through a trusted channel.",
        }

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", fake_analyze_text)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "pdf"},
            files={
                "file": (
                    "invoice-payment.pdf",
                    _build_text_pdf_bytes("Urgent verify now and use the new bank details."),
                    "application/pdf",
                ),
            },
        )

    assert response.status_code == 200

    payload = response.json()
    assert "new bank details" in captured_payload["text"].lower()
    assert payload["riskScore"] == 72
    assert payload["riskLevel"] == "high"
    assert payload["detectedScamType"] == "Payment redirection scam"
    assert payload["analysisMode"] == "ai"


@pytest.mark.anyio
async def test_post_scam_analysis_truncates_large_pdf_text_before_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_payload: dict[str, str] = {}

    async def fake_analyze_text(text: str):
        captured_payload["text"] = text
        return {
            "riskScore": 41,
            "riskLevel": "medium",
            "detectedScamType": "Suspicious payment message",
            "explanation": "Large PDF content was accepted.",
            "indicators": ["Payment request"],
            "evidence": [],
            "recommendation": "Review the document carefully.",
        }

    monkeypatch.setattr(scam_analysis_route.ai_service_client, "analyze_text", fake_analyze_text)

    long_text = "urgent payment transfer " * 2000

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "pdf"},
            files={
                "file": (
                    "large-invoice.pdf",
                    _build_text_pdf_bytes(long_text),
                    "application/pdf",
                ),
            },
        )

    assert response.status_code == 200
    assert len(captured_payload["text"]) == 20_000


@pytest.mark.anyio
async def test_post_scam_analysis_rejects_non_parseable_pdf() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/scam-analysis",
            data={"inputType": "pdf"},
            files={
                "file": ("invoice-payment.pdf", b"%PDF-1.4 not-a-real-pdf", "application/pdf"),
            },
        )

    assert response.status_code == 422
    assert response.json() == {
        "errorCode": "PDF_TEXT_EXTRACTION_FAILED",
        "message": "Could not extract readable text from the uploaded PDF.",
        "details": {
            "file": [
                "The uploaded PDF could not be parsed as a text-based document."
            ]
        },
    }


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