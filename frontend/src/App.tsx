import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { I18nProvider } from "./i18n";
import { DashboardPage } from "./pages/DashboardPage";
import { GenerationPage } from "./pages/GenerationPage";
import { MaterialsPage } from "./pages/MaterialsPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { SettingsPage } from "./pages/SettingsPage";

function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/projets" element={<ProjectsPage />} />
          <Route path="/materiel" element={<MaterialsPage />} />
          <Route path="/generation" element={<GenerationPage />} />
          <Route path="/parametres" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </I18nProvider>
  );
}
