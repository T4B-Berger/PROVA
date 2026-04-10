# App Streamlit – PROVA IA Transformation Cockpit

## Finalité
Cette app sert au **pilotage de transformation IA** (décisions, gouvernance, portefeuille 2026, enablement, roadmap), sans réouvrir l'analyse de fond.

## Dépendances de déploiement Streamlit Cloud
Le déploiement utilise **`requirements.txt` à la racine**.

## Lancement local
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Si un import manque au déploiement
1. Ajouter explicitement le package manquant dans `requirements.txt`.
2. Commit + push sur la branche de la PR existante.
3. Redéployer l'app Streamlit.

## Vues (logique de lecture)
1. **Accueil**
2. **Cockpit COMEX**
3. **Maturité**
4. **Irritants → cas d’usage**
5. **Portefeuille 2026**
6. **Gouvernance et garde-fous**
7. **Enablement / formation**
8. **Réseau Early Adopters**
9. **Roadmap 12 mois**
10. **Artefacts**

## Design system
- Theme Streamlit via `.streamlit/config.toml`.
- CSS custom léger dans `app/streamlit_app.py` (cartes KPI, encarts, badges).
- Palette documentée dans `outputs/brand_ui_rationale.md`.

## Sources de vérité
- `outputs/executive_summary.md`
- `outputs/one_pager_comex.md`
- `outputs/board_deck_outline.md`
- `outputs/analysis_report.md`
- `outputs/cleaned_data.csv`
- `outputs/variable_dictionary.csv`
- `outputs/charts/*`

## Gouvernance de contenu
- Les KPI affichés proviennent des outputs existants ou de calculs traçables.
- Toute proposition non directement issue des données est marquée **recommandation**.
