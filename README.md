# Bahi-SCAFF - Plateforme interne facade + echafaudage

Outil industriel interne pour techniciens et ingenieurs echafaudage.
Le systeme transforme une photo/plan en livrables chantier exploitables:

- elevation technique 2D (SVG, DXF, PDF)
- reconstruction 3D (OBJ, GLB, IFC)
- calcul de structure d'echafaudage conforme
- quantitatif materiel detaille
- devis chantier automatique

## Vision produit

Ce depot est concu comme un logiciel d'ingenierie metier:

- priorite a la geometrie fiable et reproductible
- IA utilisee comme assistance, pas comme source unique de verite
- controles metrologiques et regles normatives explicites

## Arborescence

```text
backend/      API FastAPI + pipeline metier
frontend/     Interface React/Canvas terrain
docs/         Architecture, flux et decisions techniques
```

## Demarrage rapide

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- `docs/architecture.md`: architecture complete, modules et contrats.
- `docs/workflow.md`: pipeline metier, controles qualite et validations.

## Qualite attendue

- tolerance geometrique cible: 1 a 2 cm
- temps calcul cible: < 5 secondes par facade
- execution deterministe et verifiable