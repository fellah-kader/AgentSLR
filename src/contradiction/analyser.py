# src/contradiction/analyser.py
"""
NeuroSLR Contradiction Analyser
Identifies when two neurology studies report conflicting findings.
This is a novel component not present in the original AgentSLR system.
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Contradiction severity levels
SEVERITY_NONE = "none"
SEVERITY_MINOR = "minor"
SEVERITY_MODERATE = "moderate"
SEVERITY_MAJOR = "major"


@dataclass
class ContradictionResult:
    """Stores the result of comparing two papers for contradictions."""
    paper_a_id: str
    paper_b_id: str
    paper_a_title: str
    paper_b_title: str
    has_contradiction: bool
    severity: str          # none / minor / moderate / major
    contradiction_type: str  # e.g. "effect direction", "effect size", "population"
    description: str       # plain English explanation of the contradiction
    paper_a_claim: str     # what paper A says
    paper_b_claim: str     # what paper B says
    confidence: float      # 0.0 to 1.0 — how confident the AI is


def build_contradiction_prompt(paper_a: dict, paper_b: dict, condition: str) -> str:
    """
    Builds the prompt sent to the LLM to detect contradictions.
    Takes two paper dictionaries and the neurological condition being reviewed.
    """
    return f"""You are an expert neurologist and systematic review specialist analysing two research papers about {condition}.

Your task is to determine whether these two papers report CONTRADICTORY findings.

## Paper A
Title: {paper_a.get('title', 'Unknown')}
Abstract: {paper_a.get('abstract', 'No abstract available')}

## Paper B  
Title: {paper_b.get('title', 'Unknown')}
Abstract: {paper_b.get('abstract', 'No abstract available')}

## Instructions
Carefully compare the two papers and determine:
1. Do they make claims about the same intervention, treatment, or biological mechanism?
2. If yes, do their findings AGREE or CONTRADICT each other?
3. How severe is any contradiction?

A contradiction exists when:
- Paper A reports a treatment is effective but Paper B reports it is ineffective
- Paper A reports a biomarker increases but Paper B reports it decreases
- Papers report significantly different effect sizes for the same outcome
- Papers reach opposite conclusions about the same clinical question

Severity levels:
- none: No contradiction, papers agree or study different things
- minor: Small numerical differences, same overall conclusion
- moderate: Different conclusions but both plausible given methodology
- major: Directly opposite conclusions on same outcome

Respond ONLY with a valid JSON object in exactly this format:
{{
    "has_contradiction": true or false,
    "severity": "none" or "minor" or "moderate" or "major",
    "contradiction_type": "brief type e.g. effect direction / effect size / population / biomarker",
    "description": "plain English explanation of the contradiction in 2-3 sentences",
    "paper_a_claim": "what Paper A specifically claims",
    "paper_b_claim": "what Paper B specifically claims",
    "confidence": 0.0 to 1.0
}}

Do not include any text outside the JSON object.
"""


def parse_contradiction_response(response_text: str) -> dict:
    """
    Safely parses the LLM JSON response.
    Returns a default 'no contradiction' result if parsing fails.
    """
    try:
        # Strip any accidental markdown fences
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, IndexError) as e:
        logger.warning(f"Failed to parse contradiction response: {e}")
        return {
            "has_contradiction": False,
            "severity": SEVERITY_NONE,
            "contradiction_type": "parse_error",
            "description": "Could not parse LLM response",
            "paper_a_claim": "",
            "paper_b_claim": "",
            "confidence": 0.0,
        }


def analyse_pair(
    paper_a: dict,
    paper_b: dict,
    condition: str,
    llm_client,
) -> ContradictionResult:
    """
    Analyses a pair of papers for contradictions.
    
    Args:
        paper_a: dict with keys 'article_id', 'title', 'abstract'
        paper_b: dict with keys 'article_id', 'title', 'abstract'
        condition: neurological condition e.g. 'alzheimers'
        llm_client: OpenAI-compatible client (Groq)
    
    Returns:
        ContradictionResult dataclass
    """
    prompt = build_contradiction_prompt(paper_a, paper_b, condition)

    logger.info(f"Analysing contradiction: {paper_a.get('article_id')} vs {paper_b.get('article_id')}")

    try:
        response = llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.1,  # Low temperature for consistent structured output
        )
        response_text = response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        response_text = "{}"

    parsed = parse_contradiction_response(response_text)

    return ContradictionResult(
        paper_a_id=paper_a.get("article_id", "unknown"),
        paper_b_id=paper_b.get("article_id", "unknown"),
        paper_a_title=paper_a.get("title", "Unknown"),
        paper_b_title=paper_b.get("title", "Unknown"),
        has_contradiction=parsed.get("has_contradiction", False),
        severity=parsed.get("severity", SEVERITY_NONE),
        contradiction_type=parsed.get("contradiction_type", "unknown"),
        description=parsed.get("description", ""),
        paper_a_claim=parsed.get("paper_a_claim", ""),
        paper_b_claim=parsed.get("paper_b_claim", ""),
        confidence=float(parsed.get("confidence", 0.0)),
    )


def analyse_all_pairs(
    included_papers: list[dict],
    condition: str,
    llm_client,
    max_pairs: int = 50,
) -> list[ContradictionResult]:
    """
    Runs contradiction analysis across all pairs of included papers.
    
    Args:
        included_papers: list of paper dicts from abstract screening
        condition: neurological condition
        llm_client: OpenAI-compatible client
        max_pairs: maximum number of pairs to analyse (default 50)
    
    Returns:
        List of ContradictionResult objects
    """
    results = []
    pairs_analysed = 0

    for i in range(len(included_papers)):
        for j in range(i + 1, len(included_papers)):
            if pairs_analysed >= max_pairs:
                logger.info(f"Reached max_pairs limit of {max_pairs}")
                return results

            result = analyse_pair(
                included_papers[i],
                included_papers[j],
                condition,
                llm_client,
            )
            results.append(result)
            pairs_analysed += 1

            if result.has_contradiction:
                logger.info(
                    f"CONTRADICTION FOUND [{result.severity}]: "
                    f"{result.paper_a_id} vs {result.paper_b_id} — {result.contradiction_type}"
                )

    logger.info(f"Contradiction analysis complete: {pairs_analysed} pairs, "
                f"{sum(1 for r in results if r.has_contradiction)} contradictions found")
    return results
