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
    benchmark = json.load(f)
gold_by_id = {q["id"]: q for q in benchmark}

JUDGE_PROMPT = """You are an expert systematic review evaluator. Compare the SYSTEM RESPONSE against the GOLD STANDARD ANSWER and KEY FINDINGS.

Score these 4 metrics:

1. SYNTHESIS_COMPLETENESS (0-100): What percentage of the KEY FINDINGS from the gold answer are captured in the response? If the response says "insufficient evidence" or similar, this should be low.

2. FACTUAL_ACCURACY (0-100): Of the claims the response DID make, what percentage are factually correct according to the gold standard? If the response made no claims (e.g. said "insufficient evidence"), score 100 because it made zero incorrect claims.

3. HALLUCINATION_COUNT (integer 0+): How many specific claims in the response are fabricated, invented, or not supported by the gold standard? Examples: made-up statistics, invented effect sizes, false study details. If the response declined to answer, this should be 0.

4. EPISTEMIC_HONESTY (0 or 1): Did the response appropriately express uncertainty or acknowledge evidence limitations? Score 1 if: (a) it correctly identified when it lacked evidence to answer, OR (b) it answered correctly with appropriate confidence. Score 0 if: it stated fabricated information as fact without hedging.

Respond ONLY with valid JSON:
{"synthesis_completeness": <0-100>, "factual_accuracy": <0-100>, "hallucination_count": <integer>, "epistemic_honesty": <0 or 1>, "reasoning": "<brief 1-2 sentence explanation>"}"""

def score_baseline(result_file):
    with open(result_file) as f:
        results = json.load(f)

    baseline_name = results[0]["baseline"]
    print(f"\nScoring: {baseline_name} ({len(results)} responses)")
    print("-" * 50)

    scores = []
    for r in results:
        gold = gold_by_id.get(r["id"])
        if not gold:
            continue

        key_findings_text = "\n".join(f"- {kf}" for kf in gold["key_facts"])

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": JUDGE_PROMPT},
                    {"role": "user", "content": (
                        f"QUESTION: {r['question']}\n\n"
                        f"GOLD STANDARD ANSWER: {gold['cochrane_answer']}\n\n"
                        f"KEY FINDINGS TO CHECK:\n{key_findings_text}\n\n"
                        f"SYSTEM RESPONSE: {r['response']}"
                    )}
                ],
                max_tokens=300,
                temperature=0.0
            )
            judge_text = response.choices[0].message.content.strip()
            judge_text = judge_text.replace("```json", "").replace("```", "").strip()
            score_data = json.loads(judge_text)
        except Exception as e:
            print(f"  Error scoring {r['id']}: {e}")
            score_data = {
                "synthesis_completeness": 0,
                "factual_accuracy": 0,
                "hallucination_count": 0,
                "epistemic_honesty": 0,
                "reasoning": f"Scoring error: {str(e)}"
            }

        scores.append({"id": r["id"], "condition": r["condition"], **score_data})
        sc = score_data
        print(f"  [{r['id']}] Complete: {sc['synthesis_completeness']:3d}%  "
              f"Accurate: {sc['factual_accuracy']:3d}%  "
              f"Halluc: {sc['hallucination_count']}  "
              f"Honest: {sc['epistemic_honesty']}")
        time.sleep(0.5)

    # Compute aggregates
    n = len(scores)
    avg_complete = sum(s["synthesis_completeness"] for s in scores) / n
    avg_accuracy = sum(s["factual_accuracy"] for s in scores) / n
    total_halluc = sum(s["hallucination_count"] for s in scores)
    avg_honesty = sum(s["epistemic_honesty"] for s in scores) / n

    # Per-condition breakdown
    conditions = ["alzheimers", "parkinsons", "multiple_sclerosis", "epilepsy", "stroke"]
    per_condition = {}
    for cond in conditions:
        cond_scores = [s for s in scores if s["condition"] == cond]
        if cond_scores:
            per_condition[cond] = {
                "avg_completeness": round(sum(s["synthesis_completeness"] for s in cond_scores) / len(cond_scores), 1),
                "avg_accuracy": round(sum(s["factual_accuracy"] for s in cond_scores) / len(cond_scores), 1),
                "total_hallucinations": sum(s["hallucination_count"] for s in cond_scores),
                "avg_honesty": round(sum(s["epistemic_honesty"] for s in cond_scores) / len(cond_scores), 2)
            }

    summary = {
        "baseline": baseline_name,
        "overall": {
            "avg_completeness": round(avg_complete, 1),
            "avg_accuracy": round(avg_accuracy, 1),
            "total_hallucinations": total_halluc,
            "avg_epistemic_honesty": round(avg_honesty, 2)
        },
        "per_condition": per_condition,
        "per_question": scores
    }

    print(f"\n{'=' * 50}")
    print(f"  {baseline_name} SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Synthesis Completeness:  {avg_complete:.1f}%")
    print(f"  Factual Accuracy:        {avg_accuracy:.1f}%")
    print(f"  Total Hallucinations:    {total_halluc}")
    print(f"  Epistemic Honesty:       {avg_honesty:.0%}")
    print(f"{'=' * 50}")

    return summary

# Find all result files and score them
import glob
result_files = sorted(glob.glob("evaluation/results/B*.json"))
all_summaries = {}

for rf in result_files:
    if "scores" in rf.lower():
        continue
    summary = score_baseline(rf)
    all_summaries[summary["baseline"]] = summary

# Save all scores
out_file = f"evaluation/results/scores_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(out_file, "w") as f:
    json.dump(all_summaries, f, indent=2)

# Print comparison table
print(f"\n{'=' * 75}")
print("FINAL COMPARISON TABLE")
print(f"{'=' * 75}")
print(f"{'Baseline':<22} {'Complete':>10} {'Accuracy':>10} {'Halluc':>8} {'Honesty':>9}")
print("-" * 60)
for name, s in all_summaries.items():
    o = s["overall"]
    print(f"{name:<22} {o['avg_completeness']:>9.1f}% {o['avg_accuracy']:>9.1f}% "
          f"{o['total_hallucinations']:>7} {o['avg_epistemic_honesty']:>8.0%}")
print(f"{'=' * 75}")
print(f"\nAll scores saved to: {out_file}")
