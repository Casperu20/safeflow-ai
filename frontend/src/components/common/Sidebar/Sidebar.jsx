import { useNavigate } from "react-router-dom";
import { ROUTES } from "../../../constants/routes.js";
import "./Sidebar.css";
import menuInfo from "../../../assets/images/Info.png";
import menuBook from "../../../assets/images/Book.png";
import menuLayers from "../../../assets/images/Layers.png";
import menuLogout from "../../../assets/images/Logout.png";

export function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();

  function handleNavigate(path) {
    navigate(path);
    onClose();
  }

  if (!isOpen) {
    return null;
  }

  return (
    <nav className="sidebar">
      <button className="sidebar__item" type="button" onClick={() => handleNavigate(ROUTES.PRIVACY)}>
        <img src={menuInfo} alt="Info icon" className="sidebar__icon" />
        Privacy
      </button>
      <button className="sidebar__item" type="button" onClick={() => handleNavigate(ROUTES.ABOUT)}>
        <img src={menuBook} alt="Book icon" className="sidebar__icon" />
        About
      </button>
      <button className="sidebar__item" type="button" onClick={() => handleNavigate(ROUTES.HISTORY)}>
        <img src={menuLayers} alt="Layers icon" className="sidebar__icon" />
        History
      </button>
      <button className="sidebar__item" type="button" onClick={() => handleNavigate(ROUTES.LOGIN)}>
        <img src={menuLogout} alt="Logout icon" className="sidebar__icon" />
        Exit
      </button>
    </nav>
  );
}
