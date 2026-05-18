import { apiClient } from "./apiClient.js";
import { normalizeAnalysisResponse } from "./analysisService.js";

export async function getHistory(params = {}) {
  const response = await apiClient.get("/analysis-history", { params });
  return response.data;
}

export async function getHistoryItem(analysisId) {
  const response = await apiClient.get(`/analysis-history/${analysisId}`);
  return response.data;
}

export async function deleteHistoryItem(analysisId) {
  const response = await apiClient.delete(`/analysis-history/${analysisId}`);
  return response.data;
}

export function normalizeHistoryItemToResult(item) {
  return normalizeAnalysisResponse({
    analysisId: item.analysisId,
    riskScore: item.riskScore,
    riskLevel: item.riskLevel,
    explanation: item.explanation,
    recommendation: item.recommendation,
    detectedScamType: item.detectedScamType,
    indicators: item.indicators,
    evidence: item.evidence,
    analysisMode: item.analysisMode,
  });
}
