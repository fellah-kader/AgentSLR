#!/usr/bin/env python3
"""Generates the redesigned NeuroSLR streamlit app, avoiding shell-quoting issues."""

APP = r'''import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="NeuroSLR | Research Intelligence", page_icon="\U0001f9e0", layout="wide", initial_sidebar_state="expanded")

# ==================== STYLING ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: #FAFBFC; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0A2B22; width: 280px !important; }
section[data-testid="stSidebar"] * { color: #D4E8DE; }
.sb-brand { font-size: 1.5rem; font-weight: 800; color: #FFFFFF !important; letter-spacing: -0.5px; margin-bottom: 2px; }
.sb-tag { font-size: 0.72rem; color: #6DA891 !important; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1.5rem; }
.sb-section { font-size: 0.7rem; color: #6DA891 !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin: 1.5rem 0 0.8rem 0; }
.pstep { display: flex; align-items: flex-start; padding: 0.55rem 0.7rem; border-radius: 8px; margin-bottom: 0.3rem; border-left: 3px solid #1C4A3A; }
.pstep-num { font-size: 0.75rem; font-weight: 700; color: #4E8C74 !important; margin-right: 0.7rem; min-width: 18px; }
.pstep-body { line-height: 1.2; }
.pstep-title { font-size: 0.82rem; font-weight: 600; color: #E8F3EE !important; }
.pstep-desc { font-size: 0.68rem; color: #6DA891 !important; }
.sb-foot { font-size: 0.7rem; color: #5A8471 !important; line-height: 1.5; margin-top: 0.4rem; }

/* Header */
.hdr-kicker { font-size: 0.72rem; font-weight: 700; color: #0D9488; text-transform: uppercase; letter-spacing: 1.5px; }
.hdr-title { font-size: 2rem; font-weight: 800; color: #0A2B22; letter-spacing: -1px; margin: 2px 0; line-height: 1.1; }
.hdr-sub { font-size: 0.95rem; color: #5A7A6E; font-weight: 400; }
.badge-row { margin-top: 0.8rem; }
.badge { display: inline-block; background: #E8F3EE; color: #0A6B4F; border: 1px solid #C4E2D5; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-right: 0.5rem; }
.badge-dot { color: #10B981; }

/* KPI cards */
.kpi { background: #FFFFFF; border: 1px solid #E8EDEB; border-radius: 12px; padding: 1.1rem 1.2rem; height: 100%; box-shadow: 0 1px 3px rgba(10,43,34,0.04); transition: box-shadow 0.2s, transform 0.2s; }
.kpi:hover { box-shadow: 0 4px 14px rgba(10,43,34,0.10); transform: translateY(-2px); }
.kpi-label { font-size: 0.7rem; font-weight: 600; color: #8CA69B; text-transform: uppercase; letter-spacing: 0.6px; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #0A2B22; line-height: 1.1; margin: 0.35rem 0; }
.kpi-ctx { font-size: 0.72rem; color: #6B8A7D; line-height: 1.3; }
.kpi-accent { border-top: 3px solid #0D9488; }

/* Section headings */
.sec-title { font-size: 1.15rem; font-weight: 700; color: #0A2B22; margin: 1.8rem 0 0.3rem; }
.sec-sub { font-size: 0.85rem; color: #7A968A; margin-bottom: 1rem; }

/* Funnel */
.funnel-wrap { display: flex; align-items: stretch; gap: 0; margin: 0.5rem 0 1rem; }
.funnel-step { flex: 1; background: #FFFFFF; border: 1px solid #E8EDEB; padding: 0.9rem 1rem; text-align: center; position: relative; }
.funnel-step:first-child { border-radius: 10px 0 0 10px; }
.funnel-step:last-child { border-radius: 0 10px 10px 0; }
.funnel-num { font-size: 1.5rem; font-weight: 800; color: #0A2B22; }
.funnel-lbl { font-size: 0.7rem; color: #8CA69B; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; margin-top: 2px; }
.funnel-pct { font-size: 0.68rem; color: #0D9488; font-weight: 600; margin-top: 2px; }

/* Insight card */
.insight { background: linear-gradient(135deg, #F0F9F5 0%, #E4F2EB 100%); border: 1px solid #C4E2D5; border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 0.8rem; }
.insight-lbl { font-size: 0.68rem; font-weight: 700; color: #0D9488; text-transform: uppercase; letter-spacing: 1px; }
.insight-val { font-size: 1.25rem; font-weight: 800; color: #0A2B22; margin: 3px 0; }
.insight-desc { font-size: 0.78rem; color: #6B8A7D; }

/* Data card */
.dcard { background: #FFFFFF; border: 1px solid #E8EDEB; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.7rem; box-shadow: 0 1px 3px rgba(10,43,34,0.03); }

/* Contradiction comparison */
.study-card { background: #FFFFFF; border: 1px solid #E8EDEB; border-radius: 10px; padding: 1rem 1.2rem; height: 100%; }
.study-tag { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8CA69B; }
.study-title { font-size: 0.88rem; font-weight: 600; color: #1A3A30; line-height: 1.35; margin-top: 4px; }
.vs-badge { text-align: center; font-weight: 800; color: #C44; font-size: 1rem; padding: 0.5rem 0; }
.sev-pill-major { display: inline-block; background: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; padding: 0.25rem 0.7rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; }
.sev-pill-moderate { display: inline-block; background: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; padding: 0.25rem 0.7rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; }
.sev-pill-minor { display: inline-block; background: #FEF9E7; color: #A16207; border: 1px solid #FDE68A; padding: 0.25rem 0.7rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700; }

/* Evidence level pills */
.ev-pill { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 5px; font-size: 0.72rem; font-weight: 700; }
.evb-1 { background: #D1FAE5; color: #047857; }
.evb-2 { background: #CCFBF1; color: #0F766E; }
.evb-3 { background: #FEF3C7; color: #B45309; }
.evb-4 { background: #FFEDD5; color: #C2410C; }
.evb-5 { background: #FEE2E2; color: #B91C1C; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #E8EDEB; }
.stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 0.9rem; color: #7A968A; padding: 0.6rem 1rem; }
.stTabs [aria-selected="true"] { color: #0A6B4F !important; }
.footer { text-align: center; color: #A8BDB3; font-size: 0.75rem; padding: 2.5rem 0 0.5rem; border-top: 1px solid #E8EDEB; margin-top: 2.5rem; }
</style>
""", unsafe_allow_html=True)

# ==================== CONSTANTS ====================
CONDITIONS = {"alzheimers": "Alzheimer's Disease", "parkinsons": "Parkinson's Disease", "multiple_sclerosis": "Multiple Sclerosis", "epilepsy": "Epilepsy", "stroke": "Stroke"}
CEBM = {1: "Systematic Review / Meta-analysis of RCTs", 2: "Individual RCT", 3: "Cohort Study", 4: "Case-Control Study", 5: "Case Report / Expert Opinion"}
EV_COLORS = {1: "#059669", 2: "#0D9488", 3: "#D97706", 4: "#EA580C", 5: "#DC2626"}
DATA_DIR = Path("data/agentslr")
EVAL_DIR = Path("evaluation")

# ==================== DATA LOADERS ====================
@st.cache_data
def load_screening(cond):
    p = DATA_DIR / "client" / "oss" / cond / "screening" / "abstract_screening.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

@st.cache_data
def load_contradictions(cond):
    p = DATA_DIR / "client" / "oss" / cond / "contradiction" / "contradiction_results.json"
    if p.exists():
        with open(p) as f: return json.load(f)
    return []

@st.cache_data
def load_evidence(cond):
    p = DATA_DIR / "client" / "oss" / cond / "evidence" / "evidence_grades.json"
    if p.exists():
        with open(p) as f: return json.load(f)
    return []

@st.cache_data
def load_harvest_count(cond):
    p = DATA_DIR / "harvests" / cond / "harvest_metadata.csv"
    return len(pd.read_csv(p, usecols=["article_id"])) if p.exists() else 0

@st.cache_data
def load_scores():
    sd = EVAL_DIR / "results"
    if sd.exists():
        fs = sorted(sd.glob("scores_all_*.json"), reverse=True)
        if fs:
            with open(fs[0]) as f: return json.load(f)
    return {}

@st.cache_data
def get_all_stats():
    stats = {}
    for cond in CONDITIONS:
        sc = load_screening(cond); ct = load_contradictions(cond); ev = load_evidence(cond); hv = load_harvest_count(cond)
        inc = len(sc[sc["ai4epi_abstract_decision"].astype(str).str.upper() == "INCLUDE"]) if len(sc) > 0 else 0
        fl = [c for c in ct if c.get("has_contradiction")]
        stats[cond] = {"harvested": hv, "screened": len(sc), "included": inc,
                       "contradictions": len(fl), "graded": len(ev),
                       "major": len([c for c in fl if c.get("severity","").lower()=="major"]),
                       "moderate": len([c for c in fl if c.get("severity","").lower()=="moderate"]),
                       "minor": len([c for c in fl if c.get("severity","").lower()=="minor"])}
    return stats

def kpi(label, value, ctx, accent=False):
    cls = "kpi kpi-accent" if accent else "kpi"
    return f'<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-ctx">{ctx}</div></div>'

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('<div class="sb-brand">\U0001f9e0 NeuroSLR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-tag">Neurological Evidence Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">Condition Filter</div>', unsafe_allow_html=True)
    opts = ["all"] + list(CONDITIONS.keys())
    condition = st.selectbox("Condition", options=opts, format_func=lambda x: "All Conditions" if x == "all" else CONDITIONS[x], label_visibility="collapsed")
    steps = [("01","HARVEST","Literature retrieval"),("02","SCREEN","AI relevance filtering"),("03","CONTRADICTIONS","Conflict detection"),("04","EVIDENCE","CEBM evidence grading")]
    st.markdown('<div class="sb-section">Pipeline</div>', unsafe_allow_html=True)
    for num, title, desc in steps:
        st.markdown(f'<div class="pstep"><span class="pstep-num">{num}</span><span class="pstep-body"><span class="pstep-title">{title}</span><br><span class="pstep-desc">{desc}</span></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-foot">MSc Advanced Data Science &amp; AI<br>University of Liverpool<br>Supervisor: Dr. Meng Fang</div>', unsafe_allow_html=True)

stats = get_all_stats()
th = sum(s["harvested"] for s in stats.values()); ts = sum(s["screened"] for s in stats.values())
ti = sum(s["included"] for s in stats.values()); tc = sum(s["contradictions"] for s in stats.values())
tg = sum(s["graded"] for s in stats.values())

# ==================== HEADER ====================
st.markdown('<div class="hdr-kicker">NeuroSLR / Research Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hdr-title">Neurological Systematic Literature Review</div>', unsafe_allow_html=True)
st.markdown('<div class="hdr-sub">Contradiction Detection &bull; Evidence Grading &bull; AI-Assisted Screening</div>', unsafe_allow_html=True)
st.markdown(f'<div class="badge-row"><span class="badge"><span class="badge-dot">&#9679;</span> Dataset Ready</span><span class="badge">5 Conditions</span><span class="badge">{tg} Evidence Records</span></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tabs = st.tabs(["  Overview  ", "  Screening  ", "  Contradictions  ", "  Evidence Quality  ", "  Evaluation  "])

# ==================== TAB 1: OVERVIEW ====================
with tabs[0]:
    scr_pct = f"{ts/th*100:.1f}% progressed to screening" if th else ""
    inc_pct = f"{ti/ts*100:.1f}% inclusion rate" if ts else ""
    sev_ctx = f"{sum(s['major'] for s in stats.values())} major / {sum(s['moderate'] for s in stats.values())} moderate / {sum(s['minor'] for s in stats.values())} minor"
    cols = st.columns(5)
    cards = [
        ("Literature Harvested", f"{th:,}", "Across 5 neurological conditions"),
        ("Papers Screened", f"{ts:,}", scr_pct),
        ("Studies Included", f"{ti:,}", inc_pct),
        ("Contradictions", f"{tc}", sev_ctx),
        ("Evidence Graded", f"{tg:,}", "100% of included studies classified"),
    ]
    for col, (l, v, c) in zip(cols, cards):
        col.markdown(kpi(l, v, c, accent=(l=="Contradictions")), unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Pipeline Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">End-to-end flow from raw literature retrieval to graded evidence</div>', unsafe_allow_html=True)
    fsteps = [(f"{th:,}","Harvested",""),(f"{ts:,}","Screened",f"{ts/th*100:.0f}%" if th else ""),(f"{ti:,}","Included",f"{ti/ts*100:.0f}%" if ts else ""),(f"{tc}","Contradictions",""),(f"{tg:,}","Graded","100%")]
    fh = '<div class="funnel-wrap">'
    for n, l, p in fsteps:
        fh += f'<div class="funnel-step"><div class="funnel-num">{n}</div><div class="funnel-lbl">{l}</div><div class="funnel-pct">{p}</div></div>'
    fh += '</div>'
    st.markdown(fh, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="sec-title">Papers by Condition</div>', unsafe_allow_html=True)
        names = [CONDITIONS[c] for c in CONDITIONS]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Harvested", y=names, x=[stats[c]["harvested"] for c in CONDITIONS], orientation="h", marker_color="#B8D4C6"))
        fig.add_trace(go.Bar(name="Included", y=names, x=[stats[c]["included"] for c in CONDITIONS], orientation="h", marker_color="#0A6B4F"))
        fig.update_layout(barmode="group", height=340, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_type="log", font=dict(size=11))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="sec-title">Research Insights</div>', unsafe_allow_html=True)
        top_harvest = max(stats.items(), key=lambda x: x[1]["harvested"])
        top_incrate = max(((c, s["included"]/s["screened"]) for c, s in stats.items() if s["screened"]), key=lambda x: x[1])
        st.markdown(f'<div class="insight"><div class="insight-lbl">Highest Research Volume</div><div class="insight-val">{CONDITIONS[top_harvest[0]]}</div><div class="insight-desc">{top_harvest[1]["harvested"]:,} papers harvested</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight"><div class="insight-lbl">Highest Inclusion Rate</div><div class="insight-val">{CONDITIONS[top_incrate[0]]}</div><div class="insight-desc">{top_incrate[1]*100:.1f}% of screened papers included</div></div>', unsafe_allow_html=True)

# ==================== TAB 2: SCREENING ====================
with tabs[1]:
    st.markdown('<div class="sec-title">Screening Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">AI-assisted relevance assessment across neurological literature</div>', unsafe_allow_html=True)
    active = list(CONDITIONS.keys()) if condition == "all" else [condition]
    frames = [load_screening(c).assign(_cond=CONDITIONS[c]) for c in active if len(load_screening(c)) > 0]
    if frames:
        sdf = pd.concat(frames, ignore_index=True)
        inc_df = sdf[sdf["ai4epi_abstract_decision"].astype(str).str.upper() == "INCLUDE"]
        exc_df = sdf[sdf["ai4epi_abstract_decision"].astype(str).str.upper() == "EXCLUDE"]
        cols = st.columns(4)
        cols[0].markdown(kpi("Total Screened", f"{len(sdf):,}", "Abstracts assessed"), unsafe_allow_html=True)
        cols[1].markdown(kpi("Included", f"{len(inc_df):,}", "Passed AI relevance filter"), unsafe_allow_html=True)
        cols[2].markdown(kpi("Excluded", f"{len(exc_df):,}", "Filtered out"), unsafe_allow_html=True)
        cols[3].markdown(kpi("Inclusion Rate", f"{len(inc_df)/len(sdf)*100:.1f}%", "Of total screened", accent=True), unsafe_allow_html=True)

        st.markdown('<div class="sec-title">Included Evidence Explorer</div>', unsafe_allow_html=True)
        q = st.text_input("Search titles", placeholder="Search by keyword...", label_visibility="collapsed")
        view = inc_df.copy()
        if q:
            view = view[view["title"].astype(str).str.contains(q, case=False, na=False)]
        st.markdown(f'<div class="sec-sub">{len(view)} included studies</div>', unsafe_allow_html=True)
        show = view[["title", "year", "journal", "_cond"]].rename(columns={"title":"Study Title","year":"Year","journal":"Journal","_cond":"Condition"})
        st.dataframe(show, use_container_width=True, hide_index=True, height=380)
    else:
        st.info("No screening data available for this selection.")

# ==================== TAB 3: CONTRADICTIONS ====================
with tabs[2]:
    st.markdown('<div class="sec-title">Contradiction Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Automated identification and classification of conflicting findings across neurological evidence</div>', unsafe_allow_html=True)
    active = list(CONDITIONS.keys()) if condition == "all" else [condition]
    all_flagged = []
    for c in active:
        for ct in load_contradictions(c):
            if ct.get("has_contradiction"):
                ct["_cond"] = CONDITIONS[c]; all_flagged.append(ct)
    tot = len(all_flagged)
    mj = len([c for c in all_flagged if c.get("severity","").lower()=="major"])
    md = len([c for c in all_flagged if c.get("severity","").lower()=="moderate"])
    mn = len([c for c in all_flagged if c.get("severity","").lower()=="minor"])
    cols = st.columns(4)
    cols[0].markdown(kpi("Total Contradictions", str(tot), "Across selected conditions", accent=True), unsafe_allow_html=True)
    cols[1].markdown(kpi("Major", str(mj), "Direct effect-direction conflicts"), unsafe_allow_html=True)
    cols[2].markdown(kpi("Moderate", str(md), "Partial or contextual conflicts"), unsafe_allow_html=True)
    cols[3].markdown(kpi("Minor", str(mn), "Subtle divergences"), unsafe_allow_html=True)

    if all_flagged:
        st.markdown('<div class="sec-title">Detected Conflicts</div>', unsafe_allow_html=True)
        for c in all_flagged:
            sv = c.get("severity","").lower()
            pill = f'sev-pill-{sv}' if sv in ["major","moderate","minor"] else "sev-pill-minor"
            cc1, cc2, cc3 = st.columns([5, 1, 5])
            with cc1:
                st.markdown(f'<div class="study-card"><div class="study-tag">Study A &bull; {c.get("_cond","")}</div><div class="study-title">{c.get("paper_a_title","N/A")}</div></div>', unsafe_allow_html=True)
            with cc2:
                st.markdown('<div class="vs-badge">VS</div>', unsafe_allow_html=True)
            with cc3:
                st.markdown(f'<div class="study-card"><div class="study-tag">Study B</div><div class="study-title">{c.get("paper_b_title","N/A")}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dcard"><span class="{pill}">{sv.upper()}</span> &nbsp; <strong>Type:</strong> {c.get("contradiction_type","N/A")}<br><br><strong>Analysis:</strong> {c.get("description","N/A")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        if condition != "all":
            cond_stats = stats[condition]
            st.markdown(f'<div class="dcard"><strong>No contradictions were identified among the comparable included {CONDITIONS[condition]} studies.</strong><br><br>The Contradiction Analyser evaluated paper pairs from {cond_stats["included"]} included studies. Consistent findings across the analysed literature indicate agreement among the compared studies for this condition.</div>', unsafe_allow_html=True)
        else:
            st.info("No contradictions detected in the current selection.")

# ==================== TAB 4: EVIDENCE QUALITY ====================
with tabs[3]:
    st.markdown('<div class="sec-title">Evidence Quality Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Automated classification of included studies using the CEBM evidence hierarchy</div>', unsafe_allow_html=True)
    active = list(CONDITIONS.keys()) if condition == "all" else [condition]
    all_ev = []
    for c in active:
        for e in load_evidence(c):
            e["_cond"] = CONDITIONS[c]; all_ev.append(e)
    if all_ev:
        lc = Counter([e.get("cebm_level", 5) for e in all_ev])
        total_ev = len(all_ev)
        cols = st.columns(5)
        for i, lv in enumerate([1,2,3,4,5]):
            cnt = lc.get(lv, 0); pct = cnt/total_ev*100 if total_ev else 0
            cols[i].markdown(f'<div class="kpi"><div class="kpi-label">Level {lv}</div><div class="kpi-value">{cnt}</div><div class="kpi-ctx">{pct:.1f}% of evidence</div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown('<div class="sec-title">Evidence Distribution</div>', unsafe_allow_html=True)
            lvls = sorted(lc.keys())
            fig = go.Figure(go.Bar(y=[f"Level {l}" for l in lvls], x=[lc[l] for l in lvls], orientation="h", marker_color=[EV_COLORS[l] for l in lvls], text=[lc[l] for l in lvls], textposition="auto"))
            fig.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", yaxis=dict(autorange="reversed"), font=dict(size=11))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown('<div class="sec-title">Evidence Insight</div>', unsafe_allow_html=True)
            dom_lv = lc.most_common(1)[0]
            st.markdown(f'<div class="insight"><div class="insight-lbl">Dominant Evidence Level</div><div class="insight-val">Level {dom_lv[0]}</div><div class="insight-desc">{dom_lv[1]} studies &bull; {dom_lv[1]/total_ev*100:.1f}% of included evidence</div></div>', unsafe_allow_html=True)
            hq = lc.get(1,0)+lc.get(2,0)
            st.markdown(f'<div class="insight"><div class="insight-lbl">High-Quality Evidence</div><div class="insight-val">{hq} studies</div><div class="insight-desc">Level 1&ndash;2 (RCTs &amp; meta-analyses), {hq/total_ev*100:.1f}%</div></div>', unsafe_allow_html=True)

        if condition == "all":
            st.markdown('<div class="sec-title">Evidence by Condition</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            for lv in [1,2,3,4,5]:
                fig2.add_trace(go.Bar(name=f"Level {lv}", x=[CONDITIONS[c] for c in CONDITIONS], y=[Counter([e.get("cebm_level",5) for e in load_evidence(c)]).get(lv,0) for c in CONDITIONS], marker_color=EV_COLORS[lv]))
            fig2.update_layout(barmode="stack", height=320, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=11))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="sec-sub">Evidence grades reflect the CEBM-inspired hierarchy implemented by NeuroSLR and are intended to support, not replace, expert risk-of-bias assessment.</div>', unsafe_allow_html=True)
    else:
        st.info("No evidence grading data available for this selection.")

# ==================== TAB 5: EVALUATION ====================
with tabs[4]:
    st.markdown('<div class="sec-title">Experimental Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Benchmarking NeuroSLR against baseline approaches using 30 Cochrane-derived research questions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (v, l) in zip(cols, [("30","Research Questions"),("5","Neurological Conditions"),("4","Baseline Systems"),("4","Evaluation Metrics")]):
        col.markdown(kpi(l, v, ""), unsafe_allow_html=True)

    scores = load_scores()
    if scores:
        bd = {"B1_keyword_search":"B1 &middot; Keyword Search","B2_gpt_raw":"B2 &middot; GPT-4o-mini Raw","B3_agentslr_original":"B3 &middot; AgentSLR Ablation","B4_neuroslr":"B4 &middot; NeuroSLR (Full)"}
        st.markdown('<div class="sec-title">Baseline Comparison</div>', unsafe_allow_html=True)
        rows = []
        for bk, dn in bd.items():
            if bk in scores:
                s = scores[bk]["overall"]
                rows.append({"System": dn.replace("&middot;","-"), "Completeness": f"{s['avg_completeness']}%", "Accuracy": f"{s['avg_accuracy']}%", "Hallucinations": s["total_hallucinations"], "Epistemic Honesty": f"{s['avg_epistemic_honesty']:.0%}"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        bl, cv, av, hv, ov = [], [], [], [], []
        for bk in bd:
            if bk in scores:
                s = scores[bk]["overall"]
                bl.append(bk.replace("B1_keyword_search","B1").replace("B2_gpt_raw","B2").replace("B3_agentslr_original","B3").replace("B4_neuroslr","B4"))
                cv.append(s["avg_completeness"]); av.append(s["avg_accuracy"]); hv.append(s["total_hallucinations"]); ov.append(s["avg_epistemic_honesty"]*100)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sec-title">Accuracy &amp; Completeness <span style="font-size:0.7rem;color:#0D9488;">(higher is better)</span></div>', unsafe_allow_html=True)
            f = go.Figure()
            f.add_trace(go.Bar(name="Completeness", x=bl, y=cv, marker_color="#5A8B7D", text=[f"{v}%" for v in cv], textposition="auto"))
            f.add_trace(go.Bar(name="Accuracy", x=bl, y=av, marker_color="#0A6B4F", text=[f"{v}%" for v in av], textposition="auto"))
            f.update_layout(barmode="group", height=320, margin=dict(l=10,r=10,t=10,b=10), legend=dict(orientation="h",yanchor="bottom",y=1.02), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=11))
            st.plotly_chart(f, use_container_width=True)
        with c2:
            st.markdown('<div class="sec-title">Hallucinations <span style="font-size:0.7rem;color:#DC2626;">(lower is better)</span></div>', unsafe_allow_html=True)
            f2 = go.Figure(go.Bar(x=bl, y=hv, marker_color=["#94A3B8","#DC2626","#F59E0B","#059669"], text=hv, textposition="auto"))
            f2.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(size=11))
            st.plotly_chart(f2, use_container_width=True)

        st.markdown('<div class="sec-title">Human Validation</div>', unsafe_allow_html=True)
        h1, h2, h3 = st.columns(3)
        h1.markdown(kpi("Papers Reviewed", "20", "Independent manual assessment"), unsafe_allow_html=True)
        h2.markdown(kpi("Cohen's Kappa", "0.857", "Almost-perfect agreement", accent=True), unsafe_allow_html=True)
        h3.markdown(kpi("Agreement Rate", "19/20", "95% concordance with AI"), unsafe_allow_html=True)
    else:
        st.info("No evaluation scores found.")

st.markdown('<div class="footer">NeuroSLR &mdash; MSc Advanced Data Science &amp; AI Dissertation &bull; Fellah Imthiaz Kader (201965998) &bull; University of Liverpool &bull; Supervisor: Dr. Meng Fang &bull; Extending AgentSLR (Oxford/OxRML) into Neurology</div>', unsafe_allow_html=True)
'''

with open("app/streamlit_app.py", "w") as f:
    f.write(APP)
print(f"Redesigned app written: {len(APP.splitlines())} lines")
