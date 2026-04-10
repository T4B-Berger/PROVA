# Rapport finalisé – Enquête IA

## 1) Points à corriger ou à renforcer
- Classification automatique des variables: utile mais partiellement fragile sans codebook officiel.
- Certaines interprétations Likert restent ambiguës (modalités Option 1-5).
- Risque de surinterprétation segmentaire vu la taille d'échantillon (N=70).
- Analyse verbatims fondée sur mots-clés (bon niveau direction, pas NLP exhaustif).
- Plusieurs questions sont conditionnelles; les taux bruts doivent être lus avec prudence.

## 2) Validation des résultats (traçabilité des chiffres clés)
- Usage IA au travail: 57/70 = 81.4% (**certain**).
- Usage IA personnel: 49/70 = 70.0% (**certain**).
- Niveau débutant IA: 41/69 = 59.4% (**certain**).
- Early adopters (Yes parmi réponses renseignées): 30/50 = 60.0% (**certain**).
- Cas d'usage dominant "Research/prep": 45 occurrences (19.7%) (**certain** sur base multi-réponses).

## 3) Hypothèses, ambiguïtés, limites
### Hypothèses retenues
- Sheet1 est la feuille d'analyse (unique feuille disponible).
- Colonnes Points/Feedback retirées car techniques Forms.
### Ambiguïtés détectées
- Étiquettes "Option 1-5" sans ancrage textuel complet dans certaines lignes.
- Certaines réponses multi-sélection contiennent des variantes de libellés.
### Limites de fiabilité
- N=70: comparaison fine par sous-population à interpréter prudemment.
- Pas de codebook officiel joint.

## 4) Diagnostic qualité des données
- Lignes: 70
- Colonnes brutes: 91
- Colonnes analytiques conservées: 33
- Doublons complets: 0
- Lignes entièrement vides: 0
- Réponses partielles: 70

## 5) Dictionnaire des variables
- Voir `outputs/variable_dictionary.csv`.

## 6) Analyse descriptive consolidée
### Rôles
- Sales / Marketing / Communication: 25 (35.7%)
- Operations / Supply / Quality: 17 (24.3%)
- R&D / Innovation: 11 (15.7%)
- Executive: 7 (10.0%)
- Finance/Legal/Procurement: 7 (10.0%)
- HR: 2 (2.9%)
- Other: 1 (1.4%)

### Niveau d'expertise IA
- Beginner: 41 (59.4%)
- Intermediate: 16 (23.2%)
- Interested, but not using it yet: 10 (14.5%)
- Advanced / Expert: 2 (2.9%)

### Usage IA au travail (30 jours)
- Yes: 57 (81.4%)
- No: 13 (18.6%)

### Fréquence d'usage (si usage travail)
- Daily: 19 (33.3%)
- Weekly: 16 (28.1%)
- 2–3 times/week: 13 (22.8%)
- 1–2 times/month: 7 (12.3%)
- Rarely: 2 (3.5%)

### Usage personnel IA
- Yes: 49 (70.0%)
- No: 21 (30.0%)

### Early adopters
- Yes: 30 (60.0%)
- Maybe: 16 (32.0%)
- No: 4 (8.0%)

### Top cas d'usage au travail (multi)
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

### Top outils IA (multi)
- ChatGPT: 47 (51.6%)
- Google Gemini: 20 (22.0%)
- Microsoft Copilot: 13 (14.3%)
- Other (please specify in next question): 7 (7.7%)
- Anthropic Claude: 4 (4.4%)

## 7) Croisements prioritaires (lecture décideur)
### what_is_your_primary_role x have_you_used_ai_for_work_in_the_last_30_days
- Observé: chi2=8.98, ddl=6, p=0.1745.
- Déduit: pas d'association statistiquement significative.
- Niveau: **exploratoire**.
- Non concluable: causalité, effet dans le temps, impact business direct.

### how_would_you_describe_your_level_of_expertise_in_ai x have_you_used_ai_for_work_in_the_last_30_days
- Observé: chi2=23.82, ddl=3, p=0.0000.
- Déduit: association statistiquement significative.
- Niveau: **certain**.
- Non concluable: causalité, effet dans le temps, impact business direct.

### do_you_use_ai_in_your_personal_life x have_you_used_ai_for_work_in_the_last_30_days
- Observé: chi2=9.52, ddl=1, p=0.0020.
- Déduit: association statistiquement significative.
- Niveau: **certain**.
- Non concluable: causalité, effet dans le temps, impact business direct.

### what_is_your_primary_role x would_you_like_to_be_part_of_the_early_adopters_team_and_be_involved_in_experimentations_for_instance_or_be_a_key_contact_for_your_team_locally
- Observé: chi2=10.38, ddl=10, p=0.4076.
- Déduit: pas d'association statistiquement significative.
- Niveau: **exploratoire**.
- Non concluable: causalité, effet dans le temps, impact business direct.

## 8) Verbatims améliorés (toutes questions ouvertes ciblées)
### Irritants
- Volume approx: 6
- Verbatim: « From sales point of view Administrative tasks : gathering all information about products sales before doing a quotation, identifying the right product to offer, identifying and proespecting the right  »
- Implication managériale: Cibler les tâches répétitives à automatiser en priorité.

### Attentes
- Volume approx: 1
- Verbatim: « To define which tool are allow to be used internally and the compliance framework.
To promote the use of AI, starting by simply & daily basis activities »
- Implication managériale: Clarifier rapidement les règles d'usage et de conformité.

### Idées d'usage
- Volume approx: 28
- Verbatim: « Sales analysis »
- Implication managériale: Prioriser des cas d'usage métiers à ROI mesurable.

### Besoins d'accompagnement
- Volume approx: 2
- Verbatim: « How to switch traditional WoW to AI WoW to save time ?
Tools box on how use in an efficient matter the AI. »
- Implication managériale: Structurer un plan de formation court, orienté pratique.

## 9) Rationalisation des graphiques
- Graphiques conservés (4): usage_ai_travail_distribution.png, repartition_roles.png, expertise_x_usage_travail.png, personnel_x_travail.png.
- Graphiques supprimés: ceux redondants/non décisifs de la version précédente.
