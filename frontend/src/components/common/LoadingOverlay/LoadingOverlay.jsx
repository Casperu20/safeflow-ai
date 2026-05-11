import "./LoadingOverlay.css";

export function LoadingOverlay({ message = "Analyzing content..." }) {
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <div className="loading-overlay__card">
        <div className="loading-overlay__spinner" />
        <p className="loading-overlay__message">{message}</p>
      </div>
    </div>
  );
}