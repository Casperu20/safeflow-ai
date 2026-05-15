import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { useAuth } from "../../context/AuthContext.jsx";
import { getApiErrorMessage } from "../../services/apiClient.js";
import { ROUTES } from "../../constants/routes.js";
import newUserIcon from "../../assets/images/Userplus.png";
import loginIcon from "../../assets/images/Login.png";
import "./LoginPage.css";

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isInitializing, login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [touchedFields, setTouchedFields] = useState({
    email: false,
    password: false,
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!isInitializing && isAuthenticated) {
      navigate(ROUTES.HOME);
    }
  }, [isAuthenticated, isInitializing, navigate]);

  const emailError =
    touchedFields.email && !email.trim() ? "Email is required." : "";

  const passwordError =
    touchedFields.password && !password.trim() ? "Password is required." : "";

  const isFormValid = email.trim() && password.trim();
  const isBusy = isSubmitting || isInitializing;

  function handleBlur(fieldName) {
    setTouchedFields((current) => ({
      ...current,
      [fieldName]: true,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setTouchedFields({
      email: true,
      password: true,
    });

    setErrorMessage("");

    if (!isFormValid || isBusy) {
      setErrorMessage("Please complete all required fields.");
      return;
    }

    setIsSubmitting(true);

    try {
      await login({ email, password });
      navigate(ROUTES.HOME);
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, "Login failed. Please try again."),
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

          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />

          <AuthCard>
            <form className="login-form" onSubmit={handleSubmit} noValidate>
              <div className="login-form__field">
                <AuthInput
                  placeholder="Email"
                  type="email"
                  value={email}
                  disabled={isBusy}
                  onChange={(event) => setEmail(event.target.value)}
                  onBlur={() => handleBlur("email")}
                  aria-invalid={Boolean(emailError)}
                />

                {emailError && (
                  <p className="login-form__error">{emailError}</p>
                )}
              </div>

              <div className="login-form__field">
                <AuthInput
                  placeholder="Password"
                  type="password"
                  value={password}
                  disabled={isBusy}
                  onChange={(event) => setPassword(event.target.value)}
                  onBlur={() => handleBlur("password")}
                  aria-invalid={Boolean(passwordError)}
                />

                {passwordError && (
                  <p className="login-form__error">{passwordError}</p>
                )}
              </div>

              <button
                className="auth-page__link"
                type="button"
                disabled={isBusy}
                onClick={() => navigate(ROUTES.RECOVER_PASSWORD)}
              >
                Forgot password?
              </button>

              <div className="auth-page__actions">
                <button
                  type="button"
                  disabled={isBusy}
                  onClick={() => navigate(ROUTES.SIGN_UP)}
                >
                  <img src={newUserIcon} alt="New user icon" />
                </button>

                <button type="submit" disabled={!isFormValid || isBusy}>
                  <img src={loginIcon} alt="Login icon" />
                </button>
              </div>
            </form>
          </AuthCard>
        </div>
      </PageContainer>

      {isBusy && <LoadingOverlay message="Logging in..." />}
    </>
  );
}
