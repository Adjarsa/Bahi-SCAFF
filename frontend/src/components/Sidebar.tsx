import { NavLink } from "react-router-dom";
import { useI18n } from "../i18n";

export function Sidebar() {
  const { t } = useI18n();
  const links = [
    { to: "/", label: t("dashboard") },
    { to: "/projets", label: t("projects") },
    { to: "/materiel", label: t("materials") },
    { to: "/generation", label: t("generation") },
    { to: "/parametres", label: t("settings") },
  ];

  return (
    <aside className="sidebar">
      <h1>{t("appTitle")}</h1>
      <nav>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}
            end={link.to === "/"}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
