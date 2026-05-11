import "./HistoryItem.css";

export function HistoryItem({ item }) {
  return (
    <article className="history-item">
      <span>{item.title}</span>
      <strong>{item.score}%</strong>
    </article>
  );
}
