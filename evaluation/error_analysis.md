# NeuroSLR Error Analysis

## Overview
Five representative cases were selected from the 30-question Cochrane benchmark
to illustrate key patterns in baseline behaviour: hallucination, epistemic honesty,
and the contribution of NeuroSLR's novel components.

---

## Case 1: ST2 — B4 answers correctly where B3 cannot
**Question:** Within what time window is alteplase licensed for use in acute ischaemic stroke?
**Gold answer:** 4.5 hours in Europe, 3 hours in USA/Canada

- **B2 (Raw GPT):** Correct (4.5 hours) — but from training memory, not evidence
- **B3 (Ablation):** "Cannot answer based on available information"
- **B4 (NeuroSLR):** Correct (4.5 hours) — grounded in pipeline evidence

**Analysis:** Both B3 and B4 had access to the same screened papers, but B4's
evidence grading enabled it to identify and synthesise from the relevant source.
This demonstrates the Contradiction Analyser and Evidence Grader's contribution
to synthesis quality (+100% completeness improvement over B3).

---

## Case 2: MS3 — B2 hallucinates a dangerously wrong clinical answer
**Question:** Is there evidence of benefit from interferon beta or glatiramer acetate beyond 1 year?
**Gold answer:** No — no evidence of benefit beyond 1 year

- **B2 (Raw GPT):** "Yes, there IS evidence supporting continued benefit" (WRONG — 5 hallucinations)
- **B3 (Ablation):** "Insufficient information" (honest)
- **B4 (NeuroSLR):** "Does not specifically address long-term benefits" (honest)

**Analysis:** This is the most clinically dangerous case in our evaluation. B2
confidently stated the opposite of the Cochrane finding. In a clinical decision
context, this could lead to unnecessary prolonged treatment. Both B3 and B4
correctly identified their evidence limitations rather than fabricating an answer.

---

## Case 3: AD3 — B2 fabricates a positive finding that does not exist
**Question:** Does donepezil improve patient-reported quality of life?
**Gold answer:** No — no effect on quality of life despite cognitive improvements

- **B2 (Raw GPT):** "Small to moderate improvement in quality of life" (FABRICATED)
- **B3 (Ablation):** "Insufficient information" (honest)
- **B4 (NeuroSLR):** "Insufficient evidence" (honest)

**Analysis:** B2 invented a positive finding directly contradicting Cochrane evidence.
This pattern — confidently reporting effects that systematic reviews have found to
be absent — represents a fundamental reliability risk of unconditioned LLM use in
evidence synthesis.

---

## Case 4: MS4 — B4 synthesises where B3 cannot
**Question:** Do DMTs reduce disability progression in relapsing-remitting MS?
**Gold answer:** Yes (RR 0.72, 95% CI 0.66-0.79)

- **B2 (Raw GPT):** Correct but without specific effect sizes
- **B3 (Ablation):** "Do not provide sufficient information"
- **B4 (NeuroSLR):** Correctly identifies DMTs reduce relapse rates with evidence support

**Analysis:** B4 achieved 75% completeness vs B3's 0% on the same paper set,
demonstrating that evidence grading and contradiction analysis enable more
effective synthesis from identical inputs.

---

## Case 5: EP5 — B4 adds evidence grading context
**Question:** What percentage of people with epilepsy experience drug-resistant seizures?
**Gold answer:** Approximately 30%

- **B2 (Raw GPT):** Correct (30%)
- **B3 (Ablation):** Correct (one-third)
- **B4 (NeuroSLR):** Correct (one-third) AND cites CEBM Level 5

**Analysis:** All retrieval-based systems answered correctly, but only B4 provided
the CEBM evidence level, giving the clinician a trustworthiness signal alongside
the finding. This demonstrates the Evidence Grader's unique value — not just
answering, but qualifying the strength of evidence behind the answer.

---

## Summary of Error Patterns

| Pattern | B1 | B2 | B3 | B4 |
|---------|----|----|----|----|
| Fabricates clinical findings | No | Yes (42 cases) | Rare (2 cases) | Rare (4 cases) |
| Admits evidence gaps honestly | Sometimes | Rarely | Yes | Yes |
| Cites evidence strength | No | No | No | Yes (CEBM levels) |
| Answers when evidence exists | No | Yes (from memory) | Sometimes | More often than B3 |
