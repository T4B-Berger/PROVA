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
.block-container {padding-top: 1.2rem; max-width: 1200px;}
h1, h2, h3 {color:#3B2A1A; letter-spacing:0.2px;}
.kpi-card {background:#FFFDF9;border:1px solid #E4D8C8;border-radius:14px;padding:14px 16px;margin-bottom:10px;}
.kpi-title {font-size:0.82rem;color:#7A6A57;text-transform:uppercase;}
.kpi-value {font-size:1.6rem;font-weight:700;color:#8C5A2B;}
.section-box {background:#FFFDF9;border-left:5px solid #8C5A2B;border-radius:8px;padding:12px 14px;margin:8px 0 14px 0;}
.badge-ok {display:inline-block;background:#DDEEE0;color:#1E5631;padding:3px 8px;border-radius:999px;font-size:0.78rem;}
.badge-rec {display:inline-block;background:#EFE8DD;color:#5C4128;padding:3px 8px;border-radius:999px;font-size:0.78rem;}
.small {color:#6B6258;font-size:0.86rem;}
</style>
""",
    unsafe_allow_html=True,
)


def find_col(df: pd.DataFrame, key: str) -> str:
    m = [c for c in df.columns if key in c]
    if not m:
        raise KeyError(f"Colonne non trouvée: {key}")
    return m[0]


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(OUT / "cleaned_data.csv")


def pct_yes(df: pd.DataFrame, col: str) -> tuple[int, int, float]:
    s = df[col].dropna().astype(str).str.strip()
    y = int((s == "Yes").sum())
    n = int(len(s))
    return y, n, round((y / n * 100), 1) if n else 0.0


def split_multi(series: pd.Series) -> pd.Series:
    return series.dropna().astype(str).str.split(";").explode().str.strip().replace("", pd.NA).dropna()


def chi2(df: pd.DataFrame, a: str, b: str):
    sub = df[[a, b]].dropna()
    ct = pd.crosstab(sub[a], sub[b])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None, None, None, ct
    c2, p, dof, _ = chi2_contingency(ct)
    return c2, p, dof, ct


def card(title: str, value: str, note: str = ""):
    st.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>{title}</div><div class='kpi-value'>{value}</div><div class='small'>{note}</div></div>",
        unsafe_allow_html=True,
    )


@st.cache_data
def load_text(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8") if p.exists() else "information non disponible dans les données fournies"


df = load_data()
role = find_col(df, "primary_role")
exp = find_col(df, "level_of_expertise")
use_work = find_col(df, "used_ai_for_work_in_the_last_30_days")
personal = find_col(df, "personal_life")
early = find_col(df, "early_adopters_team")
work_multi = find_col(df, "what_do_you_use_ai_for_at_work")
annoy = find_col(df, "most_annoying_part")
usecase_col = find_col(df, "prioritize_3_ai_use_cases_for_2026")

use_y, use_n, use_pct = pct_yes(df, use_work)
pers_y, pers_n, pers_pct = pct_yes(df, personal)
exp_s = df[exp].dropna().astype(str)
beg_n = int((exp_s == "Beginner").sum())
beg_pct = round((beg_n / len(exp_s) * 100), 1) if len(exp_s) else 0.0

menu = st.sidebar.radio(
    "Navigation",
    [
        "A. Accueil",
        "B. Cockpit COMEX",
        "C. Maturité",
        "D. Irritants → cas d’usage",
        "E. Portefeuille 2026",
        "F. Gouvernance et garde-fous",
        "G. Enablement / formation",
        "H. Réseau Early Adopters",
        "I. Roadmap 12 mois",
        "J. Artefacts",
    ],
)

if menu.startswith("A"):
    st.title("PROVA — Pilotage Transformation IA")
    st.markdown("<div class='section-box'><b>Message directeur</b><br/>L'adoption IA est engagée. La priorité n'est plus d'explorer, mais d'industrialiser de façon gouvernée.</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        card("Taille d'échantillon", f"{len(df)}", "Répondants exploitables")
    with c2:
        card("Usage IA au travail", f"{use_pct}%", f"{use_y}/{use_n}")
    with c3:
        card("Maturité débutante", f"{beg_pct}%", f"{beg_n}/{len(exp_s)}")

    st.subheader("5 constats clés")
    st.markdown("""
- Adoption déjà active sur le travail et le personnel.
- Maturité hétérogène: forte base débutante.
- Les usages dominants sont opérationnels (recherche/rédaction/traduction).
- Le besoin de gouvernance et de cadre est explicite.
- Un levier d'accélération existe via les early adopters.
""")
    st.subheader("3 décisions immédiates")
    st.markdown("""
1. Cadre d'usage IA (qualité/confidentialité/validation humaine).
2. Plan de formation métier court et pratique.
3. Sélection de 3 cas d'usage 2026 avec KPI de valeur.
""")

elif menu.startswith("B"):
    st.title("Cockpit COMEX")
    a, b, c, d = st.columns(4)
    with a:
        card("Adoption pro", f"{use_pct}%", "Signal fort")
    with b:
        card("Adoption perso", f"{pers_pct}%", f"{pers_y}/{pers_n}")
    with c:
        card("Débutants", f"{beg_pct}%", "Besoin enablement")
    with d:
        e = df[early].dropna().astype(str)
        ey = int((e == "Yes").sum())
        ep = round((ey / len(e) * 100), 1) if len(e) else 0.0
        card("Early adopters (Yes)", f"{ep}%", f"{ey}/{len(e)}")

    st.markdown("<span class='badge-ok'>Fait observé</span> <span class='small'>Adoption active</span>", unsafe_allow_html=True)
    st.markdown("<span class='badge-rec'>Recommandation</span> <span class='small'>Passer en mode pilotage de portefeuille + gouvernance</span>", unsafe_allow_html=True)
    st.subheader("Tension stratégique")
    st.write("Adoption rapide vs niveau de maîtrise inégal: risque qualité/confiance si la gouvernance n'est pas synchronisée.")
    st.subheader("Décisions à prendre maintenant")
    st.write("- Valider le cadre d'usage\n- Nommer les owners par chantier\n- Lancer les 3 pilotes à ROI court terme")

elif menu.startswith("C"):
    st.title("Maturité de transformation IA")
    maturity = pd.DataFrame([
        ["Appétence", "Élevée", "Adoption personnelle/pro déjà installée", "Consolider l'engagement par des cas concrets"],
        ["Maturité d’usage", "Intermédiaire faible", "Base débutante majoritaire", "Former par fonction"],
        ["Valeur business", "Prometteuse", "Usages orientés productivité", "Industrialiser 3 cas 2026"],
        ["Gouvernance", "À structurer", "Risque qualité/confidentialité mentionné", "Cadre autorisé/toléré/interdit"],
        ["Industrialisation", "En démarrage", "Pratiques hétérogènes", "Standardiser prompts + KPI"],
        ["Capacité de diffusion", "Disponible", "Vivier early adopters", "Activer un réseau de relais"],
    ], columns=["Dimension", "État actuel", "Lecture", "Priorité d’action"])
    st.dataframe(maturity, use_container_width=True, hide_index=True)
    st.caption("Les lignes 'Priorité d’action' sont des recommandations de pilotage (pas des faits de mesure).")

elif menu.startswith("D"):
    st.title("Irritants → cas d’usage")
    irritants = df[annoy].dropna().astype(str).head(6).tolist()
    usecases = df[usecase_col].dropna().astype(str).head(6).tolist()
    map_df = pd.DataFrame({
        "Irritant terrain (verbatim)": irritants,
        "Cas d’usage 2026 associé (verbatim)": usecases[:len(irritants)],
        "Lecture managériale": ["Transformer la friction en cas d'usage priorisé"] * min(len(irritants), len(usecases)),
    })
    st.dataframe(map_df, use_container_width=True)
    st.caption("Les correspondances sont indicatives et servent au cadrage de portefeuille.")

elif menu.startswith("E"):
    st.title("Portefeuille 2026")
    portfolio = pd.DataFrame([
        ["Automatisation rédaction & synthèse", "Usage dominant observé (rédaction/synthèse)", "Gain de temps élevé", "Moyenne", "GED, outils bureautiques", "Qualité contenu", "Direction Métiers + IT", "0–6 mois", "Temps gagné, taux adoption"],
        ["Copilote analyse commerciale", "Verbatims sur sales/analysis", "Décision plus rapide", "Moyenne", "CRM, données ventes", "Fiabilité des données", "Sales Director", "3–12 mois", "Cycle décision, précision prévision"],
        ["Assistant conformité & validation", "Risque gouvernance explicitement cité", "Réduction risque", "Élevée", "Référentiels conformité", "Rigueur process", "Compliance + DSI", "0–12 mois", "Incidents évités, taux conformité"],
    ], columns=["Cas d’usage", "Justification par les données", "Valeur attendue", "Complexité estimative", "Dépendances data / SI", "Risque", "Sponsor proposé", "Horizon", "KPI suggérés"])
    st.dataframe(portfolio, use_container_width=True)
    st.caption("Les colonnes Valeur/Complexité/KPI sont des recommandations de pilotage.")

elif menu.startswith("F"):
    st.title("Gouvernance et garde-fous")
    gov = pd.DataFrame([
        ["Autorisé", "Données publiques / non sensibles", "Rédaction, synthèse, recherche", "Hallucination", "Validation humaine systématique"],
        ["Toléré", "Interne non confidentiel", "Préparation de brouillons", "Diffusion involontaire", "Relecture + anonymisation"],
        ["Soumis à validation", "Interne sensible", "Analyse assistée", "Conformité", "Accord manager + contrôle conformité"],
        ["Interdit", "Données confidentielles non anonymisées", "Upload brut vers IA publique", "Exposition données", "Blocage + escalade"],
    ], columns=["Niveau", "Sensibilité donnée", "Usages/outils", "Risque principal", "Règle de gestion"])
    st.dataframe(gov, use_container_width=True, hide_index=True)
    st.caption("Ce cadre est une recommandation de gouvernance à valider formellement.")

elif menu.startswith("G"):
    st.title("Enablement / formation")
    en = pd.DataFrame([
        ["Débutants", "Prompting fondamental, vérification résultat", "Atelier 1h + exercices", "Sprints d'adoption par équipe"],
        ["Intermédiaires", "Cas d'usage métier", "Coaching fonctionnel", "Communauté de pratique"],
        ["Relais/experts", "Industrialisation + gouvernance", "Bootcamp avancé", "Animation réseau et standards"],
    ], columns=["Population", "Besoins prioritaires", "Format préféré", "Recommandation de déploiement"])
    st.dataframe(en, use_container_width=True, hide_index=True)
    st.caption("Plan de montée en compétence recommandé à partir des besoins exprimés.")

elif menu.startswith("H"):
    st.title("Réseau Early Adopters")
    e = df[early].dropna().astype(str)
    ey = int((e == "Yes").sum())
    em = int((e == "Maybe").sum())
    st.markdown(f"<div class='section-box'><b>Vivier identifié</b><br/>Yes: <b>{ey}</b> | Maybe: <b>{em}</b></div>", unsafe_allow_html=True)
    st.write("**Rôle des relais**: démontrer des cas d'usage, diffuser les standards, remonter les irritants.")
    st.write("**Logique d'animation** (recommandation): rituel mensuel, backlog commun, KPI d'adoption par entité.")
    st.write("**À lancer**: nomination des relais, kit d'animation, gouvernance de communauté.")

elif menu.startswith("I"):
    st.title("Roadmap 12 mois")
    roadmap = pd.DataFrame([
        ["0–3 mois", "Valider cadre usage + sélectionner 3 pilotes", "COMEX, DSI, Compliance", "Charte IA, backlog priorisé", "Cadre validé, pilotes lancés"],
        ["3–6 mois", "Déployer formation et standards", "RH, Managers métiers", "Parcours formation, kit prompts", "Taux adoption, satisfaction"],
        ["6–12 mois", "Industrialiser et mesurer la valeur", "PMO Transformation", "Tableau de bord valeur/risque", "Gains business, incidents maîtrisés"],
    ], columns=["Horizon", "Décisions", "Owners suggérés", "Livrables", "KPI / critères de succès"])
    st.dataframe(roadmap, use_container_width=True, hide_index=True)
    st.caption("Feuille de route proposée (recommandation), à arbitrer en gouvernance transformation.")

else:
    st.title("Artefacts")
    artefacts = [
        ("outputs/executive_summary.md", "Synthèse dirigeant", "Décision immédiate"),
        ("outputs/one_pager_comex.md", "Note 1 page", "Brief COMEX"),
        ("outputs/board_deck_outline.md", "Plan de deck", "Narration comité"),
        ("outputs/analysis_report.md", "Rapport détaillé", "Traçabilité analytique"),
        ("outputs/use_case_portfolio.md", "Portefeuille 2026", "Arbitrage cas d'usage"),
        ("outputs/governance_framework.md", "Cadre gouvernance", "Gestion des risques"),
        ("outputs/enablement_plan.md", "Plan enablement", "Déploiement compétences"),
        ("outputs/transformation_roadmap.md", "Roadmap 12 mois", "Pilotage exécution"),
    ]
    adf = pd.DataFrame(artefacts, columns=["Chemin", "Description", "Rôle"])
    adf["Existe"] = adf["Chemin"].apply(lambda x: (ROOT / x).exists())
    st.dataframe(adf, use_container_width=True, hide_index=True)
    st.markdown("### Charts disponibles")
    for p in sorted(CHARTS.glob("*.png")):
        st.write(f"- {p.relative_to(ROOT)}")
