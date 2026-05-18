import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageContainer } from "../../components/common/PageContainer/PageContainer.jsx";
import { Logo } from "../../components/common/Logo/Logo.jsx";
import { AuthCard } from "../../components/auth/AuthCard/AuthCard.jsx";
import { AuthInput } from "../../components/auth/AuthInput/AuthInput.jsx";
import { ErrorBanner } from "../../components/common/ErrorBanner/ErrorBanner.jsx";
import { LoadingOverlay } from "../../components/common/LoadingOverlay/LoadingOverlay.jsx";
import { useAuth } from "../../context/AuthContext.jsx";
import { ROUTES } from "../../constants/routes.js";
import "./ProfilePage.css";

export function ProfilePage() {
  const navigate = useNavigate();
  const { isAuthenticated, isInitializing, logout, user } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!isInitializing && !isAuthenticated) {
      navigate(ROUTES.LOGIN);
    }
  }, [isAuthenticated, isInitializing, navigate]);

  async function handleLogout() {
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await logout();
      navigate(ROUTES.LOGIN);
    } catch {
      setErrorMessage("Logout failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isInitializing || (!isAuthenticated && !user)) {
    return <LoadingOverlay message="Loading profile..." />;
  }

  const joinedDate = user?.createdAt
    ? new Date(user.createdAt).toLocaleDateString()
    : "Not available";

  return (
    <>
      <PageContainer>
        <div className="auth-page">
          <Logo />
          <h1>SafeFlow</h1>
          <ErrorBanner
            message={errorMessage}
            onClose={() => setErrorMessage("")}
          />
          <AuthCard>
            <AuthInput
              value={user?.fullName || "No display name set"}
              readOnly
            />
            <AuthInput value={user?.email || "No email available"} readOnly />
            <AuthInput value={`Joined ${joinedDate}`} readOnly />
            <button
              className="auth-page__link"
              type="button"
              onClick={handleLogout}
            >
              Log out
            </button>
          </AuthCard>
        </div>
      </PageContainer>
      {isSubmitting && <LoadingOverlay message="Signing out..." />}
    </>
  );
}
