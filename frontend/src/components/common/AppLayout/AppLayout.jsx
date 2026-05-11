import { useState } from "react";
import { Header } from "../Header/Header.jsx";
import { Sidebar } from "../Sidebar/Sidebar.jsx";
import "./AppLayout.css";

export function AppLayout({ children }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="app-layout">
      <Header onMenuClick={() => setIsSidebarOpen((current) => !current)} />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="app-layout__main">{children}</main>
    </div>
  );
}
