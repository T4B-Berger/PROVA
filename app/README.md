# App Streamlit – PROVA IA Transformation Cockpit

## Finalité
Cette app n'est pas un explorateur analytique lourd. Elle sert au **pilotage de transformation IA**: décisions, gouvernance, portefeuille 2026, enablement, roadmap.

## Vues (logique de lecture)
1. **Accueil**: message directeur, constats, décisions immédiates.
2. **Cockpit COMEX**: KPIs clés, tension stratégique, arbitrages à court terme.
3. **Maturité**: lecture par dimension + priorités d'action.
4. **Irritants → cas d’usage**: conversion terrain vers portefeuille.
5. **Portefeuille 2026**: priorisation actionnable.
6. **Gouvernance et garde-fous**: cadre autorisé/toléré/interdit/sous validation.
7. **Enablement / formation**: parcours par population.
8. **Réseau Early Adopters**: activation des relais.
9. **Roadmap 12 mois**: séquencement exécution + KPI.
10. **Artefacts**: inventaire livrables.

## Design system
- Theme Streamlit via `.streamlit/config.toml`.
- CSS custom léger dans `app/streamlit_app.py` (cartes KPI, callouts, badges, hiérarchie).
- Palette documentée dans `outputs/brand_ui_rationale.md`.

## Sources de vérité utilisées
- `outputs/executive_summary.md`
- `outputs/one_pager_comex.md`
- `outputs/board_deck_outline.md`
- `outputs/analysis_report.md`
- `outputs/cleaned_data.csv`
- `outputs/variable_dictionary.csv`
- `outputs/charts/*`

## Dépendances
Le déploiement Streamlit Cloud s'appuie sur `requirements.txt` racine.

## Lancement local
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Gouvernance de contenu
- Les chiffres affichés viennent des outputs existants ou de calculs traçables sur `cleaned_data.csv`.
- Toute proposition non directement issue des données est marquée comme **recommandation**.
