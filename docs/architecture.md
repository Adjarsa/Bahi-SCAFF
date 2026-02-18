# Architecture technique - Outil facade + echafaudage

## 1. Principes directeurs

Le systeme est concu pour un usage interne en environnement chantier.
Les contraintes prioritaires sont:

1. precision geometrique (erreur 1-2 cm)
2. reproductibilite des resultats
3. robustesse aux cas reels (ombres, perspective, obstacles)
4. verifiabilite de chaque etape du calcul
5. performance cible < 5 s/facade sur jeu de donnees standardise

## 2. Vue d'ensemble

```text
Frontend React/Canvas
  -> API FastAPI
     -> Pipeline d'orchestration
        -> Vision (analyse image + perspective)
        -> Calibration metrique
        -> Reconstruction geometrique
        -> Elevation technique 2D
        -> Reconstruction 3D
        -> Calcul echafaudage (R408 / EN12811)
        -> Quantitatif materiel
        -> Devis chantier
```

## 3. Stack imposee

- Backend: FastAPI
- Vision: OpenCV + PyTorch
- Geometrie: NumPy + Open3D
- Vectorisation: Shapely + SVGWrite
- Frontend: React + Canvas

L'implementation actuelle structure deja ces briques et introduit des interfaces de service
pour brancher les modeles IA et solveurs geometriques avances.

## 4. Structure backend

```text
backend/
  app/
    api/routes/          Endpoints REST
    core/                Configuration et erreurs
    domain/              Modeles metier et normes
    schemas/             Contrats API (Pydantic)
    services/            Modules fonctionnels du pipeline
    main.py              Point d'entree FastAPI
  tests/                 Tests unitaires metier
```

### Modules services

1. `image_analysis.py`
   - detection facade, ouvertures, etages, toiture
   - fusion auto + corrections manuelles
2. `perspective.py`
   - estimation lignes de fuite
   - redressement vers projection orthogonale
3. `calibration.py`
   - calibration auto/manuelle pixels->metres
4. `geometry.py`
   - grille structurelle, alignements, symetrie
5. `technical_elevation.py`
   - elevation 2D propre et export vectoriel
6. `reconstruction3d.py`
   - volume batiment et reliefs
7. `scaffolding.py`
   - decomposition en travees optimales
   - controle regles R408 / EN12811
8. `bill_of_materials.py`
   - quantitatif detaille commande depot
9. `quoting.py`
   - calcul couts, marge, TVA, total
10. `orchestration.py`
    - scenario de bout en bout, traceabilite

## 5. Structure frontend

```text
frontend/
  src/
    components/          UI terrain (mesures, canevas, resultats)
    services/            Appels API
    types.ts             Contrats de donnees partages
    App.tsx              Composition des ecrans
```

Objectif UX:
- rapidite d'execution
- lisibilite des informations critiques
- edition metrique simple sans surcharge visuelle

## 6. Contrats de fiabilite

Chaque execution pipeline retourne:

- hypotheses utilisees
- niveau de confiance calibration
- avertissements de conformite
- details de calcul du devis

Ces elements permettent audit interne et verification documentaire.

## 7. Evolutions recommandees

1. brancher un detecteur d'objets/facade type YOLO/Mask2Former
2. ajouter bundle adjustment multi-vues pour chantiers complexes
3. integrer moteur de regles normatives parametrable par pays
4. exporter IFC enrichi (classification objets + metadata chantier)
