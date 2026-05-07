import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { ROUTES } from "../../constants/routes.js";
import newUserIcon from "../../assets/images/Userplus.png";
import loginIcon from "../../assets/images/Login.png";
import "./LoginPage.css";

export function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [touchedFields, setTouchedFields] = useState({
    username: false,
    password: false,
  });
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const usernameError =
    touchedFields.username && !username.trim()
      ? "Username is required."
      : "";

  const passwordError =
    touchedFields.password && !password.trim()
      ? "Password is required."
      : "";

  const isFormValid = username.trim() && password.trim();

  function handleBlur(fieldName) {
    setTouchedFields((current) => ({
      ...current,
      [fieldName]: true,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setTouchedFields({
      username: true,
      password: true,
    });

    setErrorMessage("");

    if (!isFormValid) {
      setErrorMessage("Please complete all required fields.");
      return;
    }

    setIsSubmitting(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      navigate(ROUTES.HOME);
    } catch {
      setErrorMessage("Login failed. Please try again.");
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
                  placeholder="Username"
                  value={username}
                  disabled={isSubmitting}
                  onChange={(event) => setUsername(event.target.value)}
                  onBlur={() => handleBlur("username")}
                  aria-invalid={Boolean(usernameError)}
                />

                {usernameError && (
                  <p className="login-form__error">{usernameError}</p>
                )}
              </div>

              <div className="login-form__field">
                <AuthInput
                  placeholder="Password"
                  type="password"
                  value={password}
                  disabled={isSubmitting}
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
                disabled={isSubmitting}
                onClick={() => navigate(ROUTES.RECOVER_PASSWORD)}
              >
                Forgot password?
              </button>

              <div className="auth-page__actions">
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => navigate(ROUTES.SIGN_UP)}
                >
                  <img src={newUserIcon} alt="New user icon" />
                </button>

                <button
                  type="submit"
                  disabled={!isFormValid || isSubmitting}
                >
                  <img src={loginIcon} alt="Login icon" />
                </button>
              </div>
            </form>
          </AuthCard>
        </div>
      </PageContainer>

      {isSubmitting && <LoadingOverlay message="Logging in..." />}
    </>
  );
}
