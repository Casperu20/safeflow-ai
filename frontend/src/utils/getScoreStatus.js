export function getScoreStatus(score) {
  if (score > 80) {
    return "safe";
  }

  if (score >= 50) {
    return "medium";
  }

  return "unsafe";
}