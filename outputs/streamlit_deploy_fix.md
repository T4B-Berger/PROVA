# Diagnostic et correctif déploiement Streamlit Cloud

## 1) Diagnostic du repo
### Fichiers de dépendances recherchés
- `requirements.txt` (racine): **absent (avant correctif)**
- `app/requirements.txt`: absent
- `pyproject.toml`: absent
- `Pipfile`: absent
- `environment.yml`: absent
- `uv.lock`: absent
- `requirements_streamlit.txt`: **présent (avant correctif)**

### Cause identifiée
L'app importait `scipy` (`from scipy.stats import chi2_contingency`) mais le déploiement Streamlit Community Cloud ne prenait pas `requirements_streamlit.txt` comme source standard de dépendances. Résultat: `ModuleNotFoundError: No module named 'scipy'`.

## 2) Correctif appliqué
- Création d'un `requirements.txt` à la racine (fichier reconnu par Streamlit Cloud).
- Dépendances minimales déclarées:
  - `streamlit`
  - `pandas`
  - `numpy`
  - `scipy`
- Suppression de `requirements_streamlit.txt` pour éviter l'ambiguïté.
- Mise à jour de `app/README.md` pour documenter la source unique des dépendances.

## 3) Vérification import scipy
- Import `scipy` **utilisé** dans `app/streamlit_app.py` via `chi2_contingency`.
- Aucun retrait d'import effectué (nécessaire au fonctionnement de la page Segmentations).

## 4) Validation locale
- Installation dépendances via `requirements.txt`: OK
- `python -m py_compile app/streamlit_app.py`: OK
- `streamlit run app/streamlit_app.py --server.headless true`: démarrage OK (arrêt contrôlé via timeout)
- Aucun `ModuleNotFoundError: scipy` observé après correctif.

## 5) Résultat attendu au redéploiement
Le build Streamlit Community Cloud doit désormais installer `scipy` via `requirements.txt` racine, supprimant l'erreur de module manquant au chargement de l'app.
