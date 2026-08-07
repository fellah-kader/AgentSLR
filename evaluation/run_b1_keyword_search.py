import json
import pandas as pd
from datetime import datetime
from pathlib import Path

STOPWORDS = {
    "does","do","is","are","the","a","an","in","of","for","to","with","and",
    "or","vs","versus","compared","comparing","what","which","how","when",
    "more","most","less","than","can","has","have","been","be","that","this",
    "from","by","on","at","as","it","its","there","their","after","before",
    "between","about","into","through","during","each","all","both","no",
    "not","only","other","some","such","any","first","also","should",
    "would","could","may","might","using","use","score"
}

def extract_keywords(question):
    words = question.lower().replace("?", "").replace(",", "").replace("(", "").replace(")", "").split()
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return keywords[:8]

def search_condition(condition, keywords, top_n=3):
    csv_path = f"data/agentslr/harvests/{condition}/harvest_metadata.csv"
    df = pd.read_csv(csv_path, usecols=["title", "abstract"])
    df = df.dropna(subset=["abstract"])

    def score_row(row):
        text = f"{row['title']} {row['abstract']}".lower()
        return sum(1 for kw in keywords if kw in text)

    df["match_score"] = df.apply(score_row, axis=1)
    top_matches = df[df["match_score"] > 0].sort_values("match_score", ascending=False).head(top_n)

    snippets = []
    for _, row in top_matches.iterrows():
        snippet = f"TITLE: {row['title']}\nABSTRACT: {str(row['abstract'])[:400]}..."
        snippets.append(snippet)
    return snippets

with open("evaluation/benchmark/cochrane_benchmark.json") as f:
    questions = json.load(f)

results = []
for i, q in enumerate(questions):
    print(f"[{i+1}/30] {q['id']} - {q['condition']}")
    keywords = extract_keywords(q["question"])
    try:
        snippets = search_condition(q["condition"], keywords)
        response = "\n---\n".join(snippets) if snippets else "No matching papers found via keyword search."
    except Exception as e:
        response = f"ERROR: {str(e)}"
        print(f"  Error: {e}")

    results.append({
        "id": q["id"],
        "condition": q["condition"],
        "question": q["question"],
        "baseline": "B1_keyword_search",
        "keywords_used": keywords,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })

out_file = f"evaluation/results/B1_keyword_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(out_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Saved to {out_file}")
