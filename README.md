# ScaffoldPlan AI

Application SaaS pour la conception d'echafaudages de facade avec generation automatique, controle securite R408, quantitatif materiel et exports professionnels.

## Architecture

```text
backend/   -> API FastAPI + moteur metier + exports
frontend/  -> Interface React + visualisation Three.js
```

## Fonctionnalites couvertes

- Import facade (images/PDF/DWG) avec detection initiale d'elements.
- Calibration manuelle, automatique, LiDAR (niveau confiance + confirmation si besoin).
- Generation echafaudage:
  - decoupage en travees optimales,
  - calcul quantitatif materiel,
  - verification stock depot,
  - avertissements securite R408.
- Visualisation frontend:
  - dashboard KPI,
  - gestion projets,
  - gestion materiel,
  - simulation generation + vue 3D.
- Exports:
  - PDF technique,
  - Excel quantitatif,
  - bon de sortie depot (CSV),
  - rapport conformite (PDF).

## Lancer le backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API disponible sur `http://localhost:8000`.
Documentation Swagger: `http://localhost:8000/docs`.

## Lancer le frontend

```bash
cd frontend
npm install
npm run dev
```

UI disponible sur `http://localhost:5173`.

## Variables d'environnement backend (optionnel)

Copier `.env` dans `backend/`:

```env
DATABASE_URL=sqlite:///./scaffoldplan.db
ALLOW_ORIGINS=http://localhost:5173
API_PREFIX=/api/v1
```

## Tests

```bash
cd backend
pytest
```

## Orientation metier

Le moteur priorise:
1. Securite des personnes et conformite.
2. Faisabilite stock / materiel reel.
3. Optimisation des quantites.
4. Validation humaine en cas d'incertitude.