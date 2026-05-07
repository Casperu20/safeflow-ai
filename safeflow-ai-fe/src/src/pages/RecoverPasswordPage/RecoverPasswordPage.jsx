import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ROUTES } from "../../constants/routes.js";
import backIcon from "../../assets/images/ArrowBack.png";
import loginIcon from "../../assets/images/Login.png";
import "./RecoverPasswordPage.css";

export function RecoverPasswordPage() {
  const navigate = useNavigate();

  return (
    <PageContainer>
      <div className="auth-page">
        <Logo size="large" />
        <h1>SafeFlow</h1>
        <h2 className="auth-page__subtitle">Enter the account's mail below.<br />If the account exists, a code will be sent</h2>
        <AuthCard>
          <AuthInput placeholder="Mail" type="email" />
          <div className="auth-page__actions">
            <button type="button" onClick={() => navigate(ROUTES.LOGIN)}><img src={backIcon} alt="Back icon" className="auth-page__icon" /></button>
            <button type="button" onClick={() => navigate(ROUTES.LOGIN)}><img src={loginIcon} alt="Login icon" className="auth-page__icon" /></button>
          </div>
        </AuthCard>
      </div>
    </PageContainer>
  );
}
