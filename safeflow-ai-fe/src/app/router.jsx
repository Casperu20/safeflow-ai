import { createBrowserRouter } from "react-router-dom";
import { App } from "./App.jsx";
import { HomePage } from "../pages/HomePage/HomePage.jsx";
import { ResultPage } from "../pages/ResultPage/ResultPage.jsx";
import { PrivacyPage } from "../pages/PrivacyPage/PrivacyPage.jsx";
import { AboutPage } from "../pages/AboutPage/AboutPage.jsx";
import { HistoryPage } from "../pages/HistoryPage/HistoryPage.jsx";
import { LoginPage } from "../pages/LoginPage/LoginPage.jsx";
import { SignUpPage } from "../pages/SignUpPage/SignUpPage.jsx";
import { RecoverPasswordPage } from "../pages/RecoverPasswordPage/RecoverPasswordPage.jsx";
import { ProfilePage } from "../pages/ProfilePage/ProfilePage.jsx";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "result", element: <ResultPage /> },
      { path: "privacy", element: <PrivacyPage /> },
      { path: "about", element: <AboutPage /> },
      { path: "history", element: <HistoryPage /> },
      { path: "login", element: <LoginPage /> },
      { path: "signup", element: <SignUpPage /> },
      { path: "recover-password", element: <RecoverPasswordPage /> },
      { path: "profile", element: <ProfilePage /> }
    ]
  }
]);
