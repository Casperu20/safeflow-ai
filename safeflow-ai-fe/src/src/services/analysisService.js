import { apiClient } from "./apiClient.js";

const USE_MOCK = true;

export async function analyzeInput(payload) {
  if (USE_MOCK) {
    return analyzeInputMock(payload);
  }

  if (payload.inputType === "text") {
    return analyzeText(payload.content);
  }

  if (payload.inputType === "pdf") {
    return analyzePdf(payload.file);
  }

  if (payload.inputType === "image") {
    return analyzeImage(payload.file);
  }

  throw new Error("Unsupported input type.");
}

async function analyzeText(content) {
  const response = await apiClient.post("/scam-analysis/text", {
    content,
  });

  return response.data;
}

async function analyzePdf(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/scam-analysis/pdf", formData);

  return response.data;
}

async function analyzeImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post("/scam-analysis/image", formData);

  return response.data;
}

async function analyzeInputMock(payload) {
  await new Promise((resolve) => setTimeout(resolve, 600));

  if (payload.inputType === "text" && payload.content.toLowerCase().includes("urgent")) {
    return {
      analysisId: crypto.randomUUID(),
      score: 25,
      riskLevel: "unsafe",
      message:
        "The message contains urgency and pressure language, which are common scam indicators. Verify the sender through an official channel before taking action.",
      detectedScamType: "Urgency scam",
      indicators: ["Urgent language", "Pressure to act quickly"]
    };
  }

  if (payload.inputType === "pdf") {
    return {
      analysisId: crypto.randomUUID(),
      score: 52,
      riskLevel: "medium",
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
      riskLevel: "unsafe",
      message:
        "The uploaded image appears to contain a payment request. Verify the sender and payment details before taking action.",
      detectedScamType: "Suspicious payment screenshot",
      indicators: ["Payment request", "External verification needed"],
    };
  }

  return {
    analysisId: crypto.randomUUID(),
    score: 92,
    riskLevel: "safe",
    message:
      "No strong scam indicators were detected in the submitted content. Continue to verify payment details before proceeding.",
    indicators: [],
  };
}