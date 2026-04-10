# Toggle hotfix status

## A. cause exacte de l’absence du toggle
- Le contrôle existant était un `st.sidebar.toggle(...)` booléen sans valeurs explicites `Oui/Non`, ce qui n’assurait pas une lecture utilisateur conforme à la spec.
- La navigation n’était pas pilotée par deux listes explicites normalisées (`FACTUAL_PAGES` / `PRESCRIPTIVE_PAGES`) imposées par la consigne de hotfix.
- Le libellé d’une page factuelle ne correspondait pas exactement à la cible (`Artefacts descriptifs` au lieu de `Artefacts descriptifs / sources`).

## B. correction appliquée
- Remplacement par un contrôle explicite en haut de sidebar:
  - `Description seule` avec choix `Oui` / `Non`.
- Introduction de deux listes de référence:
  - `FACTUAL_PAGES`
  - `PRESCRIPTIVE_PAGES`
- Construction unique de la navigation depuis ces listes selon la valeur du contrôle.
- Alignement du libellé factuel: `Artefacts descriptifs / sources`.
- En mode `Oui`, suppression de la colonne prescriptive `Priorité d’action` dans la vue Maturité.

## C. emplacement exact du contrôle dans la sidebar
- Première ligne sidebar de navigation:
  - `desc_mode = st.sidebar.radio("Description seule", ["Oui", "Non"], index=0)`
- Le menu navigation est rendu après ce contrôle.

## D. pages visibles en mode Oui
- Accueil
- Cockpit COMEX factuel
- Maturité
- Segmentations
- Réponses individuelles
- Verbatims intelligents
- Artefacts descriptifs / sources

## E. pages visibles en mode Non
- Toutes les pages factuelles ci-dessus
- + Use case lab
- + Gouvernance
- + Enablement
- + Roadmap / Action tracker
- + Recommandations / priorisation

## F. validations exécutées
- `python -m py_compile app/streamlit_app.py` (OK)
- `timeout 15s streamlit run app/streamlit_app.py --server.headless true --server.port 8501` (boot OK, arrêt contrôlé timeout)
- Vérification présence des clés de navigation (`FACTUAL_PAGES`, `PRESCRIPTIVE_PAGES`, contrôle `Description seule`, radio `Navigation`) (OK)
- Vérification absence de marqueurs de conflit git (OK)

## G. limites restantes
- Validation UI faite en runtime headless (boot). Pas de capture de prod dans cet environnement.
