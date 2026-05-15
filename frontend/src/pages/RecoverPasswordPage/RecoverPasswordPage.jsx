import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { getApiErrorMessage } from "../../services/apiClient.js";
import { recoverPassword } from "../../services/authService.js";
import { ROUTES } from "../../constants/routes.js";
import backIcon from "../../assets/images/ArrowBack.png";
import loginIcon from "../../assets/images/Login.png";
import "./RecoverPasswordPage.css";

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function RecoverPasswordPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [isEmailTouched, setIsEmailTouched] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const emailError =
    isEmailTouched && !email.trim()
      ? "Email is required."
      : isEmailTouched && !isValidEmail(email)
        ? "Please enter a valid email address."
        : "";

  const isFormValid = email.trim() && isValidEmail(email);

  async function handleSubmit(event) {
    event.preventDefault();

    setIsEmailTouched(true);
    setErrorMessage("");
    setSuccessMessage("");

    if (!isFormValid) {
      setErrorMessage("Please enter a valid email address.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await recoverPassword({ email });
      setSuccessMessage(
        response.message ||
          "If an account exists for this email, a recovery code will be sent.",
      );
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          "Password recovery failed. Please try again.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <PageContainer>
        <div className="auth-page">
          <Logo size="large" />

          <h1>SafeFlow</h1>

          <p className="auth-page__subtitle">
            Enter the account's mail below. If the account exists, a code will
            be sent.
          </p>

          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />

          {successMessage && (
            <div className="recover-password-page__success" role="status">
              {successMessage}
            </div>
          )}

          <AuthCard>
            <form
              className="recover-password-form"
              onSubmit={handleSubmit}
              noValidate
            >
              <div className="recover-password-form__field">
                <AuthInput
                  placeholder="Mail"
                  type="email"
                  value={email}
                  disabled={isSubmitting}
                  onChange={(event) => setEmail(event.target.value)}
                  onBlur={() => setIsEmailTouched(true)}
                  aria-invalid={Boolean(emailError)}
                />

                {emailError && (
                  <p className="recover-password-form__error">{emailError}</p>
                )}
              </div>

              <div className="auth-page__actions">
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => navigate(ROUTES.LOGIN)}
                >
                  <img src={backIcon} alt="Back" className="auth-page__icon" />
                </button>

                <button type="submit" disabled={!isFormValid || isSubmitting}>
                  <img
                    src={loginIcon}
                    alt="Submit"
                    className="auth-page__icon"
                  />
                </button>
              </div>
            </form>
          </AuthCard>
        </div>
      </PageContainer>

      {isSubmitting && <LoadingOverlay message="Sending recovery request..." />}
    </>
  );
}
