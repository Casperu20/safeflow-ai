import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ROUTES } from "../../constants/routes.js";
import newUserIcon from "../../assets/images/Userplus.png";
import loginIcon from "../../assets/images/Login.png";
import "./LoginPage.css";

export function LoginPage() {
  const navigate = useNavigate();

  return (
    <PageContainer>
      <div className="auth-page">
        <Logo size="large" />
        <h1>SafeFlow</h1>
        <AuthCard>
          <AuthInput placeholder="Username" />
          <AuthInput placeholder="Password" type="password" />
          <button className="auth-page__link" type="button" onClick={() => navigate(ROUTES.RECOVER_PASSWORD)}>Forgot password?</button>
          <div className="auth-page__actions">
            <button type="button" onClick={() => navigate(ROUTES.SIGN_UP)}><img src={newUserIcon} alt="New user icon" className="auth-page__icon" /></button>
            <button type="button" onClick={() => navigate(ROUTES.HOME)}><img src={loginIcon} alt="Login icon" className="auth-page__icon" /></button>
          </div>
        </AuthCard>
      </div>
    </PageContainer>
  );
}
