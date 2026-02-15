import { createContext, PropsWithChildren, useContext, useMemo, useState } from "react";

type Language = "fr" | "en";

const dictionary = {
  fr: {
    dashboard: "Dashboard",
    projects: "Projets",
    materials: "Materiel",
    generation: "Generation",
    settings: "Parametres",
    appTitle: "ScaffoldPlan AI",
    createProject: "Creer un projet",
    generate: "Generer",
    warnings: "Avertissements",
    quantities: "Quantitatif",
    language: "Langue",
  },
  en: {
    dashboard: "Dashboard",
    projects: "Projects",
    materials: "Materials",
    generation: "Generation",
    settings: "Settings",
    appTitle: "ScaffoldPlan AI",
    createProject: "Create project",
    generate: "Generate",
    warnings: "Warnings",
    quantities: "Bill of materials",
    language: "Language",
  },
};

interface I18nContextValue {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: keyof (typeof dictionary)["fr"]) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: PropsWithChildren) {
  const [language, setLanguage] = useState<Language>("fr");
  const value = useMemo<I18nContextValue>(
    () => ({
      language,
      setLanguage,
      t: (key) => dictionary[language][key],
    }),
    [language],
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return ctx;
}
