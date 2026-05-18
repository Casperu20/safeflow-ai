import logging
import re
from typing import Literal
from uuid import uuid4

from app.core.config import settings
from app.schemas.errors import ApiError
from app.schemas.scam_analysis import (
    EvidenceItem,
    ScamAnalysisConfigResponse,
    ScamAnalysisResponse,
)
from app.services.ai_service_client import AiServiceClient
from app.services.extraction.image_ocr import is_ocr_runtime_available
from app.services.extraction.extraction_models import ExtractionResult
from app.utils.file_validation import (
    ACCEPTED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
)
from app.utils.text_sanitization import redact_sensitive_text, safe_text_excerpt


logger = logging.getLogger(__name__)

SUPPORTED_EXTRACTION_METHODS = [
    "plain_text",
    "pdf_text_layer",
    "pdf_ocr",
    "pdf_hybrid",
    "image_ocr",
]

HIGH_RISK_SIGNALS: dict[str, tuple[str, str, Literal["high", "medium"]]] = {
    "urgent": ("Urgent language", "Urgency and pressure language", "high"),
    "immediately": ("Immediate action requested", "Pressure to act immediately", "high"),
    "new bank details": ("New payment details", "Request to change bank details", "high"),
    "change of beneficiary": ("Beneficiary changed", "Request to change the beneficiary account", "high"),
    "bypass verification": ("Verification bypass", "Request to skip normal verification steps", "high"),
    "account suspension": ("Threat-based language", "Suspension threat used to force action", "high"),
    "verify now": ("Forced verification", "Demand to verify immediately", "medium"),
    "private link": ("Untrusted link", "Requests the victim to use a private or suspicious link", "high"),
}

MEDIUM_RISK_SIGNALS: dict[str, tuple[str, str, Literal["medium", "low"]]] = {
    "invoice": ("Invoice-related context", "Financial document language detected", "medium"),
    "payment": ("Payment request", "Payment-related wording detected", "medium"),
    "bank": ("Banking reference", "Banking details are being discussed", "low"),
    "transfer": ("Transfer request", "Funds transfer language detected", "medium"),
    "beneficiary": ("Beneficiary reference", "Beneficiary details are referenced in the document", "medium"),
    "click": ("Link interaction", "The message asks the reader to click a link or button", "low"),
}

PAYMENT_REDIRECTION_TERMS = {
    "new bank details",
    "bank",
    "payment",
    "transfer",
    "invoice",
    "change of beneficiary",
    "beneficiary",
}
PHISHING_TERMS = {"account suspension", "verify now"}

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class ScamAnalysisService:
    def __init__(self, ai_service_client: AiServiceClient | None = None) -> None:
        self.ai_service_client = ai_service_client or AiServiceClient()

    def get_config(self) -> ScamAnalysisConfigResponse:
        ocr_available = is_ocr_runtime_available()
        supported_extraction_methods = ["plain_text", "pdf_text_layer"]
        if ocr_available:
            supported_extraction_methods.extend(["pdf_ocr", "pdf_hybrid", "image_ocr"])

        return ScamAnalysisConfigResponse(
            inputTypes=["text", "pdf", "image"],
            acceptedFileTypes=ACCEPTED_FILE_TYPES,
            limits={
                "maxTextLength": settings.max_text_length,
                "maxFileSizeMB": MAX_FILE_SIZE_MB,
                "maxPdfPages": settings.max_pdf_pages,
                "maxImageWidth": settings.max_image_width,
                "maxImageHeight": settings.max_image_height,
            },
            riskThresholds={
                "low": [0, 39],
                "medium": [40, 69],
                "high": [70, 100],
            },
            analysisMode=self._effective_analysis_mode(),
            ocrEnabled=ocr_available,
            supportedExtractionMethods=supported_extraction_methods,
        )

    async def analyze_extracted_text(self, extraction: ExtractionResult) -> ScamAnalysisResponse:
        logger.info(
            "Analyzing extracted content type=%s method=%s chars=%s warnings=%s",
            extraction.input_type,
            extraction.extraction_method,
            len(extraction.normalized_text),
            len(extraction.warnings),
        )

        if not extraction.normalized_text:
            raise ApiError(
                status_code=422,
                error_code="EMPTY_TEXT_CONTENT",
                message="No readable text was extracted from the submitted input.",
                details={"file": ["Extraction produced no readable text."]},
            )

        if self._effective_analysis_mode() == "mock":
            return self._build_mock_response(extraction.normalized_text)

        return await self._analyze_with_ai(extraction.normalized_text)

    def _build_mock_response(self, content: str) -> ScamAnalysisResponse:
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
                    text=self._extract_evidence_snippet(content, phrase),
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
                        text=self._extract_evidence_snippet(content, phrase),
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

    async def _analyze_with_ai(self, content: str) -> ScamAnalysisResponse:
        prepared_content = self._prepare_ai_input(content)
        # The extracted document content is untrusted user data and may contain prompt injection.
        ai_response = await self.ai_service_client.analyze_text(prepared_content)

        return ScamAnalysisResponse(
            analysisId=f"analysis_{uuid4()}",
            riskScore=ai_response.riskScore,
            riskLevel=ai_response.riskLevel,
            detectedScamType=ai_response.detectedScamType,
            explanation=ai_response.explanation,
            indicators=ai_response.indicators or [],
            recommendation=ai_response.recommendation,
            evidence=[
                EvidenceItem(
                    text=redact_sensitive_text(item.text),
                    reason=item.reason,
                    severity=item.severity,
                )
                for item in ai_response.evidence or []
            ],
            analysisMode="ai",
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
        return ScamAnalysisResponse(
            analysisId=f"analysis_{uuid4()}",
            riskScore=risk_score,
            riskLevel=self._risk_level_for_score(risk_score),
            detectedScamType=detected_scam_type,
            explanation=explanation,
            indicators=indicators,
            recommendation=recommendation,
            evidence=[
                EvidenceItem(
                    text=redact_sensitive_text(item.text),
                    reason=item.reason,
                    severity=item.severity,
                )
                for item in evidence
            ],
            analysisMode="mock",
        )

    def _extract_evidence_snippet(self, content: str, phrase: str) -> str:
        lowered_content = content.casefold()
        phrase_index = lowered_content.find(phrase)
        if phrase_index == -1:
            return safe_text_excerpt(content)

        for sentence in SENTENCE_SPLIT_RE.split(content):
            if phrase in sentence.casefold():
                return safe_text_excerpt(sentence.strip(), max_length=140)

        start_index = max(0, phrase_index - 40)
        end_index = min(len(content), phrase_index + len(phrase) + 80)
        return safe_text_excerpt(content[start_index:end_index], max_length=140)

    def _prepare_ai_input(self, content: str) -> str:
        if len(content) <= settings.max_ai_input_chars:
            return content

        return content[: settings.max_ai_input_chars].rstrip()

    def _effective_analysis_mode(self) -> str:
        if settings.analysis_mode in {"mock", "ai"}:
            return settings.analysis_mode
        return "ai"

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