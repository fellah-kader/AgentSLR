#!/usr/bin/env python3
"""Generates the refined NeuroSLR streamlit app."""

APP = r'''import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="NeuroSLR | Research Intelligence", page_icon="\U0001f9e0", layout="wide", initial_sidebar_state="expanded")

# ==================== DESIGN SYSTEM ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }
.stApp { background: #F7F8F7; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1360px; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] { background: #0B2A21; width: 264px !important; border-right: 1px solid #16382C; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }
section[data-testid="stSidebar"] * { color: #C7DDD3; }
.sb-brand { font-family: 'Newsreader', serif; font-size: 1.55rem; font-weight: 600; color: #FFFFFF !important; letter-spacing: -0.3px; }
.sb-tag { font-size: 0.68rem; color: #5E9079 !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 1px; }
.sb-rule { height: 1px; background: #16382C; margin: 1.4rem 0 1rem; }
.sb-label { font-size: 0.64rem; color: #4E8069 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.6rem; }
.sb-phase { font-size: 0.6rem; color: #4E8069 !important; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin: 1.1rem 0 0.4rem; }
.pstep { display: flex; align-items: baseline; padding: 0.3rem 0; }
.pstep-num { font-size: 0.65rem; font-weight: 700; color: #3C6B57 !important; margin-right: 0.6rem; min-width: 14px; }
.pstep-title { font-size: 0.82rem; font-weight: 500; color: #DCEBE4 !important; }
.sb-foot { font-size: 0.68rem; color: #4E8069 !important; line-height: 1.6; }

/* Dropdown contrast fix */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div { background: #FFFFFF !important; border-color: #16382C !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] div { color: #0B2A21 !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] svg { color: #0B2A21 !important; fill: #0B2A21 !important; }

/* ---- Header ---- */
.hdr-kicker { font-size: 0.7rem; font-weight: 700; color: #0D8A6A; text-transform: uppercase; letter-spacing: 2px; }
.hdr-title { font-family: 'Newsreader', serif; font-size: 2.3rem; font-weight: 600; color: #0B2A21; letter-spacing: -0.5px; margin: 4px 0 2px; line-height: 1.05; }
.hdr-sub { font-size: 0.98rem; color: #5C7A6E; font-weight: 400; }
.hdr-rule { height: 2px; width: 52px; background: #0D8A6A; margin: 1rem 0 0; }

/* ---- Editorial lead ---- */
.lead { font-family: 'Newsreader', serif; font-size: 1.25rem; line-height: 1.55; color: #24443A; font-weight: 400; max-width: 780px; margin: 0.4rem 0 0.5rem; }
.lead b { font-weight: 600; color: #0B2A21; }

/* ---- Metric strip (not cards) ---- */
.mstrip { display: flex; border: 1px solid #E1E8E4; border-radius: 4px; background: #FFFFFF; overflow: hidden; }
.mcell { flex: 1; padding: 1.1rem 1.3rem; border-right: 1px solid #EDF1EF; }
.mcell:last-child { border-right: none; }
.mcell-val { font-family: 'Newsreader', serif; font-size: 1.85rem; font-weight: 600; color: #0B2A21; line-height: 1; }
.mcell-lbl { font-size: 0.7rem; color: #7C9488; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 0.4rem; }
.mcell-ctx { font-size: 0.72rem; color: #A0B3AA; margin-top: 3px; }
.mcell-hi .mcell-val { color: #0D8A6A; }

/* ---- Section ---- */
.sec { font-family: 'Newsreader', serif; font-size: 1.35rem; font-weight: 600; color: #0B2A21; margin: 2rem 0 0.2rem; }
.sec-sub { font-size: 0.85rem; color: #7C9488; margin-bottom: 1rem; }

/* ---- Flow ---- */
.flow { display: flex; align-items: center; margin: 0.5rem 0 0.5rem; }
.flow-node { flex: 1; text-align: center; padding: 0.2rem; }
.flow-val { font-family: 'Newsreader', serif; font-size: 1.5rem; font-weight: 600; color: #0B2A21; }
.flow-lbl { font-size: 0.68rem; color: #7C9488; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.flow-pct { font-size: 0.66rem; color: #0D8A6A; font-weight: 700; margin-top: 1px; }
.flow-arrow { color: #C4D3CC; font-size: 1.1rem; padding: 0 0.3rem; }

/* ---- Insight (editorial, left border) ---- */
.insight { border-left: 3px solid #0D8A6A; padding: 0.3rem 0 0.3rem 1rem; margin-bottom: 1.2rem; }
.insight-lbl { font-size: 0.66rem; font-weight: 700; color: #0D8A6A; text-transform: uppercase; letter-spacing: 1px; }
.insight-val { font-family: 'Newsreader', serif; font-size: 1.3rem; font-weight: 600; color: #0B2A21; margin: 2px 0; }
.insight-desc { font-size: 0.82rem; color: #5C7A6E; line-height: 1.4; }

/* ---- Finding stat (evaluation highlights) ---- */
.fstat { text-align: left; padding: 1.1rem 1.3rem; background: #0B2A21; border-radius: 4px; }
.fstat-val { font-family: 'Newsreader', serif; font-size: 2rem; font-weight: 600; color: #FFFFFF; line-height: 1; }
.fstat-lbl { font-size: 0.72rem; color: #7FB3A0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.5rem; }
.fstat-desc { font-size: 0.74rem; color: #A9C7BC; margin-top: 4px; line-height: 1.35; }

/* ---- Contradiction ---- */
.conflict-hd { display: flex; align-items: center; gap: 0.6rem; margin: 1.4rem 0 0.6rem; }
.conflict-idx { font-family: 'Newsreader', serif; font-size: 1.1rem; color: #0D8A6A; font-weight: 600; }
.sev-tag { display: inline-flex; align-items: center; gap: 5px; padding: 0.2rem 0.6rem; border-radius: 3px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.sev-major { background: #FBEAEA; color: #B4232A; border: 1px solid #EEC4C4; }
.sev-moderate { background: #FCF3E2; color: #A8680C; border: 1px solid #EAD5AE; }
.sev-minor { background: #FBF8E4; color: #897406; border: 1px solid #E7DFA8; }
.study-panel { background: #FFFFFF; border: 1px solid #E1E8E4; border-radius: 4px; padding: 0.9rem 1.1rem; height: 100%; }
.study-tag { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #9BB0A6; }
.study-title { font-size: 0.86rem; font-weight: 500; color: #1E3A31; line-height: 1.35; margin-top: 5px; }
.analysis-panel { background: #FBFCFB; border: 1px solid #E1E8E4; border-left: 3px solid #B4232A; border-radius: 4px; padding: 0.9rem 1.1rem; margin-top: 0.6rem; }
.analysis-lbl { font-size: 0.66rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #7C9488; margin-bottom: 4px; }
.analysis-txt { font-size: 0.85rem; color: #3A5449; line-height: 1.5; }
.vs-mark { text-align: center; font-family: 'Newsreader', serif; font-style: italic; color: #B89; font-size: 0.95rem; padding-top: 1.2rem; }

/* ---- Evidence tier ---- */
.tier { border: 1px solid #E1E8E4; border-radius: 4px; padding: 1rem 1.2rem; background: #FFFFFF; margin-bottom: 0.6rem; }
.tier-hi { border-left: 4px solid #0D8A6A; }
.tier-mid { border-left: 4px solid #D99514; }
.tier-lo { border-left: 4px solid #C0555A; }
.tier-name { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #7C9488; }
.tier-val { font-family: 'Newsreader', serif; font-size: 1.7rem; font-weight: 600; color: #0B2A21; }
.tier-desc { font-size: 0.76rem; color: #80988E; }

/* ---- Evidence pills ---- */
.evp { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 3px; font-size: 0.7rem; font-weight: 700; }
.evp1 { background: #D6F0E4; color: #0A6B4F; }
.evp2 { background: #D9F0EC; color: #0C7A6E; }
.evp3 { background: #FBEFD6; color: #A8680C; }
.evp4 { background: #FBE6D6; color: #B85A25; }
.evp5 { background: #FBE0E0; color: #B4232A; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] { gap: 2rem; border-bottom: 1px solid #DDE6E1; }
.stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 0.88rem; color: #7C9488; padding: 0.5rem 0; background: transparent; }
.stTabs [aria-selected="true"] { color: #0B2A21 !important; }
.stTabs [data-baseweb="tab-highlight"] { background: #0D8A6A; }

/* ---- Table ---- */
[data-testid="stDataFrame"] { border: 1px solid #E1E8E4; border-radius: 4px; }

.foot { text-align: center; color: #A9BCB2; font-size: 0.74rem; padding: 2.5rem 0 0.5rem; border-top: 1px solid #E1E8E4; margin-top: 2.5rem; }
</style>
""", unsafe_allow_html=True)

# ==================== CONSTANTS ====================
CONDITIONS = {"alzheimers": "Alzheimer's Disease", "parkinsons": "Parkinson's Disease", "multiple_sclerosis": "Multiple Sclerosis", "epilepsy": "Epilepsy", "stroke": "Stroke"}
EV_COLORS = {1: "#0A6B4F", 2: "#0C7A6E", 3: "#D99514", 4: "#B85A25", 5: "#C0555A"}
DATA_DIR = Path("data/agentslr")
EVAL_DIR = Path("evaluation")

# ==================== LOADERS ====================
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
        stats[cond] = {"harvested": hv, "screened": len(sc), "included": inc, "contradictions": len(fl), "graded": len(ev),
                       "major": len([c for c in fl if c.get("severity","").lower()=="major"]),
                       "moderate": len([c for c in fl if c.get("severity","").lower()=="moderate"]),
                       "minor": len([c for c in fl if c.get("severity","").lower()=="minor"])}
    return stats

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('<div class="sb-brand">\U0001f9e0 NeuroSLR</div><div class="sb-tag">Evidence Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-label">Condition</div>', unsafe_allow_html=True)
    opts = ["all"] + list(CONDITIONS.keys())
    condition = st.selectbox("Condition", options=opts, format_func=lambda x: "All Conditions" if x == "all" else CONDITIONS[x], label_visibility="collapsed")
    st.markdown('<div class="sb-phase">Data Collection</div>', unsafe_allow_html=True)
    st.markdown('<div class="pstep"><span class="pstep-num">01</span><span class="pstep-title">Literature Harvest</span></div><div class="pstep"><span class="pstep-num">02</span><span class="pstep-title">AI Screening</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-phase">Research Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="pstep"><span class="pstep-num">03</span><span class="pstep-title">Contradiction Analysis</span></div><div class="pstep"><span class="pstep-num">04</span><span class="pstep-title">Evidence Grading</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-phase">Validation</div>', unsafe_allow_html=True)
    st.markdown('<div class="pstep"><span class="pstep-num">05</span><span class="pstep-title">Benchmark Evaluation</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-foot">MSc Advanced Data Science &amp; AI<br>University of Liverpool<br>Supervisor: Dr. Meng Fang</div>', unsafe_allow_html=True)

stats = get_all_stats()
th = sum(s["harvested"] for s in stats.values()); ts = sum(s["screened"] for s in stats.values())
ti = sum(s["included"] for s in stats.values()); tc = sum(s["contradictions"] for s in stats.values())
tg = sum(s["graded"] for s in stats.values())
tmaj = sum(s["major"] for s in stats.values()); tmod = sum(s["moderate"] for s in stats.values())

# ==================== HEADER ====================
st.markdown('<div class="hdr-kicker">Neurological Evidence Synthesis</div>', unsafe_allow_html=True)
st.markdown('<div class="hdr-title">NeuroSLR Research Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hdr-sub">Extending AgentSLR into neurology with automated contradiction detection and evidence grading</div>', unsafe_allow_html=True)
st.markdown('<div class="hdr-rule"></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tabs = st.tabs(["Overview", "AI Screening", "Contradiction Intelligence", "Evidence Quality", "Scientific Evaluation"])

# ==================== TAB 1: OVERVIEW ====================
with tabs[0]:
    st.markdown('<p class="lead">NeuroSLR is an <b>AI-powered systematic literature review platform</b> for neurology. It harvests and screens biomedical literature across five conditions, then applies two novel analytical layers &mdash; <b>automated contradiction detection</b> and <b>CEBM evidence grading</b> &mdash; to surface not just what the research says, but where it disagrees and how far it can be trusted.</p>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Research Corpus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Scale of the evidence base processed end-to-end</div>', unsafe_allow_html=True)
    strip = '<div class="mstrip">'
    cells = [("Papers Harvested", f"{th:,}", "5 conditions", False),
             ("Screened", f"{ts:,}", f"{ts/th*100:.0f}% of harvest", False),
             ("Studies Included", f"{ti:,}", f"{ti/ts*100:.0f}% inclusion", False),
             ("Conditions", "5", "neurological", False),
             ("Evidence Graded", f"{tg:,}", "100% of included", True)]
    for lbl, val, ctx, hi in cells:
        hc = " mcell-hi" if hi else ""
        strip += f'<div class="mcell{hc}"><div class="mcell-val">{val}</div><div class="mcell-lbl">{lbl}</div><div class="mcell-ctx">{ctx}</div></div>'
    strip += '</div>'
    st.markdown(strip, unsafe_allow_html=True)

    st.markdown('<div class="sec">Pipeline Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Progressive refinement from raw literature to graded, conflict-checked evidence</div>', unsafe_allow_html=True)
    flow_nodes = [(f"{th:,}","Harvest",""),(f"{ts:,}","Screen",f"{ts/th*100:.0f}%"),(f"{ti:,}","Include",f"{ti/ts*100:.0f}%"),(f"{tc}","Contradictions",""),(f"{tg:,}","Graded","100%")]
    fh = '<div class="flow">'
    for i,(v,l,p) in enumerate(flow_nodes):
        fh += f'<div class="flow-node"><div class="flow-val">{v}</div><div class="flow-lbl">{l}</div><div class="flow-pct">{p}</div></div>'
        if i < len(flow_nodes)-1: fh += '<div class="flow-arrow">&rarr;</div>'
    fh += '</div>'
    st.markdown(fh, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown('<div class="sec">Cross-Condition Comparison</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Included studies per condition (log scale reflects harvest disparity)</div>', unsafe_allow_html=True)
        names = [CONDITIONS[c] for c in CONDITIONS]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Harvested", y=names, x=[stats[c]["harvested"] for c in CONDITIONS], orientation="h", marker_color="#C8DDD2"))
        fig.add_trace(go.Bar(name="Included", y=names, x=[stats[c]["included"] for c in CONDITIONS], orientation="h", marker_color="#0B2A21"))
        fig.update_layout(barmode="overlay", height=320, margin=dict(l=10,r=10,t=8,b=8), legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_type="log", font=dict(size=11, color="#3A5449"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="sec">Research Insights</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">What the corpus reveals</div>', unsafe_allow_html=True)
        top_h = max(stats.items(), key=lambda x: x[1]["harvested"])
        top_i = max(((c, s["included"]/s["screened"]) for c, s in stats.items() if s["screened"]), key=lambda x: x[1])
        all_lv = []
        for c in CONDITIONS: all_lv.extend([e.get("cebm_level",5) for e in load_evidence(c)])
        dom = Counter(all_lv).most_common(1)[0] if all_lv else (3,0)
        st.markdown(f'<div class="insight"><div class="insight-lbl">Largest Evidence Base</div><div class="insight-val">{CONDITIONS[top_h[0]]}</div><div class="insight-desc">{top_h[1]["harvested"]:,} papers harvested &mdash; the most heavily researched of the five conditions.</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight"><div class="insight-lbl">Conflicting Evidence</div><div class="insight-val">{tc} contradictions</div><div class="insight-desc">{tmaj} major and {tmod} moderate conflicts detected between included studies &mdash; disagreements a standard summary would hide.</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight"><div class="insight-lbl">Dominant Evidence Tier</div><div class="insight-val">Level {dom[0]}</div><div class="insight-desc">{dom[1]} of {tg} graded studies &mdash; showing where the neurology evidence base concentrates.</div></div>', unsafe_allow_html=True)

# ==================== TAB 2: SCREENING ====================
with tabs[1]:
    st.markdown('<div class="sec">AI Screening</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Neurology-specialised relevance assessment across harvested literature</div>', unsafe_allow_html=True)
    active = list(CONDITIONS.keys()) if condition == "all" else [condition]
    frames = [load_screening(c).assign(_cond=CONDITIONS[c]) for c in active if len(load_screening(c)) > 0]
    if frames:
        sdf = pd.concat(frames, ignore_index=True)
        inc_df = sdf[sdf["ai4epi_abstract_decision"].astype(str).str.upper() == "INCLUDE"]
        exc_df = sdf[sdf["ai4epi_abstract_decision"].astype(str).str.upper() == "EXCLUDE"]
        strip = '<div class="mstrip">'
        for lbl, val, ctx, hi in [("Screened", f"{len(sdf):,}", "abstracts assessed", False),
                                   ("Included", f"{len(inc_df):,}", "passed filter", True),
                                   ("Excluded", f"{len(exc_df):,}", "filtered out", False),
                                   ("Inclusion Rate", f"{len(inc_df)/len(sdf)*100:.1f}%", "of screened", False)]:
            hc = " mcell-hi" if hi else ""
            strip += f'<div class="mcell{hc}"><div class="mcell-val">{val}</div><div class="mcell-lbl">{lbl}</div><div class="mcell-ctx">{ctx}</div></div>'
        strip += '</div>'
        st.markdown(strip, unsafe_allow_html=True)

        st.markdown('<div class="sec">Included Evidence Explorer</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns([3, 1])
        with fc1:
            q = st.text_input("Search", placeholder="Search study titles by keyword...", label_visibility="collapsed")
        with fc2:
            years = sorted([int(y) for y in inc_df["year"].dropna().unique() if str(y).isdigit()], reverse=True)
            yr = st.selectbox("Year", ["All years"] + years, label_visibility="collapsed")
        view = inc_df.copy()
        if q: view = view[view["title"].astype(str).str.contains(q, case=False, na=False)]
        if yr != "All years": view = view[view["year"] == yr]
        st.markdown(f'<div class="sec-sub">{len(view)} of {len(inc_df)} included studies</div>', unsafe_allow_html=True)
        show = view[["title", "year", "journal", "_cond"]].rename(columns={"title":"Study Title","year":"Year","journal":"Journal","_cond":"Condition"})
        st.dataframe(show, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No screening data available for this selection.")

# ==================== TAB 3: CONTRADICTIONS ====================
with tabs[2]:
    st.markdown('<div class="sec">Contradiction Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">A novel NeuroSLR component &mdash; detecting and classifying conflicting findings between studies</div>', unsafe_allow_html=True)
    active = list(CONDITIONS.keys()) if condition == "all" else [condition]
    flagged = []
    for c in active:
        for ct in load_contradictions(c):
            if ct.get("has_contradiction"):
                ct["_cond"] = CONDITIONS[c]; flagged.append(ct)
    tot = len(flagged)
    mj = len([c for c in flagged if c.get("severity","").lower()=="major"])
    md = len([c for c in flagged if c.get("severity","").lower()=="moderate"])
    mn = len([c for c in flagged if c.get("severity","").lower()=="minor"])
    strip = '<div class="mstrip">'
    for lbl, val, ctx, hi in [("Conflicts Found", str(tot), "in current view", True),
                              ("Major", str(mj), "effect-direction", False),
                              ("Moderate", str(md), "contextual", False),
                              ("Minor", str(mn), "subtle", False)]:
        hc = " mcell-hi" if hi else ""
        strip += f'<div class="mcell{hc}"><div class="mcell-val">{val}</div><div class="mcell-lbl">{lbl}</div><div class="mcell-ctx">{ctx}</div></div>'
    strip += '</div>'
    st.markdown(strip, unsafe_allow_html=True)

    if flagged:
        for i, c in enumerate(flagged, 1):
            sv = c.get("severity","").lower()
            sev_cls = f"sev-{sv}" if sv in ["major","moderate","minor"] else "sev-minor"
            st.markdown(f'<div class="conflict-hd"><span class="conflict-idx">Conflict {i:02d}</span><span class="sev-tag {sev_cls}">&#9679; {sv.upper()}</span><span style="font-size:0.78rem;color:#7C9488;">{c.get("contradiction_type","")} &bull; {c.get("_cond","")}</span></div>', unsafe_allow_html=True)
            cc1, cc2, cc3 = st.columns([6, 1, 6])
            cc1.markdown(f'<div class="study-panel"><div class="study-tag">Study A</div><div class="study-title">{c.get("paper_a_title","N/A")}</div></div>', unsafe_allow_html=True)
            cc2.markdown('<div class="vs-mark">vs</div>', unsafe_allow_html=True)
            cc3.markdown(f'<div class="study-panel"><div class="study-tag">Study B</div><div class="study-title">{c.get("paper_b_title","N/A")}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div c