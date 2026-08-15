# app/streamlit_app.py
"""
NeuroSLR Streamlit Interface
Web dashboard for running and viewing systematic review results.
"""

import streamlit as st
import json
import csv
from pathlib import Path

st.set_page_config(
    page_title="NeuroSLR",
    page_icon="🧠",
    layout="wide",
)

# Brand colours
PRIMARY_COLOR = "#0F6E56"

st.markdown(f"""
<style>
    .main-header {{
        color: {PRIMARY_COLOR};
        font-size: 2.5rem;
        font-weight: 700;
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🧠 NeuroSLR</p>', unsafe_allow_html=True)
st.markdown("**Automated Systematic Literature Review for Neurology**")
st.markdown("Extending AgentSLR into neurological disease research")
st.divider()

CONDITIONS = {
    "alzheimers": "Alzheimer's Disease",
    "parkinsons": "Parkinson's Disease",
    "multiple_sclerosis": "Multiple Sclerosis",
    "epilepsy": "Epilepsy",
    "stroke": "Stroke",
}

DATA_DIR = Path("data/agentslr")

# Sidebar
st.sidebar.header("Select Condition")
condition = st.sidebar.selectbox(
    "Neurological Condition",
    options=list(CONDITIONS.keys()),
    format_func=lambda x: CONDITIONS[x],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Pipeline Stages**")
st.sidebar.markdown("1. Harvest — PubMed search")
st.sidebar.markdown("2. Screen — AI relevance filter")
st.sidebar.markdown("3. Contradiction Analysis")
st.sidebar.markdown("4. Evidence Grading")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📄 Screening Results", "⚠️ Contradictions", "📊 Evidence Grades"])

client_root = DATA_DIR / "client" / "oss" / condition

with tab1:
    st.subheader(f"Abstract Screening — {CONDITIONS[condition]}")
    screening_path = client_root / "screening" / "abstract_screening.csv"

    if screening_path.exists():
        with open(screening_path, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        included = [r for r in reader if r.get("ai4epi_abstract_decision", "").upper() == "INCLUDE"]
        excluded = [r for r in reader if r.get("ai4epi_abstract_decision", "").upper() == "EXCLUDE"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Screened", len(reader))
        col2.metric("Included", len(included))
        col3.metric("Excluded", len(excluded))

        st.markdown("### Included Papers")
        for paper in included:
            with st.expander(f"📄 {paper.get('title', 'Untitled')[:100]}"):
                st.write(f"**PMID:** {paper.get('pmid', 'N/A')}")
                st.write(f"**Journal:** {paper.get('journal', 'N/A')}")
                st.write(f"**Year:** {paper.get('year', 'N/A')}")
                st.write(f"**Abstract:** {paper.get('abstract', 'N/A')[:500]}...")
    else:
        st.info(f"No screening results yet for {CONDITIONS[condition]}. Run the abstract_screen stage first.")

with tab2:
    st.subheader(f"Contradiction Analysis — {CONDITIONS[condition]}")
    contradiction_path = client_root / "contradiction" / "contradiction_results.json"

    if contradiction_path.exists():
        with open(contradiction_path, encoding="utf-8") as f:
            results = json.load(f)

        contradictions = [r for r in results if r.get("has_contradiction")]

        col1, col2 = st.columns(2)
        col1.metric("Pairs Analysed", len(results))
        col2.metric("Contradictions Found", len(contradictions))

        severity_colors = {
            "major": "🔴",
            "moderate": "🟠",
            "minor": "🟡",
            "none": "⚪",
        }

        if contradictions:
            st.markdown("### Contradictions Detected")
            for c in contradictions:
                icon = severity_colors.get(c.get("severity", "none"), "⚪")
                with st.expander(f"{icon} [{c.get('severity', '').upper()}] {c.get('contradiction_type', '')}"):
                    st.write(f"**Paper A:** {c.get('paper_a_title', 'N/A')}")
                    st.write(f"**Claim A:** {c.get('paper_a_claim', 'N/A')}")
                    st.write(f"**Paper B:** {c.get('paper_b_title', 'N/A')}")
                    st.write(f"**Claim B:** {c.get('paper_b_claim', 'N/A')}")
                    st.write(f"**Description:** {c.get('description', 'N/A')}")
                    st.write(f"**Confidence:** {c.get('confidence', 0):.0%}")
        else:
            st.success("No contradictions found among analysed papers.")
    else:
        st.info(f"No contradiction analysis yet for {CONDITIONS[condition]}. Run the contradiction_analysis stage first.")

with tab3:
    st.subheader(f"Evidence Grading — {CONDITIONS[condition]}")
    evidence_path = client_root / "evidence" / "evidence_grades.json"

    if evidence_path.exists():
        with open(evidence_path, encoding="utf-8") as f:
            grades = json.load(f)

        level_colors = {1: "🟢", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴"}

        st.markdown("### CEBM Evidence Levels")
        for g in grades:
            icon = level_colors.get(g.get("cebm_level", 5), "⚪")
            with st.expander(f"{icon} Level {g.get('cebm_level')} — {g.get('title', 'Untitled')[:80]}"):
                st.write(f"**Study Design:** {g.get('study_design', 'N/A')}")
                st.write(f"**Sample Size:** {g.get('sample_size', 'N/A')}")
                st.write(f"**CEBM Label:** {g.get('cebm_label', 'N/A')}")
                st.write(f"**Justification:** {g.get('justification', 'N/A')}")
                st.write(f"**Confidence:** {g.get('confidence', 0):.0%}")
    else:
        st.info(f"No evidence grading yet for {CONDITIONS[condition]}. Run the evidence_grading stage first.")

st.divider()
st.caption("NeuroSLR — MSc Advanced AI & Data Science Dissertation | University of Liverpool | Extending AgentSLR (Oxford/OxRML) into Neurology")
