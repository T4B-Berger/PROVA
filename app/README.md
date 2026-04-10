# App Streamlit – PROVA IA Transformation Cockpit (Phase 3)

## Finalité
App de pilotage avec **double mode de lecture**:
- **Description seule = Oui**: vues strictement factuelles
- **Description seule = Non**: vues factuelles + vues de recommandation

## Toggle global
Dans le menu latéral: `Description seule`.

### Mode Oui (factuel uniquement)
- Accueil
- Cockpit COMEX factuel
- Maturité
- Segmentations
- Réponses individuelles
- Verbatims intelligents
- Artefacts descriptifs

### Mode Non (factuel + pilotage)
- toutes les vues ci-dessus
- + Use case lab
- + Gouvernance
- + Enablement
- + Roadmap / Action tracker
- + Recommandations / priorisation

## Logique NLU retenue
NLU léger, explicable, non opaque:
- taxonomie mots-clés (irritant, opportunite, risque, formation, cas_usage)
- tagging multi-label
- fréquence des tags
- score simple d'actionnabilité (nombre de tags)

## Limites méthodologiques
- pas de sentiment analysis opaque
- pas d'inférence causale
- les éléments prescriptifs sont explicitement marqués recommandation/proposition

## Différences de nature des contenus
- **Fait observé**: chiffre/constat traçable aux données
- **Regroupement analytique**: tag/thème explicable
- **Recommandation**: proposition d'action (uniquement en mode Non)

## Dépendances de déploiement
Le déploiement Streamlit Cloud utilise `requirements.txt` racine.

## Lancement local
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```
