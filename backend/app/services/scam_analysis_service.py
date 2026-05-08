from dataclasses import dataclass
from typing import Literal, cast
from uuid import uuid4

from starlette.datastructures import UploadFile

from app.schemas.errors import ApiError
from app.schemas.scam_analysis import (
    EvidenceItem,
    InputType,
    ScamAnalysisConfigResponse,
    ScamAnalysisResponse,
)
from app.utils.file_validation import (
    ACCEPTED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
    ValidatedUpload,
    validate_uploaded_file,
)
from app.utils.text_sanitization import sanitize_text_content, safe_text_excerpt


MAX_TEXT_LENGTH = 10_000
SUPPORTED_INPUT_TYPES = {"text", "pdf", "image"}

HIGH_RISK_SIGNALS: dict[str, tuple[str, str, Literal["high", "medium"]]] = {
    "urgent": ("Urgent language", "Urgency and pressure language", "high"),
    "immediately": ("Immediate action requested", "Pressure to act immediately", "high"),
    "new bank details": ("New payment details", "Request to change bank details", "high"),
    "account suspension": ("Threat-based language", "Suspension threat used to force action", "high"),
    "verify now": ("Forced verification", "Demand to verify immediately", "medium"),
}

MEDIUM_RISK_SIGNALS: dict[str, tuple[str, str, Literal["medium", "low"]]] = {
    "invoice": ("Invoice-related context", "Financial document language detected", "medium"),
    "payment": ("Payment request", "Payment-related wording detected", "medium"),
    "bank": ("Banking reference", "Banking details are being discussed", "low"),
    "transfer": ("Transfer request", "Funds transfer language detected", "medium"),
}

PAYMENT_REDIRECTION_TERMS = {"new bank details", "bank", "payment", "transfer", "invoice"}
PHISHING_TERMS = {"account suspension", "verify now"}


@dataclass(slots=True)
class AnalysisSubmission:
    input_type: str | None
    content: str | None = None
    file: UploadFile | None = None


class ScamAnalysisService:
    def get_config(self) -> ScamAnalysisConfigResponse:
        return ScamAnalysisConfigResponse(
            inputTypes=["text", "pdf", "image"],
            acceptedFileTypes=ACCEPTED_FILE_TYPES,
            limits={
                "maxTextLength": MAX_TEXT_LENGTH,
                "maxFileSizeMB": MAX_FILE_SIZE_MB,
                "maxPdfPages": None,
            },
            riskThresholds={
                "low": [0, 39],
                "medium": [40, 69],
                "high": [70, 100],
            },
        )

    async def analyze(self, submission: AnalysisSubmission) -> ScamAnalysisResponse:
        input_type = self._validate_input_type(submission.input_type)

        if input_type == "text":
            return self._analyze_text_submission(submission)

        return await self._analyze_file_submission(input_type, submission)

    def _validate_input_type(self, input_type: str | None) -> InputType:
        if input_type not in SUPPORTED_INPUT_TYPES:
            raise ApiError(
                status_code=400,
                error_code="INVALID_INPUT_TYPE",
                message="inputType must be one of: text, pdf, image.",
                details={
                    "inputType": ["Allowed values are text, pdf, image."],
                },
            )

        return cast(InputType, input_type)

    def _analyze_text_submission(self, submission: AnalysisSubmission) -> ScamAnalysisResponse:
        if submission.file is not None:
            raise ApiError(
                status_code=400,
                error_code="INVALID_REQUEST",
                message="Text analysis accepts content only.",
                details={
                    "file": ["Do not upload a file when inputType is text."],
                },
            )

        content = sanitize_text_content(submission.content or "")

        if not content:
            raise ApiError(
                status_code=400,
                error_code="EMPTY_TEXT_CONTENT",
                message="Text content cannot be empty.",
                details={
                    "content": ["This field is required when inputType is text."],
                },
            )

        if len(content) > MAX_TEXT_LENGTH:
            raise ApiError(
                status_code=400,
                error_code="CONTENT_TOO_LONG",
                message=f"Text content must be {MAX_TEXT_LENGTH} characters or less.",
                details={
                    "content": [f"Maximum length is {MAX_TEXT_LENGTH} characters."],
                },
            )

        return self._build_text_response(content)

    async def _analyze_file_submission(
        self,
        input_type: Literal["pdf", "image"],
        submission: AnalysisSubmission,
    ) -> ScamAnalysisResponse:
        if sanitize_text_content(submission.content or ""):
            raise ApiError(
                status_code=400,
                error_code="INVALID_REQUEST",
                message=f"{input_type.upper()} analysis accepts file uploads only.",
                details={
                    "content": [f"Do not send content when inputType is {input_type}."],
                },
            )

        validated_upload = await validate_uploaded_file(submission.file, input_type)

        if input_type == "pdf":
            return self._build_pdf_response(validated_upload)

        return self._build_image_response(validated_upload)

    def _build_text_response(self, content: str) -> ScamAnalysisResponse:
        lowered_content = content.casefold()

        matched_high_risk = [
            (phrase, HIGH_RISK_SIGNALS[phrase])
            for phrase in HIGH_RISK_SIGNALS
            if phrase in lowered_content
        ]

        if matched_high_risk:
            indicators = self._unique_values(signal[0] for _, signal in matched_high_risk)
            evidence = [
                EvidenceItem(
                    text=f"Matched phrase: {phrase}",
                    reason=signal[1],
                    severity=signal[2],
                )
                for phrase, signal in matched_high_risk[:3]
            ]

            scam_type = self._detect_text_scam_type({phrase for phrase, _ in matched_high_risk})

            return self._response(
                risk_score=86,
                detected_scam_type=scam_type,
                explanation="The message contains urgency, account pressure, or payment redirection cues that are commonly used in scams.",
                indicators=indicators,
                recommendation="Do not proceed with the payment or verification request. Confirm the request using a trusted contact method.",
                evidence=evidence,
            )

        matched_medium_risk = [
            (phrase, MEDIUM_RISK_SIGNALS[phrase])
            for phrase in MEDIUM_RISK_SIGNALS
            if phrase in lowered_content
        ]

        if matched_medium_risk:
            return self._response(
                risk_score=58,
                detected_scam_type="Suspicious payment message",
                explanation="The message references payment-related context but does not contain the strongest high-risk trigger phrases.",
                indicators=self._unique_values(signal[0] for _, signal in matched_medium_risk),
                recommendation="Pause before acting. Verify the request and payment details through a separate trusted channel.",
                evidence=[
                    EvidenceItem(
                        text=f"Matched phrase: {phrase}",
                        reason=signal[1],
                        severity=signal[2],
                    )
                    for phrase, signal in matched_medium_risk[:3]
                ],
            )

        return self._response(
            risk_score=24,
            detected_scam_type=None,
            explanation="No strong mock scam indicators were detected in the submitted text.",
            indicators=["No high-risk trigger terms detected"],
            recommendation="Continue with normal verification steps before sending money or sharing sensitive information.",
            evidence=[
                EvidenceItem(
                    text=safe_text_excerpt(content),
                    reason="A short sanitized excerpt is shown for analyst context.",
                    severity="low",
                )
            ],
        )

    def _build_pdf_response(self, upload: ValidatedUpload) -> ScamAnalysisResponse:
        normalized_name = upload.filename.casefold()

        # TODO: Add PDF text extraction once the document-analysis pipeline is introduced.
        if any(term in normalized_name for term in PAYMENT_REDIRECTION_TERMS):
            return self._response(
                risk_score=77,
                detected_scam_type="Payment redirection scam",
                explanation="The PDF upload was received successfully, and its filename suggests payment-related content that should be independently verified.",
                indicators=[
                    "PDF upload received",
                    "Payment-related filename",
                    "Manual verification recommended",
                ],
                recommendation="Do not execute the payment based on the document alone. Confirm the beneficiary and bank details through a trusted channel.",
                evidence=[
                    EvidenceItem(
                        text="PDF metadata indicates payment-oriented context.",
                        reason="Filename contains payment-related terminology.",
                        severity="high",
                    )
                ],
            )

        return self._response(
            risk_score=55,
            detected_scam_type="Document review required",
            explanation="The PDF upload was received successfully. This mock response flags documents for manual verification until PDF extraction is implemented.",
            indicators=[
                "PDF upload received",
                "No document parsing enabled yet",
                "Manual review required",
            ],
            recommendation="Review the document manually and verify sender, invoice, and payment details before proceeding.",
            evidence=[
                EvidenceItem(
                    text="PDF content has not been parsed in mock mode.",
                    reason="Future extraction is intentionally deferred for the MVP.",
                    severity="medium",
                )
            ],
        )

    def _build_image_response(self, upload: ValidatedUpload) -> ScamAnalysisResponse:
        normalized_name = upload.filename.casefold()

        # TODO: Add OCR and screenshot text extraction before introducing model-backed image analysis.
        if any(term in normalized_name for term in PAYMENT_REDIRECTION_TERMS | {"chat", "message", "screenshot"}):
            return self._response(
                risk_score=82,
                detected_scam_type="Payment redirection scam",
                explanation="The image upload was received successfully. In mock mode, screenshot-like payment requests are treated as high risk.",
                indicators=[
                    "Image upload received",
                    "Screenshot-like context",
                    "External verification needed",
                ],
                recommendation="Do not rely on the screenshot alone. Verify the request directly with the known sender using a separate channel.",
                evidence=[
                    EvidenceItem(
                        text="Image metadata suggests a payment-request screenshot.",
                        reason="Filename indicates message or payment context.",
                        severity="high",
                    )
                ],
            )

        return self._response(
            risk_score=74,
            detected_scam_type="Suspicious payment screenshot",
            explanation="The image upload was received successfully. Mock mode treats uploaded payment-related screenshots as high risk until OCR is available.",
            indicators=[
                "Image upload received",
                "OCR not enabled yet",
                "Manual verification needed",
            ],
            recommendation="Verify the payment request using trusted contact details before taking any action.",
            evidence=[
                EvidenceItem(
                    text="Image text extraction is not available in mock mode.",
                    reason="OCR is intentionally deferred for the MVP.",
                    severity="high",
                )
            ],
        )

    def _response(
        self,
        risk_score: int,
        detected_scam_type: str | None,
        explanation: str,
        indicators: list[str],
        recommendation: str,
        evidence: list[EvidenceItem],
    ) -> ScamAnalysisResponse:
        # TODO: Add prompt-injection and jailbreak handling before any real model is introduced.
        return ScamAnalysisResponse(
            analysisId=f"analysis_{uuid4()}",
            riskScore=risk_score,
            riskLevel=self._risk_level_for_score(risk_score),
            detectedScamType=detected_scam_type,
            explanation=explanation,
            indicators=indicators,
            recommendation=recommendation,
            evidence=evidence,
            analysisMode="mock",
        )

    def _detect_text_scam_type(self, phrases: set[str]) -> str:
        if phrases & PAYMENT_REDIRECTION_TERMS:
            return "Payment redirection scam"
        if phrases & PHISHING_TERMS:
            return "Account verification phishing"
        return "Urgency scam"

    def _risk_level_for_score(self, risk_score: int) -> Literal["low", "medium", "high"]:
        if risk_score >= 70:
            return "high"
        if risk_score >= 40:
            return "medium"
        return "low"

    def _unique_values(self, values: list[str] | tuple[str, ...] | object) -> list[str]:
        seen: set[str] = set()
        unique_values: list[str] = []

        for value in values:
            if value in seen:
                continue
            seen.add(value)
            unique_values.append(value)

        return unique_values