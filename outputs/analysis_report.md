# Rapport d'analyse questionnaire IA

## A. Statut de récupération du fichier
- **Observé** : URL GitHub `blob` détectée puis récupération du binaire via URL `raw`.
- **Observé** : fichier local `A quick survey on AI and your usage of AI(1-70) (1).xlsx` chargé avec succès.
- **Déduit** : le fichier est un export Forms exploitable (lecture pandas OK).
- **Hypothèse** : aucune.

## B. Inventaire des fichiers trouvés
- `A quick survey on AI and your usage of AI(1-70) (1).xlsx`
- `README.md`
- `analyze_survey.py`
- `forms_url_analysis.md`
- `outputs`

## Hypothèses, ambiguïtés, limites de fiabilité
### Hypothèses retenues
- Le fichier principal de réponses est le classeur Excel téléchargé depuis l'URL GitHub fournie.
- La feuille `Sheet1` est retenue car c'est la seule feuille disponible.
- Les colonnes `Points -` et `Feedback -` sont techniques (quiz Forms) et exclues de l'analyse métier.
### Ambiguïtés détectées
- Certaines colonnes 'Option 1..5' ne portent pas la valeur textuelle du Likert; l'interprétation sémantique fine reste à valider.
- Des réponses multi-sélection sont concaténées avec ';', sans dictionnaire officiel des modalités.
### Limites de fiabilité
- Échantillon limité (70 réponses), prudence sur les comparaisons fines par sous-segment.
- Pas de codebook fourni pour confirmer chaque libellé métier.

## C. Diagnostic qualité des données
- Lignes: **70**
- Colonnes brutes: **91**
- Colonnes conservées après nettoyage technique: **33**
- Doublons complets: **0**
- Lignes entièrement vides: **0**
- Réponses partielles (au moins une valeur manquante): **70**
- Colonnes quasi vides (>=95% manquantes): **6**
- Non-réponse: cellule vide/NaN.
- Valeur invalide: information non disponible dans les données fournies (pas de règles de validation métier explicites).

## D. Dictionnaire des variables
- Généré dans `outputs/variable_dictionary.csv` (nom colonne, libellé, type question, type analytique, mode d'analyse).

## E. Analyse descriptive
### what_is_your_primary_role
- Réponses exploitables: **70**
- Sales / Marketing / Communication: 25 (35.7%)
- Operations / Supply / Quality: 17 (24.3%)
- R&D / Innovation: 11 (15.7%)
- Executive: 7 (10.0%)
- Finance/Legal/Procurement: 7 (10.0%)
- HR: 2 (2.9%)
- Other: 1 (1.4%)
### how_would_you_describe_your_level_of_expertise_in_ai
- Réponses exploitables: **69**
- Beginner: 41 (59.4%)
- Intermediate: 16 (23.2%)
- Interested, but not using it yet: 10 (14.5%)
- Advanced / Expert: 2 (2.9%)
### have_you_used_ai_for_work_in_the_last_30_days
- Réponses exploitables: **70**
- Yes: 57 (81.4%)
- No: 13 (18.6%)
### how_often
- Réponses exploitables: **57**
- Daily: 19 (33.3%)
- Weekly: 16 (28.1%)
- 2–3 times/week: 13 (22.8%)
- 1–2 times/month: 7 (12.3%)
- Rarely: 2 (3.5%)
### which_ai_tool_s_do_you_use_for_work
- Réponses exploitables: **57**
- ChatGPT;: 26 (45.6%)
- ChatGPT;Google Gemini;: 5 (8.8%)
- ChatGPT;Microsoft Copilot;: 3 (5.3%)
- ChatGPT;Other (please specify in next question);: 3 (5.3%)
- Google Gemini;: 3 (5.3%)
- Other (please specify in next question);: 2 (3.5%)
- Microsoft Copilot;Google Gemini;: 2 (3.5%)
- ChatGPT;Google Gemini;Microsoft Copilot;: 2 (3.5%)
### do_you_use_ai_in_your_personal_life
- Réponses exploitables: **70**
- Yes: 49 (70.0%)
- No: 21 (30.0%)
### would_you_like_to_be_part_of_the_early_adopters_team_and_be_involved_in_experimentations_for_instance_or_be_a_key_contact_for_your_team_locally
- Réponses exploitables: **50**
- Yes: 30 (60.0%)
- Maybe: 16 (32.0%)
- No: 4 (8.0%)

### what_do_you_use_ai_for_at_work (multi-sélection)

- Research / prep (briefs, questions, exploration): 45 (19.7%)
- Writing / rewriting (emails, notes, minutes): 38 (16.7%)
- Translation: 35 (15.4%)
- Summarizing documents / meetings: 24 (10.5%)
- Analysis (tables, numbers, trends): 20 (8.8%)
- Ideation (names, concepts, options): 18 (7.9%)
- Visual creation (images, slides): 17 (7.5%)
- Planning (roadmaps, action plans): 11 (4.8%)
- Customer support (drafting replies, FAQs): 9 (3.9%)
- Coding / scripting / automation: 8 (3.5%)
- Other: 3 (1.3%)
### which_ai_tool_s_do_you_use_for_work (multi-sélection)

- ChatGPT: 47 (51.6%)
- Google Gemini: 20 (22.0%)
- Microsoft Copilot: 13 (14.3%)
- Other (please specify in next question): 7 (7.7%)
- Anthropic Claude: 4 (4.4%)

### Variables numériques
           col  n      moyenne      mediane   ecart_type          min          max
            id 70 3.550000e+01 3.550000e+01 2.035000e+01 1.000000e+00 7.000000e+01
heure_de_début 70 1.773865e+15 1.773854e+15 4.398995e+11 1.770372e+15 1.774339e+15
  heure_de_fin 70 1.773866e+15 1.773855e+15 4.400148e+11 1.770372e+15 1.774339e+15

## F. Croisements et segmentations
### what_is_your_primary_role x have_you_used_ai_for_work_in_the_last_30_days
- Chi2=8.98, ddl=6, p-value=0.1745
- Tableau de contingence:
```
have_you_used_ai_for_work_in_the_last_30_days  No  Yes
what_is_your_primary_role                             
Executive                                       2    5
Finance/Legal/Procurement                       0    7
HR                                              0    2
Operations / Supply / Quality                   5   12
Other                                           1    0
R&D / Innovation                                1   10
Sales / Marketing / Communication               4   21
```

## G. Analyse des verbatims
### Thèmes principaux (approximation par mots-clés)
- analyse_recherche: 26 occurrences
- creativite_marketing: 11 occurrences
- emails_admin: 8 occurrences
- gain_de_temps: 6 occurrences
- traduction_langue: 3 occurrences
- risque_qualite: 2 occurrences
- formation: 1 occurrences
### Exemples anonymisés
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « Customer service
M&A and Strategic marketing support
Flavor selection or creation »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « scientific watch / presentations help/ data analysis »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « How to switch traditional WoW to AI WoW to save time ?
Tools box on how use in an efficient matter the AI. »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « Tbc »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « To define which tool are allow to be used internally and the compliance framework.
To promote the use of AI, starting by simply & daily basis activities »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « AI use for filling in Specifications and Documents.
AI use for Marketing creation and Tools. »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « Sales analysis
Marketing presentations
New possible markets »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « Prospection support : identify targets, companies and contact names + suggest what could be interseting for them in our portfolio
Data analysis : go through the figures and alert a »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « 1. Tracking action  of routine meeting such as Top 10 
2. To raising pending action to next level of management to follow up.
3. Automtic send  Minute of meeting. »
- (if_we_had_to_prioritize_3_ai_use_cases_for_2026_what_would_you_propose_1_to_3_ideas) « Portfolio
CRM (PLM/Odoo)
Technical Recipes »

## H. Synthèse exécutive
1. Le taux de contact avec l'IA au travail est majoritairement positif dans les réponses exploitables (**observé**).
2. Les usages dominants se concentrent sur la production de contenu, synthèse et support opérationnel (**observé**).
3. Les bénéfices évoqués tournent autour du gain de temps et de la qualité des livrables (**déduit** des réponses multi-sélection).
4. Les risques perçus incluent la qualité/rigueur des réponses IA (hallucinations) et la gouvernance des usages (**observé**).
5. Le besoin de montée en compétence est explicite (formats de formation ciblés demandés) (**observé**).

### 3 points d'alerte
- Hétérogénéité potentielle des pratiques selon les rôles.
- Risque de mésusage sans cadre partagé (qualité/confidentialité).
- Données de segment limitées pour des décisions très fines.

### 3 opportunités d'action
- Déployer un socle de bonnes pratiques prompting + contrôle qualité.
- Prioriser 2–3 cas d'usage à fort ROI (emails, synthèse documentaire, analyse).
- Structurer un réseau d'early adopters pour accélérer l'adoption maîtrisée.

## I. Recommandations priorisées
1. Formaliser une politique d'usage IA (qualité, confidentialité, vérification humaine).
2. Lancer un parcours formation court par métier (ateliers pratiques + coaching).
3. Industrialiser un kit de prompts validés par cas d'usage.
4. Mettre en place un suivi trimestriel des gains (temps, qualité, satisfaction).
5. Piloter des expérimentations encadrées via un noyau d'ambassadeurs.

## J. Fichiers générés
- `outputs/analysis_report.md`
- `outputs/executive_summary.md`
- `outputs/cleaned_data.csv`
- `outputs/variable_dictionary.csv`
- `outputs/charts/*.png`
- `analyze_survey.py`
