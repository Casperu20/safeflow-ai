import { useEffect, useState } from "react";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { HistoryItem } from "../../components/history/HistoryItem/HistoryItem.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { getHistory } from "../../services/historyService.js";
import "./HistoryPage.css";

export function HistoryPage() {
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadHistory() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await getHistory();

        if (isMounted) {
          setHistoryItems(data);
        }
      } catch (error) {
        console.error("History loading failed:", error);

        if (isMounted) {
          setErrorMessage("History could not be loaded. Please try again.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <>
      <PageContainer>
        <div className="history-page">
          <Logo />

          <h1>SafeFlow</h1>

          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />

          {!isLoading && !errorMessage && historyItems.length === 0 && (
            <p className="history-page__empty">
              No analysis history available yet.
            </p>
          )}

          {!isLoading && historyItems.length > 0 && (
            <div className="history-page__list">
              {historyItems.map((item) => (
                <HistoryItem key={item.id} item={item} />
              ))}
            </div>
          )}
        </div>
      </PageContainer>

      {isLoading && <LoadingOverlay message="Loading history..." />}
    </>
  );
}