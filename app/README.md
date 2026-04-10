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
