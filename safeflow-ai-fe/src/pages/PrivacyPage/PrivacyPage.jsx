import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import "./PrivacyPage.css";

export function PrivacyPage() {
  return (
    <PageContainer>
      <div className="info-page">
        <Logo />
        <h1>SafeFlow</h1>
        <section className="info-page__content">
          SafeFlow respects privacy principles and should process submitted content only for scam analysis. AI results may not always be fully accurate, so important payment decisions should be verified through official channels.
        </section>
      </div>
    </PageContainer>
  );
}
