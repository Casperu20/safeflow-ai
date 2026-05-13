import "./ThemeToggle.css";

export function ThemeToggle({ isDarkMode, onToggle }) {
  return (
    <button
      className={`theme-toggle ${isDarkMode ? "theme-toggle--dark" : ""}`}
      type="button"
      onClick={onToggle}
      aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
      aria-pressed={isDarkMode}
    >
      <span className="theme-toggle__track">
        <span className="theme-toggle__thumb" />
      </span>
    </button>
  );
}
