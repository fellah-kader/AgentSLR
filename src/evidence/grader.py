# src/evidence/grader.py
"""
NeuroSLR Evidence Grader
Automatically assigns CEBM Level of Evidence (1-5) to included neurology papers.
This is a novel component not present in the original AgentSLR system.

CEBM Hierarchy:
Level 1 - Systematic reviews / meta-analyses of RCTs
Level 2 - Individual RCTs
Level 3 - Cohort studies
Level 4 - Case-control studies
Level 5 - Case reports, expert opinion, animal studies
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EvidenceGrade:
    """Stores the evidence grade result for a single paper."""
    article_id: str
    title: str
    cebm_level: int          # 1 to 5
    cebm_label: str          # human readable label
    study_design: str        # e.g. "Randomised Controlled Trial"
    sample_size: str         # e.g. "n=245" or "unknown"
    justification: str       # why this level was assigned
    confidence: float        # 0.0 to 1.0


CEBM_LABELS = {
    1: "Systematic Review / Meta-Analysis of RCTs",
    2: "Randomised Controlled Trial (RCT)",
    3: "Cohort Study",
    4: "Case-Control Study",
    5: "Case Report / Expert Opinion / Animal Study",
}


def build_grading_prompt(paper: dict, condition: str) -> str:
    """Builds the prompt sent to the LLM to grade evidence level."""
    return f"""You are an expert in evidence-based medicine specialising in neurology.

Your task is to assign a CEBM (Centre for Evidence-Based Medicine) Level of Evidence to the following paper about {condition}.

## Paper
Title: {paper.get('title', 'Unknown')}
Abstract: {paper.get('abstract', 'No abstract available')}

## CEBM Levels of Evidence
Level 1: Systematic review or meta-analysis of randomised controlled trials (RCTs)
Level 2: Individual randomised controlled trial (RCT)
Level 3: Cohort study (prospective or retrospective, observational)
Level 4: Case-control study
Level 5: Case report, case series, expert opinion, animal study, or in-vitro study

## Instructions
Read the abstract carefully and determine:
1. What type of study is this? (RCT, cohort, case-control, systematic review, etc.)
2. What is the sample size if mentioned?
3. Which CEBM level best fits this study design?

Respond ONLY with a valid JSON object in exactly this format:
{{
    "cebm_level": 1, 2, 3, 4, or 5,
    "cebm_label": "exact label from the levels above",
    "study_design": "specific study design e.g. Randomised Controlled Trial",
    "sample_size": "e.g. n=245 or unknown if not mentioned",
    "justification": "1-2 sentences explaining why this level was assigned",
    "confidence": 0.0 to 1.0
}}

Do not include any text outside the JSON object.
"""


def parse_grade_response(response_text: str) -> dict:
    """Safely parses the LLM JSON response for evidence grading."""
    try:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning(f"Failed to parse evidence grade response: {e}")
        return {
            "cebm_level": 5,
            "cebm_label": CEBM_LABELS[5],
            "study_design": "unknown",
            "sample_size": "unknown",
            "justification": "Could not parse LLM response - defaulting to Level 5",
            "confidence": 0.0,
        }


def grade_paper(paper: dict, condition: str, llm_client) -> EvidenceGrade:
    """
    Grades a single paper using CEBM levels.

    Args:
        paper: dict with keys 'article_id', 'title', 'abstract'
        condition: neurological condition e.g. 'alzheimers'
        llm_client: OpenAI-compatible client (Groq)

    Returns:
        EvidenceGrade dataclass
    """
    prompt = build_grading_prompt(paper, condition)
    logger.info(f"Grading evidence for: {paper.get('article_id')}")

    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
        )
        response_text = response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed for grading: {e}")
        response_text = "{}"

    parsed = parse_grade_response(response_text)
    cebm_level = int(parsed.get("cebm_level", 5))

    return EvidenceGrade(
        article_id=paper.get("article_id", "unknown"),
        title=paper.get("title", "Unknown"),
        cebm_level=cebm_level,
        cebm_label=parsed.get("cebm_label", CEBM_LABELS.get(cebm_level, "Unknown")),
        study_design=parsed.get("study_design", "unknown"),
        sample_size=parsed.get("sample_size", "unknown"),
        justification=parsed.get("justification", ""),
        confidence=float(parsed.get("confidence", 0.0)),
    )


def grade_all_papers(
    included_papers: list[dict],
    condition: str,
    llm_client,
) -> list[EvidenceGrade]:
    """
    Grades all included papers for evidence level.

    Args:
        included_papers: list of paper dicts from abstract screening
        condition: neurological condition
        llm_client: OpenAI-compatible client

    Returns:
        List of EvidenceGrade objects
    """
    results = []
    for paper in included_papers:
        grade = grade_paper(paper, condition, llm_client)
        results.append(grade)
        logger.info(
            f"Graded {grade.article_id}: "
            f"CEBM Level {grade.cebm_level} — {grade.study_design}"
        )

    # Summary statistics
    from collections import Counter
    level_counts = Counter(g.cebm_level for g in results)
    logger.info(f"Evidence grading complete: {len(results)} papers graded")
    for level in sorted(level_counts.keys()):
        logger.info(f"  Level {level} ({CEBM_LABELS[level]}): {level_counts[level]} papers")

    return results
