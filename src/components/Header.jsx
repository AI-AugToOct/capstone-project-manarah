import { useNavigate, NavLink } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();

  return (
    <header className="header">
      <div className="brand" onClick={() => navigate("/")}>
        <img src="/assets/icon1.png" alt="Logo" className="brand-icon" />
        <span className="divider">|</span>
        <span className="brand-sub">كشف مخالفات المحتوى</span>
      </div>

      <nav className="nav">
        <NavLink 
          to="/" 
          className={({ isActive }) => isActive ? "active" : ""}
          end
        >
          الرئيسية
        </NavLink>

        <NavLink 
          to="/realtime" 
          className={({ isActive }) => isActive ? "active" : ""}
        >
          الكشف اللحظي
        </NavLink>

        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => isActive ? "active" : ""}
        >
          لوحة التحكم
        </NavLink>
      </nav>

    </header>
  );
}
