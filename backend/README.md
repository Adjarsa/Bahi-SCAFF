# Backend - Bahi-SCAFF

API FastAPI qui orchestre le pipeline industriel:

1. analyse image
2. correction perspective
3. calibration metrique
4. reconstruction geometrique
5. generation elevation 2D
6. reconstruction 3D
7. calcul echafaudage
8. quantitatif materiel
9. devis chantier

## Lancement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
pytest
```
