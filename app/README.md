# App Streamlit – Restitution sponsor

## Dépendances utilisées en déploiement Streamlit Community Cloud
Le déploiement utilise **`requirements.txt` à la racine du repo**.

## Lancer en local
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Si un import manque au déploiement
1. Ajouter explicitement le package manquant dans `requirements.txt`.
2. Commit + push sur la branche de la PR existante.
3. Redéployer l'app Streamlit.

## Sources utilisées par l’app
- `outputs/cleaned_data.csv`
- `outputs/analysis_report.md`
- `outputs/executive_summary.md`
- `outputs/one_pager_comex.md`
- `outputs/board_deck_outline.md`
- `outputs/charts/*.png`

## Pages
- Accueil
- Vue d’ensemble
- Segmentations
- Verbatims
- Recommandations
- Artefacts
