import { useI18n } from "../i18n";

export function SettingsPage() {
  const { language, setLanguage } = useI18n();

  return (
    <section className="page-stack">
      <article className="card">
        <h2>Parametres</h2>
        <label>
          Langue interface
          <select value={language} onChange={(e) => setLanguage(e.target.value as "fr" | "en")}>
            <option value="fr">Francais</option>
            <option value="en">English</option>
          </select>
        </label>
        <p>Le moteur met toujours la securite en priorite et demande confirmation en cas de doute.</p>
      </article>
    </section>
  );
}
