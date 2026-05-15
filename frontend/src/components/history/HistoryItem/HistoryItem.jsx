import { formatDate } from "../../../utils/formatDate.js";
import "./HistoryItem.css";

const RISK_LABELS = {
  safe: "Safe",
  medium: "Medium",
  unsafe: "Unsafe",
};

export function HistoryItem({ item }) {
  return (
    <article className="history-item">
      <div className="history-item__content">
        <h2 className="history-item__title">{item.title}</h2>
        <p className="history-item__date">{formatDate(item.analyzedAt)}</p>
      </div>

      <span className={`history-item__badge history-item__badge--${item.riskLevel}`}>
        {RISK_LABELS[item.riskLevel] || "Medium"}
      </span>
    </article>
  );
}