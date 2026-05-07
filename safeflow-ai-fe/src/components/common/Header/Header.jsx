import { useNavigate } from "react-router-dom";
import { ROUTES } from "../../../constants/routes.js";
import menuIcon from "../../../assets/images/Menu.png";
import userIcon from "../../../assets/images/User.png";
import "./Header.css";

export function Header({ onMenuClick }) {
  const navigate = useNavigate();

  return (
    <header className="header">
      <button className="header__button" type="button" onClick={onMenuClick} aria-label="Open menu">
        <img src={menuIcon} alt="Menu icon" className="header__menu-icon" />
      </button>
      <button className="header__button" type="button" onClick={() => navigate(ROUTES.PROFILE)} aria-label="Open profile">
        <img src={userIcon} alt="Profile icon" className="header__profile-icon" />
      </button>
    </header>
  );
}
