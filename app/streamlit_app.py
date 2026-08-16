import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title='NeuroSLR', page_icon='🧠', layout='wide')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*='css'] { font-family: Inter, sans-serif; }
.main-title { font-size: 2.6rem; font-weight: 700; color: #0D3B2E; margin-bottom: 0; letter-spacing: -1px; }
.main-subtitle { font-size: 1.1rem; color: #4A7A6A; margin-top: 4px; margin-bottom: 2rem; font-weight: 400; }
.metric-card { background: linear-gradient(135deg, #EBF5F0 0%, #D4E8DE 100%); border: 1px solid #B8D4C6; border-radius: 14px; padding: 1.4rem 1.6rem; text-align: center; box-shadow: 0 2px 8px rgba(13,59,46,0.06); }
.metric-value { font-size: 2.4rem; font-weight: 700; color: #0D3B2E; line-height: 1.1; }
.metric-label { font-size: 0.78rem; color: #4A7A6A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 6px; }
.pipeline-box { background: #0D3B2E; border-radius: 10px; padding: 0.9rem; text-align: center; color: white; margin: 4px 0; font-weight: 600; font-size: 0.9rem; }
.pipeline-arrow { text-align: center; font-size: 1.2rem; color: #0D3B2E; padding: 2px 0; }
.sev-major { background: #FEE2E2; border-left: 5px solid #DC2626; padding: 1rem 1.2rem; border-radius: 0 10px 10px 0; margin: 8px 0; }
.sev-moderate { background: #FEF3C7; border-left: 5px solid #F59E0B; padding: 1rem 1.2rem; border-radius: 0 10px 10px 0; margin: 8px 0; }
.finding-card { background: linear-gradient(135deg, #F7FAF8 0%, #EDF3EF 100%); border: 1px solid #D4E8DE; border-radius: 14px; padding: 1.4rem; margin: 6px 0; box-shadow: 0 2px 8px rgba(13,59,46,0.04); }
.ev-1 { color: #059669; font-weight: 700; } .ev-2 { color: #0D9488; font-weight: 700; } .ev-3 { color: #D97706; font-weight: 700; } .ev-4 { color: #EA580C; font-weight: 700; } .ev-5 { color: #DC2626; font-weight: 700; }
div[data-testid='stTabs'] button { font-weight: 600; font-size: 0.95rem; }
.footer { text-align: center; color: #8CA69B; font-size: 0.78rem; padding: 2.5rem 0 1rem; border-top: 1px solid #D4E8DE; margin-top: 3rem; }
</style>
''', unsafe_allow_html=True)

CONDITIONS = {'alzheimers': "Alzheimer's Disease", 'parkinsons': "Parkinson's Disease", 'multiple_sclerosis': 'Multiple Sclerosis', 'epilepsy': 'Epilepsy', 'stroke': 'Stroke'}
CEBM = {1: 'Systematic Review / Meta-analysis', 2: 'Individual RCT', 3: 'Cohort Study', 4: 'Case-Control Study', 5: 'Case Report / Expert Opinion'}
DATA_DIR = Path('data/agentslr')
EVAL_DIR = Path('evaluation')

@st.cache_data
def load_screening(cond):
    p = DATA_DIR / 'client' / 'oss' / cond / 'screening' / 'abstract_screening.csv'
    return pd.read_csv(p) if p.exists() else pd.DataFrame()

@st.cache_data
def load_contradictions(cond):
    p = DATA_DIR / 'client' / 'oss' / cond / 'contradiction' / 'contradiction_results.json'
    if p.exists():
        with open(p) as f: return json.load(f)
    return []

@st.cache_data
def load_evidence(cond):
    p = DATA_DIR / 'client' / 'oss' / cond / 'evidence' / 'evidence_grades.json'
    if p.exists():
        with open(p) as f: return json.load(f)
    return []

@st.cache_data
def load_harvest_count(cond):
    p = DATA_DIR / 'harvests' / cond / 'harvest_metadata.csv'
    return len(pd.read_csv(p, usecols=['article_id'])) if p.exists() else 0

@st.cache_data
def load_scores():
    sd = EVAL_DIR / 'results'
    if sd.exists():
        fs = sorted(sd.glob('scores_all_*.json'), reverse=True)
        if fs:
            with open(fs[0]) as f: return json.load(f)
    return {}

def get_all_stats():
    stats = {}
    for cond in CONDITIONS:
        sc = load_screening(cond)
        ct = load_contradictions(cond)
        ev = load_evidence(cond)
        hv = load_harvest_count(cond)
        inc = len(sc[sc['ai4epi_abstract_decision'].astype(str).str.upper() == 'INCLUDE']) if len(sc) > 0 else 0
        fl = len([c for c in ct if c.get('has_contradiction')])
        stats[cond] = {'harvested': hv, 'screened': len(sc), 'included': inc, 'contradictions': fl, 'graded': len(ev)}
    return stats

st.markdown('<p class="main-title">🧠 NeuroSLR</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Neurology-Specialised Systematic Literature Review with Contradiction Detection and Evidence Grading</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### Navigation')
    condition = st.selectbox('Select Condition', options=list(CONDITIONS.keys()), format_func=lambda x: CONDITIONS[x])
    st.markdown('---')
    st.markdown('### Pipeline')
    for step in ['1. Harvest', '2. Screen', '3. Contradictions', '4. Evidence Grade']:
        st.markdown(f'<div class="pipeline-box">{step}</div>', unsafe_allow_html=True)
        if step != '4. Evidence Grade': st.markdown('<div class="pipeline-arrow">\u2193</div>', unsafe_allow_html=True)
    st.markdown('---')
    st.caption('MSc Advanced Data Science and AI')
    st.caption('University of Liverpool')
    st.caption('Supervisor: Dr. Meng Fang')

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Dashboard Overview', 'Screening Results', 'Contradiction Analysis', 'Evidence Grades', 'Evaluation Results'])

with tab1:
    stats = get_all_stats()
    th = sum(s['harvested'] for s in stats.values())
    ts = sum(s['screened'] for s in stats.values())
    ti = sum(s['included'] for s in stats.values())
    tc = sum(s['contradictions'] for s in stats.values())
    tg = sum(s['graded'] for s in stats.values())
    cols = st.columns(5)
    for col, (lbl, val) in zip(cols, [('Papers Harvested', f'{th:,}'), ('Papers Screened', f'{ts:,}'), ('Papers Included', f'{ti:,}'), ('Contradictions', str(tc)), ('Evidence Graded', f'{tg:,}')]):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('#### Papers by Condition')
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Harvested', x=[CONDITIONS[c] for c in CONDITIONS], y=[stats[c]['harvested'] for c in CONDITIONS], marker_color='#B8D4C6', text=[stats[c]['harvested'] for c in CONDITIONS], textposition='auto'))
        fig.add_trace(go.Bar(name='Included', x=[CONDITIONS[c] for c in CONDITIONS], y=[stats[c]['included'] for c in CONDITIONS], marker_color='#0D3B2E', text=[stats[c]['included'] for c in CONDITIONS], textposition='auto'))
        fig.update_layout(barmode='group', height=400, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('#### Evidence Grade Distribution')
        all_lv = []
        for cn in CONDITIONS: all_lv.extend([e.get('cebm_level', 5) for e in load_evidence(cn)])
        if all_lv:
            lc = Counter(all_lv)
            fig2 = go.Figure(data=[go.Pie(labels=[f'Level {l}' for l in sorted(lc.keys())], values=[lc[l] for l in sorted(lc.keys())], hole=0.45, marker_colors=['#059669','#0D9488','#D97706','#EA580C','#DC2626'][:len(lc)], textinfo='label+value')])
            fig2.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)
    st.markdown('#### Contradictions Across Conditions')
    cd = []
    for cn in CONDITIONS:
        fl = [c for c in load_contradictions(cn) if c.get('has_contradiction')]
        mj = len([c for c in fl if c.get('severity','').lower()=='major'])
        md = len([c for c in fl if c.get('severity','').lower()=='moderate'])
        cd.append({'Condition': CONDITIONS[cn], 'Major': mj, 'Moderate': md})
    cdf = pd.DataFrame(cd)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='Major', x=cdf['Condition'], y=cdf['Major'], marker_color='#DC2626'))
    fig3.add_trace(go.Bar(name='Moderate', x=cdf['Condition'], y=cdf['Moderate'], marker_color='#F59E0B'))
    fig3.update_layout(barmode='stack', height=320, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.markdown(f'### Screening Results - {CONDITIONS[condition]}')
    sdf = load_screening(condition)
    if len(sdf) > 0:
        inc_df = sdf[sdf['ai4epi_abstract_decision'].astype(str).str.upper() == 'INCLUDE']
        exc_df = sdf[sdf['ai4epi_abstract_decision'].astype(str).str.upper() == 'EXCLUDE']
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Total Screened', len(sdf))
        c2.metric('Included', len(inc_df))
        c3.metric('Excluded', len(exc_df))
        c4.metric('Inclusion Rate', f'{len(inc_df)/len(sdf)*100:.1f}%')
        fig_s = go.Figure(data=[go.Pie(labels=['Included','Excluded'], values=[len(inc_df),len(exc_df)], hole=0.4, marker_colors=['#0D3B2E','#B8D4C6'], textinfo='label+percent')])
        fig_s.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_s, use_container_width=True)
        st.markdown('#### Included Papers')
        for _, p in inc_df.iterrows():
            t = str(p.get('title', 'Untitled')) if not pd.isna(p.get('title')) else 'Untitled'
            with st.expander(t[:100]):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**PMID:** {p.get('pmid', 'N/A')}")
                c2.write(f"**Journal:** {p.get('journal', 'N/A')}")
                c3.write(f"**Year:** {p.get('year', 'N/A')}")
                ab = str(p.get('abstract', '')) if not pd.isna(p.get('abstract')) else 'No abstract'
                st.write(ab[:600])
    else: st.info('No screening results available.')

with tab3:
    st.markdown(f'### Contradiction Analysis - {CONDITIONS[condition]}')
    cdata = load_contradictions(condition)
    if cdata:
        fl = [c for c in cdata if c.get('has_contradiction')]
        nf = len(cdata) - len(fl)
        c1, c2, c3 = st.columns(3)
        c1.metric('Pairs Analysed', len(cdata))
        c2.metric('Contradictions Found', len(fl))
        c3.metric('Agreement Rate', f'{nf/len(cdata)*100:.0f}%')
        if fl:
            st.markdown('#### Detected Contradictions')
            for c in fl:
                sv = c.get('severity','').lower()
                css = 'sev-major' if sv == 'major' else 'sev-moderate'
                ct2 = c.get('contradiction_type', '')
                st.markdown(f'<div class="{css}"><strong>{sv.upper()}</strong> - {ct2}</div>', unsafe_allow_html=True)
                with st.expander(f"{c.get('paper_a_title','A')[:50]} vs {c.get('paper_b_title','B')[:50]}"):
                    ca, cb = st.columns(2)
                    ca.write(f"**Paper A:** {c.get('paper_a_title','N/A')}")
                    cb.write(f"**Paper B:** {c.get('paper_b_title','N/A')}")
                    st.write(f"**Description:** {c.get('description','N/A')}")
        else: st.success('No contradictions detected.')
    else: st.info('No contradiction data available.')

with tab4:
    st.markdown(f'### CEBM Evidence Grades - {CONDITIONS[condition]}')
    edata = load_evidence(condition)
    if edata:
        lvs = [e.get('cebm_level', 5) for e in edata]
        lc = Counter(lvs)
        cc, cl = st.columns([2, 1])
        with cc:
            cmap = {1:'#059669', 2:'#0D9488', 3:'#D97706', 4:'#EA580C', 5:'#DC2626'}
            fig_e = go.Figure(data=[go.Bar(x=[f'Level {l}' for l in sorted(lc.keys())], y=[lc[l] for l in sorted(lc.keys())], marker_color=[cmap.get(l,'#999') for l in sorted(lc.keys())], text=[lc[l] for l in sorted(lc.keys())], textposition='auto')])
            fig_e.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_title='Papers')
            st.plotly_chart(fig_e, use_container_width=True)
        with cl:
            st.markdown('**CEBM Hierarchy:**')
            for lv, lb in CEBM.items():
                cnt = lc.get(lv, 0)
                st.markdown(f'<span class="ev-{lv}">Level {lv}</span> ({cnt}) - {lb}', unsafe_allow_html=True)
        st.markdown('#### All Graded Papers')
        for g in sorted(edata, key=lambda e: e.get('cebm_level', 5)):
            lv = g.get('cebm_level', 5)
            tt = g.get('title', 'Untitled')[:90]
            cf = g.get('confidence', 0)
            with st.expander(f'Level {lv} - {tt}'):
                c1, c2 = st.columns(2)
                c1.write(f"**Study Design:** {g.get('study_design','N/A')}")
                c2.write(f"**Sample Size:** {g.get('sample_size','N/A')}")
                st.write(f"**CEBM Label:** {g.get('cebm_label','N/A')}")
                st.write(f"**Justification:** {g.get('justification','N/A')}")
                st.progress(cf, text=f'Confidence: {cf:.0%}')
    else: st.info('No evidence grading data available.')

with tab5:
    st.markdown('### Evaluation Results')
    st.markdown('30-question Cochrane benchmark across 5 neurological conditions')
    scores = load_scores()
    if scores:
        st.markdown('#### 4-Baseline Comparison')
        bd = {'B1_keyword_search':'B1 - Keyword Search','B2_gpt_raw':'B2 - GPT-4o-mini Raw','B3_agentslr_original':'B3 - AgentSLR Ablation','B4_neuroslr':'B4 - NeuroSLR'}
        td = []
        for bk, dn in bd.items():
            if bk in scores:
                s = scores[bk]['overall']
                td.append({'Baseline': dn, 'Completeness': f"{s['avg_completeness']}%", 'Accuracy': f"{s['avg_accuracy']}%", 'Hallucinations': s['total_hallucinations'], 'Honesty': f"{s['avg_epistemic_honesty']:.0%}"})
        if td: st.dataframe(pd.DataFrame(td), use_container_width=True, hide_index=True)
        bl, cv, av, hv, ov = [], [], [], [], []
        for bk, dn in bd.items():
            if bk in scores:
                s = scores[bk]['overall']
                bl.append(dn.split(' - ')[0])
                cv.append(s['avg_completeness']); av.append(s['avg_accuracy'])
                hv.append(s['total_hallucinations']); ov.append(s['avg_epistemic_honesty']*100)
        ca, cb = st.columns(2)
        with ca:
            st.markdown('#### Completeness vs Accuracy')
            fc = go.Figure()
            fc.add_trace(go.Bar(name='Completeness', x=bl, y=cv, marker_color='#5A8B7D', text=[f'{v}%' for v in cv], textposition='auto'))
            fc.add_trace(go.Bar(name='Accuracy', x=bl, y=av, marker_color='#0D3B2E', text=[f'{v}%' for v in av], textposition='auto'))
            fc.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fc, use_container_width=True)
        with cb:
            st.markdown('#### Hallucinations and Honesty')
            fh = go.Figure()
            fh.add_trace(go.Bar(name='Hallucinations', x=bl, y=hv, marker_color='#DC2626', text=hv, textposition='auto'))
            fh.add_trace(go.Bar(name='Honesty %', x=bl, y=ov, marker_color='#059669', text=[f'{v:.0f}%' for v in ov], textposition='auto'))
            fh.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=30, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fh, use_container_width=True)
        st.markdown('#### Key Findings')
        f1, f2, f3 = st.columns(3)
        f1.markdown('<div class="finding-card"><div class="metric-value" style="font-size:1.8rem;color:#DC2626;">10x</div><div class="metric-label">Fewer Hallucinations</div><p style="font-size:0.85rem;color:#666;margin-top:0.5rem;">NeuroSLR: 4 vs GPT Raw: 42</p></div>', unsafe_allow_html=True)
        f2.markdown('<div class="finding-card"><div class="metric-value" style="font-size:1.8rem;color:#059669;">95%</div><div class="metric-label">Factual Accuracy</div><p style="font-size:0.85rem;color:#666;margin-top:0.5rem;">vs 63% for unconditioned GPT-4o-mini</p></div>', unsafe_allow_html=True)
        f3.markdown('<div class="finding-card"><div class="metric-value" style="font-size:1.8rem;color:#0D3B2E;">3.4x</div><div class="metric-label">Novel Component Improvement</div><p style="font-size:0.85rem;color:#666;margin-top:0.5rem;">NeuroSLR 21.8% vs Ablation 6.5%</p></div>', unsafe_allow_html=True)
        st.markdown('#### Human-AI Agreement')
        k1, k2 = st.columns(2)
        k1.metric('Cohens Kappa', '0.857')
        k1.caption('Almost perfect agreement (Landis and Koch)')
        k2.metric('Agreement Rate', '19/20 (95%)')
        k2.caption('20-paper independent validation')
    else: st.info('No evaluation scores found.')

st.markdown('<div class="footer">NeuroSLR - MSc Advanced Data Science and AI Dissertation | Fellah Imthiaz Kader (201965998) | University of Liverpool | Supervisor: Dr. Meng Fang | Extending AgentSLR (Oxford/OxRML) into Neurology</div>', unsafe_allow_html=True)
