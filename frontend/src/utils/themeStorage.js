const THEME_STORAGE_KEY = "safeflow_theme";

export function getStoredTheme() {
  return localStorage.getItem(THEME_STORAGE_KEY);
}

export function saveTheme(theme) {
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}
