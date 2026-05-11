from fastapi.testclient import TestClient

from app.main import app
from app.utils.file_validation import MAX_FILE_SIZE_BYTES


client = TestClient(app)


def test_get_scam_analysis_config() -> None:
    response = client.get("/api/scam-analysis/config")

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


def test_post_scam_analysis_with_valid_text_json() -> None:
    response = client.post(
        "/api/scam-analysis",
        json={
            "inputType": "text",
            "content": "Urgent: verify now and use the new bank details immediately.",
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["analysisId"].startswith("analysis_")
    assert payload["riskScore"] == 86
    assert payload["riskLevel"] == "high"
    assert payload["detectedScamType"] == "Payment redirection scam"
    assert payload["analysisMode"] == "mock"
    assert payload["recommendation"]
    assert payload["indicators"]
    assert payload["evidence"]


def test_post_scam_analysis_with_empty_text() -> None:
    response = client.post(
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


def test_post_scam_analysis_with_unsupported_input_type() -> None:
    response = client.post(
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


def test_post_scam_analysis_with_pdf_upload() -> None:
    response = client.post(
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


def test_post_scam_analysis_with_image_upload() -> None:
    response = client.post(
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


def test_post_scam_analysis_rejects_unsupported_file_type() -> None:
    response = client.post(
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


def test_post_scam_analysis_rejects_file_too_large() -> None:
    response = client.post(
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