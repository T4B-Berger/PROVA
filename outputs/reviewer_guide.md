# Reviewer Guide – PR Survey Streamlit

## A. Ce que contient la PR
- Pipeline d'analyse (`analyze_survey.py`) + livrables analytiques/exécutifs sous `outputs/`.
- App Streamlit sponsor-facing (`app/streamlit_app.py`) + guide d'exécution (`app/README.md`).
- Artefacts de contrôle/publication (`outputs/final_quality_check.md`, `outputs/run_validation.md`, `outputs/publish_status.md`, `outputs/pr_ready.md`).

## B. Ce qui a changé par rapport à l’état initial
- Passage d'un diagnostic d'accès Forms à un package complet: analyse, synthèse direction, visualisations, app de restitution.
- Ajout d'une couche de vérification traçable (cohérence des chiffres, exécution app, statut publication).
- Publication GitHub finalisée: branche poussée + draft PR créée.

## C. Fichiers à relire en priorité
1. `outputs/executive_summary.md`
2. `outputs/one_pager_comex.md`
3. `outputs/board_deck_outline.md`
4. `app/streamlit_app.py`
5. `app/README.md`
6. `outputs/publish_status.md`
7. `outputs/pr_ready.md`

## D. Ce qu’un reviewer doit vérifier
- Alignement des chiffres clés entre `executive_summary.md` et `cleaned_data.csv`.
- Qualité des messages sponsor (concision, actionnabilité, limites explicites).
- Lisibilité des pages Streamlit et pertinence des 4 graphiques retenus.
- Cohérence des recommandations (sponsor/fonction propriétaire, horizon temporel).
- Traçabilité de publication (remote, push, PR draft).

## E. Limites connues
- Tests chi2: association, pas causalité.
- Taille d'échantillon limitée (N=70), prudence sur sous-segments.
- Thématisation verbatims par mots-clés (approximation directionnelle).

## F. Critères de merge recommandés
- ✅ Chiffres clés vérifiés et cohérents.
- ✅ App Streamlit démarre localement sans erreur.
- ✅ Livrables exécutifs lisibles par un sponsor non technique.
- ✅ Limites analytiques clairement documentées.
- ✅ Statut de publication et fallback PR manuel documentés.
