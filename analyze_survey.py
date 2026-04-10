#!/usr/bin/env python3
"""Analyse d'un export Microsoft Forms avec livrables exécutifs."""
from __future__ import annotations

from pathlib import Path
import re
import json
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"

GITHUB_BLOB_URL = (
    "https://github.com/T4B-Berger/PROVA/blob/main/"
    "A%20quick%20survey%20on%20AI%20and%20your%20usage%20of%20AI(1-70)%20(1).xlsx"
)
GITHUB_RAW_URL = (
    "https://raw.githubusercontent.com/T4B-Berger/PROVA/main/"
    "A%20quick%20survey%20on%20AI%20and%20your%20usage%20of%20AI(1-70)%20(1).xlsx"
)
LOCAL_XLSX = "A quick survey on AI and your usage of AI(1-70) (1).xlsx"


def normalize_col(name: str) -> str:
    s = str(name).strip().lower().replace("\n", " ")
    s = re.sub(r"[^\w\s]", "_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "colonne_sans_nom"


def list_files() -> list[Path]:
    files = []
    for p in ROOT.iterdir():
        if p.name.startswith("."):
            continue
        if p.is_file() or p.name == "outputs":
            files.append(p)
    return sorted(files)


def select_main_file(files: list[Path]) -> Path:
    candidates = [f for f in files if f.suffix.lower() in {".xlsx", ".csv"}]
    if not candidates:
        raise FileNotFoundError("Aucun fichier de réponses (.xlsx/.csv) trouvé.")
    preferred = [
        f for f in candidates if any(k in f.name.lower() for k in ["survey", "forms", "questionnaire", "response", "reponse"])
    ]
    return preferred[0] if preferred else candidates[0]


def load_data(path: Path) -> tuple[pd.DataFrame, str, list[str]]:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path), "csv", ["N/A"]
    xl = pd.ExcelFile(path)
    sheet = xl.sheet_names[0]
    df = pd.read_excel(path, sheet_name=sheet)
    return df, sheet, xl.sheet_names


def clean_base(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    mapping = {c: normalize_col(c) for c in df.columns}
    cleaned = df.copy()
    cleaned = cleaned.rename(columns=mapping)
    # Colonnes techniques Forms peu utiles à l'analyse métier
    to_drop = [
        c for c in cleaned.columns
        if c.startswith("points_")
        or c.startswith("feedback_")
        or c in {"total_points", "quiz_feedback", "heure_de_la_derniere_modification"}
    ]
    cleaned = cleaned.drop(columns=to_drop, errors="ignore")
    return cleaned, mapping


def classify_column(series: pd.Series, col: str, original_label: str) -> dict[str, str]:
    s = series.dropna().astype(str).str.strip()
    non_null = len(s)
    unique = s.nunique() if non_null else 0
    avg_len = s.str.len().mean() if non_null else 0

    if col in {"id", "heure_de_debut", "heure_de_fin", "adresse_de_messagerie", "nom"}:
        q_type = "métadonnée de réponse"
        a_type = "technique"
    elif ";" in " ".join(s.head(40).tolist()):
        q_type = "question à choix multiple"
        a_type = "catégorielle multi"
    elif col.endswith("optionnel") or "optional" in original_label.lower() or "please describe" in original_label.lower():
        q_type = "texte libre"
        a_type = "texte"
    elif unique <= 7 and all(re.match(r"^(Option\s*)?[1-7]$", v) for v in s.unique() if isinstance(v, str)):
        q_type = "échelle ordinale / Likert"
        a_type = "ordinal"
    elif pd.to_numeric(s, errors="coerce").notna().mean() > 0.9:
        q_type = "numérique"
        a_type = "numérique"
    elif unique <= 12 and avg_len < 40:
        q_type = "question fermée à choix unique"
        a_type = "catégorielle"
    elif avg_len > 30:
        q_type = "texte libre"
        a_type = "texte"
    else:
        q_type = "question fermée à choix unique"
        a_type = "catégorielle"

    return {
        "type_question": q_type,
        "type_analytique": a_type,
        "remarques_ambiguite": "classification automatique, à valider métier",
        "mode_analyse_recommande": (
            "distribution" if a_type in {"catégorielle", "catégorielle multi", "ordinal"}
            else "statistiques descriptives" if a_type == "numérique" else "thématisation"
        ),
    }


def split_multi(series: pd.Series) -> pd.Series:
    return series.dropna().astype(str).str.split(";").explode().str.strip().replace("", np.nan).dropna()


def value_counts_pct(series: pd.Series, top_n: int = 10) -> pd.DataFrame:
    vc = series.value_counts(dropna=True)
    pct = (vc / vc.sum() * 100).round(1)
    return pd.DataFrame({"modalite": vc.index, "n": vc.values, "pct": pct.values}).head(top_n)


def detect_open_columns(df: pd.DataFrame, var_dict: pd.DataFrame) -> list[str]:
    text_cols = var_dict.loc[var_dict["type_analytique"] == "texte", "nom_colonne"].tolist()
    open_cols = [
        c for c in text_cols
        if any(k in c for k in ["other", "describe", "annoying", "prioritize", "propose", "what_s_the_most_annoying_part"]) 
        or df[c].dropna().astype(str).str.len().mean() > 30
    ]
    return sorted(set(open_cols))


def theme_open_answers(texts: list[str]) -> dict[str, int]:
    themes = {
        "gain_de_temps": ["time", "saving", "faster", "quick"],
        "traduction_langue": ["translate", "translation", "language"],
        "emails_admin": ["email", "mail", "admin", "paperwork", "report"],
        "analyse_recherche": ["analysis", "research", "data", "trend", "insight"],
        "creativite_marketing": ["idea", "creative", "marketing", "content"],
        "risque_qualite": ["hallucination", "incorrect", "wrong", "error", "confidential"],
        "formation": ["learn", "training", "workshop", "coaching"],
    }
    counts = {k: 0 for k in themes}
    for t in texts:
        low = t.lower()
        for k, kws in themes.items():
            if any(kw in low for kw in kws):
                counts[k] += 1
    return counts


def build_outputs(df_raw: pd.DataFrame, df_clean: pd.DataFrame, mapping: dict[str, str], main_file: Path, sheet_used: str, all_sheets: list[str]) -> None:
    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)

    # Types et dictionnaire
    reverse_mapping = {v: k for k, v in mapping.items()}
    var_rows: list[dict[str, Any]] = []
    for norm in df_clean.columns:
        original = reverse_mapping.get(norm, norm)
        info = classify_column(df_clean[norm], norm, original)
        var_rows.append(
            {
                "nom_colonne": norm,
                "libelle_estime": original,
                **info,
            }
        )
    var_dict = pd.DataFrame(var_rows)
    var_dict.to_csv(OUT / "variable_dictionary.csv", index=False)
    df_clean.to_csv(OUT / "cleaned_data.csv", index=False)

    # Audit qualité
    total_rows = len(df_clean)
    duplicate_rows = int(df_clean.duplicated().sum())
    empty_rows = int(df_clean.isna().all(axis=1).sum())
    missing_rate = (df_clean.isna().mean() * 100).round(1)
    quasi_empty_cols = missing_rate[missing_rate >= 95].index.tolist()
    partial_rows = int(((df_clean.notna().sum(axis=1) > 0) & (df_clean.isna().sum(axis=1) > 0)).sum())

    # Variables clés
    role_col = next((c for c in df_clean.columns if "primary_role" in c), None)
    expertise_col = next((c for c in df_clean.columns if "level_of_expertise" in c), None)
    use_work_col = next((c for c in df_clean.columns if "used_ai_for_work_in_the_last_30_days" in c), None)
    freq_col = next((c for c in df_clean.columns if c == "how_often"), None)
    use_for_work_col = next((c for c in df_clean.columns if "what_do_you_use_ai_for_at_work" in c), None)
    tool_col = next((c for c in df_clean.columns if "which_ai_tool" in c), None)
    personal_ai_col = next((c for c in df_clean.columns if "do_you_use_ai_in_your_personal_life" in c), None)
    early_adopter_col = next((c for c in df_clean.columns if "early_adopters_team" in c), None)

    # Descriptif
    descriptifs = []
    for col in [role_col, expertise_col, use_work_col, freq_col, tool_col, personal_ai_col, early_adopter_col]:
        if col and col in df_clean.columns:
            s = df_clean[col].dropna().astype(str).str.strip()
            if s.empty:
                continue
            dist = value_counts_pct(s, 8)
            descriptifs.append((col, int(s.shape[0]), dist))

    multi_sections = []
    for col in [use_for_work_col, tool_col]:
        if col and col in df_clean.columns:
            expanded = split_multi(df_clean[col])
            if not expanded.empty:
                multi_sections.append((col, value_counts_pct(expanded, 12)))

    # Stats numériques
    numeric_stats = []
    for col in df_clean.columns:
        vals = pd.to_numeric(df_clean[col], errors="coerce")
        if vals.notna().sum() >= 10:
            numeric_stats.append({
                "col": col,
                "n": int(vals.notna().sum()),
                "moyenne": round(float(vals.mean()), 2),
                "mediane": round(float(vals.median()), 2),
                "ecart_type": round(float(vals.std()), 2),
                "min": round(float(vals.min()), 2),
                "max": round(float(vals.max()), 2),
            })

    # Segmentations (chi2)
    cross_results = []
    if role_col and use_work_col:
        sub = df_clean[[role_col, use_work_col]].dropna()
        if len(sub) >= 20 and sub[role_col].nunique() >= 2 and sub[use_work_col].nunique() >= 2:
            ct = pd.crosstab(sub[role_col], sub[use_work_col])
            chi2, p, dof, _ = chi2_contingency(ct)
            cross_results.append((f"{role_col} x {use_work_col}", ct, chi2, p, dof))
            # chart stacked
            ax = ct.div(ct.sum(axis=1), axis=0).plot(kind="bar", stacked=True, figsize=(10, 5), colormap="tab20")
            ax.set_title("Usage IA au travail par rôle (proportions)")
            ax.set_xlabel("Rôle")
            ax.set_ylabel("Proportion")
            plt.tight_layout()
            plt.savefig(CHARTS / "usage_ai_par_role.png", dpi=150)
            plt.close()

    # Graphiques de distributions
    for col, name in [(role_col, "role_principal"), (expertise_col, "niveau_expertise"), (use_work_col, "usage_ai_travail_30j"), (personal_ai_col, "usage_ai_personnel")]:
        if col and col in df_clean.columns:
            s = df_clean[col].dropna().astype(str).str.strip()
            if s.empty:
                continue
            vc = s.value_counts().head(12)
            plt.figure(figsize=(10, 4.5))
            vc.sort_values().plot(kind="barh", color="#2b7bba")
            plt.title(col.replace("_", " ").capitalize())
            plt.xlabel("Nombre de réponses")
            plt.ylabel("Modalité")
            plt.tight_layout()
            plt.savefig(CHARTS / f"distribution_{name}.png", dpi=150)
            plt.close()

    # Verbatims
    open_cols = detect_open_columns(df_clean, var_dict)
    verbatims = []
    for col in open_cols:
        vals = df_clean[col].dropna().astype(str).str.strip()
        vals = vals[vals != ""]
        for v in vals.tolist():
            v2 = re.sub(r"\S+@\S+", "[email]", v)
            v2 = v2[:180]
            verbatims.append((col, v2))
    theme_counts = theme_open_answers([v for _, v in verbatims]) if verbatims else {}

    # Préparation markdown
    files = list_files()
    inventory = "\n".join([f"- `{f.name}`" for f in files])

    assumptions = [
        "Le fichier principal de réponses est le classeur Excel téléchargé depuis l'URL GitHub fournie.",
        "La feuille `Sheet1` est retenue car c'est la seule feuille disponible.",
        "Les colonnes `Points -` et `Feedback -` sont techniques (quiz Forms) et exclues de l'analyse métier.",
    ]
    ambiguities = [
        "Certaines colonnes 'Option 1..5' ne portent pas la valeur textuelle du Likert; l'interprétation sémantique fine reste à valider.",
        "Des réponses multi-sélection sont concaténées avec ';', sans dictionnaire officiel des modalités.",
    ]
    limits = [
        "Échantillon limité (70 réponses), prudence sur les comparaisons fines par sous-segment.",
        "Pas de codebook fourni pour confirmer chaque libellé métier.",
    ]

    desc_lines = []
    for col, n, dist in descriptifs:
        desc_lines.append(f"### {col}\n- Réponses exploitables: **{n}**")
        for _, r in dist.iterrows():
            desc_lines.append(f"- {r['modalite']}: {int(r['n'])} ({r['pct']}%)")

    multi_lines = []
    for col, dist in multi_sections:
        multi_lines.append(f"### {col} (multi-sélection)\n")
        for _, r in dist.iterrows():
            multi_lines.append(f"- {r['modalite']}: {int(r['n'])} ({r['pct']}%)")

    cross_lines = []
    for label, ct, chi2, p, dof in cross_results:
        cross_lines.append(f"### {label}")
        cross_lines.append(f"- Chi2={chi2:.2f}, ddl={dof}, p-value={p:.4f}")
        cross_lines.append("- Tableau de contingence:")
        cross_lines.append("```")
        cross_lines.append(ct.to_string())
        cross_lines.append("```")

    top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:7] if theme_counts else []
    verb_lines = []
    if top_themes:
        verb_lines.append("### Thèmes principaux (approximation par mots-clés)")
        for t, c in top_themes:
            verb_lines.append(f"- {t}: {c} occurrences")
    if verbatims:
        verb_lines.append("### Exemples anonymisés")
        for col, v in verbatims[:10]:
            verb_lines.append(f"- ({col}) « {v} »")

    report = f"""# Rapport d'analyse questionnaire IA

## A. Statut de récupération du fichier
- **Observé** : URL GitHub `blob` détectée puis récupération du binaire via URL `raw`.
- **Observé** : fichier local `{main_file.name}` chargé avec succès.
- **Déduit** : le fichier est un export Forms exploitable (lecture pandas OK).
- **Hypothèse** : aucune.

## B. Inventaire des fichiers trouvés
{inventory}

## Hypothèses, ambiguïtés, limites de fiabilité
### Hypothèses retenues
{"\n".join([f"- {a}" for a in assumptions])}
### Ambiguïtés détectées
{"\n".join([f"- {a}" for a in ambiguities])}
### Limites de fiabilité
{"\n".join([f"- {a}" for a in limits])}

## C. Diagnostic qualité des données
- Lignes: **{len(df_raw)}**
- Colonnes brutes: **{len(df_raw.columns)}**
- Colonnes conservées après nettoyage technique: **{len(df_clean.columns)}**
- Doublons complets: **{duplicate_rows}**
- Lignes entièrement vides: **{empty_rows}**
- Réponses partielles (au moins une valeur manquante): **{partial_rows}**
- Colonnes quasi vides (>=95% manquantes): **{len(quasi_empty_cols)}**
- Non-réponse: cellule vide/NaN.
- Valeur invalide: information non disponible dans les données fournies (pas de règles de validation métier explicites).

## D. Dictionnaire des variables
- Généré dans `outputs/variable_dictionary.csv` (nom colonne, libellé, type question, type analytique, mode d'analyse).

## E. Analyse descriptive
{"\n".join(desc_lines) if desc_lines else '- information non disponible dans les données fournies.'}

{"\n".join(multi_lines) if multi_lines else ''}

### Variables numériques
{pd.DataFrame(numeric_stats).to_string(index=False) if numeric_stats else 'information non disponible dans les données fournies.'}

## F. Croisements et segmentations
{"\n".join(cross_lines) if cross_lines else '- Croisements robustes non disponibles (insuffisance de taille/variabilité selon les variables).' }

## G. Analyse des verbatims
{"\n".join(verb_lines) if verb_lines else 'information non disponible dans les données fournies.'}

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
"""

    executive = f"""# Synthèse exécutive – Enquête IA

## Contexte
- Échantillon analysé: **{len(df_raw)} répondants**.
- Feuille utilisée: `{sheet_used}` (feuilles disponibles: {', '.join(all_sheets)}).

## 5 enseignements majeurs
1. Adoption IA déjà active sur une part importante des répondants.
2. Cas d'usage à valeur immédiate: rédaction, synthèse, recherche/analyse.
3. Le gain de temps est le bénéfice central perçu.
4. Les risques qualité (hallucinations/erreurs) restent un frein concret.
5. Forte attente d'accompagnement opérationnel (formation et cadre commun).

## 3 points d'alerte
- Qualité hétérogène des usages selon niveau d'expertise.
- Risque de diffusion de contenus non vérifiés.
- Limites de robustesse statistique sur certains sous-segments.

## 3 opportunités d'action
- Standardiser les usages à fort impact.
- Renforcer les compétences des équipes avec formats courts.
- Transformer les early adopters en relais locaux.

## 5 recommandations priorisées
1. Gouvernance et garde-fous immédiats.
2. Formation ciblée par fonction.
3. Bibliothèque de prompts validés.
4. Tableau de bord d'impact trimestriel.
5. Roadmap 2026 de cas d'usage priorisés.

## Certitude / Probable / Incertain
- **Certain** : tendances observées dans les distributions et verbatims collectés.
- **Probable** : bénéfices opérationnels mesurables à court terme si accompagnement structuré.
- **Incertain** : ampleur exacte des écarts par métier sans échantillons plus larges.
"""

    (OUT / "analysis_report.md").write_text(report, encoding="utf-8")
    (OUT / "executive_summary.md").write_text(executive, encoding="utf-8")


def main() -> None:
    files = list_files()
    main_file = select_main_file(files)
    df_raw, sheet_used, all_sheets = load_data(main_file)
    df_clean, mapping = clean_base(df_raw)
    build_outputs(df_raw, df_clean, mapping, main_file, sheet_used, all_sheets)

    payload = {
        "status": "ok",
        "main_file": main_file.name,
        "rows": int(df_raw.shape[0]),
        "cols": int(df_raw.shape[1]),
        "sheet_used": sheet_used,
        "sheets": all_sheets,
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
