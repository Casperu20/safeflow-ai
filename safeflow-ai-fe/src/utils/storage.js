const ANALYSIS_RESULT_KEY = "safeflow_analysis_result";

export function saveAnalysisResult(result) {
  sessionStorage.setItem(ANALYSIS_RESULT_KEY, JSON.stringify(result));
}

export function getAnalysisResult() {
  const value = sessionStorage.getItem(ANALYSIS_RESULT_KEY);
  return value ? JSON.parse(value) : null;
}

export function clearAnalysisResult() {
  sessionStorage.removeItem(ANALYSIS_RESULT_KEY);
}
