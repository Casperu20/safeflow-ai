import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AnalysisInputPanel } from "../../components/analysis/AnalysisInputPanel/AnalysisInputPanel.jsx";
import { analyzeInput } from "../../services/analysisService.js";
import { ROUTES } from "../../constants/routes.js";
import { saveAnalysisResult } from "../../utils/storage.js";
import { validateFile } from "../../utils/validateFile.js";
import fileIcon from "../../assets/images/File.png";
import cameraIcon from "../../assets/images/Camera.png";
import "./HomePage.css";

export function HomePage() {
  const navigate = useNavigate();
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmitText() {
    if (!text.trim()) return;

    setIsSubmitting(true);

    try {
      const result = await analyzeInput({ inputType: "text", content: text });
      saveAnalysisResult(result);
      navigate(ROUTES.RESULT);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleFileChange(event, inputType) {
    const file = event.target.files?.[0];
    if (!file) return;

    const validation = validateFile(file, inputType);
    if (!validation.isValid) {
      alert(validation.message);
      event.target.value = "";
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await analyzeInput({ inputType, file });
      saveAnalysisResult(result);
      navigate(ROUTES.RESULT);
    } finally {
      setIsSubmitting(false);
      event.target.value = "";
    }
  }

  return (
    <PageContainer>
      <div className="home-page">
        <Logo />
        <h1 className="home-page__title">SafeFlow</h1>
        <p className="home-page__subtitle">Your partner in detecting scams</p>
        <AnalysisInputPanel value={text} isSubmitting={isSubmitting} onChange={setText} onClear={() => setText("")} onSubmit={handleSubmitText} />
        <p className="home-page__upload-title">Or upload...</p>
        <div className="home-page__upload-actions">
          <label className="home-page__upload-button">
            <img src={fileIcon} alt="File icon" className="home-page__upload-icon" />
            PDF
            <input type="file" accept="application/pdf" hidden onChange={(event) => handleFileChange(event, "pdf")} />
          </label>
          <label className="home-page__upload-button">
            Image
            <img src={cameraIcon} alt="Camera icon" className="home-page__upload-icon" />
            <input type="file" accept="image/png,image/jpeg,image/webp" hidden onChange={(event) => handleFileChange(event, "image")} />
          </label>
        </div>
      </div>
    </PageContainer>
  );
}
