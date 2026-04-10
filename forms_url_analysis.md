# Diagnostic d'accès Microsoft Forms

## Statut d'accès
- Tentative d'accès à l'URL fournie effectuée.
- Accès analytique impossible dans cet environnement.

## Vérifications exécutées
1. Tentative d'ouverture directe via l'outil web sur l'URL exacte fournie.
   - Résultat: erreur de sécurité de l'outil (`URL ... is not safe to open`).
2. Tentative d'ouverture de `https://forms.office.com` via l'outil web.
   - Résultat: page minimale avec contenu `Loading…` uniquement (pas de DOM exploitable rendu côté serveur).
3. Tentative réseau bas niveau via `curl` sur l'URL fournie.
   - Résultat: échec du tunnel HTTPS via proxy (`CONNECT tunnel failed, response 403`).
4. Vérification verbosité réseau via `curl -v`.
   - Résultat: blocage au niveau du proxy `http://proxy:8080` avant tout échange HTTP avec `forms.office.com`.

## Ce qui bloque
- Le proxy réseau de l'environnement refuse la connexion HTTPS vers `forms.office.com` (403 sur la phase CONNECT).
- L'outil web ne permet pas d'ouvrir l'URL d'analyse Forms avec paramètres (contrainte de sécurité interne).

## Minimum nécessaire pour poursuivre
- Soit un accès réseau sortant autorisé vers `forms.office.com` depuis cet environnement.
- Soit un artefact exporté des réponses (Excel/CSV) ou captures de la page d'analyse Forms.

## Limites
- Aucun HTML de la page cible, aucune redirection applicative Microsoft 365, aucun script de rendu Forms, aucun résultat de questionnaire n'ont pu être récupérés.
