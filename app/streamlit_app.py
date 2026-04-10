from __future__ import annotations

from pathlib import Path
import re
import pandas as pd
import streamlit as st
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"

st.set_page_config(page_title="PROVA IA Transformation Cockpit", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 1.1rem; max-width: 1220px;}
h1, h2, h3 {color:#3B2A1A;}
.kpi-card {background:#FFFDF9;border:1px solid #E4D8C8;border-radius:14px;padding:14px 16px;margin-bottom:10px;}
.kpi-title {font-size:0.82rem;color:#7A6A57;text-transform:uppercase;}
.kpi-value {font-size:1.6rem;font-weight:700;color:#8C5A2B;}
.section-box {background:#FFFDF9;border-left:5px solid #8C5A2B;border-radius:8px;padding:12px 14px;margin:8px 0 14px 0;}
.badge-fact {display:inline-block;background:#E6EFE8;color:#24543A;padding:3px 8px;border-radius:999px;font-size:0.78rem;}
.badge-rec {display:inline-block;background:#EFE8DD;color:#5C4128;padding:3px 8px;border-radius:999px;font-size:0.78rem;}
.small {color:#6B6258;font-size:0.86rem;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_df() -> pd.DataFrame:
    return pd.read_csv(OUT / "cleaned_data.csv")


def find_col(df: pd.DataFrame, key: str) -> str:
    cols = [c for c in df.columns if key in c]
    if not cols:
        raise KeyError(f"Colonne absente: {key}")
    return cols[0]


def split_multi(series: pd.Series) -> pd.Series:
    return series.dropna().astype(str).str.split(";").explode().str.strip().replace("", pd.NA).dropna()


def pct_yes(df: pd.DataFrame, col: str) -> tuple[int, int, float]:
    s = df[col].dropna().astype(str).str.strip()
    y = int((s == "Yes").sum())
    n = int(len(s))
    p = round(y / n * 100, 1) if n else 0.0
    return y, n, p


def card(title: str, value: str, note: str = ""):
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div><div class='small'>{note}</div></div>",
        unsafe_allow_html=True,
    )


def chi2_table(df: pd.DataFrame, a: str, b: str):
    sub = df[[a, b]].dropna()
    ct = pd.crosstab(sub[a], sub[b])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None, None, None, ct
    c2, p, dof, _ = chi2_contingency(ct)
    return c2, p, dof, ct


TAXONOMY = {
    "irritant": ["admin", "manual", "paperwork", "routine", "time-consuming", "annoy"],
    "opportunite": ["improve", "faster", "save", "efficiency", "value", "better"],
    "risque": ["hallucination", "wrong", "error", "confidential", "risk", "compliance"],
    "formation": ["training", "learn", "coach", "workshop", "how to"],
    "cas_usage": ["analysis", "sales", "marketing", "customer", "translation", "summary", "automation"],
}


def tag_text(text: str) -> list[str]:
    t = text.lower()
    tags = []
    for tag, kws in TAXONOMY.items():
        if any(k in t for k in kws):
            tags.append(tag)
    return tags


def anonymize_text(text: str) -> str:
    text = re.sub(r"\S+@\S+", "[email]", str(text))
    return text[:220]


def respondent_block(row: pd.Series, cols: dict[str, str]) -> dict[str, str]:
    return {
        "Profil": f"Rôle: {row.get(cols['role'], 'n/a')} | Expertise: {row.get(cols['exp'], 'n/a')}",
        "Usages": str(row.get(cols['work_multi'], "information non disponible")),
        "Bénéfices": str(row.get(cols['benefits'], "information non disponible")),
        "Risques": str(row.get(cols['issues'], "information non disponible")),
        "Formation": str(row.get(cols['learn'], "information non disponible")),
        "Verbatims": str(row.get(cols['usecase'], "information non disponible")),
    }


# Data
DF = load_df()
COLS = {
    "role": find_col(DF, "primary_role"),
    "exp": find_col(DF, "level_of_expertise"),
    "use_work": find_col(DF, "used_ai_for_work_in_the_last_30_days"),
    "freq": find_col(DF, "how_often"),
    "work_multi": find_col(DF, "what_do_you_use_ai_for_at_work"),
    "personal": find_col(DF, "personal_life"),
    "early": find_col(DF, "early_adopters_team"),
    "annoy": find_col(DF, "most_annoying_part"),
    "usecase": find_col(DF, "prioritize_3_ai_use_cases_for_2026"),
    "benefits": find_col(DF, "benefits_you_ve_experienced_at_work"),
    "issues": find_col(DF, "have_you_had_any_issues_or_bad_surprises_using_ai_at_work"),
    "learn": find_col(DF, "what_would_you_like_to_learn_first"),
}

use_y, use_n, use_pct = pct_yes(DF, COLS["use_work"])
pers_y, pers_n, pers_pct = pct_yes(DF, COLS["personal"])
exp_s = DF[COLS["exp"]].dropna().astype(str)
beg_n = int((exp_s == "Beginner").sum())
beg_pct = round((beg_n / len(exp_s) * 100), 1) if len(exp_s) else 0.0

# Global toggle
desc_only = st.sidebar.toggle("Description seule", value=False)
st.sidebar.caption("Oui = vues strictement factuelles")

factual_views = [
    "Accueil",
    "Cockpit COMEX factuel",
    "Maturité",
    "Segmentations",
    "Réponses individuelles",
    "Verbatims intelligents",
    "Artefacts descriptifs",
]

reco_views = [
    "Use case lab",
    "Gouvernance",
    "Enablement",
    "Roadmap / Action tracker",
    "Recommandations / priorisation",
]

menu_options = factual_views if desc_only else factual_views + reco_views
view = st.sidebar.radio("Vues", menu_options)

if view == "Accueil":
    st.title("PROVA — Lecture factuelle des réponses IA")
    st.markdown("<div class='section-box'><span class='badge-fact'>Fait observé</span> L'adoption IA est active et mesurable sur l'échantillon.</div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        card("Taille d'échantillon", str(len(DF)), "Réponses exploitables")
    with b:
        card("Usage IA au travail", f"{use_pct}%", f"{use_y}/{use_n}")
    with c:
        card("Débutants IA", f"{beg_pct}%", f"{beg_n}/{len(exp_s)}")
    st.subheader("5 constats clés")
    st.markdown(
        "- Adoption pro et perso observée\n"
        "- Maturité hétérogène\n"
        "- Usages majoritairement opérationnels\n"
        "- Risques qualité/confidentialité mentionnés\n"
        "- Vivier early adopters identifiable"
    )
    if not desc_only:
        st.markdown("<span class='badge-rec'>Recommandation</span> Prioriser 3 chantiers d'exécution immédiatement.", unsafe_allow_html=True)

elif view == "Cockpit COMEX factuel":
    st.title("Cockpit COMEX factuel")
    a, b, c, d = st.columns(4)
    e = DF[COLS["early"]].dropna().astype(str)
    ey = int((e == "Yes").sum())
    ep = round((ey / len(e) * 100), 1) if len(e) else 0.0
    with a: card("Adoption pro", f"{use_pct}%")
    with b: card("Adoption perso", f"{pers_pct}%")
    with c: card("Débutants", f"{beg_pct}%")
    with d: card("Early adopters (Yes)", f"{ep}%", f"{ey}/{len(e)}")

    for name in ["usage_ai_travail_distribution.png", "repartition_roles.png"]:
        p = CHARTS / name
        if p.exists():
            st.image(str(p), caption=name)

    st.markdown("<span class='badge-fact'>Fait observé</span> Tableau de bord strictement descriptif.", unsafe_allow_html=True)

elif view == "Maturité":
    st.title("Maturité")
    maturity_df = pd.DataFrame([
        ["Appétence", "Élevée", "Adoption pro/perso visible", "—" if desc_only else "Renforcer par cas d'usage"],
        ["Maturité d’usage", "Intermédiaire faible", "Débutants majoritaires", "—" if desc_only else "Former par fonction"],
        ["Valeur business", "Prometteuse", "Usages productivité dominants", "—" if desc_only else "Industrialiser 3 cas"],
        ["Gouvernance", "À structurer", "Risque cité", "—" if desc_only else "Cadre autorisé/toléré/interdit"],
        ["Industrialisation", "Démarrage", "Pratiques hétérogènes", "—" if desc_only else "Standardiser prompts/KPI"],
        ["Diffusion", "Possible", "Vivier early adopters", "—" if desc_only else "Activer réseau relais"],
    ], columns=["Dimension", "État actuel", "Lecture", "Priorité d’action"])
    st.dataframe(maturity_df, use_container_width=True, hide_index=True)
    if desc_only:
        st.caption("Mode factuel: colonne priorité neutralisée.")

elif view == "Segmentations":
    st.title("Segmentations")
    tests = [
        (COLS["exp"], COLS["use_work"], "Expertise vs usage pro"),
        (COLS["personal"], COLS["use_work"], "Usage perso vs usage pro"),
        (COLS["role"], COLS["use_work"], "Rôle vs usage pro"),
    ]
    for a, b, label in tests:
        st.subheader(label)
        c2, p, dof, ct = chi2_table(DF, a, b)
        st.dataframe(ct, use_container_width=True)
        if p is None:
            st.write("Variabilité insuffisante.")
        else:
            st.write(f"Chi2={c2:.2f}, ddl={dof}, p={p:.4f}")
        st.caption("Lecture factuelle: association statistique, pas causalité.")

elif view == "Réponses individuelles":
    st.title("Réponses individuelles")
    role_filter = st.multiselect("Filtre rôle", sorted(DF[COLS["role"]].dropna().astype(str).unique().tolist()))
    use_filter = st.multiselect("Filtre usage pro", sorted(DF[COLS["use_work"]].dropna().astype(str).unique().tolist()))
    exp_filter = st.multiselect("Filtre maturité", sorted(DF[COLS["exp"]].dropna().astype(str).unique().tolist()))
    early_filter = st.multiselect("Filtre early adopters", sorted(DF[COLS["early"]].dropna().astype(str).unique().tolist()))
    q = st.text_input("Recherche plein texte")

    sub = DF.copy()
    if role_filter:
        sub = sub[sub[COLS["role"]].astype(str).isin(role_filter)]
    if use_filter:
        sub = sub[sub[COLS["use_work"]].astype(str).isin(use_filter)]
    if exp_filter:
        sub = sub[sub[COLS["exp"]].astype(str).isin(exp_filter)]
    if early_filter:
        sub = sub[sub[COLS["early"]].astype(str).isin(early_filter)]
    if q:
        mask = sub.astype(str).apply(lambda r: r.str.contains(q, case=False, na=False)).any(axis=1)
        sub = sub[mask]

    st.write(f"Réponses filtrées: {len(sub)}")
    if len(sub) == 0:
        st.stop()

    idx = st.number_input("Naviguer réponse (index filtré)", min_value=0, max_value=len(sub)-1, value=0, step=1)
    row = sub.iloc[int(idx)]

    maturity_badge = str(row.get(COLS["exp"], "n/a"))
    st.markdown(f"<span class='badge-fact'>Profil: {maturity_badge}</span>", unsafe_allow_html=True)

    block = respondent_block(row, COLS)
    block["Profil"] = f"{block['Profil']} | Usage pro: {row.get(COLS['use_work'], 'n/a')}"
    block["Verbatims"] = anonymize_text(block["Verbatims"])

    for k, v in block.items():
        st.markdown(f"### {k}")
        st.write(v)

    st.caption("Données nominatives non affichées; extraits verbatims anonymisés/tronqués.")

elif view == "Verbatims intelligents":
    st.title("Verbatims intelligents")

    base = DF[[COLS["role"], COLS["exp"], COLS["annoy"], COLS["usecase"]]].copy()
    texts = []
    for _, r in base.iterrows():
        for source in [COLS["annoy"], COLS["usecase"]]:
            txt = str(r.get(source, "")).strip()
            if txt and txt.lower() != "nan":
                tags = tag_text(txt)
                texts.append({
                    "role": str(r.get(COLS["role"], "n/a")),
                    "maturite": str(r.get(COLS["exp"], "n/a")),
                    "source": source,
                    "verbatim": anonymize_text(txt),
                    "tags": tags,
                    "actionnabilite": len(tags),
                })

    vdf = pd.DataFrame(texts)
    if vdf.empty:
        st.write("Aucun verbatim exploitable.")
        st.stop()

    # explode tags
    ex = vdf.explode("tags").dropna(subset=["tags"])
    tag_freq = ex["tags"].value_counts().rename_axis("tag").reset_index(name="frequence")

    tag_filter = st.multiselect("Filtre thème/tag", sorted(tag_freq["tag"].unique().tolist()))
    role_filter = st.multiselect("Filtre rôle", sorted(vdf["role"].unique().tolist()))
    q = st.text_input("Recherche verbatim")

    vf = vdf.copy()
    if tag_filter:
        vf = vf[vf["tags"].apply(lambda arr: any(t in arr for t in tag_filter))]
    if role_filter:
        vf = vf[vf["role"].isin(role_filter)]
    if q:
        vf = vf[vf["verbatim"].str.contains(q, case=False, na=False)]

    st.subheader("Regroupement thématique (fréquences)")
    st.dataframe(tag_freq, use_container_width=True, hide_index=True)

    show_cols = ["role", "maturite", "source", "tags", "actionnabilite", "verbatim"]
    st.subheader("Verbatims anonymisés")
    st.dataframe(vf[show_cols].head(120), use_container_width=True, hide_index=True)

    if not desc_only:
        st.markdown("<span class='badge-rec'>Recommandation</span> Utiliser les tags dominants pour alimenter le backlog cas d’usage et le plan de formation.", unsafe_allow_html=True)

elif view == "Artefacts descriptifs":
    st.title("Artefacts descriptifs / sources")
    artefacts = [
        ("outputs/executive_summary.md", "Synthèse dirigeant"),
        ("outputs/one_pager_comex.md", "One pager COMEX"),
        ("outputs/analysis_report.md", "Rapport détaillé"),
        ("outputs/cleaned_data.csv", "Données nettoyées"),
        ("outputs/variable_dictionary.csv", "Dictionnaire de variables"),
    ]
    adf = pd.DataFrame(artefacts, columns=["Chemin", "Description"])
    adf["Existe"] = adf["Chemin"].apply(lambda p: (ROOT / p).exists())
    st.dataframe(adf, use_container_width=True, hide_index=True)

elif view == "Use case lab":
    st.title("Use case lab")
    st.markdown("<span class='badge-rec'>Proposition</span> Vue prescriptive activée car Description seule = Non.", unsafe_allow_html=True)
    st.dataframe(pd.read_markdown if False else pd.DataFrame([
        ["Automatisation rédaction & synthèse", "Irritants de charge rédactionnelle", "Gain de temps", "Moyenne", "GED/bureautique", "Direction métiers", "0–6 mois", "Temps gagné"],
        ["Copilote analyse commerciale", "Verbatims sales/analysis", "Décision accélérée", "Moyenne", "CRM/data ventes", "Direction commerciale", "3–12 mois", "Cycle décision"],
    ], columns=["Cas d’usage", "Problème métier", "Valeur attendue", "Complexité", "Dépendances SI", "Sponsor proposé", "Horizon", "KPI suggérés"]), use_container_width=True, hide_index=True)

elif view == "Gouvernance":
    st.title("Gouvernance")
    st.markdown("<span class='badge-rec'>Proposition</span> Cadre de gestion à valider en comité.", unsafe_allow_html=True)
    gdf = pd.DataFrame([
        ["Autorisé", "Public/non sensible", "Rédaction/synthèse", "Validation humaine"],
        ["Toléré", "Interne non confidentiel", "Brouillons", "Anonymisation"],
        ["Sous validation", "Interne sensible", "Analyse assistée", "Accord manager + compliance"],
        ["Interdit", "Confidentiel non anonymisé", "Upload IA publique", "Blocage"],
    ], columns=["Niveau", "Données", "Usages", "Règle"])
    st.dataframe(gdf, use_container_width=True, hide_index=True)

elif view == "Enablement":
    st.title("Enablement")
    st.markdown("<span class='badge-rec'>Proposition</span> Parcours de déploiement formation.", unsafe_allow_html=True)
    edf = pd.DataFrame([
        ["Débutants", "Prompting + vérification", "Atelier 1h", "RH + managers"],
        ["Intermédiaires", "Cas métier", "Coaching", "Managers fonctionnels"],
        ["Relais", "Industrialisation", "Bootcamp", "PMO transformation"],
    ], columns=["Population", "Besoins", "Format", "Owner suggéré"])
    st.dataframe(edf, use_container_width=True, hide_index=True)

elif view == "Roadmap / Action tracker":
    st.title("Roadmap / Action tracker")
    st.markdown("<span class='badge-rec'>Proposition</span> Plan d'exécution recommandé.", unsafe_allow_html=True)
    adf = pd.DataFrame([
        ["Valider cadre IA", "Gouvernance", "Compliance + DSI", "0–3 mois", "À lancer", "Cadre validé"],
        ["Déployer formation", "Enablement", "RH + managers", "3–6 mois", "À lancer", "Taux adoption"],
        ["Piloter 3 cas d’usage", "Cas d’usage", "Directions métiers", "6–12 mois", "Planifié", "Gains business"],
    ], columns=["Action", "Axe", "Owner suggéré", "Horizon", "Statut", "KPI"])
    st.dataframe(adf, use_container_width=True, hide_index=True)

else:
    st.title("Recommandations / priorisation")
    st.markdown("<span class='badge-rec'>Recommandation</span> Priorisation pilotage (non factuelle stricte).", unsafe_allow_html=True)
    st.write("1. Cadre d'usage IA\n2. Formation ciblée\n3. 3 pilotes KPIisés\n4. Cockpit trimestriel\n5. Réseau de relais")
