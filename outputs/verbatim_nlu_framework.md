# Verbatim NLU framework (phase 3)

## Approche
NLU léger et explicable par taxonomie mots-clés (multi-label):
- irritant
- opportunite
- risque
- formation
- cas_usage

## Sorties
- tags par verbatim
- fréquences de tags
- score d'actionnabilité simple = nombre de tags détectés

## Limites
- pas de modèle opaque
- pas de sentiment analysis gadget
- logique de matching lexical (interprétable)

## Règle d'affichage
- Description seule=Oui: thèmes/tags/fréquences/verbatims uniquement
- Description seule=Non: ajout possible de lecture de transformation (marquée recommandation)
