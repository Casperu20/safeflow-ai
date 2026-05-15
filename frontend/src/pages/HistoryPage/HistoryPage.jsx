import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { HistoryItem } from "../../components/history/HistoryItem/HistoryItem.jsx";
import { useAuth } from "../../context/AuthContext.jsx";
import { getApiErrorMessage } from "../../services/apiClient.js";
import {
  getHistory,
  getHistoryItem,
  normalizeHistoryItemToResult,
} from "../../services/historyService.js";
import { ROUTES } from "../../constants/routes.js";
import { saveAnalysisResult } from "../../utils/storage.js";
import "./HistoryPage.css";

export function HistoryPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isInitializing } = useAuth();
  const [historyItems, setHistoryItems] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingMessage, setLoadingMessage] = useState("Loading history...");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isInitializing) {
      return;
    }

    if (!isAuthenticated) {
      navigate(ROUTES.LOGIN);
      return;
    }

    let isMounted = true;

    async function loadHistory() {
      setErrorMessage("");
      setLoadingMessage("Loading history...");
      setIsLoading(true);

      try {
        const payload = await getHistory();
        if (isMounted) {
          setHistoryItems(payload.items || []);
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(
            getApiErrorMessage(error, "Could not load your analysis history."),
          );
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
  }, [isAuthenticated, isInitializing, navigate]);

  async function handleOpenHistoryItem(analysisId) {
    setErrorMessage("");
    setLoadingMessage("Opening analysis...");
    setIsLoading(true);

    try {
      const item = await getHistoryItem(analysisId);
      saveAnalysisResult(normalizeHistoryItemToResult(item));
      navigate(ROUTES.RESULT);
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, "Could not open this history item."),
      );
    } finally {
      setIsLoading(false);
    }
  }

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
          {!isLoading && historyItems.length === 0 && (
            <p className="history-page__empty">
              No saved analyses yet. Sign in, run an analysis, and it will appear here.
            </p>
          )}
          <div className="history-page__list">
            {historyItems.map((item) => (
              <HistoryItem
                key={item.analysisId}
                item={item}
                disabled={isLoading}
                onOpen={handleOpenHistoryItem}
              />
            ))}
          </div>
        </div>
      </PageContainer>
      {(isInitializing || isLoading) && <LoadingOverlay message={loadingMessage} />}
    </>
  );
}
