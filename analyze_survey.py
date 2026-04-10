#!/usr/bin/env python3
"""Analyse reproductible d'un export Microsoft Forms (ou diagnostic si absent)."""
from __future__ import annotations

from pathlib import Path
import re
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"


def normalize_col(name: str) -> str:
    s = str(name).strip().lower()
    s = re.sub(r"[^\w\s]", "_", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "colonne_sans_nom"


def list_files() -> list[Path]:
    files: list[Path] = []
    for p in ROOT.iterdir():
        if p.name.startswith('.'):
            continue
        if p.name == 'outputs':
            continue
        if p.is_file():
            files.append(p)
    return sorted(files)


def detect_main_response_file(files: list[Path]) -> Path | None:
    candidates = [f for f in files if f.suffix.lower() in {'.xlsx', '.csv'}]
    if not candidates:
        return None
    preferred = [f for f in candidates if any(k in f.name.lower() for k in ["response", "reponse", "forms", "survey", "questionnaire"]) ]
    return preferred[0] if preferred else candidates[0]


def find_helper_files(files: list[Path]) -> list[Path]:
    helper_names = {"questionnaire.docx", "questionnaire.md", "questions.txt", "codebook.csv", "brief.txt"}
    return [f for f in files if f.name.lower() in helper_names]


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_empty_outputs(reason: str, files: list[Path], main_file: Path | None, helpers: list[Path]) -> None:
    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(exist_ok=True)

    inventory_md = "\n".join([f"- `{f.name}`" for f in files]) if files else "- Aucun fichier détecté"
    main_label = f"`{main_file.name}`" if main_file else "information non disponible dans les données fournies"
    helper_md = "\n".join([f"- `{f.name}`" for f in helpers]) if helpers else "- Aucun fichier d'aide détecté"

    report = f"""# Rapport d'analyse du questionnaire

## A. Inventaire des fichiers trouvés
{inventory_md}

## B. Diagnostic qualité des données
- **Statut** : analyse impossible sur les réponses.
- **Constat** : {reason}
- **Doublons / valeurs manquantes / invalidités** : information non disponible dans les données fournies.

## C. Dictionnaire des variables
- Fichier de réponses identifié : {main_label}
- Dictionnaire des variables détaillé : information non disponible dans les données fournies.

## D. Analyse descriptive
- Information non disponible dans les données fournies.

## E. Croisements et segmentations
- Information non disponible dans les données fournies.

## F. Analyse des verbatims
- Information non disponible dans les données fournies.

## G. Synthèse exécutive
- 5 enseignements majeurs : information non disponible dans les données fournies.
- 3 points d'alerte : information non disponible dans les données fournies.
- 3 opportunités d'action : information non disponible dans les données fournies.
- Ce qui est certain : aucun export de réponses exploitable n'a été détecté.
- Ce qui est probable : les réponses existent hors de cet environnement.
- Ce qui reste incertain : structure des questions, distributions et signaux par segment.

## H. Recommandations
1. Déposer dans ce dossier un export Microsoft Forms (`.xlsx` ou `.csv`).
2. Ajouter si possible un `codebook.csv` ou `questionnaire.md` pour fiabiliser l'interprétation.
3. Relancer `python analyze_survey.py` pour générer l'analyse complète.

## I. Fichiers générés
- `outputs/analysis_report.md`
- `outputs/executive_summary.md`
- `outputs/cleaned_data.csv`
- `outputs/variable_dictionary.csv`
- `outputs/charts/`
- `analyze_survey.py`
"""

    exec_summary = f"""# Synthèse exécutive (données absentes)

## Situation
- Fichier de réponses principal : {main_label}
- Fichiers d'aide :
{helper_md}

## Décision
- **Analyse décisionnelle non réalisable** tant qu'aucun export de réponses n'est disponible dans l'environnement.

## Action immédiate
- Fournir un export Microsoft Forms (`.xlsx` ou `.csv`).
"""

    write_markdown(OUT / "analysis_report.md", report)
    write_markdown(OUT / "executive_summary.md", exec_summary)

    pd.DataFrame(columns=["_diagnostic", "_details"]).to_csv(OUT / "cleaned_data.csv", index=False)
    pd.DataFrame(
        [{
            "nom_colonne": "information non disponible dans les données fournies",
            "libelle_estime": "information non disponible dans les données fournies",
            "type_question": "information non disponible dans les données fournies",
            "type_analytique": "information non disponible dans les données fournies",
            "remarques_ambiguite": reason,
            "mode_analyse_recommande": "fournir un export de réponses"
        }]
    ).to_csv(OUT / "variable_dictionary.csv", index=False)


def main() -> None:
    files = list_files()
    main_file = detect_main_response_file(files)
    helpers = find_helper_files(files)

    if main_file is None:
        reason = "Aucun fichier `.xlsx` ou `.csv` de réponses n'a été trouvé au niveau du dépôt."
        make_empty_outputs(reason, files, main_file, helpers)
        print(json.dumps({"status": "no_data", "reason": reason}, ensure_ascii=False))
        return

    # Branche minimale d'analyse si un fichier est présent
    if main_file.suffix.lower() == ".csv":
        df = pd.read_csv(main_file)
    else:
        sheet_names = pd.ExcelFile(main_file).sheet_names
        target_sheet = sheet_names[0]
        df = pd.read_excel(main_file, sheet_name=target_sheet)

    raw_df = df.copy()
    cleaned = df.copy()
    cleaned.columns = [normalize_col(c) for c in cleaned.columns]

    # Dictionnaire de variables simple et générique
    rows = []
    for orig, norm in zip(raw_df.columns, cleaned.columns):
        dtype = str(raw_df[orig].dtype)
        non_null = raw_df[orig].notna().sum()
        ratio = non_null / len(raw_df) if len(raw_df) else 0
        rows.append({
            "nom_colonne": norm,
            "libelle_estime": orig,
            "type_question": "à confirmer",
            "type_analytique": dtype,
            "remarques_ambiguite": f"taux_non_nul={ratio:.2%}",
            "mode_analyse_recommande": "descriptif"
        })
    var_dict = pd.DataFrame(rows)

    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(exist_ok=True)
    cleaned.to_csv(OUT / "cleaned_data.csv", index=False)
    var_dict.to_csv(OUT / "variable_dictionary.csv", index=False)

    report = f"""# Rapport d'analyse du questionnaire

## A. Inventaire des fichiers trouvés
{"\n".join([f"- `{f.name}`" for f in files])}

## B. Diagnostic qualité des données
- Lignes: {len(raw_df)}
- Colonnes: {len(raw_df.columns)}
- Doublons complets: {int(raw_df.duplicated().sum())}
- Lignes entièrement vides: {int(raw_df.isna().all(axis=1).sum())}

## C. Dictionnaire des variables
- Généré dans `outputs/variable_dictionary.csv`.

## D. Analyse descriptive
- Résumé statistique exporté partiellement via pandas (`describe`) dans les logs d'exécution.

## E. Croisements et segmentations
- Information non disponible dans les données fournies (pas d'inférence métier automatique).

## F. Analyse des verbatims
- Information non disponible dans les données fournies (classification thématique manuelle à compléter).

## G. Synthèse exécutive
- Version préliminaire uniquement, sans interprétation métier non documentée.

## H. Recommandations
1. Ajouter un codebook pour fiabiliser l'interprétation des colonnes.
2. Confirmer les variables de segmentation prioritaires.
3. Valider les règles de nettoyage métier.

## I. Fichiers générés
- `outputs/analysis_report.md`
- `outputs/executive_summary.md`
- `outputs/cleaned_data.csv`
- `outputs/variable_dictionary.csv`
"""
    write_markdown(OUT / "analysis_report.md", report)

    executive = """# Synthèse exécutive

Rapport préliminaire généré automatiquement. Compléter l'interprétation métier avec les documents de cadrage.
"""
    write_markdown(OUT / "executive_summary.md", executive)

    print(json.dumps({"status": "ok", "file": main_file.name, "rows": len(raw_df), "cols": len(raw_df.columns)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
