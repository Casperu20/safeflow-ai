import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { HistoryItem } from "../../components/history/HistoryItem/HistoryItem.jsx";
import "./HistoryPage.css";

const mockHistory = [
  { id: "1", title: "Suspicious email analysis", score: 85, riskLevel: "unsafe", createdAt: "2026-04-22" },
  { id: "2", title: "Invoice PDF analysis", score: 50, riskLevel: "medium", createdAt: "2026-04-22" },
  { id: "3", title: "Message check", score: 12, riskLevel: "safe", createdAt: "2026-04-22" }
];

export function HistoryPage() {
  return (
    <PageContainer>
      <div className="history-page">
        <Logo />
        <h1>SafeFlow</h1>
        <div className="history-page__list">
          {mockHistory.map((item) => <HistoryItem key={item.id} item={item} />)}
        </div>
      </div>
    </PageContainer>
  );
}
