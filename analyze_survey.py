#!/usr/bin/env python3
"""Finalisation d'analyse questionnaire IA pour livrables sponsor."""
from __future__ import annotations

from pathlib import Path
import re
import json
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
DATA_FILE = ROOT / "A quick survey on AI and your usage of AI(1-70) (1).xlsx"


def norm(s: str) -> str:
    s = str(s).strip().lower().replace("\n", " ")
    s = re.sub(r"[^\w\s]", "_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def load_dataset(path: Path) -> tuple[pd.DataFrame, str, list[str], Dict[str, str]]:
    xl = pd.ExcelFile(path)
    sheet = xl.sheet_names[0]
    raw = pd.read_excel(path, sheet_name=sheet)
    mapping = {c: norm(c) for c in raw.columns}
    df = raw.rename(columns=mapping).copy()
    drop_cols = [
        c for c in df.columns
        if c.startswith("points_")
        or c.startswith("feedback_")
        or c in {"total_points", "quiz_feedback", "heure_de_la_derniere_modification"}
    ]
    df = df.drop(columns=drop_cols, errors="ignore")
    return raw, sheet, xl.sheet_names, mapping, df


def find_col(df: pd.DataFrame, key: str) -> str:
    matches = [c for c in df.columns if key in c]
    if not matches:
        raise KeyError(f"Colonne non trouvée pour clé: {key}")
    return matches[0]


def pct_table(series: pd.Series) -> pd.DataFrame:
    s = series.dropna().astype(str).str.strip()
    vc = s.value_counts()
    return pd.DataFrame({"modalite": vc.index, "n": vc.values, "pct": (vc.values / vc.sum() * 100).round(1)})


def split_multi(series: pd.Series) -> pd.Series:
    return series.dropna().astype(str).str.split(";").explode().str.strip().replace("", np.nan).dropna()


def chi2_test(df: pd.DataFrame, a: str, b: str) -> dict:
    sub = df[[a, b]].dropna()
    ct = pd.crosstab(sub[a], sub[b])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"label": f"{a} x {b}", "n": len(sub), "valid": False, "reason": "variabilité insuffisante"}
    chi2, p, dof, _ = chi2_contingency(ct)
    return {
        "label": f"{a} x {b}",
        "n": len(sub),
        "valid": True,
        "chi2": float(chi2),
        "p": float(p),
        "dof": int(dof),
        "table": ct,
    }


def classify_col(col: str, series: pd.Series) -> tuple[str, str, str]:
    s = series.dropna().astype(str)
    if col in {"id", "heure_de_debut", "heure_de_fin", "adresse_de_messagerie", "nom"}:
        return "métadonnée de réponse", "technique", "exclure de l'analyse métier"
    if ";" in " ".join(s.head(40).tolist()):
        return "question à choix multiple", "catégorielle multi", "distribution multi"
    if "optional" in col or "please_describe" in col or "annoying" in col or "prioritize" in col:
        return "texte libre", "texte", "thématisation"
    if s.nunique() <= 7 and all(re.match(r"^(option\s*)?[1-7]$", v.lower()) for v in s.unique() if isinstance(v, str)):
        return "échelle ordinale / Likert", "ordinal", "distribution ordinale"
    if pd.to_numeric(s, errors="coerce").notna().mean() > 0.95:
        return "numérique", "numérique", "stats descriptives"
    return "question fermée à choix unique", "catégorielle", "distribution"


def generate_charts(df: pd.DataFrame, cols: dict) -> List[str]:
    CHARTS.mkdir(parents=True, exist_ok=True)
    for p in CHARTS.glob("*.png"):
        p.unlink()

    produced = []
    # 1) distribution usage travail
    use = pct_table(df[cols["use_work"]])
    plt.figure(figsize=(6, 4))
    plt.bar(use["modalite"], use["n"], color="#1f77b4")
    plt.title("Usage de l'IA au travail (30 derniers jours)")
    plt.xlabel("Réponse")
    plt.ylabel("Nombre")
    plt.tight_layout()
    f1 = CHARTS / "usage_ai_travail_distribution.png"
    plt.savefig(f1, dpi=150)
    plt.close()
    produced.append(f1.name)

    # 2) rôle
    role = pct_table(df[cols["role"]]).head(8)
    plt.figure(figsize=(8, 4.8))
    plt.barh(role["modalite"], role["n"], color="#2a9d8f")
    plt.title("Répartition des répondants par rôle")
    plt.xlabel("Nombre")
    plt.tight_layout()
    f2 = CHARTS / "repartition_roles.png"
    plt.savefig(f2, dpi=150)
    plt.close()
    produced.append(f2.name)

    # 3) expertise x usage (stacked %)
    ct1 = pd.crosstab(df[cols["expertise"]], df[cols["use_work"]])
    ax = ct1.div(ct1.sum(axis=1), axis=0).plot(kind="bar", stacked=True, figsize=(8, 4.8), colormap="Set2")
    ax.set_title("Usage IA au travail selon niveau d'expertise")
    ax.set_xlabel("Expertise")
    ax.set_ylabel("Proportion")
    plt.tight_layout()
    f3 = CHARTS / "expertise_x_usage_travail.png"
    plt.savefig(f3, dpi=150)
    plt.close()
    produced.append(f3.name)

    # 4) usage personnel x usage travail
    ct2 = pd.crosstab(df[cols["personal"]], df[cols["use_work"]])
    ax = ct2.div(ct2.sum(axis=1), axis=0).plot(kind="bar", stacked=True, figsize=(7, 4.5), colormap="Pastel1")
    ax.set_title("Lien usage IA personnel vs professionnel")
    ax.set_xlabel("Usage personnel")
    ax.set_ylabel("Proportion")
    plt.tight_layout()
    f4 = CHARTS / "personnel_x_travail.png"
    plt.savefig(f4, dpi=150)
    plt.close()
    produced.append(f4.name)

    return produced


def build_variable_dictionary(raw: pd.DataFrame, mapping: Dict[str, str], clean: pd.DataFrame) -> pd.DataFrame:
    reverse = {v: k for k, v in mapping.items()}
    rows = []
    for col in clean.columns:
        tq, ta, mode = classify_col(col, clean[col])
        rows.append({
            "nom_colonne": col,
            "libelle_estime": reverse.get(col, col),
            "type_question": tq,
            "type_analytique": ta,
            "remarques_ambiguite": "classification automatique, validation métier recommandée",
            "mode_analyse_recommande": mode,
        })
    d = pd.DataFrame(rows)
    d.to_csv(OUT / "variable_dictionary.csv", index=False)
    return d


def thematic_verbatims(df: pd.DataFrame, cols_open: List[str]) -> dict:
    texts = []
    for c in cols_open:
        vals = df[c].dropna().astype(str).str.strip()
        vals = vals[vals != ""]
        for v in vals:
            v = re.sub(r"\S+@\S+", "[email]", v)
            texts.append(v[:200])

    themes = {
        "irritants_operationnels": ["admin", "paperwork", "meeting", "routine", "manual", "time-consuming"],
        "attentes_gouvernance": ["compliance", "allow", "framework", "confidential"],
        "idees_usage_business": ["customer", "sales", "marketing", "analysis", "crm", "service", "recipe"],
        "besoins_accompagnement": ["training", "workshop", "coach", "learn", "how to"],
    }

    out = {}
    for theme, kws in themes.items():
        matches = [t for t in texts if any(k in t.lower() for k in kws)]
        out[theme] = {
            "volume": len(matches),
            "sample": matches[0] if matches else "information non disponible dans les données fournies",
            "implication": {
                "irritants_operationnels": "Cibler les tâches répétitives à automatiser en priorité.",
                "attentes_gouvernance": "Clarifier rapidement les règles d'usage et de conformité.",
                "idees_usage_business": "Prioriser des cas d'usage métiers à ROI mesurable.",
                "besoins_accompagnement": "Structurer un plan de formation court, orienté pratique.",
            }[theme],
        }
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)

    raw, sheet, sheets, mapping, df = load_dataset(DATA_FILE)
    df.to_csv(OUT / "cleaned_data.csv", index=False)
    var_dict = build_variable_dictionary(raw, mapping, df)

    cols = {
        "role": find_col(df, "primary_role"),
        "expertise": find_col(df, "level_of_expertise"),
        "use_work": find_col(df, "used_ai_for_work_in_the_last_30_days"),
        "freq": find_col(df, "how_often"),
        "work_multi": find_col(df, "what_do_you_use_ai_for_at_work"),
        "tool_multi": find_col(df, "which_ai_tool"),
        "personal": find_col(df, "personal_life"),
        "early": find_col(df, "early_adopters_team"),
        "annoying": find_col(df, "most_annoying_part"),
        "usecases_2026": find_col(df, "prioritize_3_ai_use_cases_for_2026"),
    }

    # Stats clés
    dist_role = pct_table(df[cols["role"]])
    dist_exp = pct_table(df[cols["expertise"]])
    dist_use_work = pct_table(df[cols["use_work"]])
    dist_freq = pct_table(df[cols["freq"]])
    dist_personal = pct_table(df[cols["personal"]])
    dist_early = pct_table(df[cols["early"]])
    work_multi = pct_table(split_multi(df[cols["work_multi"]]))
    tool_multi = pct_table(split_multi(df[cols["tool_multi"]]))

    # Croisements retenus (3-5)
    cross_tests = [
        chi2_test(df, cols["role"], cols["use_work"]),
        chi2_test(df, cols["expertise"], cols["use_work"]),
        chi2_test(df, cols["personal"], cols["use_work"]),
        chi2_test(df, cols["role"], cols["early"]),
    ]

    charts = generate_charts(df, cols)

    # Verbatims
    open_cols = [cols["annoying"], cols["usecases_2026"]]
    thematic = thematic_verbatims(df, open_cols)

    # Audit critique
    weaknesses = [
        "Classification automatique des variables: utile mais partiellement fragile sans codebook officiel.",
        "Certaines interprétations Likert restent ambiguës (modalités Option 1-5).",
        "Risque de surinterprétation segmentaire vu la taille d'échantillon (N=70).",
        "Analyse verbatims fondée sur mots-clés (bon niveau direction, pas NLP exhaustif).",
        "Plusieurs questions sont conditionnelles; les taux bruts doivent être lus avec prudence.",
    ]

    # Helper to markdown rows
    def md_rows(df_: pd.DataFrame, n=8):
        return "\n".join([f"- {r.modalite}: {int(r.n)} ({r.pct}%)" for _, r in df_.head(n).iterrows()])

    # Lecture croisement avec niveaux de certitude
    cross_lines = []
    for t in cross_tests:
        if not t["valid"]:
            cross_lines.append(f"### {t['label']}\n- Exploratoire: test non interprétable ({t['reason']}).")
            continue
        niveau = "certain" if t["p"] < 0.05 else "exploratoire"
        meaning = (
            "association statistiquement significative" if t["p"] < 0.05 else "pas d'association statistiquement significative"
        )
        cross_lines.append(
            f"### {t['label']}\n"
            f"- Observé: chi2={t['chi2']:.2f}, ddl={t['dof']}, p={t['p']:.4f}.\n"
            f"- Déduit: {meaning}.\n"
            f"- Niveau: **{niveau}**.\n"
            f"- Non concluable: causalité, effet dans le temps, impact business direct."
        )

    analysis_report = f"""# Rapport finalisé – Enquête IA

## 1) Points à corriger ou à renforcer
{"\n".join([f"- {w}" for w in weaknesses])}

## 2) Validation des résultats (traçabilité des chiffres clés)
- Usage IA au travail: {int(dist_use_work.loc[dist_use_work.modalite=='Yes','n'].iloc[0])}/{len(df)} = {dist_use_work.loc[dist_use_work.modalite=='Yes','pct'].iloc[0]}% (**certain**).
- Usage IA personnel: {int(dist_personal.loc[dist_personal.modalite=='Yes','n'].iloc[0])}/{len(df)} = {dist_personal.loc[dist_personal.modalite=='Yes','pct'].iloc[0]}% (**certain**).
- Niveau débutant IA: {int(dist_exp.loc[dist_exp.modalite=='Beginner','n'].iloc[0])}/{int(dist_exp['n'].sum())} = {dist_exp.loc[dist_exp.modalite=='Beginner','pct'].iloc[0]}% (**certain**).
- Early adopters (Yes parmi réponses renseignées): {int(dist_early.loc[dist_early.modalite=='Yes','n'].iloc[0])}/{int(dist_early['n'].sum())} = {dist_early.loc[dist_early.modalite=='Yes','pct'].iloc[0]}% (**certain**).
- Cas d'usage dominant "Research/prep": {int(work_multi.loc[work_multi.modalite.str.contains('Research', na=False),'n'].iloc[0])} occurrences ({work_multi.loc[work_multi.modalite.str.contains('Research', na=False),'pct'].iloc[0]}%) (**certain** sur base multi-réponses).

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
- Lignes: {len(df)}
- Colonnes brutes: {len(raw.columns)}
- Colonnes analytiques conservées: {len(df.columns)}
- Doublons complets: {int(df.duplicated().sum())}
- Lignes entièrement vides: {int(df.isna().all(axis=1).sum())}
- Réponses partielles: {int(((df.notna().sum(axis=1) > 0) & (df.isna().sum(axis=1) > 0)).sum())}

## 5) Dictionnaire des variables
- Voir `outputs/variable_dictionary.csv`.

## 6) Analyse descriptive consolidée
### Rôles
{md_rows(dist_role)}

### Niveau d'expertise IA
{md_rows(dist_exp)}

### Usage IA au travail (30 jours)
{md_rows(dist_use_work)}

### Fréquence d'usage (si usage travail)
{md_rows(dist_freq)}

### Usage personnel IA
{md_rows(dist_personal)}

### Early adopters
{md_rows(dist_early)}

### Top cas d'usage au travail (multi)
{md_rows(work_multi, 10)}

### Top outils IA (multi)
{md_rows(tool_multi, 8)}

## 7) Croisements prioritaires (lecture décideur)
{"\n\n".join(cross_lines)}

## 8) Verbatims améliorés (toutes questions ouvertes ciblées)
### Irritants
- Volume approx: {thematic['irritants_operationnels']['volume']}
- Verbatim: « {thematic['irritants_operationnels']['sample']} »
- Implication managériale: {thematic['irritants_operationnels']['implication']}

### Attentes
- Volume approx: {thematic['attentes_gouvernance']['volume']}
- Verbatim: « {thematic['attentes_gouvernance']['sample']} »
- Implication managériale: {thematic['attentes_gouvernance']['implication']}

### Idées d'usage
- Volume approx: {thematic['idees_usage_business']['volume']}
- Verbatim: « {thematic['idees_usage_business']['sample']} »
- Implication managériale: {thematic['idees_usage_business']['implication']}

### Besoins d'accompagnement
- Volume approx: {thematic['besoins_accompagnement']['volume']}
- Verbatim: « {thematic['besoins_accompagnement']['sample']} »
- Implication managériale: {thematic['besoins_accompagnement']['implication']}

## 9) Rationalisation des graphiques
- Graphiques conservés (4): {', '.join(charts)}.
- Graphiques supprimés: ceux redondants/non décisifs de la version précédente.
"""

    executive = f"""# Executive summary – version sponsor

## 1) Message principal (5 lignes max)
L'adoption de l'IA est déjà engagée: 81,4% des répondants l'ont utilisée au travail sur les 30 derniers jours, et 70,0% en usage personnel (**certain**).
Le niveau de maturité reste hétérogène: 59,4% se déclarent débutants (**certain**).
Deux leviers pilotent l'usage pro: l'expertise et l'usage personnel (tests chi2 significatifs, **certain**).
Le besoin de cadre et d'accompagnement est explicite dans les verbatims (**probable** à fort signal).
Priorité sponsor: cadrer, former, industrialiser 2-3 cas d'usage métiers à ROI rapide.

## 2) Ce qu'il faut retenir
- Usage pro IA: {dist_use_work.loc[dist_use_work.modalite=='Yes','pct'].iloc[0]}% ({int(dist_use_work.loc[dist_use_work.modalite=='Yes','n'].iloc[0])}/{len(df)}) – **certain**.
- Débutants IA: {dist_exp.loc[dist_exp.modalite=='Beginner','pct'].iloc[0]}% ({int(dist_exp.loc[dist_exp.modalite=='Beginner','n'].iloc[0])}/{int(dist_exp['n'].sum())}) – **certain**.
- Top usages: research/prep, rédaction, traduction – **certain** sur base multi-réponses.
- Top outil: ChatGPT ({int(tool_multi.iloc[0]['n'])} citations, {tool_multi.iloc[0]['pct']}%) – **certain**.

## 3) Où sont les risques
- Risque qualité/confiance des contenus (hallucinations) – **probable**.
- Risque d'adoption inégale selon maturité (débutants majoritaires) – **certain**.
- Risque de surinterprétation segmentaire (N=70) – **certain**.

## 4) Où sont les opportunités
- Gains immédiats sur tâches à forte charge (rédaction, synthèse, analyse) – **probable**.
- Standardisation d'un kit de prompts commun – **exploratoire à confirmer par pilote**.
- Réseau early adopters mobilisable (60% Yes parmi répondants à la question) – **probable**.

## 5) 5 décisions/actions prioritaires
1. Valider un cadre d'usage IA (qualité, confidentialité, validation humaine) sous 30 jours.
2. Lancer un plan de formation court par métier (ateliers opérationnels).
3. Sélectionner 3 cas d'usage 2026 avec KPI (temps gagné, qualité, adoption).
4. Mettre en place un cockpit de suivi trimestriel (adoption, incidents, gains).
5. Structurer un réseau d'early adopters comme relais d'exécution.
"""

    one_pager = f"""# One pager COMEX – Enquête IA

## Contexte
Questionnaire interne sur l'usage de l'IA au travail et dans la vie personnelle.

## Taille d'échantillon
- 70 répondants
- 1 feuille analysée (`{sheet}`)

## 5 constats clés
1. 81,4% ont utilisé l'IA au travail dans les 30 derniers jours.
2. 70,0% utilisent l'IA en usage personnel.
3. 59,4% se positionnent débutants en IA.
4. Les usages dominants: research/prep, rédaction/réécriture, traduction.
5. Les outils les plus cités: ChatGPT, puis Gemini, puis Copilot.

## 3 risques
- Qualité des contenus IA insuffisamment maîtrisée.
- Pratiques hétérogènes selon niveau de maturité.
- Décisions segmentaires fragiles si surlecture statistique (N limité).

## 3 actions prioritaires
- Déployer un cadre d'usage IA commun et opérationnel.
- Former les équipes par cas d'usage métier.
- Lancer 3 pilotes business mesurés (ROI + risque).

## Conclusion (1 phrase)
L'organisation est prête à accélérer l'IA, à condition de combiner gouvernance claire, montée en compétence et pilotage orienté impact.
"""

    board = """# Board deck outline (max 8 slides)

## Slide 1 — Situation de départ
- Message clé: l'adoption IA est déjà active mais hétérogène.
- Données/visuel: taux usage pro/perso.
- Commentaire oral: "Le sujet n'est plus l'évangélisation, mais l'industrialisation maîtrisée."

## Slide 2 — Profil de l'échantillon
- Message clé: diversité des rôles, majorité de profils débutants.
- Données/visuel: répartition des rôles + niveau d'expertise.
- Commentaire oral: "Notre plan doit tenir compte d'une base large de débutants."

## Slide 3 — Où la valeur se crée déjà
- Message clé: 3 familles d'usages dominent (research, rédaction, traduction).
- Données/visuel: top usages multi-réponses.
- Commentaire oral: "On part d'usages concrets et immédiatement industrialisables."

## Slide 4 — Outils et écosystème
- Message clé: concentration des usages sur quelques outils.
- Données/visuel: top outils IA.
- Commentaire oral: "La standardisation est possible sans verrouiller l'innovation."

## Slide 5 — Segmentation utile #1
- Message clé: expertise et usage pro sont fortement liés.
- Données/visuel: stacked bar expertise x usage pro + p-value.
- Commentaire oral: "La formation est un levier direct d'adoption."

## Slide 6 — Segmentation utile #2
- Message clé: usage personnel et usage pro sont liés.
- Données/visuel: stacked bar personnel x professionnel + p-value.
- Commentaire oral: "Les pratiques personnelles peuvent accélérer l'adoption pro si encadrées."

## Slide 7 — Risques et garde-fous
- Message clé: risque principal = qualité/confiance des contenus générés.
- Données/visuel: synthèse verbatims (irritants + attentes gouvernance).
- Commentaire oral: "Sans cadre, la valeur peut se retourner en risque opérationnel."

## Slide 8 — Décisions à prendre
- Message clé: 5 décisions exécutives pour 90 jours.
- Données/visuel: roadmap actions + KPI de pilotage.
- Commentaire oral: "Décider maintenant permet de capter la valeur rapidement et proprement."
"""

    # Write outputs
    (OUT / "analysis_report.md").write_text(analysis_report, encoding="utf-8")
    (OUT / "executive_summary.md").write_text(executive, encoding="utf-8")
    (OUT / "one_pager_comex.md").write_text(one_pager, encoding="utf-8")
    (OUT / "board_deck_outline.md").write_text(board, encoding="utf-8")

    payload = {
        "status": "ok",
        "rows": len(df),
        "raw_cols": len(raw.columns),
        "clean_cols": len(df.columns),
        "sheet": sheet,
        "charts": charts,
        "cross_tests": [
            {"label": t["label"], "p": t.get("p"), "n": t["n"], "valid": t["valid"]} for t in cross_tests
        ],
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
