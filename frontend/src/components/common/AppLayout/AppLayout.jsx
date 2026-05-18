import { useState } from "react";
import { Header } from "../Header/Header.jsx";
import { Sidebar } from "../Sidebar/Sidebar.jsx";
import { useTheme } from "../../../hooks/useTheme.js";
import "./AppLayout.css";

export function AppLayout({ children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="app-layout">
      <Header
        onMenuClick={() => setIsSidebarOpen((current) => !current)}
        isDarkMode={isDarkMode}
        onThemeToggle={toggleTheme}
      />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="app-layout__main">{children}</main>
    </div>
  );
}
