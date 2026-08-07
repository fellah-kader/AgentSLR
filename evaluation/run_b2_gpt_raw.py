import json
import os
import time
from datetime import datetime
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

with open("evaluation/benchmark/cochrane_benchmark.json") as f:
    questions = json.load(f)

results = []
for i, q in enumerate(questions):
    print(f"[{i+1}/30] {q['id']} - {q['condition']}")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a neurology research assistant. Answer based on systematic review evidence. Be specific about effect sizes and study details where possible. Keep answers to 3-5 sentences."},
                {"role": "user", "content": q["question"]}
            ],
            max_tokens=400,
            temperature=0.1
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"ERROR: {str(e)}"
        print(f"  Error: {e}")

    results.append({
        "id": q["id"],
        "condition": q["condition"],
        "question": q["question"],
        "baseline": "B2_gpt_raw",
        "response": answer,
        "timestamp": datetime.now().isoformat()
    })
    time.sleep(1)

out_file = f"evaluation/results/B2_gpt_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(out_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. Saved to {out_file}")
