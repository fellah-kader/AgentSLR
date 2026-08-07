import json
import os
import time
import pandas as pd
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def load_condition_data(condition):
    base = f"data/agentslr/client/oss/{condition}"

    # Screened papers (included only)
    screening_csv = f"{base}/screening/abstract_screening.csv"
    df = pd.read_csv(screening_csv)
    included = df[df["ai4epi_abstract_decision"].astype(str).str.lower().str.contains("include", na=False)]
    included_ids = set(included["article_id"].astype(str))

    # Evidence grades
    evidence_path = f"{base}/evidence/evidence_grades.json"
    with open(evidence_path) as f:
        evidence = json.load(f)
    evidence_by_id = {e["article_id"]: e for e in evidence}

    # Contradictions (only flagged ones)
    contradiction_path = f"{base}/contradiction/contradiction_results.json"
    with open(contradiction_path) as f:
        contradictions = json.load(f)
    flagged_contradictions = [c for c in contradictions if c.get("has_contradiction")]

    return included, included_ids, evidence_by_id, flagged_contradictions

def build_context(included, evidence_by_id, flagged_contradictions):
    lines = ["=== INCLUDED PAPERS WITH EVIDENCE GRADES ==="]
    for _, row in included.iterrows():
        aid = str(row["article_id"])
        ev = evidence_by_id.get(aid, {})
        lines.append(
            f"\n- TITLE: {row['title']}\n"
            f"  ABSTRACT: {str(row['abstract'])[:300]}...\n"
            f"  CEBM LEVEL: {ev.get('cebm_level', 'N/A')} ({ev.get('cebm_label', 'N/A')})\n"
            f"  STUDY DESIGN: {ev.get('study_design', 'N/A')}"
        )

    lines.append("\n\n=== DETECTED CONTRADICTIONS ===")
    if flagged_contradictions:
        for c in flagged_contradictions:
            lines.append(
                f"\n- {c['paper_a_title']} vs {c['paper_b_title']}\n"
                f"  Severity: {c['severity']}\n"
                f"  Description: {c.get('description', '')[:300]}"
            )
    else:
        lines.append("\nNo contradictions detected among included papers.")

    return "\n".join(lines)

with open("evaluation/benchmark/cochrane_benchmark.json") as f:
    questions = json.load(f)

results = []
condition_cache = {}

for i, q in enumerate(questions):
    print(f"[{i+1}/30] {q['id']} - {q['condition']}")
    condition = q["condition"]

    if condition not in condition_cache:
        try:
            condition_cache[condition] = load_condition_data(condition)
        except Exception as e:
            print(f"  Failed to load data for {condition}: {e}")
            condition_cache[condition] = None

    data = condition_cache[condition]
    if data is None:
        response = "ERROR: Could not load pipeline data for this condition."
    else:
        included, included_ids, evidence_by_id, flagged_contradictions = data
        context = build_context(included, evidence_by_id, flagged_contradictions)

        try:
            api_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": (
                        "You are NeuroSLR, a neurology-specialised systematic review system. "
                        "Answer the question using ONLY the pipeline evidence provided below. "
                        "Cite CEBM evidence levels where relevant. If the evidence is insufficient "
                        "to fully answer, say so explicitly. Keep answers to 3-5 sentences."
                    )},
                    {"role": "user", "content": f"QUESTION: {q['question']}\n\nPIPELINE EVIDENCE:\n{context}"}
                ],
                max_tokens=500,
                temperature=0.1
            )
            response = api_response.choices[0].message.content.strip()
        except Exception as e:
            response = f"ERROR: {str(e)}"
            print(f"  Error: {e}")

    results.append({
        "id": q["id"],
        "condition": q["condition"],
        "question": q["question"],
        "baseline": "B4_neuroslr",
        "response": response,
        "timestamp": datetime.now().isoformat()
    })
    time.sleep(1)

out_file = f"evaluation/results/B4_neuroslr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(out_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Saved to {out_file}")
