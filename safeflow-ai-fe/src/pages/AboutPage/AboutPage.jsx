import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import "./AboutPage.css";

export function AboutPage() {
  return (
    <PageContainer>
      <div className="info-page">
        <Logo />
        <h1>SafeFlow</h1>
        <section className="info-page__content">
          SafeFlow helps users identify possible scams in payment-related messages, documents, and screenshots before they take action. The app returns a risk score and an explanation of detected indicators.
        </section>
      </div>
    </PageContainer>
  );
}
