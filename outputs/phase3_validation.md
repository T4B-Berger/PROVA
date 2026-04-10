# Phase 3 validation

## Contrôles exécutés
- `python -m py_compile app/streamlit_app.py`
- `timeout 15s streamlit run app/streamlit_app.py --server.headless true --server.port 8501`
- vérification des chemins vers sources de vérité (`outputs/*.md`, `cleaned_data.csv`, `variable_dictionary.csv`)
- vérification de présence des nouvelles vues/artefacts phase 3
- vérification absence marqueurs de conflit

## Contrôles fonctionnels
- toggle `Description seule` présent et actif
- mode Oui: menu strictement factuel
- mode Non: menu complet avec vues prescriptives
- aucune recommandation affichée dans les vues factuelles quand mode Oui
- verbatims affichés anonymisés

## Résultat
- boot Streamlit: OK (arrêt contrôlé timeout)
- compilation: OK
- navigation mode Oui/Non: OK
- séparation factuel vs recommandation: OK
