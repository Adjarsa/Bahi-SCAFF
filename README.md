# Bahi-SCAFF

Maquette fonctionnelle d'un outil pro pour entreprise d'echafaudage.

## Objectif

Ce prototype couvre vos 3 etapes metier:

1. Import photo(s) facade ou plan facade, puis mise a l'echelle.
2. Generation d'une implantation echafaudage avec trames predefinies et controles de base R408.
3. Generation d'un quantitatif materiel avec comparaison stock depot et reste a commander.

## Contenu du depot

- `mockup/index.html` : interface principale (maquette ecran final).
- `mockup/styles.css` : style visuel (look produit pro).
- `mockup/app.js` : logique de calibration, implantation, controles et quantitatif.

## Lancer la maquette

Option rapide: ouvrir `mockup/index.html` dans votre navigateur.

Option serveur local:

```bash
cd /workspace/mockup
python3 -m http.server 8080
```

Puis ouvrir `http://localhost:8080`.

## Fonctionnalites presentes

- Import multi-fichiers (photos + plan).
- Calibration via cote reelle (m) / cote image (px).
- Decomposition automatique de largeur facade en travees (3 m, 2 m, 1.5 m, 1 m, 0.75 m selon preset).
- Generation du plan facade cote sur canvas (avec image de fond si disponible).
- Controles automatises:
  - travees <= 3 m,
  - ancrages <= 24 m2 / point,
  - verification acces verticaux,
  - presence plinthes / filets,
  - alerte facade haute > 24 m.
- Quantitatif materiel detaille:
  - plateaux,
  - poteaux,
  - moises,
  - garde-corps,
  - diagonales,
  - ancrages,
  - verins,
  - options (plinthes, filets, signalisation nuit).
- Export:
  - plan facade en PNG,
  - quantitatif en CSV.

## Important

Cette version est une maquette produit (prototype). Les calculs sont indicatifs.

Avant usage chantier reel:

- validation obligatoire par un responsable technique,
- verification reglementaire complete (R408 + contexte chantier),
- controle structurel et plan de montage definitif.