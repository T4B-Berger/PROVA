# Toggle hotfix status

## A. cause exacte de l’absence du toggle
- L'implémentation précédente ne respectait pas le contrat de publication demandé (contrôle explicite Oui/Non + navigation basée sur listes explicites).

## B. correction appliquée
- Le contrôle `Description seule` avec choix `Oui` / `Non` pilote maintenant la navigation via `FACTUAL_PAGES` et `PRESCRIPTIVE_PAGES`.

## C. emplacement exact du contrôle dans la sidebar
- Contrôle placé avant la radio de navigation dans la sidebar.

## D. pages visibles en mode Oui
- Accueil
- Cockpit COMEX factuel
- Maturité
- Segmentations
- Réponses individuelles
- Verbatims intelligents
- Artefacts descriptifs / sources

## E. pages visibles en mode Non
- Toutes les pages du mode Oui
- + Use case lab
- + Gouvernance
- + Enablement
- + Roadmap / Action tracker
- + Recommandations / priorisation

## F. validations exécutées
- `python -m py_compile app/streamlit_app.py` ✅
- `timeout 15s streamlit run app/streamlit_app.py --server.headless true --server.port 8501` ✅ (boot local validé)

## G. limites restantes
- Publication GitHub bloquée par authentification:
  - `git push -u origin hotfix/sidebar-toggle-navigation`
  - `fatal: could not read Username for 'https://github.com': No such device or address`
- Sans push, la PR ne peut pas être créée dans cet environnement.
