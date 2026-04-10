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


EXPERTISE_ORDER = [
    "Advanced / Expert",
    "Intermediate",
    "Beginner",
    "Interested, but not using it yet",
]

QUESTION_LABELS = {
    "role": "Fonction principale",
    "exp": "Niveau d’expertise en intelligence artificielle",
    "use_work": "Utilisation de l’intelligence artificielle au travail (30 derniers jours)",
    "freq": "Fréquence d’utilisation de l’intelligence artificielle",
    "work_multi": "Usages de l’intelligence artificielle au travail",
    "personal": "Utilisation de l’intelligence artificielle dans la vie personnelle",
    "early": "Présence d’early adopters dans l’équipe",
    "annoy": "Irritants principaux dans le travail",
    "usecase": "Cas d’usage prioritaires pour 2026",
    "benefits": "Bénéfices observés au travail",
    "issues": "Incidents ou risques rencontrés avec l’intelligence artificielle",
    "learn": "Apprentissages prioritaires",
}


def ordered_expertise(values: list[str]) -> list[str]:
    uniq = [v for v in values if isinstance(v, str)]
    preferred = [v for v in EXPERTISE_ORDER if v in uniq]
    other = sorted([v for v in uniq if v not in EXPERTISE_ORDER])
    return preferred + other


def sort_index_expertise(df: pd.DataFrame) -> pd.DataFrame:
    present = [v for v in EXPERTISE_ORDER if v in df.index]
    others = [v for v in df.index if v not in EXPERTISE_ORDER]
    return df.reindex(present + others)


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

# Navigation lists (single source of truth)
FACTUAL_PAGES = [
    "Accueil",
    "Cockpit COMEX factuel",
    "Maturité",
    "Segmentations",
    "Réponses individuelles",
    "Verbatims intelligents",
    "Artefacts descriptifs / sources",
]

PRESCRIPTIVE_PAGES = [
    "Use case lab",
    "Gouvernance",
    "Enablement",
    "Roadmap / Action tracker",
    "Recommandations / priorisation",
]

# Global control (must be first element in sidebar)
desc_mode = st.sidebar.radio("Description seule", ["Oui", "Non"], index=0)
if "prescriptive_unlocked" not in st.session_state:
    st.session_state["prescriptive_unlocked"] = False

if desc_mode == "Non" and not st.session_state["prescriptive_unlocked"]:
    st.sidebar.warning("Accès au mode prescriptif protégé.")
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Valider l’accès", use_container_width=True):
        if pwd == "iqo":
            st.session_state["prescriptive_unlocked"] = True
            st.sidebar.success("Accès prescriptif autorisé pour cette session.")
        else:
            st.sidebar.error("Mot de passe incorrect.")

desc_only = not (desc_mode == "Non" and st.session_state["prescriptive_unlocked"])
if desc_mode == "Non" and desc_only:
    st.sidebar.info("Restez en mode descriptif tant que le mot de passe n'est pas validé.")
st.sidebar.caption("Protection légère d’accès au mode prescriptif (non destinée à la sécurité forte).")

menu_options = FACTUAL_PAGES if desc_only else FACTUAL_PAGES + PRESCRIPTIVE_PAGES
view = st.sidebar.radio("Navigation", menu_options)

if view == "Accueil":
    st.title("PROVA — Lecture factuelle des réponses IA")
    st.markdown(
        "<div class='section-box'><span class='badge-fact'>Message directeur</span> "
        "L’entreprise n’est plus au stade de l’exploration : l’usage est déjà large, la valeur est visible, "
        "et le prochain enjeu est de cadrer le risque puis d’industrialiser quelques cas d’usage prioritaires."
        "</div>",
        unsafe_allow_html=True,
    )
    a, b, c = st.columns(3)
    with a:
        card("Taille d'échantillon", str(len(DF)), "Réponses exploitables")
    with b:
        card("Usage IA au travail", f"{use_pct}%", f"{use_y}/{use_n}")
    with c:
        card("Débutants IA", f"{beg_pct}%", f"{beg_n}/{len(exp_s)}")
    st.subheader("Quatre messages de synthèse")
    st.markdown(
        "1. Le sujet n’est plus exploratoire : l’usage est déjà installé.\n"
        "2. La valeur est visible : gains de temps, qualité et créativité.\n"
        "3. Le frein principal est le risque : confidentialité, conformité, fiabilité.\n"
        "4. Le prochain mouvement est opérationnel : cadre simple, pilotes ciblés, diffusion."
    )
    if not desc_only:
        st.markdown(
            "<span class='badge-rec'>Décision attendue</span> Passer d’usages individuels non gouvernés "
            "à une première vague pilotée, bornée et mesurable.",
            unsafe_allow_html=True,
        )

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

    st.subheader("Synthèse compacte pour comité de direction")
    c1, c2 = st.columns([1, 1])
    with c1:
        p = CHARTS / "usage_ai_travail_distribution.png"
        if p.exists():
            st.image(str(p), caption="Répartition de l’usage au travail", width=360)
    with c2:
        exp_counts = DF[COLS["exp"]].value_counts(dropna=True)
        exp_table = pd.DataFrame({"Niveau d’expertise": exp_counts.index, "Volume": exp_counts.values})
        exp_table["Niveau d’expertise"] = pd.Categorical(exp_table["Niveau d’expertise"], categories=EXPERTISE_ORDER, ordered=True)
        exp_table = exp_table.sort_values("Niveau d’expertise")
        st.dataframe(exp_table, hide_index=True, use_container_width=True)

    st.markdown("<span class='badge-fact'>Fait observé</span> Vue direction générale : indicateurs clés et visuels compacts.", unsafe_allow_html=True)
    st.subheader("Lecture COMEX en quatre messages")
    summary = pd.DataFrame(
        [
            ["Le sujet n’est plus exploratoire", "57/70 utilisent déjà l’intelligence artificielle au travail"],
            ["La valeur est déjà visible", "Les bénéfices de productivité et de qualité sont déjà observables"],
            ["Le frein principal est le risque", "La maîtrise des données et la fiabilité doivent être cadrées"],
            ["Le prochain mouvement est organisationnel", "Cadre, pilotes, diffusion et mesure légère des gains"],
        ],
        columns=["Message de direction", "Élément factuel"],
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)

elif view == "Maturité":
    st.title("Maturité")
    rows = [
        ["Appétence", "Élevée", "Adoption pro/perso visible", "Renforcer par cas d'usage"],
        ["Maturité d’usage", "Intermédiaire faible", "Débutants majoritaires", "Former par fonction"],
        ["Valeur business", "Prometteuse", "Usages productivité dominants", "Industrialiser 3 cas"],
        ["Gouvernance", "À structurer", "Risque cité", "Cadre autorisé/toléré/interdit"],
        ["Industrialisation", "Démarrage", "Pratiques hétérogènes", "Standardiser les pratiques et les indicateurs clés"],
        ["Diffusion", "Possible", "Vivier early adopters", "Activer réseau relais"],
    ]
    maturity_df = pd.DataFrame(rows, columns=["Dimension", "État actuel", "Lecture", "Priorité d’action"])
    if desc_only:
        maturity_df = maturity_df.drop(columns=["Priorité d’action"])
    st.dataframe(maturity_df, use_container_width=True, hide_index=True)

elif view == "Segmentations":
    st.title("Segmentations")
    tests = [
        (COLS["exp"], COLS["use_work"], "Niveau d’expertise et usage au travail"),
        (COLS["personal"], COLS["use_work"], "Usage personnel et usage au travail"),
        (COLS["role"], COLS["use_work"], "Fonction et usage au travail"),
    ]
    for a, b, label in tests:
        st.subheader(label)
        c2, p, dof, ct = chi2_table(DF, a, b)
        if a == COLS["exp"]:
            ct = sort_index_expertise(ct)
        st.dataframe(ct, use_container_width=True)
        if p is None:
            st.write("Variabilité insuffisante.")
        else:
            st.write(f"Chi2={c2:.2f}, ddl={dof}, p={p:.4f}")
        st.caption("Lecture factuelle: association statistique, pas causalité.")

elif view == "Réponses individuelles":
    st.title("Réponses individuelles")
    role_filter = st.multiselect(f"Filtre — {QUESTION_LABELS['role']}", sorted(DF[COLS["role"]].dropna().astype(str).unique().tolist()))
    use_filter = st.multiselect(f"Filtre — {QUESTION_LABELS['use_work']}", sorted(DF[COLS["use_work"]].dropna().astype(str).unique().tolist()))
    exp_filter = st.multiselect(f"Filtre — {QUESTION_LABELS['exp']}", ordered_expertise(DF[COLS["exp"]].dropna().astype(str).unique().tolist()))
    early_filter = st.multiselect(f"Filtre — {QUESTION_LABELS['early']}", sorted(DF[COLS["early"]].dropna().astype(str).unique().tolist()))
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

    idx = st.number_input("Naviguer dans les réponses filtrées", min_value=0, max_value=len(sub)-1, value=0, step=1)
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
                source_label = QUESTION_LABELS["annoy"] if source == COLS["annoy"] else QUESTION_LABELS["usecase"]
                texts.append({
                    "role": str(r.get(COLS["role"], "n/a")),
                    "maturite": str(r.get(COLS["exp"], "n/a")),
                    "source": source_label,
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
    role_filter = st.multiselect(f"Filtre — {QUESTION_LABELS['role']}", sorted(vdf["role"].unique().tolist()))
    q = st.text_input("Recherche verbatim")

    vf = vdf.copy()
    if tag_filter:
        vf = vf[vf["tags"].apply(lambda arr: any(t in arr for t in tag_filter))]
    if role_filter:
        vf = vf[vf["role"].isin(role_filter)]
    if q:
        vf = vf[vf["verbatim"].str.contains(q, case=False, na=False)]

    st.subheader("Regroupement thématique")
    st.dataframe(tag_freq, use_container_width=True, hide_index=True)

    show_cols = ["role", "maturite", "source", "tags", "actionnabilite", "verbatim"]
    st.subheader("Verbatims anonymisés")
    st.dataframe(vf[show_cols].head(120), use_container_width=True, hide_index=True)

    st.subheader("Verbatims par thème")
    themes = sorted(tag_freq["tag"].tolist())
    selected_theme = st.selectbox("Thème à explorer", themes)
    themed = vf[vf["tags"].apply(lambda arr: selected_theme in arr)]
    st.write(f"Volume pour le thème « {selected_theme} » : {len(themed)}")
    for i, (_, rec) in enumerate(themed.head(30).iterrows(), start=1):
        with st.expander(f"Verbatim {i} — {rec['role']} — {rec['maturite']}"):
            st.write(rec["verbatim"])
            st.caption("Texte anonymisé et tronqué pour confidentialité.")

    if not desc_only:
        st.markdown("<span class='badge-rec'>Lecture managériale</span> Les thèmes dominants peuvent guider les priorités d’accompagnement.", unsafe_allow_html=True)

elif view == "Artefacts descriptifs / sources":
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
    st.title("Laboratoire des cas d’usage")
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
    st.title("Développement des compétences")
    st.markdown("<span class='badge-rec'>Proposition</span> Parcours de déploiement formation.", unsafe_allow_html=True)
    edf = pd.DataFrame([
        ["Débutants", "Prompting + vérification", "Atelier 1h", "RH + managers"],
        ["Intermédiaires", "Cas métier", "Coaching", "Managers fonctionnels"],
        ["Relais", "Industrialisation", "Bootcamp", "PMO transformation"],
    ], columns=["Population", "Besoins", "Format", "Responsable suggéré"])
    st.dataframe(edf, use_container_width=True, hide_index=True)

elif view == "Roadmap / Action tracker":
    st.title("Feuille de route / Suivi des actions")
    st.markdown("<span class='badge-rec'>Proposition</span> Plan d'exécution recommandé.", unsafe_allow_html=True)
    adf = pd.DataFrame([
        ["Valider cadre IA", "Gouvernance", "Compliance + DSI", "0–3 mois", "À lancer", "Cadre validé"],
        ["Déployer formation", "Enablement", "RH + managers", "3–6 mois", "À lancer", "Taux adoption"],
        ["Piloter 3 cas d’usage", "Cas d’usage", "Directions métiers", "6–12 mois", "Planifié", "Gains business"],
    ], columns=["Action", "Axe", "Responsable suggéré", "Horizon", "Statut", "Indicateur clé"])
    st.dataframe(adf, use_container_width=True, hide_index=True)

else:
    st.title("Recommandations / priorisation")
    st.markdown("<span class='badge-rec'>Décisions COMEX attendues</span> Quatre arbitrages suffisent pour sortir du statu quo.", unsafe_allow_html=True)
    st.write(
        "1. Valider un cadre d’usage de l’intelligence artificielle simple et clair.\n"
        "2. Nommer un sponsor exécutif global et un responsable métier par pilote.\n"
        "3. Lancer deux gains rapides transverses et un pilote métier différenciant.\n"
        "4. Activer l’adoption : formation par fonction, réseau de relais, mesure légère des gains."
    )
