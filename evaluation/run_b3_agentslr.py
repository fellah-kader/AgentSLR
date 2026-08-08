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

def load_screening_only(condition):
    screening_csv = f"data/agentslr/client/oss/{condition}/screening/abstract_screening.csv"
    df = pd.read_csv(screening_csv)
    included = df[df["ai4epi_abstract_decision"].astype(str).str.lower().str.contains("include", na=False)]
    return included

def build_generic_context(included):
    lines = ["=== INCLUDED PAPERS (no evidence grading, no contradiction analysis) ==="]
    for _, row in included.iterrows():
        lines.append(
            f"\n- TITLE: {row['title']}\n"
            f"  ABSTRACT: {str(row['abstract'])[:300]}..."
        )
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
            condition_cache[condition] = load_screening_only(condition)
        except Exception as e:
            print(f"  Failed to load data for {condition}: {e}")
            condition_cache[condition] = None

    data = condition_cache[condition]
    if data is None:
        response = "ERROR: Could not load pipeline data for this condition."
    else:
        context = build_generic_context(data)

        try:
            api_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": (
                        "You are a general-purpose systematic literature review assistant. "
                        "You have access to screened research papers but NO evidence grading "
                        "and NO contradiction analysis. Answer the question based on the "
                        "paper abstracts provided. If the papers do not contain sufficient "
                        "information to answer, say so. Keep answers to 3-5 sentences."
                    )},
                    {"role": "user", "content": f"QUESTION: {q['question']}\n\nSCREENED PAPERS:\n{context}"}
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
        "baseline": "B3_agentslr_original",
        "response": response,
        "timestamp": datetime.now().isoformat()
    })
    time.sleep(1)

out_file = f"evaluation/results/B3_agentslr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(out_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Saved to {out_file}")
