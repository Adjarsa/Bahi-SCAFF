# Backend ScaffoldPlan AI

API FastAPI pour:
- gestion projets facade,
- gestion stock materiel,
- generation echafaudage et controles R408,
- exports PDF/Excel/CSV.

## Demarrage rapide

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
pytest
```
