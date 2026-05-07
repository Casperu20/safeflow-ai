import { apiClient } from "./apiClient.js";

const USE_MOCK = true;

export async function analyzeInput(payload) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 600));

    if (payload.inputType === "text" && payload.content.toLowerCase().includes("urgent")) {
      return {
        analysisId: crypto.randomUUID(),
        score: 90,
        riskLevel: "unsafe",
        message: "The message contains urgency and pressure language, which are common scam indicators. Verify the sender through an official channel before taking action.",
        detectedScamType: "Urgency scam",
        indicators: ["Urgent language", "Pressure to act quickly"]
      };
    }

    if (payload.inputType === "pdf") {
      return {
        analysisId: crypto.randomUUID(),
        score: 52,
        riskLevel: "medium",
        message: "The uploaded PDF contains payment-related content. Some elements may require verification before proceeding.",
        detectedScamType: "Payment document review",
        indicators: ["Payment-related document", "Requires manual verification"]
      };
    }

    if (payload.inputType === "image") {
      return {
        analysisId: crypto.randomUUID(),
        score: 72,
        riskLevel: "unsafe",
        message: "The uploaded image appears to contain a payment request. Verify the sender and payment details before taking action.",
        detectedScamType: "Suspicious payment screenshot",
        indicators: ["Payment request", "External verification needed"]
      };
    }

    return {
      analysisId: crypto.randomUUID(),
      score: 15,
      riskLevel: "safe",
      message: "No strong scam indicators were detected in the submitted content. Continue to verify payment details before proceeding.",
      indicators: []
    };
  }

  if (payload.inputType === "text") {
    const response = await apiClient.post("/scam-analysis", payload);
    return response.data;
  }

  const formData = new FormData();
  formData.append("inputType", payload.inputType);
  formData.append("file", payload.file);

  const response = await apiClient.post("/scam-analysis", formData);
  return response.data;
}
