import "./HistoryItem.css";

function formatHistoryDate(value) {
  return new Date(value).toLocaleDateString();
}

function buildHistoryTitle(item) {
  if (item.detectedScamType) {
    return item.detectedScamType;
  }

  return `${item.inputType.toUpperCase()} analysis`;
}

export function HistoryItem({ item, onOpen, disabled = false }) {
  return (
    <button
      className="history-item"
      type="button"
      onClick={() => onOpen(item.analysisId)}
      disabled={disabled}
    >
      <span className="history-item__content">
        <strong className="history-item__title">
          {buildHistoryTitle(item)}
        </strong>
        <span className="history-item__preview">
          {item.inputPreview || "No preview available."}
        </span>
      </span>
      <span className="history-item__meta">
        <span className="history-item__date">
          {formatHistoryDate(item.createdAt)}
        </span>
        <strong>{item.riskScore}%</strong>
      </span>
    </button>
  );
}
