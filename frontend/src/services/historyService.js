import { apiClient } from "./apiClient.js";

export async function getHistory() {
  const response = await apiClient.get("/history");

  return response.data.map(normalizeHistoryItem);
}

function normalizeHistoryItem(item) {
  return {
    id: item.id || item.analysisId || crypto.randomUUID(),
    title: item.title || item.detectedScamType || "Scam analysis",
    analyzedAt: item.analyzedAt || item.createdAt || item.date || "",
    riskLevel: normalizeRiskLevel(item.riskLevel),
  };
}

function normalizeRiskLevel(riskLevel) {
  if (!riskLevel) {
    return "medium";
  }

  const normalizedRiskLevel = riskLevel.toLowerCase();

  if (normalizedRiskLevel === "low" || normalizedRiskLevel === "safe") {
    return "safe";
  }

  if (normalizedRiskLevel === "medium") {
    return "medium";
  }

  if (normalizedRiskLevel === "high" || normalizedRiskLevel === "unsafe") {
    return "unsafe";
  }

  return "medium";
}