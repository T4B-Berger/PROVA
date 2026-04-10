from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"

st.set_page_config(page_title="Sponsor Report IA", layout="wide")


def find_col(df: pd.DataFrame, key: str) -> str:
    matches = [c for c in df.columns if key in c]
    if not matches:
        raise KeyError(f"Colonne non trouvée: {key}")
    return matches[0]


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(OUT / "cleaned_data.csv")


def pct_yes(df: pd.DataFrame, col: str) -> tuple[int, int, float]:
    s = df[col].dropna().astype(str).str.strip()
    yes = int((s == "Yes").sum())
    n = int(s.shape[0])
    pct = round(yes / n * 100, 1) if n else 0.0
    return yes, n, pct


def chi2(df: pd.DataFrame, a: str, b: str):
    sub = df[[a, b]].dropna()
    ct = pd.crosstab(sub[a], sub[b])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None, None, None, ct
    chi2_v, p, dof, _ = chi2_contingency(ct)
    return chi2_v, p, dof, ct


def extract_verbatims(df: pd.DataFrame):
    open_cols = [c for c in df.columns if "most_annoying_part" in c or "prioritize_3_ai_use_cases_for_2026" in c]
    texts = []
    for c in open_cols:
        vals = df[c].dropna().astype(str).str.strip()
        vals = vals[vals != ""]
        for v in vals:
            v = re.sub(r"\S+@\S+", "[email]", v)
            texts.append(v[:180])
    themes = {
        "Irritants opérationnels": ["admin", "paperwork", "meeting", "routine", "manual"],
        "Attentes de gouvernance": ["compliance", "framework", "confidential", "allow"],
        "Idées d'usage business": ["sales", "customer", "marketing", "analysis", "crm", "service"],
        "Besoins d'accompagnement": ["training", "workshop", "learn", "how to", "coach"],
    }
    out = []
    for theme, kws in themes.items():
        hits = [t for t in texts if any(k in t.lower() for k in kws)]
        out.append((theme, len(hits), hits[0] if hits else "information non disponible dans les données fournies"))
    return out


try:
    df = load_data()
except Exception as e:
    st.error(f"Impossible de charger les données: {e}")
    st.stop()

role_col = find_col(df, "primary_role")
exp_col = find_col(df, "level_of_expertise")
use_work_col = find_col(df, "used_ai_for_work_in_the_last_30_days")
personal_col = find_col(df, "personal_life")
early_col = find_col(df, "early_adopters_team")

yes_work, n_work, pct_work = pct_yes(df, use_work_col)
yes_pers, n_pers, pct_pers = pct_yes(df, personal_col)
exp = df[exp_col].dropna().astype(str)
beg_n = int((exp == "Beginner").sum())
beg_pct = round((beg_n / len(exp) * 100), 1) if len(exp) else 0.0

page = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Vue d’ensemble", "Segmentations", "Verbatims", "Recommandations", "Artefacts"],
)

if page == "Accueil":
    st.title("Restitution sponsor – Enquête IA")
    st.markdown("### Contexte")
    st.write("Questionnaire interne sur l'usage de l'IA, à visée décisionnelle (adoption, risques, priorités 2026).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Taille d'échantillon", f"{len(df)} répondants")
    c2.metric("Usage IA travail (Yes)", f"{pct_work}%")
    c3.metric("Usage IA personnel (Yes)", f"{pct_pers}%")

    st.markdown("### Message principal")
    st.info(
        f"L'adoption est engagée ({pct_work}% usage pro), mais la maturité reste hétérogène "
        f"({beg_pct}% débutants). Priorité: gouvernance + formation + cas d'usage à ROI rapide."
    )

    st.markdown("### 5 constats clés")
    st.write(
        "1) 81,4% usage IA au travail\n"
        "2) 70,0% usage IA personnel\n"
        "3) 59,4% débutants\n"
        "4) Usages dominants: research/prep, rédaction, traduction\n"
        "5) Outil dominant: ChatGPT"
    )

    st.markdown("### 3 actions prioritaires")
    st.write(
        "- Cadre d'usage IA (qualité/confidentialité/validation humaine)\n"
        "- Formation courte par métier\n"
        "- 3 pilotes business 2026 avec KPI"
    )

elif page == "Vue d’ensemble":
    st.title("Vue d’ensemble")
    a, b, c, d = st.columns(4)
    a.metric("Répondants", len(df))
    a.metric("Colonnes analytiques", df.shape[1])
    b.metric("Usage pro (Yes)", f"{yes_work}/{n_work}")
    b.metric("Usage perso (Yes)", f"{yes_pers}/{n_pers}")
    c.metric("Débutants IA", f"{beg_n}/{len(exp)}")
    early = df[early_col].dropna().astype(str)
    c.metric("Early adopters - Yes", f"{int((early=='Yes').sum())}/{len(early)}")
    d.metric("Rôles distincts", int(df[role_col].nunique(dropna=True)))
    d.metric("Expertises distinctes", int(df[exp_col].nunique(dropna=True)))

    st.markdown("### Graphiques clés")
    for name in [
        "usage_ai_travail_distribution.png",
        "repartition_roles.png",
        "expertise_x_usage_travail.png",
        "personnel_x_travail.png",
    ]:
        p = CHARTS / name
        if p.exists():
            st.image(str(p), caption=name)

    st.markdown("### Lecture courte")
    st.write("Adoption élevée mais hétérogène, avec un gradient fort lié à l'expertise et aux pratiques personnelles.")

elif page == "Segmentations":
    st.title("Segmentations utiles")
    tests = [
        (exp_col, use_work_col, "Expertise vs usage IA au travail"),
        (personal_col, use_work_col, "Usage personnel vs usage IA au travail"),
        (role_col, use_work_col, "Rôle vs usage IA au travail"),
        (role_col, early_col, "Rôle vs intérêt early adopters"),
    ]
    for a, b, label in tests:
        st.subheader(label)
        chi2_v, p, dof, ct = chi2(df, a, b)
        st.dataframe(ct)
        if p is None:
            st.warning("Test non interprétable (variabilité insuffisante).")
        else:
            niveau = "certain" if p < 0.05 else "exploratoire"
            st.write(f"Chi2={chi2_v:.2f}, ddl={dof}, p={p:.4f} → niveau **{niveau}**")
            st.caption("Limite: test d'association, pas de causalité; prudence sur petits sous-échantillons.")

elif page == "Verbatims":
    st.title("Analyse des verbatims")
    st.caption("Extraits anonymisés et tronqués.")
    for theme, vol, sample in extract_verbatims(df):
        st.markdown(f"### {theme}")
        st.write(f"Volume approximatif: **{vol}**")
        st.write(f"Exemple: « {sample} »")
        if theme == "Irritants opérationnels":
            st.write("Lecture managériale: cibler les tâches répétitives à automatiser en priorité.")
        elif theme == "Attentes de gouvernance":
            st.write("Lecture managériale: clarifier le cadre d'usage et conformité.")
        elif theme == "Idées d'usage business":
            st.write("Lecture managériale: prioriser 2-3 cas d'usage à ROI court terme.")
        else:
            st.write("Lecture managériale: déployer un accompagnement pratique par métier.")

elif page == "Recommandations":
    st.title("Recommandations priorisées")
    recos = [
        ("Cadre d'usage IA (qualité/confidentialité/validation)", "Direction IT / Data / Compliance", "Court terme"),
        ("Formation métier orientée cas d'usage", "RH + Managers métiers", "Court terme"),
        ("Sélection de 3 cas d'usage KPIisés", "Comex + Directions métiers", "Court terme"),
        ("Cockpit trimestriel adoption/risque/gains", "PMO Transformation", "Moyen terme"),
        ("Réseau early adopters comme relais", "RH + Sponsors locaux", "Moyen terme"),
    ]
    st.table(pd.DataFrame(recos, columns=["Recommandation", "Sponsor / propriétaire", "Horizon"]))

else:
    st.title("Artefacts")
    artifacts = [
        ("outputs/analysis_report.md", "Rapport analytique consolidé"),
        ("outputs/executive_summary.md", "Synthèse dirigeant"),
        ("outputs/one_pager_comex.md", "Note 1 page COMEX"),
        ("outputs/board_deck_outline.md", "Plan de deck board"),
        ("outputs/cleaned_data.csv", "Données nettoyées"),
        ("outputs/variable_dictionary.csv", "Dictionnaire de variables"),
    ]
    df_art = pd.DataFrame(artifacts, columns=["Fichier", "Description"]) 
    df_art["Existe"] = df_art["Fichier"].apply(lambda p: (ROOT / p).exists())
    st.dataframe(df_art)

    st.markdown("### Graphiques")
    for p in sorted(CHARTS.glob("*.png")):
        st.write(f"- {p.relative_to(ROOT)}")
