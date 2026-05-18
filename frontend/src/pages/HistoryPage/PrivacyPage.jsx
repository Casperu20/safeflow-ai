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
          SafeFlow respects privacy principles and should process submitted content only for scam analysis. AI results may not always be fully accurate, so important payment decisions should be verified through official channels. By creating an account and submitting content, you acknowledge that SafeFlow may use the submitted content for scam analysis and may share it with third-party AI services for processing as well as storing it for future reference. SafeFlow does not sell or share your personal information with third parties for marketing purposes. For more details, please refer to our full Privacy Policy on our website.
        </section>
      </div>
    </PageContainer>
  );
}
