# Streamlit Release Note

## A. Objectif de l’app
Fournir une restitution sponsor-facing, lisible et actionnable des résultats du questionnaire IA.

## B. Public cible
- Sponsors de transformation
- Managers métiers
- Équipe Data/Transformation

## C. Dépendances
- `streamlit`
- `pandas`
- `scipy`
(voir `requirements_streamlit.txt`)

## D. Commande de lancement locale
```bash
pip install -r requirements_streamlit.txt
streamlit run app/streamlit_app.py
```

## E. Fichiers sources utilisés
- `outputs/cleaned_data.csv`
- `outputs/analysis_report.md`
- `outputs/executive_summary.md`
- `outputs/one_pager_comex.md`
- `outputs/board_deck_outline.md`
- `outputs/charts/*.png`

## F. Limites d’usage
- Les segmentations affichent des associations statistiques, pas des causalités.
- Les verbatims sont regroupés par approche mots-clés (orientation managériale, non NLP exhaustif).
- L'app n'est pas un outil d'édition des données, uniquement de lecture/restitution.

## G. Précautions de confidentialité / diffusion
- Limiter la diffusion aux parties prenantes internes.
- Ne pas exposer publiquement les extraits verbatim hors contexte.
- Vérifier que les exports partagés sont conformes aux règles internes (données personnelles, gouvernance IA).
