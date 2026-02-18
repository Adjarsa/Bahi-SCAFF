# Workflow metier et controles qualite

## 1. Entrees

- photo facade terrain (ou plan)
- dimensions connues (optionnel)
- corrections manuelles operateur (optionnel)
- contraintes chantier (sol, acces, hauteur, zones interdites)

## 2. Pipeline de calcul

### Etape A - Analyse image

Sorties:
- contour facade principal
- ouvertures
- segmentation des niveaux
- indices de corniche/toiture

Controle:
- ratio couverture facade > seuil minimum
- detection des incoherences de tailles d'ouvertures

### Etape B - Correction perspective

Sorties:
- matrice de transformation vers projection quasi-orthogonale
- score de qualite redressement

Controle:
- verticalite moyenne residuelle
- ecart d'horizontalite des lignes de plancher

### Etape C - Calibration metrique

Sorties:
- facteur pixels->metres
- mode calibration (auto/manuelle)
- confiance

Controle:
- validation plage plausible (2 a 500 px/m)
- avertissement si confiance faible

### Etape D - Reconstruction geometrique

Sorties:
- grille structurelle (X, Y)
- alignements et symetrie corriges

Controle:
- coherence des entre-axes
- regularite verticale des travees

### Etape E - Livrables techniques

Sorties:
- elevation 2D exportable (SVG/DXF/PDF)
- modele 3D (OBJ/GLB/IFC)

Controle:
- fermeture topologique des polylignes
- metadonnees de version de calcul

### Etape F - Echafaudage + quantitatif + devis

Sorties:
- plan de travees et niveaux
- liste materiels
- devis detaille

Controle:
- regles normatives R408 / EN12811
- controle densite d'ancrages
- audit des formules economiques

## 3. SLA interne recommande

- temps de calcul nominal < 5 s/facade
- disponibilite cible API > 99.5%
- traçabilite complete des versions de regles

## 4. Procedure de verification terrain

1. lancer calcul initial
2. verifier 3 cotes de reference
3. ajuster calibration si besoin
4. regenerer echafaudage
5. valider quantitatif avant emission devis
