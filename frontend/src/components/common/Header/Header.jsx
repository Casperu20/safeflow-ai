import { useLocation, useNavigate } from "react-router-dom";
import { ROUTES } from "../../../constants/routes.js";
import { ThemeToggle } from "../ThemeToggle/ThemeToggle.jsx";
import menuIcon from "../../../assets/images/Menu.png";
import userIcon from "../../../assets/images/User.png";
import arrowBackIcon from "../../../assets/images/ArrowBack.png";
import "./Header.css";

const ROUTES_WITH_HOME_BUTTON = [
  ROUTES.PRIVACY,
  ROUTES.ABOUT,
  ROUTES.HISTORY,
  ROUTES.PROFILE,
];

export function Header({ onMenuClick, isDarkMode, onThemeToggle }) {
  const navigate = useNavigate();
  const location = useLocation();

  const shouldShowHomeButton = ROUTES_WITH_HOME_BUTTON.includes(
    location.pathname,
  );

  return (
    <header className="header">
      <div className="header__left-actions">
        <button
          className="header__button"
          type="button"
          onClick={onMenuClick}
          aria-label="Open menu"
        >
          <img src={menuIcon} alt="Menu icon" className="header__menu-icon" />
        </button>
        <ThemeToggle isDarkMode={isDarkMode} onToggle={onThemeToggle} />
      </div>

      <div className="header__right-actions">
        {shouldShowHomeButton && (
          <button
            className="header__button"
            type="button"
            onClick={() => navigate(ROUTES.HOME)}
            aria-label="Go to home page"
          >
            <img src={arrowBackIcon} alt="Home icon" className="header__icon" />
          </button>
        )}
        <button
          className="header__button"
          type="button"
          onClick={() => navigate(ROUTES.PROFILE)}
          aria-label="Open profile"
        >
          <img
            src={userIcon}
            alt="Profile icon"
            className="header__profile-icon"
          />
        </button>
      </div>
    </header>
  );
}
