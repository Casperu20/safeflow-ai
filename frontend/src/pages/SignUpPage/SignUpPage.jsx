import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { ROUTES } from "../../constants/routes.js";
import backIcon from "../../assets/images/ArrowBack.png";
import loginIcon from "../../assets/images/Login.png";
import "./SignUpPage.css";

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function SignUpPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [touchedFields, setTouchedFields] = useState({
    username: false,
    email: false,
    password: false,
  });

  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const usernameError =
    touchedFields.username && !username.trim()
      ? "Username is required."
      : "";

  const emailError =
    touchedFields.email && !email.trim()
      ? "Email is required."
      : touchedFields.email && !isValidEmail(email)
        ? "Please enter a valid email address."
        : "";

  const passwordError =
    touchedFields.password && !password
      ? "Password is required."
      : touchedFields.password && password.length < 8
        ? "Password must be at least 8 characters."
        : "";

  const isFormValid =
    username.trim() &&
    email.trim() &&
    isValidEmail(email) &&
    password.length >= 8;

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
      email: true,
      password: true,
    });

    setErrorMessage("");

    if (!isFormValid) {
      setErrorMessage("Please complete all required fields correctly.");
      return;
    }

    setIsSubmitting(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      navigate(ROUTES.HOME);
    } catch {
      setErrorMessage("Sign-up failed. Please try again.");
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
            Sign Up below to become a member
          </p>

          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />

          <AuthCard>
            <form className="sign-up-form" onSubmit={handleSubmit} noValidate>
              <div className="sign-up-form__field">
                <AuthInput
                  placeholder="Username"
                  value={username}
                  disabled={isSubmitting}
                  onChange={(event) => setUsername(event.target.value)}
                  onBlur={() => handleBlur("username")}
                  aria-invalid={Boolean(usernameError)}
                />

                {usernameError && (
                  <p className="sign-up-form__error">{usernameError}</p>
                )}
              </div>

              <div className="sign-up-form__field">
                <AuthInput
                  placeholder="Mail"
                  type="email"
                  value={email}
                  disabled={isSubmitting}
                  onChange={(event) => setEmail(event.target.value)}
                  onBlur={() => handleBlur("email")}
                  aria-invalid={Boolean(emailError)}
                />

                {emailError && (
                  <p className="sign-up-form__error">{emailError}</p>
                )}
              </div>

              <div className="sign-up-form__field">
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
                  <p className="sign-up-form__error">{passwordError}</p>
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

                <button
                  type="submit"
                  disabled={!isFormValid || isSubmitting}
                >
                  <img src={loginIcon} alt="Submit" className="auth-page__icon" />
                </button>
              </div>
            </form>
          </AuthCard>
        </div>
      </PageContainer>

      {isSubmitting && <LoadingOverlay message="Creating account..." />}
    </>
  );
}
