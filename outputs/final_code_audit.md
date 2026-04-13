# Audit technique final — Streamlit app

## A. structure actuelle
- Application monofichier `app/streamlit_app.py` pilotée par navigation sidebar.
- Constantes métier déjà présentes (ordres expertise, labels, taxonomie, pages).
- Helpers existants pour calculs statistiques, anonymisation et affichage.

## B. faiblesses techniques
- Contrôle d’accès limité au mode prescriptif (porte partielle, non globale).
- Duplication de logique de filtres sur les réponses individuelles.
- Répétition de patterns d’extraction de valeurs uniques triées.
- Présence d’un artefact technique inutile (`pd.read_markdown if False else ...`).

## C. optimisations retenues
1. Porte d’accès **globale** et centralisée via `ensure_global_access()` avec session state.
2. Centralisation du secret applicatif dans une constante unique + comparaison sûre (`hmac.compare_digest`).
3. Factorisation des filtres communs via `apply_common_filters()`.
4. Factorisation de l’extraction de valeurs triées via `unique_sorted_values()`.
5. Nettoyage de code mort/placeholder dans la table Use case lab.

## D. optimisations volontairement écartées
- Découpage en plusieurs modules Python (gain limité vs risque de régression en phase finale).
- Refonte UI/CSS (interdit par consigne, pas de gain métier immédiat).
- Changement de logique métier/statistique des pages existantes (hors périmètre).

## E. risques de régression à surveiller
- Vérifier que la porte globale stoppe bien tout rendu avant authentification.
- Vérifier que le mode `Description seule` continue d’ouvrir/fermer les pages prescriptives.
- Vérifier que les filtres de la page Réponses individuelles donnent les mêmes résultats qu’avant.
