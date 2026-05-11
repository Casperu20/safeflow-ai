import logo from "../../../assets/images/logo.png";
import "./Logo.css";

export function Logo({ size = "small" }) {
  return (
    <img
      className={`logo logo--${size}`}
      src={logo}
      alt="SafeFlow logo"
    />
  );
}