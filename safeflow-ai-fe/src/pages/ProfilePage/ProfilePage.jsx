import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import trashIcon from "../../assets/images/Trash21.png";
import "./ProfilePage.css";

export function ProfilePage() {
  return (
    <PageContainer>
      <div className="auth-page">
        <Logo />
        <h1>SafeFlow</h1>
        <AuthCard>
          <AuthInput value="Username" readOnly />
          <AuthInput value="Mail" readOnly />
          <AuthInput value="Date Joined" readOnly />
          <button className="auth-page__link" type="button"><img src={trashIcon} alt="Trash icon" className="auth-page__icon" /></button>
        </AuthCard>
      </div>
    </PageContainer>
  );
}
