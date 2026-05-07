import "./ResultScore.css";

export function ResultScore({ score, riskLevel }) {
  return <strong className={`result-score result-score--${riskLevel}`}>{score}%</strong>;
}
