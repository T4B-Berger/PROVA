# Main deploy fix status (Streamlit boot)

## A. état initial de main
- Branche déployée: `main` (d'après logs Streamlit Cloud).
- `app/streamlit_app.py` importait `scipy`.
- `requirements.txt` racine: absent.
- `requirements_streamlit.txt`: présent.
- Symptôme observé: `ModuleNotFoundError: No module named 'scipy'`.

## B. action appliquée
- Application sur `main` du correctif déjà validé sur la branche feature (cherry-pick commit `7aafd12`).
- Résultat correctif dépendances:
  - `requirements.txt` racine présent,
  - `scipy` déclaré,
  - `requirements_streamlit.txt` retiré (renommé vers `requirements.txt`).

## C. état final de main
- `requirements.txt` présent à la racine avec: `streamlit`, `pandas`, `numpy`, `scipy`.
- `requirements_streamlit.txt` absent.
- `app/streamlit_app.py` conservé sur le fond (import `scipy` maintenu car utilisé).

## D. validations exécutées
- `python -m pip install -r requirements.txt -q`
- `python -m py_compile app/streamlit_app.py`
- `timeout 15s streamlit run app/streamlit_app.py --server.headless true --server.port 8501`
- Vérification logs: aucune erreur `ModuleNotFoundError` liée à `scipy`.

## E. statut git final
- Branche locale: `main`.
- Commits appliqués sur main:
  - `ddbfff8` (fix dépendances Streamlit Cloud)
  - `0cc771a` (ce rapport de statut)
- Push main: effectué.

## F. impact attendu sur le redéploiement Streamlit
Le redéploiement Streamlit Cloud pointé sur `main` doit désormais booter sans erreur `No module named 'scipy'`, car la dépendance est installable via `requirements.txt` racine reconnu par Streamlit Cloud.
