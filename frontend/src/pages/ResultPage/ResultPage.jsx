import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { ResultScore } from "../../components/analysis/ResultScore/ResultScore.jsx";
import { ResultMessage } from "../../components/analysis/ResultMessage/ResultMessage.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import {
  analyzeInput,
  getApiErrorMessage,
} from "../../services/analysisService.js";
import { ROUTES } from "../../constants/routes.js";
import { getAnalysisResult, saveAnalysisResult } from "../../utils/storage.js";
import { validateFile } from "../../utils/validateFile.js";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { getScoreStatus } from "../../utils/getScoreStatus.js";
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Analyzing content...");
  const imageInputRef = useRef(null);
  const pdfInputRef = useRef(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const storedResult = getAnalysisResult();

    if (!storedResult) {
      navigate(ROUTES.HOME);
      return;
    }

    setResult(storedResult);
  }, [navigate]);

  async function handleFileChange(event, inputType) {
    const file = event.target.files?.[0];

    if (!file || isSubmitting) return;

    setErrorMessage("");

    const validation = validateFile(file, inputType);

    if (!validation.isValid) {
      setErrorMessage(validation.message);
      event.target.value = "";
      return;
    }

    setLoadingMessage(
      inputType === "pdf" ? "Analyzing PDF..." : "Analyzing image...",
    );
    setIsSubmitting(true);

    try {
      const analysisResult = await analyzeInput({ inputType, file });
      saveAnalysisResult(analysisResult);
      setResult(analysisResult);
    } catch (error) {
      console.error("Result page analysis failed:", error);
      setErrorMessage(
        getApiErrorMessage(
          error,
          inputType === "pdf"
            ? "PDF analysis failed. Please upload another PDF or try again."
            : "Image analysis failed. Please upload another image or try again.",
        ),
      );
    } finally {
      setIsSubmitting(false);
      event.target.value = "";
    }
  }

  if (!result) return null;
  const scoreStatus = result.uiRiskLevel || getScoreStatus(result.score);

  return (
    <>
      <PageContainer>
        <div className="result-page">
          <Logo />
          <h1 className="result-page__title">SafeFlow</h1>
          <p className="result-page__subtitle">Risk score:</p>
          <ResultScore score={result.score} riskLevel={scoreStatus} />
          <div
            className={`result-page__icon result-page__icon--${scoreStatus}`}
          >
            {scoreStatus === "safe" && (
              <img
                src={thumbsUpIcon}
                alt="Thumbs up icon"
                className="result-page__thumbs-icon"
              />
            )}
            {scoreStatus === "medium" && (
              <img
                src={crossIcon}
                alt="Cross icon"
                className="result-page__thumbs-icon"
              />
            )}
            {scoreStatus === "unsafe" && (
              <img
                src={thumbsDownIcon}
                alt="Thumbs down icon"
                className="result-page__thumbs-icon"
              />
            )}
          </div>

          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />

          <div className="result-page__content">
            <aside className="result-page__side-actions">
              <button
                type="button"
                onClick={() => navigate(ROUTES.HOME)}
                disabled={isSubmitting}
              >
                <img
                  src={arrowIcon}
                  alt="Arrow icon"
                  className="result-page__arrow-icon"
                />
              </button>

              <button
                className="result-page__upload-action"
                type="button"
                disabled={isSubmitting}
                onClick={() => imageInputRef.current?.click()}
              >
                <img
                  src={cameraIcon}
                  alt="Camera icon"
                  className="result-page__camera-icon"
                />
              </button>

              <input
                ref={imageInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                hidden
                disabled={isSubmitting}
                onChange={(event) => handleFileChange(event, "image")}
              />

              <button
                className="result-page__upload-action"
                type="button"
                disabled={isSubmitting}
                onClick={() => pdfInputRef.current?.click()}
              >
                <img
                  src={fileIcon}
                  alt="File icon"
                  className="result-page__file-icon"
                />
              </button>

              <input
                ref={pdfInputRef}
                type="file"
                accept="application/pdf"
                hidden
                disabled={isSubmitting}
                onChange={(event) => handleFileChange(event, "pdf")}
              />
            </aside>

            <ResultMessage message={result.message} />
          </div>
        </div>
      </PageContainer>

      {isSubmitting && <LoadingOverlay message={loadingMessage} />}
    </>
  );
}
