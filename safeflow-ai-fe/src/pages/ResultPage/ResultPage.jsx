import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { ResultScore } from "../../components/analysis/ResultScore/ResultScore.jsx";
import { ResultMessage } from "../../components/analysis/ResultMessage/ResultMessage.jsx";
import { ROUTES } from "../../constants/routes.js";
import { getAnalysisResult } from "../../utils/storage.js";
import thumbsUpIcon from "../../assets/images/Thumbsup.png";
import thumbsDownIcon from "../../assets/images/Thumbsdown.png";
import crossIcon from "../../assets/images/Crosshair.png";
import fileIcon from "../../assets/images/File.png";
import cameraIcon from "../../assets/images/Camera.png";
import arrowIcon from "../../assets/images/ArrowResult.png";
import "./ResultPage.css";

export function ResultPage() {
  const navigate = useNavigate();
  const [result, setResult] = useState(null);

  useEffect(() => {
    const storedResult = getAnalysisResult();
    if (!storedResult) {
      navigate(ROUTES.HOME);
      return;
    }
    setResult(storedResult);
  }, [navigate]);

  if (!result) return null;

  return (
    <PageContainer>
      <div className="result-page">
        <Logo />
        <h1 className="result-page__title">SafeFlow</h1>
        <p className="result-page__subtitle">Your score is:</p>
        <ResultScore score={result.score} riskLevel={result.riskLevel} />
        <div className={`result-page__icon result-page__icon--${result.riskLevel}`}>
          {result.riskLevel === "safe" && <img src={thumbsUpIcon} alt="Thumbs up icon" className="result-page__thumbs-icon" />}
          {result.riskLevel === "medium" && <img src={crossIcon} alt="Cross icon" className="result-page__thumbs-icon" />}
          {result.riskLevel === "unsafe" && <img src={thumbsDownIcon} alt="Thumbs down icon" className="result-page__thumbs-icon" />}
        </div>
        <div className="result-page__content">
          <aside className="result-page__side-actions">
            <button type="button" onClick={() => navigate(ROUTES.HOME)}><img src={arrowIcon} alt="Arrow icon" className="result-page__side-icon" /></button>
            <button type="button">
              <img src={cameraIcon} alt="Camera icon" className="result-page__side-icon" />
            </button>
            <button type="button">
              <img src={fileIcon} alt="File icon" className="result-page__side-icon" />
            </button>
          </aside>
          <ResultMessage message={result.message} />
        </div>
      </div>
    </PageContainer>
  );
}
