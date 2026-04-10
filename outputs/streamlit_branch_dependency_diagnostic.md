# Diagnostic branche déployée / dépendances Streamlit Cloud

## A. Branche effectivement déployée
- D'après les logs fournis: **déploiement depuis `main`**.

## B. État de `main`
- `app/streamlit_app.py`: présent.
- Import `scipy` dans l'app: présent (`from scipy.stats import chi2_contingency`).
- `requirements.txt` racine: **absent**.
- `requirements_streamlit.txt`: présent, contient `streamlit`, `pandas`, `scipy`.
- Autres fichiers dépendances reconnus (app/requirements.txt, pyproject.toml, Pipfile, environment.yml, uv.lock): absents.

## C. État de la branche feature (`feat/survey-streamlit-pr`)
- `app/streamlit_app.py`: présent.
- Import `scipy`: présent.
- `requirements.txt` racine: **présent**, contient `streamlit`, `pandas`, `numpy`, `scipy`.
- `requirements_streamlit.txt`: absent (ambiguïté supprimée).

## D. Cause racine la plus probable
- Streamlit Cloud déploie `main`.
- Sur `main`, il n'y a pas de `requirements.txt` racine (fichier typiquement résolu par Streamlit Cloud).
- L'app importe `scipy`, mais l'environnement de build de `main` n'installe pas `scipy` via un fichier de dépendances pris en compte.
- Le correctif dépendances est donc **sur la branche feature mais pas sur la branche déployée**.

## E. Correction minimale à appliquer
Option 1 (recommandée):
1. **Merger la PR feature vers `main`**.
2. Redéployer Streamlit Cloud (toujours pointé sur `main`).

Option 2 (alternative):
1. Reconfigurer Streamlit Cloud pour déployer `feat/survey-streamlit-pr`.

## F. Statut de sécurité du redéploiement
- Tant que Streamlit déploie `main` sans `requirements.txt` racine: **risque élevé de nouveau crash** (`ModuleNotFoundError: scipy`).
- Après merge feature -> main (ou changement de branche déployée): **redéploiement sûr attendu** sur le point dépendances.
