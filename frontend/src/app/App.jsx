import { Outlet } from "react-router-dom";
import { AppLayout } from "../components/common/AppLayout/AppLayout.jsx";

export function App() {
  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
}
