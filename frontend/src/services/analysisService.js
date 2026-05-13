import { apiClient } from "./apiClient.js";

const USE_MOCK = false;

export async function analyzeInput(payload) {
  if (USE_MOCK) {
    return analyzeInputMock(payload);
  }

  if (payload.inputType === "text") {
    return analyzeText(payload.content);
  }

  if (payload.inputType === "pdf" || payload.inputType === "image") {
    return analyzeFile(payload.file, payload.inputType);
  }

  throw new Error("Unsupported input type.");
}

async function analyzeText(content) {
  const response = await apiClient.post("/scam-analysis", {
    inputType: "text",
    content,
  });

  return normalizeAnalysisResponse(response.data);
}

async function analyzeFile(file, inputType) {
  const formData = new FormData();

  formData.append("inputType", inputType);
  formData.append("file", file);

  const response = await apiClient.post("/scam-analysis", formData);

  return normalizeAnalysisResponse(response.data);
}

export function getApiErrorMessage(error, fallbackMessage) {
  const responseData = error?.response?.data;

  if (
    typeof responseData?.message === "string" &&
    responseData.message.trim()
  ) {
    const detailMessages = Object.values(responseData.details || {})
      .flat()
      .filter((value) => typeof value === "string" && value.trim());

    if (detailMessages.length > 0) {
      return `${responseData.message} ${detailMessages[0]}`;
    }

    return responseData.message;
  }

  if (error?.code === "ERR_NETWORK") {
    return "Cannot reach the backend service. Check that the backend is running on http://127.0.0.1:8000.";
  }

  return fallbackMessage;
}

function normalizeAnalysisResponse(data) {
  const explanation = data.explanation || "";
  const recommendation = data.recommendation || "";
  const riskScore = data.riskScore ?? 0;
  const normalizedRiskLevel = normalizeBackendRiskLevel(
    data.riskLevel,
    riskScore,
  );

  return {
    analysisId: data.analysisId || crypto.randomUUID(),
    score: riskScore,
    riskLevel: normalizedRiskLevel,
    uiRiskLevel: mapBackendRiskLevelToUi(normalizedRiskLevel),
    message: buildAnalysisMessage(explanation, recommendation),
    detectedScamType: data.detectedScamType,
    indicators: data.indicators || [],
    evidence: data.evidence || [],
    analysisMode: data.analysisMode,
  };
}

function normalizeBackendRiskLevel(riskLevel, riskScore) {
  if (riskLevel === "low" || riskLevel === "medium" || riskLevel === "high") {
    return riskLevel;
  }

  if (riskScore >= 70) {
    return "high";
  }

  if (riskScore >= 40) {
    return "medium";
  }

  return "low";
}

function mapBackendRiskLevelToUi(riskLevel) {
  if (riskLevel === "low") {
    return "safe";
  }

  if (riskLevel === "medium") {
    return "medium";
  }

  return "unsafe";
}

function buildAnalysisMessage(explanation, recommendation) {
  if (explanation && recommendation) {
    return `${explanation}\n\nRecommendation: ${recommendation}`;
  }

  if (explanation) {
    return explanation;
  }

  if (recommendation) {
    return `Recommendation: ${recommendation}`;
  }

  return "No explanation was provided.";
}

async function analyzeInputMock(payload) {
  await new Promise((resolve) => setTimeout(resolve, 600));

  if (
    payload.inputType === "text" &&
    payload.content.toLowerCase().includes("urgent")
  ) {
    return {
      analysisId: crypto.randomUUID(),
      score: 25,
      message:
        "The message contains urgency and pressure language, which are common scam indicators. Verify the sender through an official channel before taking action.",
      detectedScamType: "Urgency scam",
      indicators: ["Urgent language", "Pressure to act quickly"],
    };
  }

  if (payload.inputType === "pdf") {
    return {
      analysisId: crypto.randomUUID(),
      score: 65,
      message:
        "The uploaded PDF contains payment-related content. Some elements may require verification before proceeding.",
      detectedScamType: "Payment document review",
      indicators: ["Payment-related document", "Requires manual verification"],
    };
  }

  if (payload.inputType === "image") {
    return {
      analysisId: crypto.randomUUID(),
      score: 35,
      message:
        "The uploaded image appears to contain a payment request. Verify the sender and payment details before taking action.",
      detectedScamType: "Suspicious payment screenshot",
      indicators: ["Payment request", "External verification needed"],
    };
  }

  return {
    analysisId: crypto.randomUUID(),
    score: 92,
    message:
      "No strong scam indicators were detected in the submitted content. Continue to verify payment details before proceeding.",
    indicators: [],
  };
}
