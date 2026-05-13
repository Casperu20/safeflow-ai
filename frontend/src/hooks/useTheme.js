import { useEffect, useState } from "react";
import { getStoredTheme, saveTheme } from "../utils/themeStorage.js";

const DEFAULT_THEME = "light";

export function useTheme() {
  const [theme, setTheme] = useState(() => {
    return getStoredTheme() || DEFAULT_THEME;
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    saveTheme(theme);
  }, [theme]);

  function toggleTheme() {
    setTheme((currentTheme) => {
      return currentTheme === "light" ? "dark" : "light";
    });
  }

  return {
    theme,
    toggleTheme,
    isDarkMode: theme === "dark",
  };
}