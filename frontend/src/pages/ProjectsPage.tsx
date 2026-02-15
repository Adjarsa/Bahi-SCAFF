import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Project } from "../types";

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  const refresh = () =>
    apiClient
      .listProjects()
      .then(setProjects)
      .catch(() => setMessage("Erreur lors du chargement des projets."));

  useEffect(() => {
    refresh();
  }, []);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    try {
      await apiClient.createProject({ name, description });
      setName("");
      setDescription("");
      setMessage("Projet cree avec succes.");
      refresh();
    } catch {
      setMessage("Echec de creation du projet.");
    }
  };

  return (
    <section className="page-stack">
      <article className="card">
        <h2>Creer un projet</h2>
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            Nom du projet
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Facade Rue Victor Hugo" />
          </label>
          <label>
            Description
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Type echafaudage, contraintes, delais..."
            />
          </label>
          <button type="submit">Enregistrer</button>
        </form>
        {message ? <p>{message}</p> : null}
      </article>

      <article className="card">
        <h2>Liste projets</h2>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Statut</th>
              <th>Cree le</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id}>
                <td>{project.name}</td>
                <td>{project.status}</td>
                <td>{new Date(project.created_at).toLocaleString("fr-FR")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}
