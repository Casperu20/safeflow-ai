import "./ErrorBanner.css";

export function ErrorBanner({ message, onClose }) {
  if (!message) {
    return null;
  }

  return (
    <div className="error-banner" role="alert">
      <p className="error-banner__message">{message}</p>

      {onClose && (
        <button
          className="error-banner__close"
          type="button"
          onClick={onClose}
          aria-label="Close error message"
        >
          ×
        </button>
      )}
    </div>
  );
}