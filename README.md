# Facade2D — Génération de façades architecturales 2D depuis photo smartphone

## Objectif

`facade2d` est un outil orienté production pour transformer une photo de façade prise au smartphone en élévation 2D exploitable.

La pipeline conserve :

- la **structure globale** de la façade,
- le **nombre d’ouvertures** (fenêtres/portes),
- la **forme** des ouvertures (rectangulaire / cintrée),
- des **éléments décoratifs horizontaux** (bandeaux),
- une **échelle métrique** via segment de référence connu.

> Exemple cible : photo perspective réelle -> façade 2D à plat, comme dans tes visuels de référence.

---

## Fonctionnalités

1. **Redressement de perspective (homographie)**
   - détection automatique de façade quadrangulaire, ou
   - corners manuels ultra-précis.

2. **Détection d’ouvertures**
   - segmentation robuste des ouvertures,
   - filtrage morphologique et NMS,
   - extraction de la trame verticale/horizontale.

3. **Détection de bandeaux décoratifs**
   - pics de texture + couverture d’arêtes horizontales.

4. **Sorties professionnelles**
   - `rectified.png` : façade redressée,
   - `overlay.png` : QA visuelle (boîtes + bandeaux),
   - `facade_2d.svg` : élévation vectorielle 2D,
   - `facade_2d.json` : données structurées (ouvertures, dimensions, axes, niveaux).

5. **Modes d’intégration**
   - CLI,
   - API REST (FastAPI).

---

## Installation rapide (recommandée)

### Option 0 — Fichier direct unique (le plus simple)

```bash
bash facade2d_direct.sh --input ./photo_facade.jpg --output ./out
```

Ce fichier :
- installe automatiquement l’outil si nécessaire,
- puis lance le traitement.

Autres modes :

```bash
bash facade2d_direct.sh install
bash facade2d_direct.sh process --input ./photo_facade.jpg --output ./out
bash facade2d_direct.sh api
```

### Option A — Script automatique

```bash
bash scripts/install_facade2d.sh
```

Le script gère 2 cas automatiquement :
- installation dans `.venv-facade2d` (si `python3 -m venv` est disponible),
- sinon fallback en mode `--user` (machines cloud/minimales).

Puis lancer un traitement :

```bash
bash scripts/facade2d_process.sh --input ./photo_facade.jpg --output ./out
```

Ou lancer l’API :

```bash
bash scripts/facade2d_api.sh
```

### Option B — Manuelle

```bash
python3 -m venv .venv-facade2d
source .venv-facade2d/bin/activate
pip install -e .
```

---

## Utilisation via Makefile

```bash
make install
make process ARGS="--input ./photo_facade.jpg --output ./out"
make api
```

---

## CLI

### Traitement standard

```bash
facade2d process \
  --input ./photo_facade.jpg \
  --output ./out
```

### Avec corners manuels + référence métrique

```bash
facade2d process \
  --input ./photo_facade.jpg \
  --output ./out \
  --corners "120,90 920,80 980,1380 90,1400" \
  --reference "430,1260,560,1260,1.20"
```

- `--corners`: 4 coins de façade dans l’image source  
  format `"x1,y1 x2,y2 x3,y3 x4,y4"`
- `--reference`: segment de longueur connue (m) dans l’image source  
  format `"x1,y1,x2,y2,longueur_m"`

### Désactiver auto-corners

```bash
facade2d process \
  --input ./photo_facade.jpg \
  --output ./out \
  --no-auto-corners
```

---

## API REST

Lancer le serveur :

```bash
facade2d-api
```

Endpoints :

- `GET /health`
- `POST /process` (multipart/form-data)
  - `image` (fichier) [obligatoire]
  - `corners` (texte optionnel)
  - `reference` (texte optionnel)
  - `auto_corners` (bool optionnel)
  - `output_dir` (texte optionnel)
  - `include_svg` (bool optionnel)

Exemple cURL :

```bash
curl -X POST "http://localhost:8000/process" \
  -F "image=@./photo_facade.jpg" \
  -F "corners=120,90 920,80 980,1380 90,1400" \
  -F "reference=430,1260,560,1260,1.20"
```

---

## Précision et bonnes pratiques terrain

Pour une erreur minimale d’échelle et de géométrie :

1. Photographier la façade avec un angle frontal le plus proche possible.
2. Éviter les focales extrêmes (ultra grand-angle).
3. Fournir les 4 corners manuels pour les projets sensibles.
4. Fournir un segment de référence réel (porte, trame connue, etc.).
5. Vérifier `overlay.png` pour contrôle qualité.

---

## Arborescence

```text
src/facade2d/
  api.py
  cli.py
  detection.py
  geometry.py
  models.py
  parsing.py
  pipeline.py
  rendering.py
scripts/
  install_facade2d.sh
  facade2d_process.sh
  facade2d_api.sh
Makefile
tests/
  test_pipeline_synthetic.py
```

---

## Roadmap (partie suivante)

- export DXF,
- module de calibration caméra avancée,
- apprentissage supervisé pour ornements complexes,
- interface web interactive de correction manuelle.