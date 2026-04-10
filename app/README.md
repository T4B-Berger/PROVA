# Application Streamlit — PROVA (hotfix comité de direction)

## 1) Protection du mode prescriptif
Le contrôle global de la sidebar est `Description seule`.
- `Oui` : mode strictement descriptif.
- `Non` : accès au mode prescriptif uniquement après validation du mot de passe de session.

### Protection mise en place
- Mot de passe requis pour activer le mode `Non` : `iqo`.
- Saisie masquée (`type="password"`).
- État mémorisé par session (`st.session_state`).
- Cette protection est **légère** (contrôle d’accès applicatif), et **ne remplace pas** un dispositif de sécurité forte.

## 2) Ordre métier
L’ordre métier de l’expertise en intelligence artificielle est appliqué dans les vues concernées :
1. `Advanced / Expert`
2. `Intermediate`
3. `Beginner`
4. `Interested, but not using it yet`

Aucun tri alphabétique n’est utilisé pour cette variable dans les filtres et tableaux concernés.

## 3) Libellés lisibles
Un mapping centralisé transforme les champs techniques en libellés lisibles pour l’interface (filtres, vues individuelles, verbatims, segmentations).
Objectif : ne pas exposer de noms de colonnes techniques dans l’interface.

## 4) Verbatims enrichis
La page `Verbatims intelligents` propose :
- regroupement thématique avec volumes,
- filtres par thème et fonction,
- vue dédiée `Verbatims par thème` (liste dépliable),
- anonymisation systématique des extraits.

## 5) Navigation
- `Description seule = Oui` : pages factuelles uniquement.
- `Description seule = Non` : pages factuelles + pages prescriptives (si mot de passe validé).

## 6) Lancement local
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## 7) Intégration éditoriale du deck COMEX
L’application intègre une sélection raisonnée du deck COMEX (et non un copier-coller).

### Ce qui a été repris
- Message directeur d’ouverture (passage de l’exploration à l’exécution pilotée).
- Storyline en quatre messages pour structurer la lecture de direction.
- Bloc décisionnel en quatre arbitrages sur la vue de priorisation.
- Renforcement de la hiérarchie de lecture sur le cockpit COMEX.

### Ce qui n’a pas été repris
- Annexes trop détaillées slide par slide.
- Redondances chiffrées déjà visibles dans les pages factuelles.
- Éléments “slideware” qui alourdissent l’interface sans gain décisionnel.

### Pourquoi
- Conserver une interface lisible, orientée décision.
- Améliorer la narration sans surcharge ni duplication.
- Maintenir la séparation stricte entre constat factuel et contenus prescriptifs.

## 8) Lisibilité des tableaux de segmentation
Principe appliqué : chaque tableau croisé doit être lisible sans connaissance du questionnaire source.

### Règles de lisibilité
- Pas de colonnes ou lignes ambiguës `Yes` / `No` affichées seules.
- Libellés binaires explicités en français (usage au travail, usage personnel, early adopters).
- Sous-titres d’aide pour préciser le sens des lignes et des colonnes.
- Totaux de ligne/colonne et pourcentages par ligne pour faciliter l’interprétation COMEX.
