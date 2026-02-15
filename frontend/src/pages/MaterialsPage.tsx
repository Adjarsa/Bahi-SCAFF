import { FormEvent, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { Material } from "../types";

const initialForm: Omit<Material, "id"> = {
  name: "",
  type: "plateaux",
  dimension: "3.00m",
  weight_kg: 0,
  compatibility: "universel",
  stock_quantity: 0,
  condition: "bon",
};

export function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const refresh = () =>
    apiClient
      .listMaterials()
      .then(setMaterials)
      .catch(() => setMessage("Erreur de chargement du materiel."));

  useEffect(() => {
    refresh();
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await apiClient.createMaterial(form);
      setMessage("Piece ajoutee.");
      setForm(initialForm);
      refresh();
    } catch {
      setMessage("Echec de creation.");
    }
  };

  return (
    <section className="page-stack">
      <article className="card">
        <h2>Ajouter une piece de stock</h2>
        <form className="form-grid two-cols" onSubmit={submit}>
          <label>
            Nom
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Type
            <input value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })} />
          </label>
          <label>
            Dimension
            <input value={form.dimension} onChange={(e) => setForm({ ...form, dimension: e.target.value })} />
          </label>
          <label>
            Poids (kg)
            <input
              type="number"
              step="0.1"
              value={form.weight_kg}
              onChange={(e) => setForm({ ...form, weight_kg: Number(e.target.value) })}
            />
          </label>
          <label>
            Compatibilite
            <input
              value={form.compatibility}
              onChange={(e) => setForm({ ...form, compatibility: e.target.value })}
            />
          </label>
          <label>
            Quantite stock
            <input
              type="number"
              value={form.stock_quantity}
              onChange={(e) => setForm({ ...form, stock_quantity: Number(e.target.value) })}
            />
          </label>
          <button type="submit">Ajouter</button>
        </form>
        {message ? <p>{message}</p> : null}
      </article>

      <article className="card">
        <h2>Stock disponible</h2>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Type</th>
              <th>Dimension</th>
              <th>Poids</th>
              <th>Stock</th>
            </tr>
          </thead>
          <tbody>
            {materials.map((material) => (
              <tr key={material.id}>
                <td>{material.name}</td>
                <td>{material.type}</td>
                <td>{material.dimension}</td>
                <td>{material.weight_kg}</td>
                <td>{material.stock_quantity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </article>
    </section>
  );
}
