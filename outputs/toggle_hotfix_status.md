# Toggle hotfix status

## A. cause exacte de l’absence du toggle
- L'ancienne livraison ne garantissait pas un contrôle global explicite `Description seule` en `Oui/Non` branché sur des listes de pages dédiées.

## B. correction appliquée
- Navigation pilotée par deux listes explicites (`FACTUAL_PAGES`, `PRESCRIPTIVE_PAGES`) et contrôle global `Description seule`.

## C. emplacement exact du contrôle dans la sidebar
- Contrôle `Description seule` affiché avant la radio de navigation.

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
- `timeout 15s streamlit run app/streamlit_app.py --server.headless true --server.port 8501` ✅
- Publication GitHub hotfix: push ✅, PR ✅ (https://github.com/T4B-Berger/PROVA/pull/3)

## G. limites restantes
- Aucune limite technique bloquante côté PR: PR #3 est ouverte, non draft, mergeable.
